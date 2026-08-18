"""Backtest: project past seasons and score vs what actually happened.

The target is fantasy points per game PLAYED x 12 (health-conditional,
matching what the models project; >=4 games to keep rates meaningful),
for the top N players per position by that measure. A player a model didn't
project (e.g. a freshman the heuristic can't see) counts as a prediction of
0, so covering breakouts is rewarded. Reports MAE and Spearman rank
correlation for the naive "repeat last season's rate" baseline, the
heuristic, and the ML model. Usage: python3 backtest.py [years...]
"""
import sys

import pandas as pd

from features import games_played
from model import predict_year
from projections import GAMES, project, season_points

TOP_N = {"QB": 40, "RB": 60, "WR": 80, "TE": 40}


def spearman(a, b):
    return a.rank().corr(b.rank())  # avoids the scipy dependency


def rate_points(year, min_games):
    s = season_points(year).groupby("playerId").agg(
        position=("position", "first"), team=("team", "first"), pts=("points", "sum"))
    fbs = pd.read_csv(f"data/sp_{year}.csv")["team"]
    s = s[s["team"].isin(fbs)]  # FBS fantasy leagues only
    s["gp"] = games_played(year).reindex(s.index).fillna(0)
    s = s[s["gp"] >= min_games]
    s["actual"] = (s["pts"] / s["gp"].where(s["gp"] > 0)) * GAMES
    return s


def season_yield(year):
    """What a season of each player was actually worth to a fantasy owner:
    per-game rate x 12 for players with a real sample, raw total for cameos."""
    s = rate_points(year, min_games=0)
    return s["actual"].where(s["gp"] >= 6, s["pts"])


def evaluate(year):
    actual = rate_points(year, min_games=4)
    yields = season_yield(year)
    preds = {
        "naive": rate_points(year - 1, min_games=1)[["position", "actual"]]
                 .rename(columns={"actual": "proj_points"}),
        "heur": project(year).set_index("playerId")[["position", "proj_points"]],
        "ml": predict_year(year).set_index("playerId")[["position", "proj_points"]],
    }
    rows = []
    for pos, g in actual.groupby("position"):
        g = g.nlargest(TOP_N[pos], "actual")
        row = {"year": year, "pos": pos, "n": len(g)}
        for name, p in preds.items():
            pr = p["proj_points"].reindex(g.index).fillna(0)
            row[f"{name}_mae"] = round((pr - g["actual"]).abs().mean(), 1)
            row[f"{name}_rho"] = round(spearman(pr, g["actual"]), 3)
            # draft-board quality: what the model's own top N would have scored
            picks = p[p["position"] == pos].nlargest(TOP_N[pos], "proj_points")
            row[f"{name}_yield"] = round(yields.reindex(picks.index).fillna(0).mean(), 1)
        rows.append(row)
    return rows


if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:]] or [2023, 2024, 2025]
    results = pd.DataFrame([r for y in years for r in evaluate(y)])
    print(results.to_string(index=False))
    print("\noverall means:")
    cols = [c for c in results.columns if c.endswith(("_mae", "_rho", "_yield"))]
    print(results[cols].mean().round(3).to_string())
