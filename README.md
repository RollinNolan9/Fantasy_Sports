# Fantasy_Sports v2

Season-long college football projections for an 18-team Fantrax league:
1QB / 2RB / 2WR / 3 FLEX (RB/WR). Not superflex. TEs, K, D/ST not started.

Scoring: 0.5 PPR, 4-pt pass TD (`SCORING` in `projections.py`).

```bash
pip install -r requirements.txt
echo "CFBD_API_KEY=<key>" > .env
python3 fetch.py            # cached after the first run
python3 model.py 2026       # -> projections_2026.csv
python3 backtest.py         # 2023-2025, don't ship a change that loses here
```

`overrides.csv` (name,role) and `playcallers.csv` (year,team,source_team)
are the two knobs. Everything else is frozen.

## What v2 is

Gradient boosting on post-COVID regular-season data, health-conditional
(points per game played x 12), gated by predicted role, ranked by points
above replacement. Last season is an input feature; it is not mixed in again
after the model (a 0–100% stickiness sweep lost to 0% on MAE and yield).
New college playcallers inherit their previous stop's pace/pass rate; SP+
stays with the current roster. RB/QB rooms: the #2 is capped at 70% of the
lead so a committee doesn't mint two first-round backs. (Small backtest
tax vs uncapped: yield 106.6 vs 107.6.)

## Backtest (2023-2025)

| metric | naive | heuristic | v2 |
|---|---|---|---|
| Spearman | 0.200 | 0.209 | 0.202 |
| MAE | 91.7 | 110.1 | **71.1** |
| Yield (own top picks) | 82.9 | 100.0 | **106.6** |

Yield is the draft metric. Rank correlation did not beat naive; MAE and
yield did. Playcaller mapping is 2026-only and is not in this table.
Last-year rate is a model *feature*, not a post-hoc blend: sweeping 0–100%
stickiness on last season's raw rate, 0% won MAE (69.7) and yield (107.6).

Rejected: momentum, HC-as-scheme, pre-COVID training, shrinking mop-up
rates (the role gate handles that). Not in v2: K, D/ST, full OC history,
strength of schedule.
