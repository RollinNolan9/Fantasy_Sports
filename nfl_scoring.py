"""ESPN standard PPR scoring (10-team default)."""

PASS_YD = 0.04       # 1 pt / 25 yards
PASS_TD = 4.0
INT = -2.0
RUSH_YD = 0.1        # 1 pt / 10 yards
RUSH_TD = 6.0
REC = 1.0            # full PPR
REC_YD = 0.1
REC_TD = 6.0
FUM_LOST = -2.0

SKILL = ("QB", "RB", "WR", "TE")
STAT_COLS = (
    "pass_yds", "pass_td", "interceptions",
    "rush_yds", "rush_td",
    "receptions", "rec_yds", "rec_td",
    "fumbles",
)

# Typical yards/catch when a book lists yards but not receptions.
YPR = {"WR": 12.8, "TE": 11.2, "RB": 8.0, "QB": 10.0}


def _f(row, col):
    v = row[col] if hasattr(row, "__getitem__") else getattr(row, col, 0)
    try:
        if v is None or v == "":
            return 0.0
        x = float(v)
        return 0.0 if x != x else x  # NaN
    except (TypeError, ValueError):
        return 0.0


def skill_points(row):
    """Season ESPN PPR points from counting stats (scalar row)."""
    return (
        _f(row, "pass_yds") * PASS_YD
        + _f(row, "pass_td") * PASS_TD
        + _f(row, "interceptions") * INT
        + _f(row, "rush_yds") * RUSH_YD
        + _f(row, "rush_td") * RUSH_TD
        + _f(row, "receptions") * REC
        + _f(row, "rec_yds") * REC_YD
        + _f(row, "rec_td") * REC_TD
        + _f(row, "fumbles") * FUM_LOST
    )


def skill_points_vec(stats):
    """Vectorized ESPN PPR points. `stats` maps column -> array."""
    import numpy as np

    def z(c):
        return np.asarray(stats.get(c, 0.0), dtype=float)

    return (
        z("pass_yds") * PASS_YD
        + z("pass_td") * PASS_TD
        + z("interceptions") * INT
        + z("rush_yds") * RUSH_YD
        + z("rush_td") * RUSH_TD
        + z("receptions") * REC
        + z("rec_yds") * REC_YD
        + z("rec_td") * REC_TD
        + z("fumbles") * FUM_LOST
    )


def complete_stats(df):
    """Fill missing counting stats on a player table. Returns a copy."""
    import pandas as pd

    out = df.copy()
    extra = ("pass_att", "pass_cmp", "rush_att")
    for c in STAT_COLS + extra:
        if c not in out.columns:
            out[c] = float("nan")
        out[c] = pd.to_numeric(out[c], errors="coerce")

    ypr = out["position"].map(YPR).fillna(12.0)
    miss_rec = out["receptions"].isna() & out["rec_yds"].gt(0)
    out.loc[miss_rec, "receptions"] = (out.loc[miss_rec, "rec_yds"] / ypr[miss_rec]).round(1)
    miss_yds = out["rec_yds"].isna() & out["receptions"].gt(0)
    out.loc[miss_yds, "rec_yds"] = (out.loc[miss_yds, "receptions"] * ypr[miss_yds]).round(1)

    qb = out["position"].eq("QB")
    miss_att = qb & out["pass_att"].isna() & out["pass_yds"].gt(0)
    out.loc[miss_att, "pass_att"] = (out.loc[miss_att, "pass_yds"] / 7.3).round(0)
    miss_int = qb & out["interceptions"].isna() & out["pass_att"].gt(0)
    out.loc[miss_int, "interceptions"] = (out.loc[miss_int, "pass_att"] * 0.023).round(1)

    miss_fum = out["fumbles"].isna()
    out.loc[miss_fum & qb, "fumbles"] = 2.5
    out.loc[miss_fum & out["position"].eq("RB"), "fumbles"] = 1.2
    out.loc[miss_fum & out["position"].isin(["WR", "TE"]), "fumbles"] = 0.8

    out[list(STAT_COLS) + list(extra)] = out[list(STAT_COLS) + list(extra)].fillna(0.0)
    return out
