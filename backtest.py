"""Backtest: project past seasons and score vs what actually happened.

Evaluates the top N players per position by ACTUAL points -- the slice that
decides fantasy leagues. A player a model didn't project (e.g. a freshman the
heuristic can't see) counts as a prediction of 0, so covering breakouts is
rewarded. Reports MAE and Spearman rank correlation for the naive
"repeat last season" baseline, the heuristic, and the ML model.
Usage: python3 backtest.py [years...]
"""
import sys

import pandas as pd

from model import predict_year
from projections import GAMES, project, season_points

TOP_N = {"QB": 40, "RB": 60, "WR": 80, "TE": 40}


def spearman(a, b):
    return a.rank().corr(b.rank())  # avoids the scipy dependency


def evaluate(year):
    actual = season_points(year).groupby("playerId").agg(
        position=("position", "first"), actual=("fppg", "sum"))
    actual["actual"] *= GAMES
    preds = {
        "naive": season_points(year - 1).groupby("playerId")["fppg"].sum() * GAMES,
        "heur": project(year).set_index("playerId")["proj_points"],
        "ml": predict_year(year).set_index("playerId")["proj_points"],
    }
    rows = []
    for pos, g in actual.groupby("position"):
        g = g.nlargest(TOP_N[pos], "actual")
        row = {"year": year, "pos": pos, "n": len(g)}
        for name, p in preds.items():
            pr = p.reindex(g.index).fillna(0)
            row[f"{name}_mae"] = round((pr - g["actual"]).abs().mean(), 1)
            row[f"{name}_rho"] = round(spearman(pr, g["actual"]), 3)
        rows.append(row)
    return rows


if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:]] or [2023, 2024, 2025]
    results = pd.DataFrame([r for y in years for r in evaluate(y)])
    print(results.to_string(index=False))
    print("\noverall means:")
    cols = [c for c in results.columns if c.endswith(("_mae", "_rho"))]
    print(results[cols].mean().round(3).to_string())
