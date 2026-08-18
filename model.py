"""Gradient-boosted projections from role/coaching/context features.

Trains on all historical seasons before the target and predicts fantasy
points per team-game for everyone on the target year's roster (including
freshmen and transfers). Usage: python3 model.py <target_year>
"""
import sys

import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from features import build_features
from projections import GAMES, POSITIONS

FIRST_FEATURE_YEAR = 2017  # needs 3 prior stat seasons; data starts 2014

FEATURES = [
    "fppg_1", "fppg_2", "fppg_3", "played_1",
    "share_1", "vac_share", "ret_rank", "grp_fppg_1",
    "class_year", "recruit_rating", "recruit_stars",
    "plays_pg_1", "pass_rate_1",
    "hc_change", "hc_plays_delta", "hc_passrate_delta",
    "sp_off_1", "transferred", "transfer_off_delta", "followed_hc",
] + [f"pos_{p}" for p in POSITIONS]


def predict_year(target):
    train = pd.concat([build_features(y) for y in range(FIRST_FEATURE_YEAR, target)])
    # params picked by backtest sweep; differences vs defaults were small
    m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05,
                                      l2_regularization=1.0, random_state=0)
    m.fit(train[FEATURES], train["label"])
    te = build_features(target).copy()
    te["proj_points"] = (pd.Series(m.predict(te[FEATURES]))
                         .clip(lower=0) * GAMES).round(1)
    return (te.sort_values("proj_points", ascending=False)
            [["playerId", "name", "position", "team", "proj_points"]])


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    out = predict_year(year)
    out.to_csv(f"projections_{year}.csv", index=False)
    print(out.head(30).to_string(index=False))
    print(f"\n{len(out)} players -> projections_{year}.csv")
