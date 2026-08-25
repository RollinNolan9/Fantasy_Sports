"""Post-process the v2 board into league-specific draft ranks.

Does not retrain model.py. Reads projections_{year}.csv, applies depth-chart
role facts, then ranks with a lineup optimizer instead of per-position
replacement.

python3 valuation.py [year]
"""
import json
import sys
from datetime import date, datetime

import pandas as pd

from projections import BONUSES, GAMES, PLAYOFF_WEEKS, SCORING, score_stat

# League: keep in sync with model.py. valuation does not import model (sklearn).
TEAMS = 14
SLOTS = {"QB": 2, "RB": 2, "WR": 2, "K": 1, "DST": 1}
FLEX = 2
FLEX_ELIGIBLE = {"RB", "WR", "TE"}
QB_BACKUP = 0.25
ROLE_ALIAS = {"contested": 0.70}

# --- league / scoring (documented defaults; do not invent extras) ---
EXPECTED_QBS_ROSTERED_PER_TEAM = 3.0
QB_ROSTERED_SENSITIVITY = (28, 35, 42)
NAMED_QB_STARTER_PRIOR_FRAC = 0.90  # of unmodified QB29 12-game points
NAMED_QB_PRIOR_WEIGHT_LOW_ROLE = 0.75  # model never treated them as the starter
NAMED_QB_PRIOR_WEIGHT = 0.50
COPILOT_SHARE = 0.70          # RB committee loser keeps this share of the lead
QB_SPLIT_PRIMARY = 0.70       # dual-QB winner snap share; loser 1-this
QB_SPLIT_P = 0.50             # P(each is the primary); must sum to 1 with 1-P
CONTESTED_ROLE = ROLE_ALIAS["contested"]
DEPTH_STALE_DAYS = 14
AS_OF = date(2026, 8, 25)
TOLERANCE_TEAM_SHARE = 0.02
N_STARTERS_OFFENSE = TEAMS * (SLOTS["QB"] + SLOTS["RB"] + SLOTS["WR"] + FLEX)

assert abs(QB_SPLIT_P + (1 - QB_SPLIT_P) - 1.0) < 1e-12
assert SLOTS.get("TE", 0) == 0 or "TE" not in SLOTS


def n_qb_starters():
    return SLOTS["QB"] * TEAMS


def n_skill_starters():
    return (SLOTS["RB"] + SLOTS["WR"] + FLEX) * TEAMS


def min_rb_starters():
    return SLOTS["RB"] * TEAMS


def min_wr_starters():
    return SLOTS["WR"] * TEAMS


def load_overrides(path="overrides.csv"):
    ov = pd.read_csv(path)
    role_n = ov["role"].map(lambda x: ROLE_ALIAS.get(str(x).strip().lower(),
                            pd.to_numeric(x, errors="coerce")))
    ov = ov.copy()
    ov["role_n"] = role_n
    return ov


def load_depth(path="depth_chart.csv"):
    try:
        d = pd.read_csv(path, dtype={"player_id": str})
    except FileNotFoundError:
        return pd.DataFrame()
    d["player_id"] = d["player_id"].astype(str)
    return d


def attach_availability(df, ov):
    games_ov = dict(zip(ov["name"], ov["games"])) if "games" in ov.columns else {}
    out = df.copy()
    out["projected_games"] = out["name"].map(games_ov)
    out["projected_games"] = pd.to_numeric(out["projected_games"], errors="coerce").fillna(GAMES)
    out["projected_active_games"] = out["projected_games"]
    out["projected_games_available"] = out["projected_games"]
    out["active_frac"] = (out["projected_games"] / GAMES).clip(0, 1)
    return out


def pts_full_role(df):
    """Undo games scale and the role scalar so role-1 12-game points are available."""
    role = df["role"].clip(lower=0.01)
    return (df["proj_points"] / df["active_frac"].clip(lower=1 / GAMES) / role)


def apply_roles(df, ov):
    """Scale 12-game points to the latest override role; lock named-QB backups."""
    desired = dict(zip(ov["name"], ov["role_n"]))
    qb_names = set(df.loc[df["position"] == "QB", "name"])
    named_qb = set(ov.loc[ov["role_n"] == 1, "name"]) & qb_names
    named_teams = set(df.loc[df["name"].isin(named_qb) & (df["position"] == "QB"), "team"])

    out = df.copy()
    out["pts_full"] = pts_full_role(out)
    out["role_in"] = out["role"]
    new_role = out["name"].map(desired).astype(float)
    # lock non-named QBs on a named-starter team
    backup = ((out["position"] == "QB") & out["team"].isin(named_teams)
              & ~out["name"].isin(named_qb))
    new_role = new_role.where(~backup, QB_BACKUP)
    new_role = new_role.fillna(out["role"])
    out["role"] = new_role.round(2)
    out["pts12"] = (out["pts_full"] * out["role"]).round(4)
    out["named_starter"] = out["name"].isin(named_qb) | (
        (out["position"] != "QB") & out["name"].map(desired).eq(1)
    )
    out["contested"] = out["name"].isin(set(ov.loc[ov["role"].astype(str).str.lower().eq("contested"), "name"]))
    return out, named_qb


