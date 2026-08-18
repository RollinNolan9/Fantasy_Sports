"""Player-season feature table for the ML model.

For target season N, every QB/RB/WR/TE on an FBS roster gets one row with
preseason-knowable features only: production history, role opportunity
(vacated production, returning depth rank), class year, recruit pedigree,
coaching change + the new HC's historical play-calling profile, and team
context (pace, pass rate, SP+ offense). Label = fantasy points per team-game
actually scored in season N (0 if rostered but never produced).
"""
import ast
from functools import lru_cache

import pandas as pd

from projections import POSITIONS, season_points

FIRST_DATA_YEAR = 2014


@lru_cache(maxsize=None)
def team_stats(year):
    t = pd.read_csv(f"data/teams_{year}.csv")
    w = t.pivot_table(index="team", columns="statName", values="statValue", aggfunc="first")
    w["plays_pg"] = (w["passAttempts"] + w["rushingAttempts"]) / w["games"]
    w["pass_rate"] = w["passAttempts"] / (w["passAttempts"] + w["rushingAttempts"])
    return w


@lru_cache(maxsize=None)
def roster(year):
    r = pd.read_csv(f"data/roster_{year}.csv", dtype={"id": str}).drop_duplicates("id")
    r["name"] = (r["firstName"].fillna("") + " " + r["lastName"].fillna("")).str.strip()
    return r.set_index("id")


@lru_cache(maxsize=None)
def coach_seasons():
    return pd.read_csv("data/coach_seasons.csv")


@lru_cache(maxsize=None)
def head_coach(team, year):
    c = coach_seasons()
    rows = c[(c["team"] == team) & (c["year"] == year)]
    return rows.sort_values("games").iloc[-1]["coach"] if len(rows) else None


def hc_profile(coach, year):
    """Mean pace and pass rate over the coach's last 3 HC seasons before `year`."""
    c = coach_seasons()
    rows = c[(c["coach"] == coach) & (c["year"] < year)].nlargest(3, "year")
    vals = []
    for r in rows.itertuples():
        try:
            ts = team_stats(r.year)
        except FileNotFoundError:
            continue
        if r.team in ts.index:
            vals.append(ts.loc[r.team, ["plays_pg", "pass_rate"]])
    return pd.DataFrame(vals).mean() if vals else None


@lru_cache(maxsize=None)
def recruit_map(max_year):
    """Cumulative recruit pedigree lookups: by CFBD athleteId and by recruit id."""
    by_athlete, by_recruit = {}, {}
    for y in range(FIRST_DATA_YEAR, max_year + 1):
        try:
            rec = pd.read_csv(f"data/recruits_{y}.csv", dtype={"athleteId": str, "id": str})
        except FileNotFoundError:
            continue
        for r in rec.itertuples():
            val = (float(r.rating), float(r.stars))
            if isinstance(r.athleteId, str):
                by_athlete[r.athleteId] = val
            by_recruit[str(r.id)] = val
    return by_athlete, by_recruit


def _hc_features(teams, year):
    """(hc_change, plays_pg delta, pass_rate delta) per team for season `year`."""
    ts_prev = team_stats(year - 1)
    out = {}
    for team in teams:
        now, before = head_coach(team, year), head_coach(team, year - 1)
        change = int(now is not None and before is not None and now != before)
        d_plays = d_pass = 0.0
        if change:
            prof = hc_profile(now, year)
            if prof is not None and team in ts_prev.index:
                d_plays = float(prof["plays_pg"] - ts_prev.loc[team, "plays_pg"])
                d_pass = float(prof["pass_rate"] - ts_prev.loc[team, "pass_rate"])
        out[team] = (change,
                     d_plays if pd.notna(d_plays) else 0.0,
                     d_pass if pd.notna(d_pass) else 0.0)
    return out


