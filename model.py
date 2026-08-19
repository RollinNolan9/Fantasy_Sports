"""v2 season-long CFB fantasy projections.

python3 model.py [year]  ->  projections_{year}.csv
"""
import sys
import warnings

import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

warnings.filterwarnings("ignore", message="invalid value encountered in subtract")

from features import RATE_SHRINK, build_features, games_played
from projections import GAMES, POSITIONS, season_points

VERSION = "2"
FIRST_FEATURE_YEAR = 2021
ALPHA = 5
BLEND = 0.0   # backtest: any last-year stickiness hurt MAE and yield; rho was flat
FULL_ROLE_GAMES = 9

TEAMS = 18
SLOTS = {"QB": 1, "RB": 2, "WR": 2}
FLEX = 3
FLEX_ELIGIBLE = {"RB", "WR"}

FEATURES = [
    "fppg_1", "fppg_2", "fppg_3", "played_1", "games_1", "rate_1",
    "share_1", "vac_share", "ret_rank", "grp_fppg_1",
    "class_year", "recruit_rating", "recruit_stars",
    "plays_pg_1", "pass_rate_1", "new_playcaller",
    "hc_change", "hc_plays_delta", "hc_passrate_delta",
    "sp_off_1", "transferred", "transfer_off_delta", "followed_hc", "from_fcs",
    "comp_max_rate", "comp_transfer_fppg", "comp_fresh_rating",
    "pass_rate_1p", "rush_rate_1p", "rec_rate_1p",
] + [f"pos_{p}" for p in POSITIONS]


def replacement_points(df):
    """First player at each position who doesn't start (dedicated slots, then flex)."""
    leftover = {p: n * TEAMS for p, n in SLOTS.items()}
    flex_left = FLEX * TEAMS
    repl = {}
    for r in df.sort_values("proj_points", ascending=False).itertuples():
        pos = r.position
        if leftover.get(pos, 0) > 0:
            leftover[pos] -= 1
        elif pos in FLEX_ELIGIBLE and flex_left > 0:
            flex_left -= 1
        elif pos not in repl:
            repl[pos] = r.proj_points
    for pos, g in df.groupby("position"):
        repl.setdefault(pos, g["proj_points"].min())
    return repl


def predict_year(target):
    train = pd.concat([build_features(y) for y in range(FIRST_FEATURE_YEAR, target)])
    # defaults: a backtest sweep found no config meaningfully better
    m = HistGradientBoostingRegressor(random_state=0)
    m.fit(train[FEATURES], train["label"],
          sample_weight=train["weight"] * (1 + train["label"] / ALPHA))
    # second model: expected games played, i.e. will he actually have a role?
    # Gates backups stuck behind entrenched starters without re-pricing injury
    # risk for full-time roles (factor is 1 at >= FULL_ROLE_GAMES).
    gm = HistGradientBoostingRegressor(random_state=0)
    gm.fit(train[FEATURES], train["label_games"])
    te = build_features(target).set_index("playerId").copy()
    # sqrt softens the gate: backtest sweep found it keeps most of the ungated
    # rank correlation while retaining nearly all of the yield gain
    role = ((pd.Series(gm.predict(te[FEATURES]), index=te.index)
             / FULL_ROLE_GAMES).clip(0, 1)) ** 0.5
    ml = pd.Series(m.predict(te[FEATURES]), index=te.index).clip(lower=0) * GAMES
    # blend last season's per-game rate (FCS-sourced rates excluded)
    pts = season_points(target - 1).groupby("playerId")["points"].sum()
    gp = games_played(target - 1).reindex(pts.index)
    last_rate = (pts * ((12 + RATE_SHRINK) / 12) / (gp + RATE_SHRINK)).dropna() * GAMES
    lr = last_rate.reindex(te.index)
    lr = lr.where(te["from_fcs"] == 0)  # raw FCS rates don't translate; ML only
    te["role"] = role.round(2)
    # human depth-chart knowledge beats preseason data: overrides.csv
    # (name,role) replaces the predicted role factor, e.g. "Deuce Knight,0.1"
    # for a confirmed backup or "Some Riser,1" for a camp-battle winner
    try:
        ov = pd.read_csv("overrides.csv")
        te["role"] = te["name"].map(dict(zip(ov["name"], ov["role"]))).fillna(te["role"])
    except FileNotFoundError:
        pass
    te["proj_points"] = ((BLEND * lr + (1 - BLEND) * ml).where(lr.notna(), ml)
                         * te["role"]).round(1)
    te = te.reset_index().sort_values("proj_points", ascending=False)
    repl = replacement_points(te)
    te["draft_value"] = (te["proj_points"] - te["position"].map(repl)).round(1)
    te = te.sort_values("draft_value", ascending=False)
    te["rank"] = range(1, len(te) + 1)
    te["pos_rank"] = (te["position"]
                      + te.groupby("position")["proj_points"]
                          .rank(ascending=False, method="first").astype(int).astype(str))
    return te[["rank", "pos_rank", "playerId", "name", "position", "team",
               "role", "proj_points", "draft_value"]]


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    out = predict_year(year)
    out.to_csv(f"projections_{year}.csv", index=False)
    print(out.head(30).to_string(index=False))
    repl = replacement_points(out)
    print("\nreplacement:", {p: round(repl[p], 1) for p in POSITIONS})
    print(f"v{VERSION}  {len(out)} players -> projections_{year}.csv")
