"""Post-process the v2 board into league-specific draft ranks.

Does not retrain model.py. Reads projections_{year}.csv, applies depth-chart
role facts, then ranks with a lineup optimizer instead of per-position
replacement.

python3 valuation.py [year]
"""
import json
import os
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
PRIMARY_SHARE = 0.65          # winner's share of ONE team RB budget
SECONDARY_SHARE = 0.35        # remainder split across every other RB on the team
QB_SPLIT_PRIMARY = 0.70       # dual-QB winner snap share; loser 1-this
QB_SPLIT_P = 0.50             # P(each is the primary); must sum to 1 with 1-P
CONTESTED_ROLE = ROLE_ALIAS["contested"]
DEPTH_STALE_DAYS = 14
AS_OF = date(2026, 8, 25)
PROJECTION_RUN_DATE = AS_OF
# games already baked into projections_2026.csv (undo these, then apply current overrides)
BAKED_GAMES = {"Ahmad Hardy": 10, "Jordon Davison": 6}
WAIVER_REPLACEMENT_POS = "RB"
WAIVER_REPLACEMENT_RANK = 100  # 1-based; missed weeks use this PPG, not FLEX/RB56
STASH_GAMES = 4
STASH_COST = 4.0               # subtracted from draft value when missed >= STASH_GAMES
RAMP_GAMES = 2
RAMP_SHARE = 0.60              # first active games after return are not full PPG
SCORING_PPR = SCORING[("receiving", "REC")]
TOLERANCE_TEAM_SHARE = 0.02
N_STARTERS_OFFENSE = TEAMS * (SLOTS["QB"] + SLOTS["RB"] + SLOTS["WR"] + FLEX)

assert abs(QB_SPLIT_P + (1 - QB_SPLIT_P) - 1.0) < 1e-12
assert abs(PRIMARY_SHARE + SECONDARY_SHARE - 1.0) < 1e-12
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
    """Undo the CSV's baked games scale and role scalar → role-1 12-game points."""
    baked = df["name"].map(BAKED_GAMES).fillna(GAMES)
    role = df["role"].clip(lower=0.01)
    return df["proj_points"] / (baked / GAMES).clip(lower=1 / GAMES) / role


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


def transfer_displaced_rb_opportunity(df):
    """If a named RB1's teammate was role-cut, move that workload to the lead.

    Stops committee cuts from deleting carries instead of reassigning them.
    """
    out = df.copy()
    for _, g in out[out["position"] == "RB"].groupby("team"):
        leads = g[g["named_starter"]]
        if len(leads) != 1:
            continue
        li = leads.index[0]
        displaced = 0.0
        for i in g.index:
            if i == li:
                continue
            dropped = float(out.at[i, "role_in"]) - float(out.at[i, "role"])
            if dropped > 0.05:
                displaced += float(out.at[i, "pts_full"]) * dropped
        if displaced > 0:
            out.at[li, "pts12"] = float(out.at[li, "pts12"]) + displaced
            full = max(float(out.at[li, "pts_full"]), 1e-9)
            out.at[li, "expected_opportunity_share"] = min(
                1.0, float(out.at[li, "pts12"]) / full)
    return out


def _rb_fp(rush_yds=0, rush_td=0, rec=0, rec_yds=0, rec_td=0):
    """0.5 PPR fantasy points from RB rushing + receiving components."""
    return (score_stat("rushing", "YDS", rush_yds) + score_stat("rushing", "TD", rush_td)
            + score_stat("receiving", "REC", rec) + score_stat("receiving", "YDS", rec_yds)
            + score_stat("receiving", "TD", rec_td))


# Last available season component totals. Rates only — not 2026 point totals.
# playerId -> (rush_yds, rush_td, rec, rec_yds, rec_td, games, same_2026_team)
RB_LAST = {
    "5193580": (1124, 14, 25, 224, 2, 14, True),   # Dickey TTU 2025
    "5086393": (868, 6, 35, 388, 2, 14, True),     # Williams TTU 2025
    "4917949": (478, 3, 12, 89, 1, 12, False),     # Joyner USC 2024 (missed 2025)
    "5146712": (1125, 10, 15, 149, 2, 14, True),   # Riley BOIS 2025
    "5147379": (811, 8, 11, 72, 1, 14, True),      # Gaines BOIS 2025
    "5295318": (576, 5, 7, 55, 0, 6, True),        # Jordan USC 2025 (6g)
    "5233016": (972, 8, 0, 0, 0, 13, True),        # Miller USC 2025; rec not sourced
}

