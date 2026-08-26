"""Season-long Monte Carlo around market-implied stat means.

Season-long betting lines already price expected missed games, so this does
not apply a second injury haircut. Each sim draws team-level offensive
environment plus idiosyncratic residual, then scores ESPN PPR.

Returns mean / 10th / 90th season points. Seed is fixed so the board is stable.
"""
import numpy as np
import pandas as pd

from nfl_scoring import STAT_COLS, skill_points, skill_points_vec

N_SIMS = 4000
SEED = 0
TEAM_SHOCK = 0.08   # ~8% shared offense variance
IDIO_YDS = 0.16     # remaining player variance in yards
IDIO_COUNT = 0.18


def _sigma(col, mean):
    m = np.maximum(mean, 0.0)
    if col.endswith("_yds"):
        return np.maximum(80.0, IDIO_YDS * m)
    if col == "receptions":
        return np.maximum(6.0, IDIO_COUNT * m)
    if col.endswith("_td") or col in ("interceptions", "fumbles"):
        return np.maximum(1.2, np.sqrt(m) * 1.15)
    return np.maximum(1.0, 0.20 * m)


def simulate(df, n_sims=N_SIMS, seed=SEED):
    """Add proj_points, floor, ceil. K/DST keep source_points (no stat lines)."""
    out = df.copy()
    rng = np.random.default_rng(seed)
    n = len(out)
    skill = out["position"].isin(["QB", "RB", "WR", "TE"]).to_numpy()
    means = {c: pd.to_numeric(out.get(c, 0), errors="coerce").fillna(0).to_numpy()
             for c in STAT_COLS}

    teams = out["team"].fillna("").astype(str).to_numpy() if "team" in out.columns else np.array([""] * n)
    uniq = {t: i for i, t in enumerate(sorted(set(teams)))}
    team_id = np.array([uniq[t] for t in teams], dtype=int)
    n_teams = max(len(uniq), 1)

    totals = np.zeros((n, n_sims), dtype=float)
    for i in range(n_sims):
        shock = rng.normal(1.0, TEAM_SHOCK, size=n_teams).clip(0.75, 1.25)
        mult = shock[team_id]
        row = {}
        for c, mu in means.items():
            draw = rng.normal(mu, _sigma(c, mu))
            if c in ("pass_yds", "pass_td", "rush_yds", "rush_td",
                     "receptions", "rec_yds", "rec_td"):
                draw = draw * mult
            row[c] = np.clip(draw, 0, None)
        totals[:, i] = skill_points_vec(row)

    # Rank on the market mean (closed-form ESPN conversion). Recenter the
    # sim so floor/ceiling are a distribution around that number, not a
    # second noisy estimate of it.
    det = np.zeros(n)
    if skill.any():
        det[skill] = out.loc[skill, list(STAT_COLS)].apply(skill_points, axis=1).to_numpy()
    totals = totals - totals.mean(1, keepdims=True) + det[:, None]
    totals = np.clip(totals, 0, None)
    out["proj_points"] = np.round(det, 1)
    out["floor"] = np.round(np.quantile(totals, 0.10, axis=1), 1)
    out["ceil"] = np.round(np.quantile(totals, 0.90, axis=1), 1)

    # K / DST: books rarely post counting stats. Trust the snapshot points.
    kdst = ~skill
    if "source_points" in out.columns:
        src = pd.to_numeric(out["source_points"], errors="coerce")
        out.loc[kdst, "proj_points"] = src[kdst].fillna(0).round(1)
        out.loc[kdst, "floor"] = (src[kdst].fillna(0) * 0.80).round(1)
        out.loc[kdst, "ceil"] = (src[kdst].fillna(0) * 1.20).round(1)
    return out
