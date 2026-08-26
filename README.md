# Fantasy_Sports v2

Season-long college football projections for a 14-team Fantrax league:
2QB / 2RB / 2WR / 2 FLEX (RB/WR/TE) / 1 K / 1 D/ST. 0.5 PPR, 4-pt pass TD.
No required TE. Redraft.

Scoring lives in `projections.py` `SCORING`. Explicit defaults (not guesses):
no yardage/big-play bonuses, no 2-pt/return TD (those stats are not in the
CFBD extract), 12 regular-season weeks, 0 playoff weeks. K and D/ST are
rostered but not projected.

```bash
pip install -r requirements.txt
echo "CFBD_API_KEY=<key>" > .env
python3 fetch.py            # cached after the first run
python3 model.py 2026       # -> projections_2026.csv (ML + role gate)
python3 valuation.py        # -> projections_2026_tuned.csv (draft ranks)
python3 test_valuation.py
python3 backtest.py         # 2023-2025, needs data/; don't ship a change that loses here
```

`overrides.csv` (name,role,games) and `depth_chart.csv` (football-role facts,
no ranks) are the knobs. Empty games leaves the 12-game health-conditional
proj. `valuation.py` turns that board into this league's ranks: lineup-optimizer
VORP (28 QB + 84 RB/WR/TE with min 28 RB / 28 WR), WR29 for mandatory WR
starters (not FLEX), managed waiver replacement on missed games (default RB100),
and QB 28/35/42 roster sensitivity. Default draft rank uses 42 rostered QBs
(`expected_qbs_rostered_per_team = 3`).

## What v2 is

Gradient boosting on post-COVID regular-season data, health-conditional
(points per game played x 12), gated by predicted role, ranked by points
above replacement. Last season is an input feature; it is not mixed in again
after the model (a 0–100% stickiness sweep lost to 0% on MAE and yield).
New college playcallers inherit their previous stop's pace/pass rate; SP+
stays with the current roster. RB rooms: the #2 is capped at 70% of the
lead so a committee doesn't mint two first-round backs. QBs are not a
committee — a named starter owns the job and the rest of the room is a
backup. (Small backtest tax vs uncapped RB rooms: yield 106.6 vs 107.6.)

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
strength of schedule, team-play budgets, walk-forward valuation backtest.


## What v2 is

Gradient boosting on post-COVID regular-season data, health-conditional
(points per game played x 12), gated by predicted role, ranked by points
above replacement. Last season is an input feature; it is not mixed in again
after the model (a 0–100% stickiness sweep lost to 0% on MAE and yield).
New college playcallers inherit their previous stop's pace/pass rate; SP+
stays with the current roster. RB rooms: the #2 is capped at 70% of the
lead so a committee doesn't mint two first-round backs. QBs are not a
committee — a named starter owns the job and the rest of the room is a
backup. (Small backtest tax vs uncapped RB rooms: yield 106.6 vs 107.6.)

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