# Evidence-based 2026 workload priors (sum ~1 per room). Not final ranks.
RB_WORKLOAD = {
    "5193580": 0.47, "5086393": 0.33, "4917949": 0.17,   # TTU Dickey/Williams/Joyner
    "5146712": 0.48, "5147379": 0.34, "5124975": 0.12,   # BOIS Riley/Gaines/Goff
    "5295318": 0.57, "5233016": 0.33, "5144164": 0.10,  # USC Jordan/Miller/Wormley
    "5093886": 0.50, "5155048": 0.38,                      # IOWA Moulton/Phillips
}


def _rb_last_fp(pid):
    row = RB_LAST.get(str(pid))
    if not row:
        return None
    yds, td, rec, recy, rtd, games, same = row
    return _rb_fp(yds, td, rec, recy, rtd), games, same, yds, td, rec, recy, rtd


def apply_rb_committee_scenarios(df):
    """Mutually exclusive winner scenarios on one component-scored team RB pool.

    Pool = 12-game pace of last-year RB rush+rec fantasy points for this team
    (fallback: share-weighted pts_full). Rush follows the winner scenario;
    receiving stays with player-specific rec rates. Shares and P(win) sum to 1.
    """
    out = df.copy()
    out["pts12"] = out["pts12"].astype(float)
    out["pts_full"] = out["pts_full"].astype(float)
    if "starter_probability" not in out.columns:
        out["starter_probability"] = float("nan")
    if "workload_share" not in out.columns:
        out["workload_share"] = float("nan")
    rbs = out[out["position"] == "RB"]
    for _team, grp in rbs.groupby("team"):
        contested = grp[grp["contested"]]
        if len(contested) < 2:
            continue
        w = pd.to_numeric(out.loc[grp.index, "workload_share"], errors="coerce").fillna(0.0)
        extra = grp.index[w > 0.05]
        win_ids = list(dict.fromkeys(list(contested.index) + list(extra)))
        prior = pd.to_numeric(out.loc[win_ids, "starter_probability"], errors="coerce").fillna(0.0)
        if float(prior.sum()) <= 0:
            prior = out.loc[win_ids, "pts_full"].clip(lower=1e-6)
        p_win = prior / prior.sum()

        if float(w.sum()) <= 0:
            w = out.loc[grp.index, "pts_full"].clip(lower=1e-9)
        leftover = max(0.0, 1.0 - float(w.sum()))
        rest = grp.index[w <= 0]
        if leftover > 0 and len(rest):
            rw = out.loc[rest, "pts_full"].clip(lower=1e-9)
            w.loc[rest] = leftover * rw / rw.sum()
        w = w / w.sum()

        rush_w = pd.Series(0.0, index=grp.index)
        rec_w = pd.Series(0.0, index=grp.index)
        hist_fp, hist_games = 0.0, 0.0
        for idx in grp.index:
            last = _rb_last_fp(out.at[idx, "playerId"])
            if last:
                fp, games, same, yds, td, rec, recy, rtd = last
                rush_w.loc[idx] = (score_stat("rushing", "YDS", yds)
                                   + score_stat("rushing", "TD", td)) / games
                rec_w.loc[idx] = (score_stat("receiving", "REC", rec)
                                  + score_stat("receiving", "YDS", recy)
                                  + score_stat("receiving", "TD", rtd)) / games
                if same:
                    hist_fp += fp
                    hist_games = max(hist_games, games)
            else:
                ppg = float(out.at[idx, "pts_full"]) / GAMES
                rush_w.loc[idx] = 0.80 * ppg
                rec_w.loc[idx] = 0.20 * ppg
        rush_w = rush_w.clip(lower=1e-6)
        rec_w = rec_w.clip(lower=1e-9) * w.clip(lower=1e-6)
        if hist_fp > 0 and hist_games > 0:
            budget = hist_fp / hist_games * GAMES
        else:
            budget = float((w * out.loc[grp.index, "pts_full"]).sum())
        if budget <= 0:
            continue
        rec_share_fixed = rec_w / rec_w.sum()
        rush_mass = float((w * rush_w).sum())
        rec_mass = float(rec_w.sum())
        rec_frac = rec_mass / (rush_mass + rec_mass) if (rush_mass + rec_mass) else 0.20
        rec_pool = rec_frac * budget
        rush_pool = budget - rec_pool

        def rush_shares(winner):
            s = pd.Series(0.0, index=grp.index)
            s.loc[winner] = PRIMARY_SHARE
            rest_i = grp.index.difference([winner])
            rw = w.loc[rest_i].clip(lower=1e-9)
            s.loc[rest_i] = SECONDARY_SHARE * rw / rw.sum()
            return s

        def pts_from(rs):
            rush_pts = rush_pool * (rs * rush_w) / (rs * rush_w).sum()
            rec_pts = rec_pool * rec_share_fixed
            return rush_pts + rec_pts

        scenarios = {wid: pts_from(rush_shares(wid)) for wid in win_ids}
        exp_pts = sum((float(p_win.loc[wid]) * scenarios[wid] for wid in win_ids),
                      pd.Series(0.0, index=grp.index))
        exp_share = sum((float(p_win.loc[wid]) * rush_shares(wid) for wid in win_ids),
                        pd.Series(0.0, index=grp.index))
        # receiving is a usage share too; blend so reported share sums to 1
        exp_share = 0.5 * exp_share + 0.5 * rec_share_fixed
        exp_share = exp_share / exp_share.sum()
        for idx in grp.index:
            outcomes = [float(scenarios[wid].loc[idx]) for wid in win_ids]
            lo, hi = min(outcomes), max(outcomes)
            exp = float(exp_pts.loc[idx])
            out.at[idx, "pts12"] = exp
            if hi - lo >= 0.5:
                out.at[idx, "p10"] = lo
                out.at[idx, "p25"] = lo
                out.at[idx, "p50"] = exp
                out.at[idx, "p75"] = hi
                out.at[idx, "p90"] = hi
            p = float(p_win.loc[idx]) if idx in p_win.index else 0.0
            out.at[idx, "starter_probability"] = p
            out.at[idx, "expected_opportunity_share"] = float(exp_share.loc[idx])
            out.at[idx, "role"] = round(float(exp_share.loc[idx]), 2)
            out.at[idx, "role_confidence"] = 0.50 if p > 0 else 0.40
            out.at[idx, "breakout_probability"] = round(p, 3)
            out.at[idx, "_room_expected"] = float(exp_pts.sum())
            out.at[idx, "_room_budget"] = budget
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
            out.at[i, "p25"] = lo
            out.at[i, "p50"] = exp
            out.at[i, "p75"] = hi
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
    out.loc[low, "starter_probability"] = out.loc[low, "starter_probability"].fillna(0.85).clip(lower=0.85)
    out["prior_applied"] = False
    out.loc[low, "prior_applied"] = True
    return out, prior


