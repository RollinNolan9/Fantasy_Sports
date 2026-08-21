"""Expected stats for players (or stats) DraftKings didn't post.

Monte Carlo the previous two regular seasons (2024, 2025): draw games-played
and per-game rates from those years, take the mean of the draws. That mean is
the 'line' we would have posted. DK numbers always win when present.

Companion stats (TDs, receptions, attempts) are then scaled to any DK yardage
so a 1200-yard rushing line doesn't sit on last year's TD count if workload moved.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from nfl_fetch import name_key
from nfl_scoring import STAT_COLS, skill_points

HIST_YEARS = (2024, 2025)
W_RECENT = 0.65
W_PRIOR = 0.35
N_SIMS = 2000
SEED = 1
URL = ("https://github.com/nflverse/nflverse-data/releases/download/"
       "stats_player/stats_player_reg_{year}.csv")
STAT_MAP = {
    "attempts": "pass_att",
    "completions": "pass_cmp",
    "passing_yards": "pass_yds",
    "passing_tds": "pass_td",
    "passing_interceptions": "interceptions",
    "carries": "rush_att",
    "rushing_yards": "rush_yds",
    "rushing_tds": "rush_td",
    "receptions": "receptions",
    "receiving_yards": "rec_yds",
    "receiving_tds": "rec_td",
}
FILL_COLS = list(STAT_COLS) + ["pass_att", "pass_cmp", "rush_att"]
VOLUME = {
    "rush_yds": ("rush_td", "rush_att"),
    "rec_yds": ("rec_td", "receptions"),
    "pass_yds": ("pass_td", "interceptions", "pass_att", "pass_cmp"),
}


def _read_year(year, cache_dir):
    cache = Path(cache_dir) / f"hist_{year}.csv"
    if cache.exists() and cache.stat().st_size > 1000:
        return pd.read_csv(cache)
    r = requests.get(URL.format(year=year), timeout=60)
    r.raise_for_status()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(r.content)
    return pd.read_csv(cache)


def load_hist(cache_dir="nfl"):
    frames = []
    for y in HIST_YEARS:
        df = _read_year(y, cache_dir)
        df["position"] = df["position"].replace({"FB": "RB"})
        df = df[df["position"].isin(["QB", "RB", "WR", "TE"])].copy()
        out = pd.DataFrame({
            "name": df["player_display_name"],
            "key": df["player_display_name"].map(name_key),
            "position": df["position"],
            "team": df["recent_team"],
            "season": df["season"],
            "games": pd.to_numeric(df["games"], errors="coerce").fillna(0),
        })
        for src, dst in STAT_MAP.items():
            out[dst] = pd.to_numeric(df[src], errors="coerce").fillna(0)
        out["fumbles"] = (
            pd.to_numeric(df.get("rushing_fumbles_lost"), errors="coerce").fillna(0)
            + pd.to_numeric(df.get("receiving_fumbles_lost"), errors="coerce").fillna(0)
            + pd.to_numeric(df.get("sack_fumbles_lost"), errors="coerce").fillna(0)
        )
        frames.append(out)
    return pd.concat(frames, ignore_index=True)


def _yoy_cv(hist, col):
    a = hist[hist.season == HIST_YEARS[0]].set_index("key")
    b = hist[hist.season == HIST_YEARS[1]].set_index("key")
    both = a.index.intersection(b.index)
    if len(both) < 20:
        return 0.25
    r1 = a.loc[both, col] / a.loc[both, "games"].clip(lower=1)
    r2 = b.loc[both, col] / b.loc[both, "games"].clip(lower=1)
    mu = ((r1 + r2) / 2).replace(0, np.nan)
    cv = ((r2 - r1).abs() / mu).replace([np.inf, -np.inf], np.nan).median()
    return float(cv) if pd.notna(cv) else 0.25


def expected_from_hist(hist, n_sims=N_SIMS, seed=SEED):
    """One row per player: MC-expected season stats from the last two years."""
    rng = np.random.default_rng(seed)
    cvs = {c: _yoy_cv(hist, c) for c in FILL_COLS}
    rows = []
    for key, g in hist.groupby("key"):
        g = g.sort_values("season")
        years = {int(r.season): r for r in g.itertuples()}
        y4, y5 = years.get(HIST_YEARS[0]), years.get(HIST_YEARS[1])
        last = y5 or y4
        rec = {"key": key, "name": last.name, "position": last.position, "team": last.team}
        # itertuples uses .name for the pandas name field? NO - .name is the Index.
        rec["name"] = last.player_display_name if hasattr(last, "player_display_name") else None
        rec["name"] = g.iloc[-1]["name"]
        rec["position"] = g.iloc[-1]["position"]
        rec["team"] = g.iloc[-1]["team"]
        for col in FILL_COLS:
            rates, gps, ws = [], [], []
            for row, w in ((y4, W_PRIOR), (y5, W_RECENT)):
                if row is None or row.games <= 0:
                    continue
                rates.append(getattr(row, col) / max(row.games, 1))
                gps.append(row.games)
                ws.append(w)
            if not rates:
                rec[col] = 0.0
                continue
            w = np.asarray(ws, dtype=float)
            w = w / w.sum()
            mu_rate = float(np.dot(w, rates))
            mu_gp = float(np.dot(w, gps))
            sig_rate = max(cvs[col] * abs(mu_rate), np.std(rates) if len(rates) > 1 else 0.0, 1e-6)
            sig_gp = max(1.5, float(np.std(gps)) if len(gps) > 1 else 2.0)
            gp = rng.normal(mu_gp, sig_gp, n_sims).clip(0, 17)
            rate = rng.normal(mu_rate, sig_rate, n_sims).clip(0)
            rec[col] = round(float((gp * rate).mean()), 2)
        rows.append(rec)
    return pd.DataFrame(rows)


def fill_from_hist(dk_wide, hist_exp):
    """DK values stay. Missing stats/players come from the 2-year MC."""
    dk = dk_wide.copy()
    dk["key"] = dk["name"].map(name_key)
    hx = hist_exp.copy()
    if "key" not in hx.columns:
        hx["key"] = hx["name"].map(name_key)

    hx_pts = hx.apply(skill_points, axis=1)
    extra = hx.loc[hx_pts >= 40].copy()
    extra = extra[~extra["key"].isin(set(dk["key"]))]
    extra["line_source"] = "hist"
    extra["n_dk"] = 0
    all_p = pd.concat([dk, extra], ignore_index=True, sort=False)
    all_p["n_dk"] = all_p["n_dk"].fillna(0)

    hlook = hx.drop_duplicates("key").set_index("key")
    for c in FILL_COLS:
        if c not in all_p.columns:
            all_p[c] = np.nan
        if c not in hlook.columns:
            continue
        miss = all_p[c].isna() & all_p["key"].isin(hlook.index)
        all_p.loc[miss, c] = all_p.loc[miss, "key"].map(hlook[c])

    all_p.loc[all_p["n_dk"].gt(0), "line_source"] = "dk+hist"

    dk_posted = {c: set(dk.loc[dk[c].notna(), "key"]) for c in FILL_COLS if c in dk.columns}
    for yds, comps in VOLUME.items():
        if yds not in all_p.columns or yds not in hlook.columns:
            continue
        hist_yds = all_p["key"].map(hlook[yds]).replace(0, np.nan)
        scale = (all_p[yds] / hist_yds).clip(0.4, 2.5)
        dk_has_yds = all_p["key"].isin(dk_posted.get(yds, set()))
        for c in comps:
            if c not in all_p.columns:
                continue
            adj = dk_has_yds & ~all_p["key"].isin(dk_posted.get(c, set()))
            adj = adj & all_p[c].notna() & scale.notna()
            all_p.loc[adj, c] = (all_p.loc[adj, c] * scale[adj]).round(2)

    return all_p.drop(columns=["key"], errors="ignore")
