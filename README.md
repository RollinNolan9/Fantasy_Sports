# Fantasy_Sports

Season-long fantasy football projections for college football, built on the
[CollegeFootballData API](https://collegefootballdata.com/).

## Setup

```bash
pip install -r requirements.txt
echo "CFBD_API_KEY=<your key>" > .env   # free key from collegefootballdata.com
```

## Usage

```bash
python3 fetch.py               # download 2019-2026 stats + rosters to data/ (cached)
python3 projections.py 2026    # -> projections_2026.csv, ranked by projected points
python3 backtest.py            # score the model vs actuals for 2022-2025
```

Scoring is 0.5 PPR with 4-point passing TDs; edit `SCORING` in `projections.py`
to match your league.

## Model

Projected points = 12 games x a blend of the player's fantasy points per
team-game over the last 3 seasons (weighted 0.6/0.3/0.1, most recent first),
regressed 25% toward the positional mean. Only players on the target year's
FBS roster are projected, so graduations/NFL departures drop out and transfers
land on their new team.

## Backtest (2022-2025, top players per position by actual points)

| metric | model | naive "repeat last year" |
|---|---|---|
| Spearman rank corr | 0.159 | 0.143 |
| MAE (points) | 113.0 | 107.0 |

Pure production history is a weak signal in college football -- roster churn
means breakouts dominate. Known gaps, in rough order of expected value: depth
chart / returning-starter signals, freshman & recruit projections, team pace
and strength-of-schedule adjustments. Any addition must beat these numbers in
`backtest.py` to ship.