def apply_injury_ramp(df):
    """Short-game players: return-date band + reduced early-game workload.

    Missed weeks are valued later at waiver PPG, not here.
    """
    out = df.copy()
    out["injury_confidence"] = 1.0
    short = out["projected_games"] < GAMES
    for i in out.index[short]:
        n = float(out.at[i, "projected_games"])
        ppg = float(out.at[i, "pts12"]) / GAMES

        def season(games, ramp_n, ramp_w):
            games = max(1.0, games)
            ramp_n = min(ramp_n, games)
            return ramp_n * ramp_w * ppg + (games - ramp_n) * ppg

        s50 = season(n, RAMP_GAMES, RAMP_SHARE)
        s10 = season(max(1.0, n - 2), RAMP_GAMES + 1, 0.50)
        s90 = season(min(float(GAMES), n + 1), max(1, RAMP_GAMES - 1), 0.75)
        out.at[i, "pts12"] = s50 / n * GAMES
        out.at[i, "p10"] = s10 / max(1.0, n - 2) * GAMES
        out.at[i, "p25"] = 0.5 * out.at[i, "p10"] + 0.5 * out.at[i, "pts12"]
        out.at[i, "p50"] = out.at[i, "pts12"]
        out.at[i, "p75"] = 0.5 * (s90 / min(float(GAMES), n + 1) * GAMES) + 0.5 * out.at[i, "pts12"]
        out.at[i, "p90"] = s90 / min(float(GAMES), n + 1) * GAMES
        out.at[i, "injury_confidence"] = 0.55
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


def _nth(df, pos, n, pts_col="pts12"):
    """1-based: WR29 is the 29th WR (iloc 28)."""
    g = df[df["position"] == pos].sort_values([pts_col, "playerId"], ascending=[False, True])
    i = min(max(n - 1, 0), len(g) - 1)
    return float(g.iloc[i][pts_col])


def _waiver_baseline(df, pts_col="pts12"):
    pts = _nth(df, WAIVER_REPLACEMENT_POS, WAIVER_REPLACEMENT_RANK, pts_col)
    return pts, pts / GAMES


