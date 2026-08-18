"""Season-long fantasy projections. Usage: python3 projections.py <target_year>"""
import sys
from functools import lru_cache

import pandas as pd

# 0.5 PPR, 4pt pass TD. Edit to match your league.
SCORING = {
    ("passing", "YDS"): 0.04, ("passing", "TD"): 4.0, ("passing", "INT"): -2.0,
    ("rushing", "YDS"): 0.1, ("rushing", "TD"): 6.0,
    ("receiving", "REC"): 0.5, ("receiving", "YDS"): 0.1, ("receiving", "TD"): 6.0,
    ("fumbles", "LOST"): -2.0,
}
POSITIONS = ["QB", "RB", "WR", "TE"]
WEIGHTS = {1: 0.6, 2: 0.3, 3: 0.1}  # seasons back -> weight
SHRINK = 0.75                       # weight on player history vs positional mean
GAMES = 12                          # regular-season games to project


@lru_cache(maxsize=None)
def season_points(year):
    """Fantasy points per team-game for every QB/RB/WR/TE player-season.

    Cached: callers must not mutate the returned frame (use .copy()).
    """
    df = pd.read_csv(f"data/players_{year}.csv", dtype={"playerId": str})
    df = df[df["position"].isin(POSITIONS)].copy()
    stat = pd.to_numeric(df["stat"], errors="coerce").fillna(0)
    pts = [SCORING.get(k, 0.0) for k in zip(df["category"], df["statType"])]
    df["points"] = stat * pts
    fp = df.groupby(["playerId", "player", "position", "team"], as_index=False)["points"].sum()
    games = pd.read_csv(f"data/teamgames_{year}.csv").set_index("team")["games"]
    fp["fppg"] = fp["points"] / fp["team"].map(games).fillna(GAMES)
    fp["season"] = year
    return fp


def project(target_year):
    """Project season fantasy points for target_year from the prior 3 seasons.

    Only players on a target_year FBS roster are projected (handles graduation,
    NFL departures, and puts transfers on their new team).
    ponytail: no depth-chart or freshman modeling yet -- players with no prior
    stats are absent, and backups promoted to starter are underrated.
    """
    hist = pd.concat([season_points(y) for y in range(target_year - 3, target_year)])
    roster = (pd.read_csv(f"data/roster_{target_year}.csv", dtype={"id": str})
              .drop_duplicates("id").set_index("id"))
    hist["w"] = (target_year - hist["season"]).map(WEIGHTS)
    hist["wf"] = hist["fppg"] * hist["w"]

    g = hist.groupby("playerId")[["wf", "w"]].sum()
    hist_rate = g["wf"] / g["w"]
    # regression target: mean rate among players who actually produced
    pos_mean = hist[hist["fppg"] > 2].groupby("position")["fppg"].mean()

    proj = (hist.sort_values("season").groupby("playerId").tail(1)
            .set_index("playerId")[["player", "position", "team"]])
    proj = proj[proj.index.isin(roster.index)]
    proj["team"] = roster["team"].reindex(proj.index)
    proj["proj_fppg"] = SHRINK * hist_rate + (1 - SHRINK) * proj["position"].map(pos_mean)
    proj["proj_points"] = (proj["proj_fppg"] * GAMES).round(1)
    return (proj.reset_index()
            .sort_values("proj_points", ascending=False)
            [["playerId", "player", "position", "team", "proj_points"]])


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    out = project(year)
    out.to_csv(f"projections_{year}.csv", index=False)
    print(out.head(30).to_string(index=False))
    print(f"\n{len(out)} players -> projections_{year}.csv")
