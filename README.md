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
python3 fetch.py               # download 2014-2026 stats, rosters, recruits,
                               # SP+ ratings, coach history to data/ (cached)
python3 model.py 2026          # -> projections_2026.csv, ranked by projected points
python3 backtest.py            # score all models vs actuals for 2023-2025
python3 projections.py 2026    # simple heuristic baseline, for comparison
```

Scoring is 0.5 PPR with 4-point passing TDs; edit `SCORING` in `projections.py`
to match your league.

## Model

Gradient boosting (`model.py`) trained on every player-season since 2017,
predicting fantasy points per team-game for everyone on the target year's FBS
roster -- including true freshmen and transfers. Features (`features.py`), all
knowable preseason:

- production history: fantasy pts/team-game in each of the last 3 seasons
- role opportunity: share of the team's position-group production that
  departed (roster diff), the player's returning depth rank, prior usage share
- progression: class year, 247-composite recruit rating/stars
- transfers: placed on their new team, with an SP+ offense quality delta
  between old and new school; coach-follow transfers (new team's new HC is
  the player's old HC) are flagged and exempt from that delta, since the
  new team's last-season offense rating isn't the offense they're joining
- coaching: HC change flag + how the new HC's historical pace/pass-rate
  profile differs from the team's (HC only -- CFBD has no coordinator data)
- team context: pace, pass rate, SP+ offensive rating

`projections.py` keeps the simple heuristic (3-yr weighted average regressed
to positional mean) as a baseline.

## Backtest (2023-2025, top players per position by actual points)

Players a model can't see (e.g. freshmen for the heuristic) count as
projections of 0, so covering breakouts is rewarded.

| metric | naive "repeat last year" | heuristic | ML model |
|---|---|---|---|
| Spearman rank corr | 0.183 | 0.196 | **0.214** |
| MAE (points) | 106.3 | 114.9 | **105.0** |

Permutation importance says last-year production dominates (as it should),
with real contributions from transfer status, vacated share, class year, and
recruit rating. The HC play-calling features contribute ~nothing at the
player level. Known gaps: coordinator (OC) histories would need scraping an
external source; per-player games played (injury detection) isn't in the CFBD
season endpoint; strength of schedule. Any addition must beat these numbers
in `backtest.py` to ship.
