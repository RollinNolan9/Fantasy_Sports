"""Gradient-boosted projections from role/coaching/context features.

Trains on post-COVID seasons before the target and predicts fantasy points
per game PLAYED (x12) for everyone on the target year's roster, including
freshmen and transfers. Projections are health-conditional: they assume the
player is on the field, since injuries can't be predicted preseason.
Usage: python3 model.py <target_year>
"""
import sys

import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from features import build_features, games_played
from projections import GAMES, POSITIONS, season_points

FIRST_FEATURE_YEAR = 2021  # post-COVID only: portal/NIL era is a different game
ALPHA = 5    # extra training weight per ~5 pts/game: fit the players who matter
BLEND = 0.25  # weight on last season's raw rate in the final projection

FEATURES = [
    "fppg_1", "fppg_2", "fppg_3", "played_1", "games_1", "rate_1",
    "share_1", "vac_share", "ret_rank", "grp_fppg_1",
    "class_year", "recruit_rating", "recruit_stars",
    "plays_pg_1", "pass_rate_1",
    "hc_change", "hc_plays_delta", "hc_passrate_delta",
    "sp_off_1", "transferred", "transfer_off_delta", "followed_hc",
    "comp_max_rate", "comp_transfer_fppg", "comp_fresh_rating",
] + [f"pos_{p}" for p in POSITIONS]


def predict_year(target):
    train = pd.concat([build_features(y) for y in range(FIRST_FEATURE_YEAR, target)])
    # defaults: a backtest sweep found no config meaningfully better
    m = HistGradientBoostingRegressor(random_state=0)
    m.fit(train[FEATURES], train["label"],
          sample_weight=train["weight"] * (1 + train["label"] / ALPHA))
    te = build_features(target).set_index("playerId").copy()
    ml = pd.Series(m.predict(te[FEATURES]), index=te.index).clip(lower=0) * GAMES
    # blend in last season's raw per-game rate: the ML mean under-spreads the top
    pts = season_points(target - 1).groupby("playerId")["points"].sum()
    last_rate = (pts / games_played(target - 1).reindex(pts.index)).dropna() * GAMES
    lr = last_rate.reindex(te.index)
    te["proj_points"] = (BLEND * lr + (1 - BLEND) * ml).where(lr.notna(), ml).round(1)
    te = te.reset_index().sort_values("proj_points", ascending=False)
    te["rank"] = range(1, len(te) + 1)
    te["pos_rank"] = (te["position"]
                      + te.groupby("position")["proj_points"]
                          .rank(ascending=False, method="first").astype(int).astype(str))
    return te[["rank", "pos_rank", "playerId", "name", "position", "team", "proj_points"]]


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    out = predict_year(year)
    out.to_csv(f"projections_{year}.csv", index=False)
    print(out.head(30).to_string(index=False))
    print(f"\n{len(out)} players -> projections_{year}.csv")
