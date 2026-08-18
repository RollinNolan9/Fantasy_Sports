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

Gradient boosting (`model.py`) trained on post-COVID player-seasons (2021+,
the portal/NIL era), predicting fantasy points per game PLAYED (x12) for
everyone on the target year's FBS roster -- including true freshmen and
transfers. Projections are health-conditional: they assume the player is on
the field, since injuries and opt-outs can't be predicted preseason. Games
played are derived from per-week box scores; training rows are weighted by
games played so 2-game rates count as weak evidence. Features
(`features.py`), all knowable preseason:

- production history: fantasy pts/team-game in each of the last 3 seasons,
  plus last season's games played and pts per game played
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

## Backtest (2023-2025, top players per position)

Target = actual fantasy pts per game played x 12 (>=4 games), matching the
health-conditional projections. Players a model can't see (e.g. freshmen for
the heuristic) count as projections of 0, so covering breakouts is rewarded.

| metric | naive "repeat last year's rate" | heuristic | ML model |
|---|---|---|---|
| Spearman rank corr | 0.226 | 0.216 | **0.227** |
| MAE (points) | 95.1 | 127.1 | **85.4** |

Permutation importance says last-year production dominates (as it should),
with real contributions from transfer status, vacated share, class year, and
recruit rating. Tried and rejected via backtest: momentum extrapolation,
coach-aware team context (HC profiles replacing team history), pre-COVID
training data. Known gaps: coordinator (OC) histories would need scraping an
external source; strength of schedule. Any addition must beat these numbers
in `backtest.py` to ship.
