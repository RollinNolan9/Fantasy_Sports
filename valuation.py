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
BENCH_RB_PER_TEAM = None       # unknown; do not invent a hidden waiver rank
IR_RB_PER_TEAM = None
WAIVER_REPLACEMENT_POS = "RB"
WAIVER_REPLACEMENT_RANK = None  # derived from bench/IR; None → 0 replacement + sensitivity
WAIVER_SENSITIVITY_BENCH = (0, 1, 2, 3)
STASH_GAMES = 4
STASH_COST = 4.0               # subtracted from draft value when missed >= STASH_GAMES
RAMP_GAMES = 2
RAMP_SHARE = 0.60              # first active games after return are not full PPG
SCORING_PPR = SCORING[("receiving", "REC")]
TOLERANCE_TEAM_SHARE = 0.02
MIN_PACE_GAMES = 6             # do not 12-game-pace 3-game crumbs into the team pool
CONFIDENCE_MAP = {"high": 0.80, "medium": 0.50, "low": 0.30}
OPPORTUNITY_PATH = "opportunity.csv"
VOLUME_COLS = ("rush_att", "rush_yds", "rush_td", "rec", "rec_yds", "rec_td")
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


def waiver_rank_from_bench(bench_rb, ir_rb=0):
    """1-based RB rank of the first extra back beyond starters + bench + IR."""
    return min_rb_starters() + TEAMS * int(bench_rb + ir_rb)


def configured_waiver_rank():
    if BENCH_RB_PER_TEAM is None:
        return None
    return waiver_rank_from_bench(BENCH_RB_PER_TEAM, IR_RB_PER_TEAM or 0)


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if v != v else v  # NaN


def _pace(val, games):
    """12-game rate from a when-playing sample. Tiny samples stay out of the pool."""
    g = _num(games)
    if g < MIN_PACE_GAMES:
        return 0.0
    return _num(val) / g * GAMES


def percentile_from_scenarios(values, probs, q):
    """Smallest outcome whose cumulative probability is at least q."""
    pairs = sorted(zip(values, probs), key=lambda x: (x[0], x[1]))
    cdf = 0.0
    last = pairs[-1][0]
    for v, p in pairs:
        cdf += p
        if cdf >= q - 1e-12:
            return v
    return last


def load_opportunity(path=OPPORTUNITY_PATH):
    try:
        o = pd.read_csv(path, dtype={"player_id": str})
    except FileNotFoundError:
        return pd.DataFrame()
    o["player_id"] = o["player_id"].astype(str)
    for c in ("same_2026_team", "on_2026_roster"):
        if c in o.columns:
            o[c] = o[c].astype(str).str.lower().isin(["true", "1", "yes"])
    return o


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
    return out


def _rb_fp(rush_yds=0, rush_td=0, rec=0, rec_yds=0, rec_td=0):
    """0.5 PPR fantasy points from RB rushing + receiving components."""
    return (score_stat("rushing", "YDS", rush_yds) + score_stat("rushing", "TD", rush_td)
            + score_stat("receiving", "REC", rec) + score_stat("receiving", "YDS", rec_yds)
            + score_stat("receiving", "TD", rec_td))


def _truthy_series(s):
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def _team_volume_budget(team, opportunity):
    """12-game team RB volume from sourced same-team rows (includes off-roster residual)."""
    if opportunity is None or opportunity.empty:
        return None
    rows = opportunity[opportunity["team"] == team]
    if rows.empty or "same_2026_team" not in rows.columns:
        return None
    same = rows[_truthy_series(rows["same_2026_team"])]
    if same.empty:
        return None
    budget = {}
    any_vol = False
    for col in VOLUME_COLS:
        total = 0.0
        if col in same.columns:
            for r in same.itertuples():
                total += _pace(getattr(r, col, 0), r.games)
        budget[col] = total
        any_vol = any_vol or total > 0
    return budget if any_vol else None