def _pair_groups(df, positions, contested_only=True):
    d = df[df["position"].isin(positions)]
    if contested_only:
        d = d[d["contested"]]
    groups = []
    for (team, pos), g in d.groupby(["team", "position"]):
        if len(g) == 2:
            groups.append(g)
    return groups


def apply_rb_committee_scenarios(df):
    """Two contested RBs: 50/50 who leads; loser keeps COPILOT_SHARE of the lead.

    Expected room total = lead_full + copilot, not two copilot discounts.
    """
    out = df.copy()
    out["pts12"] = out["pts12"].astype(float)
    out["pts_full"] = out["pts_full"].astype(float)
    out["scenario_p"] = 1.0
    out["p10"] = out["pts12"]
    out["p25"] = out["pts12"]
    out["p50"] = out["pts12"]
    out["p75"] = out["pts12"]
    out["p90"] = out["pts12"]
    out["starter_probability"] = out["role"].clip(0, 1)
    out["expected_opportunity_share"] = out["role"]
    out["role_confidence"] = out["role"].clip(0, 1)
    out["breakout_probability"] = 0.0

    for g in _pair_groups(out, ["RB"]):
        ids = list(g.index)
        full = {i: float(out.at[i, "pts_full"]) for i in ids}
        a, b = ids

        def cond(lead, trail):
            lp, tp = full[lead], full[trail]
            return lp, min(tp, COPILOT_SHARE * lp)

        a_lead, b_trail = cond(a, b)
        b_lead, a_trail = cond(b, a)
        p = 0.5
        exp_a = p * a_lead + (1 - p) * a_trail
        exp_b = p * b_trail + (1 - p) * b_lead
        for i, exp, hi, lo in (
            (a, exp_a, max(a_lead, a_trail), min(a_lead, a_trail)),
            (b, exp_b, max(b_lead, b_trail), min(b_lead, b_trail)),
        ):
            out.at[i, "pts12"] = exp
            out.at[i, "p10"] = lo
            out.at[i, "p25"] = 0.5 * lo + 0.5 * exp
            out.at[i, "p50"] = exp
            out.at[i, "p75"] = 0.5 * hi + 0.5 * exp
            out.at[i, "p90"] = hi
            out.at[i, "starter_probability"] = p
            out.at[i, "expected_opportunity_share"] = exp / max(full[i], 1e-9)
            out.at[i, "role_confidence"] = 0.50
            out.at[i, "scenario_p"] = 1.0  # the two scenarios sum to 1; stored per player
            out.at[i, "breakout_probability"] = round(p, 3)
            out.at[i, "role"] = round(exp / max(full[i], 1e-9), 2)
        # room share check attached for tests
        out.at[a, "_room_expected"] = exp_a + exp_b
        out.at[b, "_room_expected"] = exp_a + exp_b
        out.at[a, "_room_budget"] = max(full[a], full[b]) + COPILOT_SHARE * max(full[a], full[b])
    return out


def apply_qb_split_scenarios(df):
    """Two contested QBs share one passing job. Snap shares sum to 1.0 per scenario."""
    out = df.copy()
    out["pts12"] = out["pts12"].astype(float)
    out["pts_full"] = out["pts_full"].astype(float)
    p_a = QB_SPLIT_P
    share_w, share_l = QB_SPLIT_PRIMARY, 1.0 - QB_SPLIT_PRIMARY
    for g in _pair_groups(out, ["QB"]):
        ids = list(g.index)
        a, b = ids
        fa, fb = out.at[a, "pts_full"], out.at[b, "pts_full"]
        # scenario A: a primary; scenario B: b primary
        a1, b1 = share_w * fa, share_l * fb
        a2, b2 = share_l * fa, share_w * fb
        exp_a = p_a * a1 + (1 - p_a) * a2
        exp_b = p_a * b1 + (1 - p_a) * b2
        for i, exp, hi, lo, full in (
            (a, exp_a, max(a1, a2), min(a1, a2), fa),
            (b, exp_b, max(b1, b2), min(b1, b2), fb),
        ):
            out.at[i, "pts12"] = exp
            out.at[i, "p10"] = lo
            out.at[i, "p25"] = 0.5 * lo + 0.5 * exp
            out.at[i, "p50"] = exp
            out.at[i, "p75"] = 0.5 * hi + 0.5 * exp
            out.at[i, "p90"] = hi
            out.at[i, "starter_probability"] = p_a if i == a else (1 - p_a)
            out.at[i, "expected_opportunity_share"] = exp / max(full, 1e-9)
            out.at[i, "role_confidence"] = 0.50
            out.at[i, "breakout_probability"] = round(share_w * (p_a if i == a else 1 - p_a), 3)
            out.at[i, "role"] = round(exp / max(full, 1e-9), 2)
        # shares sum to 1 in each scenario
        out.at[a, "_qb_share_sum"] = share_w + share_l
        out.at[b, "_qb_share_sum"] = share_w + share_l
    return out