@lru_cache(maxsize=None)
def build_features(year):
    """Feature table for season `year`. Cached: callers must .copy() before mutating."""
    ros = roster(year)
    df = pd.DataFrame(index=ros.index)
    df["name"] = ros["name"]
    df["team"] = ros["team"]
    df["class_year"] = pd.to_numeric(ros["year"], errors="coerce").fillna(0)

    # production history, most recent 3 seasons
    hist = {}
    for k in (1, 2, 3):
        s = season_points(year - k)
        hist[k] = s.groupby("playerId").agg(
            fppg=("fppg", "sum"), position=("position", "first"), team=("team", "first"))
        df[f"fppg_{k}"] = hist[k]["fppg"].reindex(df.index).fillna(0)
    df["played_1"] = (hist[1]["fppg"].reindex(df.index).notna()).astype(int)

    # position: prefer stats-derived (most recent), fall back to roster listing
    pos = hist[1]["position"].reindex(df.index)
    for k in (2, 3):
        pos = pos.combine_first(hist[k]["position"].reindex(df.index))
    df["position"] = pos.combine_first(ros["position"])
    df = df[df["position"].isin(POSITIONS)].copy()

    # role opportunity: last season's usage share, vacated share, returning depth rank
    s1 = season_points(year - 1).copy()
    grp_tot = s1.groupby(["team", "position"])["fppg"].sum().clip(lower=0.01)
    s1["share"] = s1["fppg"].clip(lower=0) / grp_tot.reindex(
        pd.MultiIndex.from_frame(s1[["team", "position"]])).values
    team_1 = hist[1]["team"].reindex(df.index)
    df["share_1"] = s1.set_index("playerId")["share"].reindex(df.index).fillna(0)
    # share of last year's production at (current team, position) that departed
    s1["now_team"] = s1["playerId"].map(ros["team"])
    retained = (s1[s1["now_team"] == s1["team"]]
                .groupby(["team", "position"])["share"].sum())
    key = pd.MultiIndex.from_frame(df[["team", "position"]])
    df["vac_share"] = (1 - retained.reindex(key).fillna(0)).clip(0, 1).values
    df["grp_fppg_1"] = grp_tot.reindex(key).fillna(0).values
    df["ret_rank"] = df.groupby(["team", "position"])["fppg_1"].rank(
        ascending=False, method="first")

    # team context from last season
    ts1 = team_stats(year - 1)
    df["plays_pg_1"] = ts1["plays_pg"].reindex(df["team"]).fillna(ts1["plays_pg"].mean()).values
    df["pass_rate_1"] = ts1["pass_rate"].reindex(df["team"]).fillna(ts1["pass_rate"].mean()).values

    # coaching: HC change + how the new HC's historical profile differs
    hc = _hc_features(tuple(sorted(df["team"].unique())), year)
    df[["hc_change", "hc_plays_delta", "hc_passrate_delta"]] = [hc[t] for t in df["team"]]

    # SP+ offense of current team; quality delta for transfers
    sp = pd.read_csv(f"data/sp_{year - 1}.csv").set_index("team")["offense.rating"]
    df["sp_off_1"] = sp.reindex(df["team"]).fillna(sp.mean()).values
    df["transferred"] = ((df["played_1"] == 1) & (team_1 != df["team"])).astype(int)
    old_off = sp.reindex(team_1).fillna(sp.min()).values  # missing old team ~ FCS-level
    df["transfer_off_delta"] = (df["sp_off_1"] - old_off) * df["transferred"]
    # coach-follow transfers: new team's new HC is the player's old HC, so the
    # new team's last-season offense rating says nothing about what he's joining
    prev_hc = {t: head_coach(t, year - 1) for t in df["team"].unique()}
    now_hc = {t: head_coach(t, year) for t in df["team"].unique()}
    old_hc = team_1.map(lambda t: head_coach(t, year - 1) if pd.notna(t) else None)
    df["followed_hc"] = ((df["transferred"] == 1)
                         & (df["team"].map(now_hc) == old_hc)
                         & (df["team"].map(now_hc) != df["team"].map(prev_hc))).astype(int)
    df.loc[df["followed_hc"] == 1, "transfer_off_delta"] = 0.0

    # recruit pedigree (0 for walk-ons / unrated)
    by_athlete, by_recruit = recruit_map(year)
    ratings = []
    for pid in df.index:
        val = by_athlete.get(pid)
        if val is None and "recruitIds" in ros.columns:
            raw = ros.at[pid, "recruitIds"]
            try:
                ids = ast.literal_eval(raw) if isinstance(raw, str) else []
            except (ValueError, SyntaxError):
                ids = []
            vals = [by_recruit[str(i)] for i in ids if str(i) in by_recruit]
            val = max(vals) if vals else None
        ratings.append(val or (0.0, 0.0))
    df[["recruit_rating", "recruit_stars"]] = ratings

    for p in POSITIONS:
        df[f"pos_{p}"] = (df["position"] == p).astype(int)

    # label: fantasy points per team-game actually scored (0 = rostered, no stats)
    try:
        lab = season_points(year).groupby("playerId")["fppg"].sum()
        df["label"] = lab.reindex(df.index).fillna(0)
    except FileNotFoundError:
        df["label"] = float("nan")

    return df.rename_axis("playerId").reset_index()