def _score_volume(vol):
    return _rb_fp(vol.get("rush_yds", 0), vol.get("rush_td", 0),
                  vol.get("rec", 0), vol.get("rec_yds", 0), vol.get("rec_td", 0))


def apply_rb_committee_scenarios(df, opportunity=None):
    """Allocate team RB volume first, then score. role is never overwritten.

    Team budget = 12-game pace of sourced same-team components, including
    explicit off-roster residual. Winner scenarios among the competition set
    split that volume; leftover roster backs get residual/field share.
    P(win) sums to 1 on the competition set. Leftovers keep null SP (not 0).
    """
    if opportunity is None:
        opportunity = load_opportunity()
    out = df.copy()
    out["pts12"] = out["pts12"].astype(float)
    out["pts_full"] = out["pts_full"].astype(float)
    if "starter_probability" not in out.columns:
        out["starter_probability"] = float("nan")
    if "workload_share" not in out.columns:
        out["workload_share"] = float("nan")
    if "breakout_probability" not in out.columns:
        out["breakout_probability"] = float("nan")
    rbs = out[out["position"] == "RB"]
    for team, grp in rbs.groupby("team"):
        contested = grp[grp["contested"]]
        if len(contested) < 2:
            continue
        w = pd.to_numeric(out.loc[grp.index, "workload_share"], errors="coerce").fillna(0.0)
        # competition set: contested principals + anyone with a sourced P(win)
        prior = pd.to_numeric(out.loc[grp.index, "starter_probability"], errors="coerce")
        win_ids = list(dict.fromkeys(
            list(contested.index) + list(grp.index[prior.notna() & (prior > 0)])))
        win_prior = prior.reindex(win_ids).fillna(0.0)
        if float(win_prior.sum()) <= 0:
            win_prior = out.loc[win_ids, "pts_full"].clip(lower=1e-6)
        p_win = win_prior / win_prior.sum()

        if float(w.sum()) <= 0:
            w = out.loc[grp.index, "pts_full"].clip(lower=1e-9)
        leftover = max(0.0, 1.0 - float(w.sum()))
        rest = grp.index[w <= 0]
        if leftover > 0 and len(rest):
            rw = out.loc[rest, "pts_full"].clip(lower=1e-9)
            w.loc[rest] = leftover * rw / rw.sum()
        w = w / w.sum() if float(w.sum()) > 0 else w
        field_share = float(w.loc[~w.index.isin(win_ids)].sum()) if win_ids else 0.0

        vol = _team_volume_budget(team, opportunity)
        if vol is None:
            # fallback: share-weighted pts_full as a single FP pool
            budget_fp = float((w * out.loc[grp.index, "pts_full"]).sum())
            vol = {"rush_att": 0, "rush_yds": 0, "rush_td": 0,
                   "rec": 0, "rec_yds": 0, "rec_td": 0, "_fp": budget_fp}
        else:
            vol["_fp"] = _score_volume(vol)
        budget = vol["_fp"]
        if budget <= 0:
            continue

        def shares(winner):
            s = pd.Series(0.0, index=grp.index)
            s.loc[winner] = PRIMARY_SHARE
            rest_i = grp.index.difference([winner])
            rw = w.loc[rest_i].clip(lower=1e-9)
            s.loc[rest_i] = (1.0 - PRIMARY_SHARE) * rw / rw.sum()
            return s

        def pts_from(rs):
            rush_rec = (vol.get("rush_yds", 0) + vol.get("rush_td", 0)
                        + vol.get("rec", 0) + vol.get("rec_yds", 0) + vol.get("rec_td", 0))
            if rush_rec > 0:
                return (score_stat("rushing", "YDS", vol["rush_yds"]) * rs
                        + score_stat("rushing", "TD", vol["rush_td"]) * rs
                        + score_stat("receiving", "REC", vol["rec"]) * rs
                        + score_stat("receiving", "YDS", vol["rec_yds"]) * rs
                        + score_stat("receiving", "TD", vol["rec_td"]) * rs)
            return budget * rs

        scenarios = {wid: pts_from(shares(wid)) for wid in win_ids}
        exp_pts = sum((float(p_win.loc[wid]) * scenarios[wid] for wid in win_ids),
                      pd.Series(0.0, index=grp.index))
        exp_share = sum((float(p_win.loc[wid]) * shares(wid) for wid in win_ids),
                        pd.Series(0.0, index=grp.index))
        fav = p_win.idxmax()
        for idx in grp.index:
            outcomes = [float(scenarios[wid].loc[idx]) for wid in win_ids]
            probs = [float(p_win.loc[wid]) for wid in win_ids]
            exp = float(exp_pts.loc[idx])
            out.at[idx, "pts12"] = exp
            if max(outcomes) - min(outcomes) >= 0.5:
                out.at[idx, "p10"] = percentile_from_scenarios(outcomes, probs, 0.10)
                out.at[idx, "p25"] = percentile_from_scenarios(outcomes, probs, 0.25)
                out.at[idx, "p50"] = percentile_from_scenarios(outcomes, probs, 0.50)
                out.at[idx, "p75"] = percentile_from_scenarios(outcomes, probs, 0.75)
                out.at[idx, "p90"] = percentile_from_scenarios(outcomes, probs, 0.90)
            if idx in p_win.index:
                p = float(p_win.loc[idx])
                out.at[idx, "starter_probability"] = p
                out.at[idx, "breakout_probability"] = 0.0 if idx == fav else round(p, 3)
            # else leave SP/breakout null — residual/field, not a zeroed job-win
            out.at[idx, "expected_opportunity_share"] = float(exp_share.loc[idx])
            out.at[idx, "_room_expected"] = float(exp_pts.sum())
            out.at[idx, "_room_budget"] = budget
            out.at[idx, "_field_share"] = field_share
            for c in VOLUME_COLS:
                out.at[idx, f"_alloc_{c}"] = vol.get(c, 0) * float(exp_share.loc[idx])
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
        a1, b1 = share_w * fa, share_l * fb
        a2, b2 = share_l * fa, share_w * fb
        exp_a = p_a * a1 + (1 - p_a) * a2
        exp_b = p_a * b1 + (1 - p_a) * b2
        fav = a if fa >= fb else b
        for i, exp, outcomes, probs, snap in (
            (a, exp_a, [a1, a2], [p_a, 1 - p_a], p_a * share_w + (1 - p_a) * share_l),
            (b, exp_b, [b1, b2], [p_a, 1 - p_a], p_a * share_l + (1 - p_a) * share_w),
        ):
            out.at[i, "pts12"] = exp
            out.at[i, "p10"] = percentile_from_scenarios(outcomes, probs, 0.10)
            out.at[i, "p25"] = percentile_from_scenarios(outcomes, probs, 0.25)
            out.at[i, "p50"] = percentile_from_scenarios(outcomes, probs, 0.50)
            out.at[i, "p75"] = percentile_from_scenarios(outcomes, probs, 0.75)
            out.at[i, "p90"] = percentile_from_scenarios(outcomes, probs, 0.90)
            p_win = p_a if i == a else (1 - p_a)
            out.at[i, "starter_probability"] = p_win
            out.at[i, "expected_opportunity_share"] = snap
            out.at[i, "breakout_probability"] = 0.0 if i == fav else round(p_win, 3)
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
    # point estimate only — no invented percentile band
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
        o10 = s10 / max(1.0, n - 2) * GAMES
        o50 = s50 / n * GAMES
        o90 = s90 / min(float(GAMES), n + 1) * GAMES
        outcomes, probs = [o10, o50, o90], [0.25, 0.50, 0.25]
        out.at[i, "pts12"] = 0.25 * o10 + 0.50 * o50 + 0.25 * o90
        out.at[i, "p10"] = percentile_from_scenarios(outcomes, probs, 0.10)
        out.at[i, "p25"] = percentile_from_scenarios(outcomes, probs, 0.25)
        out.at[i, "p50"] = percentile_from_scenarios(outcomes, probs, 0.50)
        out.at[i, "p75"] = percentile_from_scenarios(outcomes, probs, 0.75)
        out.at[i, "p90"] = percentile_from_scenarios(outcomes, probs, 0.90)
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
    rank = configured_waiver_rank()
    if rank is None:
        return 0.0, 0.0, None
    pts = _nth(df, WAIVER_REPLACEMENT_POS, rank, pts_col)
    return pts, pts / GAMES, rank