def apply_named_qb_prior(df, qb29_unmodified):
    """Blend a named QB1 toward a starter prior when the ML 12-game is too low.

    Prior = NAMED_QB_STARTER_PRIOR_FRAC * unmodified QB29. Not a rank override.
    """
    prior = NAMED_QB_STARTER_PRIOR_FRAC * qb29_unmodified
    out = df.copy()
    named = out["named_starter"] & (out["position"] == "QB")
    low = named & (out["pts12"] < prior)
    w = pd.Series(NAMED_QB_PRIOR_WEIGHT, index=out.index)
    w = w.where(out["role_in"] >= 0.85, NAMED_QB_PRIOR_WEIGHT_LOW_ROLE)
    blended = (1 - w) * out["pts12"] + w * prior
    out.loc[low, "pts12"] = blended[low]
    out.loc[low, "p50"] = out.loc[low, "pts12"]
    out.loc[low, "p10"] = out.loc[low, "pts12"] * 0.80
    out.loc[low, "p25"] = out.loc[low, "pts12"] * 0.90
    out.loc[low, "p75"] = out.loc[low, "pts12"] * 1.05
    out.loc[low, "p90"] = out.loc[low, "pts12"] * 1.15
    out.loc[low, "role_confidence"] = out.loc[low, "role_confidence"].clip(upper=0.60)
    out.loc[low, "starter_probability"] = out.loc[low, "starter_probability"].clip(lower=0.85)
    out["prior_applied"] = False
    out.loc[low, "prior_applied"] = True
    return out, prior


def apply_availability_bands(df):
    """Missed games stay in managed VORP. Percentiles stay production-when-active.

    P10/P90 for a short-game player are a 3-point games band around the override
    applied to season-raw points, stored back as 12-game equivalents so the
    columns stay comparable. This is not a medical week tree.
    """
    out = df.copy()
    out["injury_confidence"] = 1.0
    short = out["projected_games"] < GAMES
    g = out["projected_games"]
    g10 = (g - 2).clip(lower=1)
    g90 = (g + 1).clip(upper=GAMES)
    pts = out["pts12"]
    out.loc[short, "p10"] = pts[short] * (g10 / g)[short]
    out.loc[short, "p25"] = pts[short] * (((g10 + g) / 2) / g)[short]
    out.loc[short, "p90"] = pts[short] * (g90 / g)[short]
    out.loc[short, "p75"] = pts[short] * (((g90 + g) / 2) / g)[short]
    out.loc[short, "injury_confidence"] = 0.55
    return out


def select_lineup(df, pts_col="pts12", exclude=(), force=()):
    exclude, force = set(exclude), set(force)
    d = df[~df["playerId"].astype(str).isin(exclude)].copy()
    n_qb, n_skill = n_qb_starters(), n_skill_starters()
    min_rb, min_wr = min_rb_starters(), min_wr_starters()
    forced = d[d["playerId"].astype(str).isin(force)]
    rest = d[~d["playerId"].astype(str).isin(force)].sort_values(
        [pts_col, "playerId"], ascending=[False, True])
    chunks = [forced]
    have_qb = int((forced["position"] == "QB").sum())
    chunks.append(rest[rest["position"] == "QB"].head(max(0, n_qb - have_qb)))
    have = pd.concat(chunks)
    skill_rest = rest[rest["position"].isin(FLEX_ELIGIBLE)]
    chunks.append(skill_rest[skill_rest["position"] == "RB"].head(
        max(0, min_rb - int((have["position"] == "RB").sum()))))
    have = pd.concat(chunks)
    chunks.append(skill_rest[skill_rest["position"] == "WR"].head(
        max(0, min_wr - int((have["position"] == "WR").sum()))))
    have = pd.concat(chunks)
    skill_have = int(have["position"].isin(FLEX_ELIGIBLE).sum())
    left = skill_rest[~skill_rest["playerId"].astype(str).isin(set(have["playerId"].astype(str)))]
    chunks.append(left.head(max(0, n_skill - skill_have)))
    sel = pd.concat(chunks).drop_duplicates("playerId")
    return sel


