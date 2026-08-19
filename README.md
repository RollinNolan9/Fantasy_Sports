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
above replacement. Last-year rate is blended at 25% except FCS-sourced
seasons. New college playcallers inherit their previous stop's pace/pass
rate; SP+ stays with the current roster.

## Backtest (2023-2025)

| metric | naive | heuristic | v2 |
|---|---|---|---|
| Spearman | 0.200 | 0.209 | 0.209 |
| MAE | 91.7 | 110.1 | **72.8** |
| Yield (own top picks) | 82.9 | 100.0 | **104.0** |

Yield is the draft metric. Rank correlation did not beat naive; MAE and
yield did. Playcaller mapping is 2026-only and is not in this table.

Rejected: momentum, HC-as-scheme, pre-COVID training, shrinking mop-up
rates (the role gate handles that). Not in v2: K, D/ST, full OC history,
strength of schedule.