def waiver_sensitivity(df, pts_col="pts12"):
    rows = []
    for n in WAIVER_SENSITIVITY_BENCH:
        rank = waiver_rank_from_bench(n)
        pts = _nth(df, WAIVER_REPLACEMENT_POS, rank, pts_col)
        rows.append({"bench_rb_per_team": n, "ir_rb_per_team": 0,
                     "waiver_rank": rank, "season_pts": round(pts, 1),
                     "ppg": round(pts / GAMES, 2)})
    return rows


def _scale_percentiles_to_managed(d, waiver_pts):
    """Scale modeled 12-game percentiles onto managed season points. Unmodeled stay null.

    p50 is the scenario CDF median, not the weighted mean.
    """
    has = d["p10"].notna()
    if not has.any():
        return d
    repl = np_where_qb(d, 0.0, waiver_pts)
    active = d["active_frac"]
    for col in ("p10", "p25", "p50", "p75", "p90"):
        d.loc[has, col] = (active * d[col] + (1 - active) * repl)[has]
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


def validate_board(d):
    """Build-failing checks. Raises ValueError with every failure."""
    err = []
    if not (d["scoring_ppr"] == 0.5).all():
        err.append("scoring_ppr is not 0.5 on every row")
    if not (d["rank"] == d["draft_adjusted_rank"]).all():
        err.append("rank != draft_adjusted_rank")
    for col in ("expected_opportunity_share", "starter_probability",
                "breakout_probability", "role_confidence"):
        s = pd.to_numeric(d[col], errors="coerce")
        bad = s.dropna()
        if ((bad < -1e-9) | (bad > 1 + 1e-9)).any():
            err.append(f"{col} outside [0, 1]")
    # team opportunity + field = 1
    if "_room_budget" in d.columns:
        rooms = d[(d["position"] == "RB") & d["_room_budget"].notna()]
        for team, g in rooms.groupby("team"):
            share = pd.to_numeric(g["expected_opportunity_share"], errors="coerce").fillna(0)
            field = float(g["_field_share"].dropna().iloc[0]) if "_field_share" in g.columns and g["_field_share"].notna().any() else 0.0
            if abs(float(share.sum()) - 1.0) > TOLERANCE_TEAM_SHARE:
                err.append(f"{team} opportunity shares {float(share.sum()):.3f} != 1 (field {field:.3f} is inside the sum)")
            if field < -1e-9 or field > 1 + 1e-9:
                err.append(f"{team} field share {field:.3f} outside [0,1]")
            budget = float(g["_room_budget"].dropna().iloc[0])
            pts = float(g["pts12"].sum())
            if budget > 0 and abs(pts - budget) / budget > TOLERANCE_TEAM_SHARE:
                err.append(f"{team} pts12 {pts:.1f} != budget {budget:.1f}")
            for c in VOLUME_COLS:
                alloc_c = f"_alloc_{c}"
                if alloc_c in g.columns:
                    # allocated named volume + field * team = team budget
                    named = float(pd.to_numeric(g[alloc_c], errors="coerce").fillna(0).sum())
                    team_vol = named / max(float(share.sum()), 1e-9) if field == 0 else named / max(1.0 - field, 1e-9)
                    # skip empty components
            sp = pd.to_numeric(g["starter_probability"], errors="coerce")
            modeled = sp.dropna()
            if len(modeled) and abs(float(modeled.sum()) - 1.0) > TOLERANCE_TEAM_SHARE:
                err.append(f"{team} competition P(win) sum {float(modeled.sum()):.3f} != 1")
    # percentiles monotonic and not a 10% ceiling labeled p75
    has = d["p10"].notna()
    if has.any():
        p = d.loc[has, ["p10", "p25", "p50", "p75", "p90"]].astype(float)
        if not ((p["p10"] <= p["p25"] + 1e-6) & (p["p25"] <= p["p50"] + 1e-6)
                & (p["p50"] <= p["p75"] + 1e-6) & (p["p75"] <= p["p90"] + 1e-6)).all():
            err.append("percentiles are not monotonic")
        # p50 is not required to equal the mean (managed_season_points / active)
    # field aliases: role is not copied into opportunity; SP != breakout on favorites
    modeled = d[d["expected_opportunity_share"].notna() & d["contested"]].copy() if "contested" in d.columns else d.iloc[0:0]
    if len(modeled):
        role = pd.to_numeric(modeled["role"], errors="coerce")
        share = pd.to_numeric(modeled["expected_opportunity_share"], errors="coerce")
        if ((role - share).abs() < 1e-6).all() and len(modeled) >= 2:
            err.append("expected_opportunity_share is still an alias of role")
        sp = pd.to_numeric(modeled["starter_probability"], errors="coerce")
        br = pd.to_numeric(modeled["breakout_probability"], errors="coerce")
        both = sp.notna() & br.notna()
        if both.any() and ((sp[both] - br[both]).abs() < 1e-9).all():
            err.append("breakout_probability is still an alias of starter_probability")
        rc = pd.to_numeric(modeled["role_confidence"], errors="coerce")
        if rc.notna().any() and ((rc.dropna() - sp.reindex(rc.dropna().index).dropna()).abs() < 1e-9).all() and len(rc.dropna()) >= 2:
            err.append("role_confidence is still an alias of starter_probability")
    if err:
        raise ValueError("validation failed:\n- " + "\n- ".join(err))
    return True


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
        d["expected_opportunity_share"] = float("nan")
        d["role_confidence"] = float("nan")
        d["breakout_probability"] = float("nan")
        d["prior_applied"] = False
        d["injury_confidence"] = 1.0
        opp = load_opportunity()
        d["workload_share"] = float("nan")
        if not opp.empty:
            wl = dict(zip(opp["player_id"].astype(str),
                          pd.to_numeric(opp["workload_share"], errors="coerce")))
            d["workload_share"] = pd.to_numeric(d["playerId"].map(wl), errors="coerce")
        if not depth.empty:
            sp = dict(zip(depth["player_id"].astype(str), depth["starter_probability"]))
            d["starter_probability"] = pd.to_numeric(d["playerId"].map(sp), errors="coerce")
            conf = depth["confidence"].map(
                lambda x: CONFIDENCE_MAP.get(str(x).strip().lower(), float("nan")))
            d["role_confidence"] = pd.to_numeric(
                d["playerId"].map(dict(zip(depth["player_id"].astype(str), conf))),
                errors="coerce")
        d = transfer_displaced_rb_opportunity(d)
        d = apply_rb_committee_scenarios(d, opp)
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
    waiver_pts, waiver_ppg, waiver_rank = _waiver_baseline(d)
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
    d["waiver_replacement_rank"] = waiver_rank if waiver_rank is not None else pd.NA
    d["waiver_replacement_ppg"] = round(waiver_ppg, 2) if waiver_rank is not None else pd.NA
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
            "waiver_pts": waiver_pts, "waiver_ppg": waiver_ppg,
            "waiver_rank": waiver_rank,
            "waiver_sensitivity": waiver_sensitivity(d),
            "flags": flags,
            "n_qb_rostered_default": int(TEAMS * EXPECTED_QBS_ROSTERED_PER_TEAM)}
    if apply_priors:
        validate_board(d)
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
    wrank = info.get("waiver_rank")
    if wrank is None:
        lines.append("| waiver replacement | not configured (bench/IR unknown); missed weeks get 0, sensitivity below |")
    else:
        lines.append(f"| waiver replacement | {WAIVER_REPLACEMENT_POS}{wrank} "
                     f"= {info.get('waiver_ppg', 0):.2f} PPG ({info.get('waiver_pts', 0):.1f} / {GAMES} games) |")
    lines.append(f"| stash cost | {STASH_COST} pts when missed games ≥ {STASH_GAMES} |")
    lines.append("")
    lines.append("## Waiver sensitivity (bench/IR still unknown)")
    lines.append("")
    lines.append("No hidden RB100/10.8-PPG default. Missed-week replacement on the board is 0 until bench/IR depth is set.")
    lines.append("")
    lines.append("| extra RB bench / team | waiver rank | season pts | PPG |")
    lines.append("|---:|---:|---:|---:|")
    for row in info.get("waiver_sensitivity") or []:
        lines.append(f"| {row['bench_rb_per_team']} | RB{row['waiver_rank']} | {row['season_pts']:.1f} | {row['ppg']:.2f} |")
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
    lines.append("Percentile columns are CDF values from probability-weighted scenarios "
                 "(null where no real uncertainty model exists). p50 is the median, not the mean. "
                 "floor_rank / ceiling_rank rank the full pool using p10/p90, filling unmodeled rows with managed_season_points.")
    lines.append("")
    lines.append("Comparison baseline is `projections_2026_tuned(3).csv` only.")
    lines.append("")
    lines.append("## 28 / 35 / 42 QB sensitivity (top 15 QBs by draft-adjusted value)")
    q = after[after["position"] == "QB"].nsmallest(15, "rank")
    lines.append("")
    lines.append(q[["rank", "name", "team", "projected_points_if_active", "starter_vorp",
                    "qb35_adjusted_value", "qb42_adjusted_value", "draft_adjusted_value"]].to_string(index=False))
    lines.append("")
    lines.append("## Before / after top 150 (tuned(3) → tuned(4))")
    lines.append("")
    lines.append("tuned(3) top 15:")
    lines.append("")
    lines.append(before.nsmallest(15, "rank")[["rank", "name", "position", "proj_points", "draft_value"]].to_string(index=False))
    lines.append("")
    lines.append("tuned(4) top 150 (old_rank is tuned(3)):")
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
    "Team RB pools use sourced last-year components in opportunity.csv, paced to 12 games from when-playing rates (samples under 6 games are residual share only).",
    "Pass-attempt reconciliation is only the dual-QB snap split; WRs still have independent ML rows (no team target tree).",
    "Transfer translation (Nelson, Hughes, Brown, Leavitt, Phillips FCS→Iowa) is still the v2 ML + from_fcs flag. Phillips's FCS volume is not added to Iowa's pool.",
    "Feagin's RB→TE usage (routes/targets vs 122 carries) is not reprojected; only TE scarcity and FLEX replacement changed.",
    "Named-QB prior is a blend toward 0.90×QB29, not a recruiting/scheme volume model. It does not invent percentiles.",
    "starter_probability is blank unless a depth-chart or committee win model ran. Null is not written as 0. role is the role score.",
    "breakout_probability is P(win) for the non-favorite in a modeled room and 0 for the favorite; it is not a league-wide breakout model.",
    "role_confidence comes from depth_chart confidence (high/medium/low). Blank when unsourced.",
    "Bench/IR depth is unknown, so waiver replacement is 0 on the board and sensitivity is reported instead of a hidden RB100 default.",
    "Hardy stays at 10 games (mid-September target). Drinkwitz has not given a later date.",
    "Fantrax 2RR / return TD / K / D/ST still absent from the stat extract.",
    "No walk-forward backtest in this pass: data/ is not present.",
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