def lineup_counts(sel):
    return {
        "n_qb": int((sel["position"] == "QB").sum()),
        "n_skill": int(sel["position"].isin(FLEX_ELIGIBLE).sum()),
        "n_rb": int((sel["position"] == "RB").sum()),
        "n_wr": int((sel["position"] == "WR").sum()),
        "n_te": int((sel["position"] == "TE").sum()),
    }


def starter_vorps(df, pts_col="pts12"):
    """Leave-one-out / force-in VORP vs the optimal 28-QB + 84-skill lineup."""
    sel = select_lineup(df, pts_col)
    sel_ids = set(sel["playerId"].astype(str))
    n_rb = int((sel["position"] == "RB").sum())
    n_wr = int((sel["position"] == "WR").sum())
    rest = df[~df["playerId"].astype(str).isin(sel_ids)].sort_values(
        [pts_col, "playerId"], ascending=[False, True])
    skill = list(FLEX_ELIGIBLE)
    def first(frame, pred):
        hit = frame[pred(frame)]
        return float(hit.iloc[0][pts_col]) if len(hit) else 0.0

    next_qb = first(rest, lambda x: x["position"] == "QB")
    next_skill = first(rest, lambda x: x["position"].isin(skill))
    next_rb = first(rest, lambda x: x["position"] == "RB")
    next_wr = first(rest, lambda x: x["position"] == "WR")
    skill_sel = sel[sel["position"].isin(skill)]
    worst_qb = float(sel.loc[sel["position"] == "QB", pts_col].min())
    worst_skill = float(skill_sel[pts_col].min())
    worst_non_wr = float(skill_sel.loc[skill_sel["position"] != "WR", pts_col].min())
    worst_non_rb = float(skill_sel.loc[skill_sel["position"] != "RB", pts_col].min())

    vorp = []
    for r in df.itertuples():
        pts = float(getattr(r, pts_col))
        pid = str(r.playerId)
        pos = r.position
        if pid in sel_ids:
            if pos == "QB":
                v = pts - next_qb
            elif pos == "RB" and n_rb <= min_rb_starters():
                v = pts - next_rb
            elif pos == "WR" and n_wr <= min_wr_starters():
                v = pts - next_wr
            else:
                v = pts - next_skill
        else:
            if pos == "QB":
                v = pts - worst_qb
            elif pos == "WR" and n_wr <= min_wr_starters() and n_rb <= min_rb_starters():
                v = pts - worst_skill
            elif pos == "RB" and n_wr <= min_wr_starters():
                v = pts - worst_non_wr
            elif pos == "WR" and n_rb <= min_rb_starters():
                v = pts - worst_non_rb
            else:
                v = pts - worst_skill
        vorp.append(v)
    out = df.copy()
    out["starter_vorp"] = pd.Series(vorp, index=df.index).round(1)
    out["in_lineup"] = out["playerId"].astype(str).isin(sel_ids)
    return out, sel, {"next_qb": next_qb, "next_skill": next_skill,
                      "next_rb": next_rb, "next_wr": next_wr,
                      "worst_qb": worst_qb, "worst_skill": worst_skill}


def qb_cutoffs(df, pts_col="pts12"):
    q = df[df["position"] == "QB"].sort_values([pts_col, "playerId"], ascending=[False, True])
    cuts = {}
    for n in QB_ROSTERED_SENSITIVITY:
        cuts[n] = float(q.iloc[n][pts_col]) if len(q) > n else float(q.iloc[-1][pts_col])
    return cuts, q


def rank_by(df, cols):
    """Unique contiguous ranks. Last key is the stable playerId ascending tiebreak."""
    asc = [False] * (len(cols) - 1) + [True]
    order = df.sort_values(cols, ascending=asc, kind="mergesort")
    return pd.Series(range(1, len(order) + 1), index=order.index)