def _scale_percentiles_to_managed(d, waiver_pts):
    """p10/p50/p90 live on managed_season_points. Unmodeled rows stay null."""
    has = d["p10"].notna()
    if not has.any():
        return d
    repl = np_where_qb(d, 0.0, waiver_pts)
    active = d["active_frac"]
    for col in ("p10", "p25", "p50", "p75", "p90"):
        d.loc[has, col] = (active * d[col] + (1 - active) * repl)[has]
    d.loc[has, "p50"] = d.loc[has, "managed_season_points"]
    return d


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
        d["p10"] = d["p25"] = d["p50"] = d["p75"] = d["p90"] = float("nan")
        d["starter_probability"] = d["role"].clip(0, 1)
        d["expected_opportunity_share"] = d["role"]
        d["role_confidence"] = d["role"].clip(0, 1)
        d["breakout_probability"] = 0.0
        d["injury_confidence"] = 1.0
        d["prior_applied"] = False
        d["active_frac"] = 1.0  # old board treated listed points as the full season
    else:
        d, _ = apply_roles(d, ov)
        d["p10"] = d["p25"] = d["p50"] = d["p75"] = d["p90"] = float("nan")
        d["starter_probability"] = float("nan")
        d["expected_opportunity_share"] = d["role"]
        d["role_confidence"] = d["role"].clip(0, 1)
        d["breakout_probability"] = 0.0
        d["prior_applied"] = False
        d["injury_confidence"] = 1.0
        d["workload_share"] = pd.to_numeric(d["playerId"].map(RB_WORKLOAD), errors="coerce")
        if not depth.empty:
            sp = dict(zip(depth["player_id"].astype(str), depth["starter_probability"]))
            d["starter_probability"] = pd.to_numeric(d["playerId"].map(sp), errors="coerce")
        d = transfer_displaced_rb_opportunity(d)
        d = apply_rb_committee_scenarios(d)
        d = apply_qb_split_scenarios(d)
        baked = d["name"].map(BAKED_GAMES).fillna(GAMES)
        raw_pts = pd.DataFrame({
            "playerId": df["playerId"].astype(str),
            "position": df["position"],
            "pts12": (df["proj_points"] / (baked / GAMES)).values,
        })
        qb_cuts_raw, _ = qb_cutoffs(raw_pts)
        d, _prior = apply_named_qb_prior(d, qb_cuts_raw[28])
        d = apply_injury_ramp(d)
        d["projection_run_date"] = PROJECTION_RUN_DATE.isoformat()
        d["role_source_date"] = pd.NA
        d["injury_source_date"] = pd.NA
        d["source_url"] = pd.NA
        if not depth.empty:
            src = dict(zip(depth["player_id"].astype(str), depth["effective_date"]))
            d["role_source_date"] = d["playerId"].map(src)
            inj = depth[depth["injury_status"].astype(str).str.lower().isin(["out", "injured"])]
            d["injury_source_date"] = d["playerId"].map(
                dict(zip(inj["player_id"].astype(str), inj["effective_date"])))
            urls = dict(zip(depth["player_id"].astype(str), depth["source_url"]))
            d["source_url"] = d["playerId"].map(urls)
        d["source_as_of"] = d["role_source_date"]
    if "source_as_of" not in d.columns:
        d["source_as_of"] = pd.NA
    if "projection_run_date" not in d.columns:
        d["projection_run_date"] = PROJECTION_RUN_DATE.isoformat()
        d["role_source_date"] = pd.NA
        d["injury_source_date"] = pd.NA
        d["source_url"] = pd.NA

    d, sel, margins = starter_vorps(d, "pts12")
    cuts, qbs = qb_cutoffs(d, "pts12")
    flex_repl = margins["next_skill"]
    wr29 = _nth(d, "WR", 29)
    waiver_pts, waiver_ppg = _waiver_baseline(d)
    d["projected_points_if_active"] = d["pts12"].round(1)
    d["projected_ppg"] = (d["pts12"] / GAMES).round(2)
    d["raw_season_points"] = (d["pts12"] * d["active_frac"]).round(1)
    missed = (1 - d["active_frac"])
    # skill missed weeks: waiver RB, not FLEX starter. QBs: no RB-waiver credit.
    d["replacement_points_during_absences"] = (
        missed * np_where_qb(d, 0.0, waiver_pts)).round(1)
    d["managed_season_points"] = (
        d["raw_season_points"] + d["replacement_points_during_absences"]).round(1)
    d["stash_cost"] = 0.0
    d.loc[(GAMES - d["projected_games"]) >= STASH_GAMES, "stash_cost"] = STASH_COST
    pos_repl = pd.Series(flex_repl, index=d.index)
    pos_repl = pos_repl.where(d["position"] != "WR", wr29)
    pos_repl = pos_repl.where(d["position"] != "QB", cuts[42])
    d["draft_adjusted_value"] = (
        d["managed_season_points"] - pos_repl - d["stash_cost"]).round(1)
    starter_repl = pd.Series(flex_repl, index=d.index).where(d["position"] != "QB", cuts[28])
    d["managed_vorp"] = (d["managed_season_points"] - starter_repl).round(1)
    d["qb35_adjusted_value"] = np_where_qb(
        d, d["managed_season_points"] - cuts[35], d["draft_adjusted_value"]).round(1)
    d["qb42_adjusted_value"] = np_where_qb(
        d, d["managed_season_points"] - cuts[42], d["draft_adjusted_value"]).round(1)
    d["starter_vorp"] = d["starter_vorp"].round(1)
    d["scoring_ppr"] = SCORING_PPR
    d["waiver_replacement_rank"] = WAIVER_REPLACEMENT_RANK
    d["waiver_replacement_ppg"] = round(waiver_ppg, 2)
    d = _scale_percentiles_to_managed(d, waiver_pts)

    d["_p50"] = d["p50"].fillna(d["managed_season_points"])
    d["_p90"] = d["p90"].fillna(d["managed_season_points"])
    d["_p10"] = d["p10"].fillna(d["managed_season_points"])
    keys_draft = ["draft_adjusted_value", "managed_season_points", "_p50", "_p90", "playerId"]
    d["rank"] = rank_by(d, keys_draft)
    d["draft_adjusted_rank"] = d["rank"]
    d["starter_vorp_rank"] = rank_by(d, ["starter_vorp", "managed_season_points", "_p50", "_p90", "playerId"])
    d["managed_points_rank"] = rank_by(d, ["managed_season_points", "_p50", "_p90", "playerId"])
    d["ppg_rank"] = rank_by(d, ["projected_ppg", "_p90", "playerId"])
    d["floor_rank"] = rank_by(d, ["_p10", "_p50", "playerId"])
    d["ceiling_rank"] = rank_by(d, ["_p90", "_p50", "playerId"])
    d["pos_rank"] = d["position"] + rank_by_group(d, "position", keys_draft).astype(str)

    d["upside_score"] = d["_p90"] + np_where_qb(d, (d["qb42_adjusted_value"] > 0).astype(float) * 20, 0)
    bench = d[~d["in_lineup"]].copy()
    bench["bench_rank"] = rank_by(bench, ["upside_score", "projected_ppg", "_p90", "playerId"])
    starters = d[d["in_lineup"]].copy()
    starters["bench_rank"] = rank_by(starters, ["upside_score", "projected_ppg", "playerId"]) + len(bench)
    d["bench_rank"] = pd.concat([bench["bench_rank"], starters["bench_rank"]])
    d["upside_rank"] = rank_by(d, ["upside_score", "projected_ppg", "_p90", "playerId"])

    d["draft_value"] = d["draft_adjusted_value"]
    d["proj_points"] = d["raw_season_points"]
    d["role"] = d["role"].round(2)
    flags = freshness_flags(d, depth)
    info = {"selected": sel, "counts": lineup_counts(sel), "margins": margins,
            "qb_cuts": cuts, "flex_repl": flex_repl, "wr29": wr29,
            "waiver_pts": waiver_pts, "waiver_ppg": waiver_ppg, "flags": flags,
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
    "injury_confidence", "breakout_probability",
    "projection_run_date", "role_source_date", "injury_source_date", "source_url", "source_as_of",
    "scoring_ppr", "waiver_replacement_rank", "waiver_replacement_ppg",
    "stash_cost",
]