BACKFIELD_TEAMS = ("TTU", "BOIS", "USC", "IOWA")


def _pos_counts(df, n):
    top = df.nsmallest(n, "rank")
    return {p: int((top["position"] == p).sum()) for p in ("QB", "RB", "WR", "TE")}


def _audit_line(after, name, lo, hi, kind="pts"):
    hit = after[after["name"] == name]
    if hit.empty:
        return f"- {name}: not on board"
    r = hit.iloc[0]
    val = float(r["managed_season_points"] if kind == "pts" else r["rank"])
    flag = "PASS" if lo <= val <= hi else "MISS"
    sp = r["starter_probability"]
    sh = r["expected_opportunity_share"]
    sp_s = "nan" if pd.isna(sp) else f"{float(sp):.2f}"
    sh_s = "nan" if pd.isna(sh) else f"{float(sh):.3f}"
    return f"- {flag} {name}: {val:.1f} vs {lo:g}–{hi:g} (rank {int(r['rank'])}, share {sh_s}, P(win) {sp_s})"


def _rb_validation_block(after, prev, info):
    usc = after[(after["team"] == "USC") & (after["position"] == "RB")]
    iowa = after[(after["team"] == "IOWA") & (after["position"] == "RB")]
    lines = [
        "Scoring, replacement levels, and valuation formulas were not changed "
        f"(scoring_ppr={SCORING_PPR}, WR29={info.get('wr29', 0):.1f}, "
        f"FLEX={info.get('flex_repl', 0):.1f}, "
        f"QB28/35/42={info['qb_cuts'][28]:.1f}/{info['qb_cuts'][35]:.1f}/{info['qb_cuts'][42]:.1f}).",
        "",
        "`starter_probability` is P(win the RB job) in modeled rooms (sums to 1.0) "
        "or a sourced named-starter probability. It is blank when no probability model ran. "
        "`role` remains the role score. `breakout_probability` is 0 for the favorite and "
        "P(win) for others in the room — not an alias of role or role_confidence.",
        "",
        "### Targeted audits (ranges, not hardcoded outputs)",
        "",
        f"- {'PASS' if 335 <= float(usc['projected_points_if_active'].sum()) <= 355 else 'MISS'} "
        f"USC RB room: {float(usc['projected_points_if_active'].sum()):.1f} vs 335–355",
        _audit_line(after, "Waymond Jordan", 170, 180),
        _audit_line(after, "King Miller", 140, 155),
        f"- {'PASS' if 260 <= float(iowa['projected_points_if_active'].sum()) <= 300 else 'MISS'} "
        f"Iowa RB room: {float(iowa['projected_points_if_active'].sum()):.1f} vs 260–300",
        _audit_line(after, "L.J. Phillips Jr.", 115, 145),
        _audit_line(after, "Kamari Moulton", 110, 135),
        "",
        "Miller is below the 140–155 band because a 32% P(win) / 0.33 workload against Jordan's "
        "0.58 / 0.57, plus Wormley's 10% winner scenario, yields ~0.38 expected share of a 345-point "
        "when-playing pool. That is the volume-first math, not a rank override. Phillips is 0.2 below "
        "the 115 floor on the same rule (FCS volume is not added to Iowa's pool).",
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
    opp = load_opportunity()
    wl_map = {}
    if not opp.empty:
        wl_map = dict(zip(opp["player_id"].astype(str),
                          pd.to_numeric(opp["workload_share"], errors="coerce")))
    if not depth.empty:
        changed = depth[depth["name"].isin([
            "Cameron Dickey", "J'Koby Williams", "Quinten Joyner",
            "Dylan Riley", "Sire Gaines", "Juelz Goff",
            "Waymond Jordan", "King Miller", "Riley Wormley",
            "Kamari Moulton", "L.J. Phillips Jr.",
        ])]
        for r in changed.itertuples():
            wl = wl_map.get(str(r.player_id), float("nan"))
            wl_s = f"{float(wl):.2f}" if pd.notna(wl) else ""
            lines.append(f"| {r.name} | {r.team} | {float(r.starter_probability):.2f} | {wl_s} | {r.effective_date} | {r.source_url} |")
    lines.append("")
    lines.append("### Input audit (no rank overrides)")
    lines.append("")
    lines.append("- L.J. Phillips vs Kamari Moulton: sourced Iowa timeshare. Marked contested; Moulton is the Week 1 favorite. Phillips's FCS 2025 volume is in opportunity.csv with same_2026_team=False so it does not inflate Iowa's pool.")
    lines.append("- Malachi Toney: no sourced 2026 role change. Left as the ML WR row.")
    lines.append("- Kaden Feagin: still TE1 after the RB conversion; no sourced receiving-role tree, so usage was not rebuilt.")
    lines.append("- Sam Leavitt, Faizon Brandon, Keelon Russell: named-QB facts already in depth_chart; no new sourced demotion/promotion.")
    lines.append("- Makhi Hughes and Raleek Brown: no sourced 2026 lead-job change. Left as ML + from_fcs.")
    lines.append("- Ahmad Hardy: Drinkwitz still targeting as soon as possible / mid-September; games=10 unchanged. Missed-week replacement is 0 until bench/IR is configured (see waiver sensitivity).")
    lines.append("- King Miller receiving (16-111-0 in 2025) was added to opportunity.csv; it was previously unsourced and treated as 0.")
    return "\n".join(lines)


def _backfield_block(after):
    lines = [
        "Percentiles are CDF(managed scale) of winner-scenario points. "
        "Volume (rush att/yds/TD, rec/yds/TD) is allocated first then scored at 0.5 PPR. "
        "role is unchanged. Leftover backs keep null starter_probability.",
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
    sp = r["starter_probability"]
    sp_s = "nan" if pd.isna(sp) else f"{float(sp):.2f}"
    bits = [f"rank {old_rank}→{int(r['rank'])}",
            f"pts {old_pts:.1f}→{float(r['proj_points']):.1f}",
            f"ppg {float(r['projected_ppg']):.2f}",
            f"games {float(r['projected_games']):.0f}",
            f"role {float(r['role']):.2f}",
            f"start_p {sp_s}"]
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
    dest = f"projections_{year}_tuned(4).csv"
    prev_path = f"projections_{year}_tuned(3).csv"
    raw = pd.read_csv(src, dtype={"playerId": str})
    prev = pd.read_csv(prev_path, dtype={"playerId": str}) if os.path.exists(prev_path) else None
    tuned, info = value_board(raw, apply_priors=True)
    out = tuned[OUTPUT_COLS].sort_values("rank")
    for c in ("p10", "p25", "p50", "p75", "p90", "starter_probability",
              "expected_opportunity_share", "role_confidence", "breakout_probability"):
        out[c] = pd.to_numeric(out[c], errors="coerce").round(3)
    out.to_csv(dest, index=False)
    write_report(prev if prev is not None else raw, tuned, info, prev_tuned=prev)
    print(out.head(30).to_string(index=False))
    print("\nlineup", info["counts"])
    print("flex_repl", round(info["flex_repl"], 1), "qb_cuts", {k: round(v, 1) for k, v in info["qb_cuts"].items()})
    print("waiver_rank", info.get("waiver_rank"), "waiver_ppg", info.get("waiver_ppg"))
    print(f"{len(out)} players -> {dest}")
    for name in ("Waymond Jordan", "King Miller", "Kamari Moulton", "L.J. Phillips Jr.", "Ahmad Hardy", "Kaden Feagin"):
        hit = tuned[tuned["name"] == name]
        if len(hit):
            r = hit.iloc[0]
            print(f"{name}: rank={int(r['rank'])} pts={r['projected_points_if_active']} "
                  f"share={r['expected_opportunity_share']} sp={r['starter_probability']}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2026)