def freshness_flags(df, depth, as_of=AS_OF):
    flags = []
    if depth.empty:
        return flags
    d = depth.copy()
    d["player_id"] = d["player_id"].astype(str)
    board = df.set_index(df["playerId"].astype(str))
    for r in d.itertuples():
        pid = str(r.player_id)
        try:
            eff = datetime.strptime(str(r.effective_date), "%Y-%m-%d").date()
            age = (as_of - eff).days
        except (TypeError, ValueError):
            eff, age = None, None
        if r.status == "starter" and float(r.starter_probability) < 0.85:
            flags.append({"player": r.name, "flag": "named_starter_low_probability",
                          "detail": f"starter_probability={r.starter_probability}"})
        if age is not None and age > DEPTH_STALE_DAYS:
            flags.append({"player": r.name, "flag": "stale_depth",
                          "detail": f"{age} days since {eff}"})
        if str(r.injury_status) not in ("healthy", "nan", "") and not r.effective_date:
            flags.append({"player": r.name, "flag": "injury_missing_date", "detail": r.injury_status})
        if pid in board.index:
            row = board.loc[pid]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            if r.status == "starter" and row["position"] == r.position:
                teammates = df[(df["team"] == row["team"]) & (df["position"] == r.position)
                               & (df["playerId"].astype(str) != pid)]
                higher = teammates[
                    (teammates["starter_probability"] > float(r.starter_probability) + 1e-9)
                    & (teammates["projected_points_if_active"]
                       > float(row["projected_points_if_active"]) + 1.0)
                ]
                if len(higher):
                    flags.append({"player": r.name, "flag": "backup_ahead_of_named_starter",
                                  "detail": ", ".join(higher["name"].head(3))})
            if str(r.position) != str(row["position"]):
                flags.append({"player": r.name, "flag": "position_changed",
                              "detail": f"depth {r.position} vs board {row['position']}"})
        notes = str(r.notes)
        if "Confirm" in notes or "not confirmed" in notes.lower() or "confirm official" in notes.lower():
            flags.append({"player": r.name, "flag": "needs_manual_confirmation", "detail": notes})
    # mutually exclusive unreconciled leads: two teammates role>=0.95 at RB
    for (team, pos), g in df.groupby(["team", "position"]):
        if pos != "RB":
            continue
        pts = g["projected_points_if_active"] if "projected_points_if_active" in g else g["pts12"]
        leads = g[(g["expected_opportunity_share"] >= 0.95) & (pts >= 140)]
        if len(leads) > 1:
            flags.append({"player": ", ".join(leads["name"]), "flag": "unreconciled_lead_roles",
                          "detail": f"{team} {pos} {list(leads['expected_opportunity_share'].round(2))}"})
    return flags