def write_report(before, after, info, path="valuation_report.md", prev_tuned=None):
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
    lines.append(f"| scoring_ppr | {SCORING_PPR} |")
    lines.append(f"| waiver replacement | {WAIVER_REPLACEMENT_POS}{WAIVER_REPLACEMENT_RANK} "
                 f"= {info.get('waiver_ppg', 0):.2f} PPG ({info.get('waiver_pts', 0):.1f} / {GAMES} games) |")
    lines.append(f"| stash cost | {STASH_COST} pts when missed games ≥ {STASH_GAMES} |")
    lines.append("")
    lines.append("## Starter composition")
    lines.append("")
    lines.append(json.dumps(counts, indent=2))
    lines.append("")
    lines.append(f"FLEX replacement (first excluded skill): {info['flex_repl']:.1f}")
    wr29 = info.get("wr29", 0)
    lines.append(f"WR29 (mandatory-WR replacement): {wr29:.1f}")
    lines.append(f"QB cutoffs (first player outside N rostered): 28→{cuts[28]:.1f}, 35→{cuts[35]:.1f}, 42→{cuts[42]:.1f}")
    lines.append(f"TE in the 84 skill starters: {counts['n_te']} (optional FLEX only)")
    lines.append("")
    lines.append("Percentile columns p10/p50/p90 are **managed_season_points** "
                 "(null unless a committee, dual-QB, named-QB-prior, or injury-ramp scenario exists). "
                 "floor_rank / ceiling_rank rank the full pool using p10/p90, filling unmodeled rows with managed_season_points.")
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
    top = after.nsmallest(150, "rank")[["rank", "playerId", "name", "team", "position", "pos_rank",
        "proj_points", "managed_vorp", "starter_vorp", "draft_adjusted_value", "role"]].copy()
    top["old_rank"] = top["playerId"].astype(str).map(
        dict(zip(before["playerId"].astype(str), before["rank"])))
    lines.append(top.to_string(index=False))
    lines.append("")
    lines.append("## 20 largest risers (better rank)")
    lines.append("")
    for r in risers.head(20).itertuples():
        driver = _driver(r)
        lines.append(f"- {r.name} ({r.position} {r.team}): {int(r.rank_old)} → {int(r.rank)}  {driver}")
    lines.append("")
    lines.append("## 20 largest fallers (worse rank)")
    lines.append("")
    for r in fallers.head(20).itertuples():
        driver = _driver(r)
        lines.append(f"- {r.name} ({r.position} {r.team}): {int(r.rank_old)} → {int(r.rank)}  {driver}")
    lines.append("")
    lines.append("## Player-level regression diagnostics")
    lines.append("")
    lines.append(_regression_block(after, before))
    lines.append("")
    lines.append("## Contested backfield distributions")
    lines.append("")
    lines.append(_backfield_block(after))
    lines.append("")
    lines.append("## RB-room validation")
    lines.append("")
    lines.append(_rb_validation_block(after, prev_tuned, info))
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
    "Team RB pools for contested rooms use last-year rush+rec components (12-game pace) when sourced; other teams still use independent ML rows.",
    "Transfer translation (Nelson, Hughes, Brown, Leavitt) is still the v2 ML + from_fcs flag.",
    "Feagin's RB→TE usage (routes/targets vs 122 carries) is not reprojected; only TE scarcity and FLEX replacement changed. No sourced 2026 receiving-role split.",
    "Named-QB prior is a blend toward 0.90×QB29, not a recruiting/scheme volume model.",
    "starter_probability is blank unless a depth-chart or committee win model ran. `role` is the role score, not a probability.",
    "Percentiles p10/p50/p90 are managed_season_points when a scenario exists; otherwise they stay null. floor_rank/ceiling_rank still cover the full pool.",
    "Hardy stays at 10 games (mid-September target). Drinkwitz has not given a later date.",
    "Fantrax 2RR / return TD / K / D/ST still absent from the stat extract.",
    "No walk-forward backtest in this pass: data/ is not present.",
    "Tennessee WR stack (Staley/Matthews) still comes from independent ML rows, not one team passing forecast.",
]


