"""Backtest: project past seasons and score vs what actually happened.

Evaluates fantasy-relevant players (top N per position by actual points) who
had prior-season stats. Compares the model to a naive 'repeat last season'
baseline on MAE and Spearman rank correlation. Usage: python3 backtest.py
"""
import sys

import pandas as pd

from projections import GAMES, project, season_points

TOP_N = {"QB": 40, "RB": 60, "WR": 80, "TE": 40}


def spearman(a, b):
    return a.rank().corr(b.rank())  # avoids the scipy dependency


def evaluate(year):
    m = project(year).merge(
        season_points(year)[["playerId", "fppg"]], on="playerId")
    m["actual"] = m["fppg"] * GAMES
    prev = season_points(year - 1)[["playerId", "fppg"]].rename(columns={"fppg": "prev"})
    m = m.merge(prev, on="playerId", how="left")
    m["naive"] = m["prev"].fillna(0) * GAMES

    rows = []
    for pos, g in m.groupby("position"):
        g = g.nlargest(TOP_N[pos], "actual")
        rows.append({
            "year": year, "pos": pos, "n": len(g),
            "model_mae": round((g["proj_points"] - g["actual"]).abs().mean(), 1),
            "naive_mae": round((g["naive"] - g["actual"]).abs().mean(), 1),
            "model_rho": round(spearman(g["proj_points"], g["actual"]), 3),
            "naive_rho": round(spearman(g["naive"], g["actual"]), 3),
        })
    return rows


if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:]] or [2022, 2023, 2024, 2025]
    results = pd.DataFrame([r for y in years for r in evaluate(y)])
    print(results.to_string(index=False))
    print("\noverall means:")
    print(results[["model_mae", "naive_mae", "model_rho", "naive_rho"]].mean().round(3).to_string())