def value_board(df, ov=None, depth=None, apply_priors=True):
    """Full valuation. apply_priors=False is the Feagin regression on the raw CSV."""
    ov = load_overrides() if ov is None else ov
    depth = load_depth() if depth is None else depth
    d = df.copy()
    d["playerId"] = d["playerId"].astype(str)
    d = attach_availability(d, ov if apply_priors else ov)  # games from overrides either way
    if not apply_priors:
        # CSV proj_points are the season totals the old board ranked on (games already baked in).
        d["pts_full"] = d["proj_points"].astype(float)
        d["pts12"] = d["proj_points"].astype(float)
        d["named_starter"] = False
        d["contested"] = False
        d["role_in"] = d["role"]
        d["p10"] = d["p25"] = d["p50"] = d["p75"] = d["p90"] = d["pts12"]
        d["starter_probability"] = d["role"].clip(0, 1)
        d["expected_opportunity_share"] = d["role"]
        d["role_confidence"] = d["role"].clip(0, 1)
        d["breakout_probability"] = 0.0
        d["injury_confidence"] = 1.0
        d["prior_applied"] = False
        d["active_frac"] = 1.0  # old board treated listed points as the full season
    else:
        d, _ = apply_roles(d, ov)
        d["p10"] = d["p25"] = d["p50"] = d["p75"] = d["p90"] = d["pts12"]
        d["starter_probability"] = d["role"].clip(0, 1)
        d["expected_opportunity_share"] = d["role"]
        d["role_confidence"] = d["role"].clip(0, 1)
        d["breakout_probability"] = 0.0
        d["prior_applied"] = False
        d = apply_rb_committee_scenarios(d)
        d = apply_qb_split_scenarios(d)
        raw_avail = attach_availability(df.copy(), ov)
        raw_pts = pd.DataFrame({
            "playerId": df["playerId"].astype(str),
            "position": df["position"],
            "pts12": (df["proj_points"] / raw_avail["active_frac"]).values,
        })
        qb_cuts_raw, _ = qb_cutoffs(raw_pts)
        d, _prior = apply_named_qb_prior(d, qb_cuts_raw[28])
        d = apply_availability_bands(d)
        if not depth.empty:
            sp = dict(zip(depth["player_id"].astype(str), depth["starter_probability"]))
            has = d["playerId"].map(sp)
            d["starter_probability"] = has.fillna(d["starter_probability"])
            src = dict(zip(depth["player_id"].astype(str), depth["effective_date"]))
            d["source_as_of"] = d["playerId"].map(src)
    d["source_as_of"] = d.get("source_as_of", AS_OF.isoformat())
    d["source_as_of"] = d["source_as_of"].fillna(AS_OF.isoformat())

    d, sel, margins = starter_vorps(d, "pts12")
    cuts, qbs = qb_cutoffs(d, "pts12")
    flex_repl = margins["next_skill"]
    d["projected_points_if_active"] = d["pts12"].round(1)
    d["projected_ppg"] = (d["pts12"] / GAMES).round(2)
    d["raw_season_points"] = (d["pts12"] * d["active_frac"]).round(1)
    repl12 = np_where_qb(d, cuts[28], flex_repl)
    draft_repl = np_where_qb(d, cuts[42], flex_repl)
    d["replacement_points_during_absences"] = ((1 - d["active_frac"]) * repl12).round(1)
    d["managed_season_points"] = (d["raw_season_points"] + d["replacement_points_during_absences"]).round(1)
    d["managed_vorp"] = (d["active_frac"] * (d["pts12"] - repl12)).round(1)
    d["qb35_adjusted_value"] = np_where_qb(
        d, d["active_frac"] * (d["pts12"] - cuts[35]), d["managed_vorp"]).round(1)
    d["qb42_adjusted_value"] = np_where_qb(
        d, d["active_frac"] * (d["pts12"] - cuts[42]), d["managed_vorp"]).round(1)
    d["draft_adjusted_value"] = np_where_qb(
        d, d["active_frac"] * (d["pts12"] - cuts[42]), d["managed_vorp"]).round(1)
    # starter_vorp stays the 12-game LOO (when-active). Scale QBs the same as skill for rank transparency.
    d["starter_vorp"] = d["starter_vorp"].round(1)

    keys_draft = ["draft_adjusted_value", "managed_season_points", "p50", "p90", "playerId"]
    d["rank"] = rank_by(d, keys_draft)
    d["draft_adjusted_rank"] = d["rank"]
    d["starter_vorp_rank"] = rank_by(d, ["starter_vorp", "managed_season_points", "p50", "p90", "playerId"])
    d["managed_points_rank"] = rank_by(d, ["managed_season_points", "p50", "p90", "playerId"])
    d["ppg_rank"] = rank_by(d, ["projected_ppg", "p90", "playerId"])
    d["floor_rank"] = rank_by(d, ["p10", "p50", "playerId"])
    d["ceiling_rank"] = rank_by(d, ["p90", "p50", "playerId"])
    d["pos_rank"] = d["position"] + rank_by_group(d, "position", keys_draft).astype(str)

    # bench/upside: after the starting pool, sort by ceiling and QB3 scarcity, not more-negative VORP
    d["upside_score"] = d["p90"] + np_where_qb(d, (d["qb42_adjusted_value"] > 0).astype(float) * 20, 0)
    bench = d[~d["in_lineup"]].copy()
    bench["bench_rank"] = rank_by(bench, ["upside_score", "projected_ppg", "p90", "playerId"])
    starters = d[d["in_lineup"]].copy()
    starters["bench_rank"] = rank_by(starters, ["upside_score", "projected_ppg", "playerId"]) + len(bench)
    d["bench_rank"] = pd.concat([bench["bench_rank"], starters["bench_rank"]])
    d["upside_rank"] = rank_by(d, ["upside_score", "projected_ppg", "p90", "playerId"])

    d["draft_value"] = d["draft_adjusted_value"]
    d["proj_points"] = d["raw_season_points"]
    d["role"] = d["role"].round(2)
    flags = freshness_flags(d, depth)
    info = {"selected": sel, "counts": lineup_counts(sel), "margins": margins,
            "qb_cuts": cuts, "flex_repl": flex_repl, "flags": flags,
            "n_qb_rostered_default": int(TEAMS * EXPECTED_QBS_ROSTERED_PER_TEAM)}
    return d, info


def np_where_qb(df, qb_val, other):
    if hasattr(qb_val, "where"):
        return qb_val.where(df["position"] == "QB", other)
    s = pd.Series(other, index=df.index, dtype=float) if not hasattr(other, "loc") else other.astype(float)
    qb = pd.Series(qb_val, index=df.index, dtype=float) if not hasattr(qb_val, "loc") else qb_val.astype(float)
    return qb.where(df["position"] == "QB", s)


def rank_by_group(df, group, cols):
    parts = []
    for _, g in df.groupby(group, sort=False):
        parts.append(rank_by(g, cols))
    return pd.concat(parts)


OUTPUT_COLS = [
    "rank", "pos_rank", "starter_vorp_rank", "draft_adjusted_rank", "managed_points_rank",
    "ppg_rank", "floor_rank", "ceiling_rank", "bench_rank", "upside_rank",
    "playerId", "name", "team", "position",
    "projected_games", "projected_active_games", "projected_games_available",
    "projected_ppg", "projected_points_if_active", "raw_season_points", "proj_points",
    "replacement_points_during_absences", "managed_season_points", "managed_vorp",
    "starter_vorp", "qb35_adjusted_value", "qb42_adjusted_value", "draft_adjusted_value",
    "draft_value",
    "p10", "p25", "p50", "p75", "p90",
    "starter_probability", "expected_opportunity_share", "role", "role_confidence",
    "injury_confidence", "breakout_probability", "source_as_of",
]