DIAGNOSTIC_UNDER = [
    "Malachi Toney", "Jordan Marshall", "Sam Leavitt", "Isaiah Sategna III",
    "Keelon Russell", "David McComb", "Makhi Hughes", "Raleek Brown",
]
DIAGNOSTIC_OVER = [
    "Nick Osho", "Kaden Feagin", "L.J. Phillips Jr.", "L.J. Phillips",
    "Cameron Dickey", "J'Koby Williams", "Braylon Staley", "Mike Matthews",
    "Ahmad Hardy",
]

BACKFIELD_TEAMS = ("TTU", "BOIS", "USC")


def _pos_counts(df, n):
    top = df.nsmallest(n, "rank")
    return {p: int((top["position"] == p).sum()) for p in ("QB", "RB", "WR", "TE")}


def _rb_validation_block(after, prev, info):
    lines = [
        "Scoring, replacement levels, and valuation formulas were not changed "
        f"(scoring_ppr={SCORING_PPR}, WR29={info.get('wr29', 0):.1f}, "
        f"FLEX={info.get('flex_repl', 0):.1f}, "
        f"QB28/35/42={info['qb_cuts'][28]:.1f}/{info['qb_cuts'][35]:.1f}/{info['qb_cuts'][42]:.1f}).",
        "",
        "`starter_probability` is P(win the RB job) in modeled rooms (sums to 1.0) "
        "or a sourced named-starter probability. It is blank when no probability model ran. "
        "`role` remains the role score.",
        "",
    ]
    teams = sorted(after.loc[after["position"].eq("RB") & after["_room_budget"].notna(), "team"].unique()) if "_room_budget" in after.columns else []
    lines.append("### Team RB point pool and share sum")
    lines.append("")
    lines.append("| team | before pool | after pool | before share sum | after share sum | after P(win) |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for team in teams:
        new = after[(after["team"] == team) & (after["position"] == "RB")]
        after_pool = float(new["_room_budget"].dropna().iloc[0])
        after_share = float(new["expected_opportunity_share"].sum())
        after_p = float(new["starter_probability"].fillna(0).sum())
        if prev is not None and "projected_points_if_active" in prev.columns:
            old = prev[(prev["team"] == team) & (prev["position"] == "RB")]
            before_pool = float(old["projected_points_if_active"].sum()) if len(old) else float("nan")
            before_share = float(pd.to_numeric(old.get("expected_opportunity_share"), errors="coerce").sum()) if len(old) else float("nan")
        else:
            before_pool = before_share = float("nan")
        lines.append(f"| {team} | {before_pool:.1f} | {after_pool:.1f} | {before_share:.3f} | {after_share:.3f} | {after_p:.3f} |")
    lines.append("")
    if prev is not None:
        lines.append("### Top-112 / top-126 positional composition")
        lines.append("")
        lines.append("| cut | when | QB | RB | WR | TE |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for n in (112, 126):
            for label, df in (("before", prev), ("after", after)):
                c = _pos_counts(df, n)
                lines.append(f"| top {n} | {label} | {c['QB']} | {c['RB']} | {c['WR']} | {c['TE']} |")
        lines.append("")
        old150 = set(prev.nsmallest(150, "rank")["playerId"].astype(str))
        new150 = set(after.nsmallest(150, "rank")["playerId"].astype(str))
        entered = after[after["playerId"].astype(str).isin(new150 - old150)].nsmallest(50, "rank")
        left = prev[prev["playerId"].astype(str).isin(old150 - new150)].nsmallest(50, "rank")
        lines.append("### Players entering top 150")
        lines.append("")
        if entered.empty:
            lines.append("- none")
        else:
            for r in entered.itertuples():
                lines.append(f"- {r.name} ({r.position} {r.team}) rank {int(r.rank)}")
        lines.append("")
        lines.append("### Players leaving top 150")
        lines.append("")
        if left.empty:
            lines.append("- none")
        else:
            for r in left.itertuples():
                lines.append(f"- {r.name} ({r.position} {r.team}) was rank {int(r.rank)}")
        lines.append("")
    lines.append("### Manually changed role priors (source URL + as-of)")
    lines.append("")
    lines.append("| player | team | P(win) | workload | as-of | source |")
    lines.append("|---|---|---:|---:|---|---|")
    depth = load_depth()
    if not depth.empty:
        changed = depth[depth["name"].isin([
            "Cameron Dickey", "J'Koby Williams", "Quinten Joyner",
            "Dylan Riley", "Sire Gaines", "Juelz Goff",
            "Waymond Jordan", "King Miller", "Riley Wormley",
            "Kamari Moulton", "L.J. Phillips Jr.",
        ])]
        for r in changed.itertuples():
            wl = RB_WORKLOAD.get(str(r.player_id), "")
            wl_s = f"{wl:.2f}" if wl != "" else ""
            lines.append(f"| {r.name} | {r.team} | {float(r.starter_probability):.2f} | {wl_s} | {r.effective_date} | {r.source_url} |")
    lines.append("")
    lines.append("### Input audit (no rank overrides)")
    lines.append("")
    lines.append("- L.J. Phillips vs Kamari Moulton: sourced Iowa timeshare. Marked contested; Moulton is the Week 1 favorite. FCS translation still from the ML row, not a hand-entered total.")
    lines.append("- Malachi Toney: no sourced 2026 role change. Left as the ML WR row.")
    lines.append("- Kaden Feagin: still TE1 after the RB conversion; no sourced receiving-role tree, so usage was not rebuilt.")
    lines.append("- Sam Leavitt, Faizon Brandon, Keelon Russell: named-QB facts already in depth_chart; no new sourced demotion/promotion.")
    lines.append("- Makhi Hughes and Raleek Brown: no sourced 2026 lead-job change. Left as ML + from_fcs.")
    lines.append("- Ahmad Hardy: Drinkwitz still targeting as soon as possible / mid-September; games=10 unchanged.")
    return "\n".join(lines)


def _backfield_block(after):
    lines = [
        "p10 / p50 / p90 are managed_season_points. "
        "Rush follows mutually exclusive winner scenarios; receiving stays player-specific. "
        "Every RB on the team is in the remainder.",
        "",
    ]
    for team in BACKFIELD_TEAMS:
        room = after[(after["team"] == team) & (after["position"] == "RB")].sort_values(
            ["starter_probability", "managed_season_points", "playerId"],
            ascending=[False, False, True])
        budget = float(room["_room_budget"].dropna().iloc[0]) if "_room_budget" in room.columns and room["_room_budget"].notna().any() else float("nan")
        share_sum = float(room["expected_opportunity_share"].sum())
        sp_sum = float(room["starter_probability"].sum())
        lines.append(f"### {team} (budget={budget:.1f}, shares={share_sum:.3f}, P(win)={sp_sum:.3f})")
        lines.append("")
        cols = ["playerId", "name", "managed_season_points", "expected_opportunity_share",
                "starter_probability", "p10", "p50", "p75", "p90"]
        lines.append(room[cols].to_string(index=False))
        lines.append("")
    return "\n".join(lines)


def _regression_block(after, before):
    b = before.copy()
    b["playerId"] = b["playerId"].astype(str)
    old = b.drop_duplicates("playerId").set_index("playerId")
    lines = [
        "Drivers only. Not forced to consensus.",
        "",
        "Potentially underprojected:",
    ]
    for name in DIAGNOSTIC_UNDER:
        hit = after[after["name"] == name]
        if not hit.empty:
            lines.append(_diag_line(hit.iloc[0], old))
        else:
            lines.append(f"- {name}: not on board")
    lines += ["", "Potentially overprojected:"]
    for name in DIAGNOSTIC_OVER:
        hit = after[after["name"] == name]
        if not hit.empty:
            lines.append(_diag_line(hit.iloc[0], old))
    return "\n".join(lines)


def _diag_line(r, old):
    prev = old.loc[str(r["playerId"])] if str(r["playerId"]) in old.index else None
    old_rank = int(prev["rank"]) if prev is not None else "?"
    old_pts = float(prev["proj_points"]) if prev is not None else float("nan")
    bits = [f"rank {old_rank}→{int(r['rank'])}",
            f"pts {old_pts:.1f}→{float(r['proj_points']):.1f}",
            f"ppg {float(r['projected_ppg']):.2f}",
            f"games {float(r['projected_games']):.0f}",
            f"role {float(r['role']):.2f}",
            f"start_p {float(r['starter_probability']):.2f}"]
    if bool(r.get("prior_applied", False)):
        bits.append("named-QB prior")
    if bool(r.get("contested", False)):
        bits.append("committee budget split")
    if float(r["projected_games"]) < GAMES:
        bits.append("injury/ramp + waiver missed-games")
    if r["position"] == "TE":
        bits.append("FLEX replacement (no TE premium)")
    if r["position"] == "WR":
        bits.append("WR29 draft baseline")
    return f"- {r['name']} ({r['position']} {r['team']}): " + "; ".join(bits)


def main(year=2026):
    src = f"projections_{year}.csv"
    dest = f"projections_{year}_tuned.csv"
    raw = pd.read_csv(src, dtype={"playerId": str})
    prev = pd.read_csv(dest, dtype={"playerId": str}) if os.path.exists(dest) else None
    tuned, info = value_board(raw, apply_priors=True)
    out = tuned[OUTPUT_COLS].sort_values("rank")
    for c in ("p10", "p25", "p50", "p75", "p90", "starter_probability",
              "expected_opportunity_share", "role_confidence", "breakout_probability"):
        out[c] = pd.to_numeric(out[c], errors="coerce").round(3)
    out.to_csv(dest, index=False)
    write_report(raw, tuned, info, prev_tuned=prev)
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