def write_report(before, after, info, path="valuation_report.md"):
    b = before.set_index(before["playerId"].astype(str))
    a = after.set_index(after["playerId"].astype(str))
    both = a.join(b[["rank", "proj_points", "draft_value", "pos_rank", "role"]], how="inner", rsuffix="_old")
    both["rank_delta"] = both["rank_old"] - both["rank"]
    both["pts_delta"] = both["proj_points"] - both["proj_points_old"]
    notable = both[(both["rank_old"] <= 300) | (both["rank"] <= 300)
                   | (both["pts_delta"].abs() >= 20)]
    risers = notable.sort_values("rank_delta", ascending=False).head(25)
    fallers = notable.sort_values("rank_delta").head(25)
    counts = info["counts"]
    cuts = info["qb_cuts"]
    lines = []
    lines.append("# 2026 valuation report")
    lines.append("")
    lines.append("## Detected scoring and league config")
    lines.append("")
    lines.append("| setting | value |")
    lines.append("|---|---|")
    lines.append(f"| passing yards per point | {1/SCORING[('passing','YDS')]:.0f} (0.04 pts/yard) |")
    lines.append(f"| passing TD | {SCORING[('passing','TD')]} |")
    lines.append(f"| interception | {SCORING[('passing','INT')]} |")
    lines.append(f"| rushing/receiving yards per point | {1/SCORING[('rushing','YDS')]:.0f} (0.1 pts/yard) |")
    lines.append(f"| rushing/receiving TD | {SCORING[('rushing','TD')]} |")
    lines.append(f"| reception | {SCORING[('receiving','REC')]} (half-PPR) |")
    lines.append(f"| fumble lost | {SCORING[('fumbles','LOST')]} |")
    lines.append(f"| yardage/big-play bonuses | none (`BONUSES={BONUSES}`) |")
    lines.append(f"| 2-pt / return TD | 0 (not in CFBD extract) |")
    lines.append(f"| fantasy regular-season weeks | {GAMES} |")
    lines.append(f"| playoff weeks | {PLAYOFF_WEEKS} |")
    lines.append(f"| teams | {TEAMS} |")
    lines.append(f"| lineup | {SLOTS['QB']}QB / {SLOTS['RB']}RB / {SLOTS['WR']}WR / {FLEX} FLEX {sorted(FLEX_ELIGIBLE)} / {SLOTS.get('K',1)}K / {SLOTS.get('DST',1)} D/ST |")
    lines.append("| required TE | 0 |")
    lines.append(f"| expected QBs rostered per team | {EXPECTED_QBS_ROSTERED_PER_TEAM} (default {int(TEAMS*EXPECTED_QBS_ROSTERED_PER_TEAM)} total) |")
    lines.append(f"| named-QB prior | {NAMED_QB_STARTER_PRIOR_FRAC} × unmodified QB29 |")
    lines.append("")
    lines.append("## Starter composition")
    lines.append("")
    lines.append(json.dumps(counts, indent=2))
    lines.append("")
    lines.append(f"FLEX replacement (first excluded skill): {info['flex_repl']:.1f}")
    lines.append(f"QB cutoffs (first player outside N rostered): 28→{cuts[28]:.1f}, 35→{cuts[35]:.1f}, 42→{cuts[42]:.1f}")
    lines.append(f"TE in the 84 skill starters: {counts['n_te']} (optional FLEX only)")
    lines.append("")
    lines.append("## 28 / 35 / 42 QB sensitivity (top 15 QBs by draft-adjusted value)")
    q = after[after["position"] == "QB"].nsmallest(15, "rank")
    lines.append("")
    lines.append(q[["rank", "name", "team", "projected_points_if_active", "starter_vorp",
                    "qb35_adjusted_value", "qb42_adjusted_value", "draft_adjusted_value"]].to_string(index=False))
    lines.append("")
    lines.append("## Before / after top 150")
    lines.append("")
    lines.append("Old board top 15:")
    lines.append("")
    lines.append(before.nsmallest(15, "rank")[["rank", "name", "position", "proj_points", "draft_value"]].to_string(index=False))
    lines.append("")
    lines.append("Tuned board top 15 (old_rank is the previous overall rank):")
    lines.append("")
    top = after.nsmallest(150, "rank")[["rank", "name", "team", "position", "pos_rank",
        "proj_points", "managed_vorp", "starter_vorp", "draft_adjusted_value", "role"]].copy()
    top["old_rank"] = top["name"].map(dict(zip(before["name"], before["rank"])))
    lines.append(top.to_string(index=False))
    lines.append("")
    lines.append("## 25 largest risers (better rank)")
    lines.append("")
    for r in risers.itertuples():
        driver = _driver(r)
        lines.append(f"- {r.name} ({r.position} {r.team}): {int(r.rank_old)} → {int(r.rank)}  {driver}")
    lines.append("")
    lines.append("## 25 largest fallers (worse rank)")
    lines.append("")
    for r in fallers.itertuples():
        driver = _driver(r)
        lines.append(f"- {r.name} ({r.position} {r.team}): {int(r.rank_old)} → {int(r.rank)}  {driver}")
    lines.append("")
    lines.append("## Depth-chart / news audit")
    lines.append("")
    if info["flags"]:
        for f in info["flags"]:
            lines.append(f"- `{f['flag']}` {f['player']}: {f['detail']}")
    else:
        lines.append("- no flags")
    lines.append("")
    lines.append("## K / D/ST")
    lines.append("")
    lines.append("No kicking or team-defense stats in `fetch.py` (`CATEGORIES` is passing/rushing/receiving/fumbles). Not fabricated. Stream K15 / D/ST15 in the client.")
    lines.append("")
    lines.append("## Unresolved assumptions")
    lines.append("")
    for u in UNRESOLVED:
        lines.append(f"- {u}")
    path_open = open(path, "w")
    path_open.write("\n".join(lines) + "\n")
    path_open.close()
    return path


def _driver(r):
    bits = []
    if getattr(r, "prior_applied", False):
        bits.append("named-QB prior")
    if r.position == "TE":
        bits.append("FLEX replacement (no TE baseline)")
    if r.position == "QB" and float(getattr(r, "role", 1)) <= 0.26:
        bits.append("named-QB backup lock")
    if r.position == "QB" and r.starter_vorp < 0 <= r.draft_adjusted_value:
        bits.append("QB42 backup scarcity")
    if r.position == "QB" and r.draft_adjusted_value > r.starter_vorp + 5:
        bits.append("QB42 vs starter VORP")
    if abs(r.pts_delta) >= 5:
        bits.append(f"proj {r.proj_points_old:.1f}→{r.proj_points:.1f}")
    if r.projected_games < GAMES:
        bits.append(f"managed replacement on {int(GAMES-r.projected_games)} missed games")
    if bool(getattr(r, "contested", False)):
        bits.append("committee/split scenario")
    return "; ".join(bits) or "lineup-optimizer VORP vs old per-position replacement"


UNRESOLVED = [
    "No CFBD dump in this environment, so model.py was not retrained. Tuned board is a post-process of projections_2026.csv.",
    "Team opportunity budgets (plays/attempts/targets/goal-line) are not reconciled; only 2-player contested rooms get a scenario identity.",
    "Transfer translation (Nelson, Phillips, Hughes, Brown, Leavitt) is still the v2 ML + from_fcs flag, not a split workload/efficiency/LOC model.",
    "Feagin's RB→TE usage (routes/targets vs 122 carries) is not reprojected; the TE scarcity bug is fixed, the skill mix is not.",
    "Named-QB prior is a blend toward 0.90×QB29, not a recruiting/scheme volume model.",
    "Role percentiles for non-committee players are a documented residual band, not a weekly Monte Carlo.",
    "Hardy/Davison availability is a games band around the override, not a week-by-week return tree.",
    "UNT Osho vs White and Miami (OH) QB depth were not confirmed on official team sites as of 2026-08-25.",
    "Fantrax 2RR / return TD / K / D/ST still absent from the stat extract.",
    "No walk-forward backtest in this pass: data/ is not present.",
]


def main(year=2026):
    src = f"projections_{year}.csv"
    raw = pd.read_csv(src, dtype={"playerId": str})
    tuned, info = value_board(raw, apply_priors=True)
    out = tuned[OUTPUT_COLS].sort_values("rank")
    for c in ("p10", "p25", "p50", "p75", "p90", "starter_probability",
              "expected_opportunity_share", "role_confidence", "breakout_probability"):
        out[c] = out[c].astype(float).round(3)
    dest = f"projections_{year}_tuned.csv"
    out.to_csv(dest, index=False)
    write_report(raw, tuned, info)
    print(out.head(30).to_string(index=False))
    print("\nlineup", info["counts"])
    print("flex_repl", round(info["flex_repl"], 1), "qb_cuts", {k: round(v, 1) for k, v in info["qb_cuts"].items()})
    print(f"{len(out)} players -> {dest}")
    feagin = tuned[tuned["name"] == "Kaden Feagin"]
    if len(feagin):
        r = feagin.iloc[0]
        print(f"Feagin: rank={int(r['rank'])} starter_vorp={r['starter_vorp']} pts12={r['projected_points_if_active']}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2026)
