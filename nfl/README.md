# NFL sportsbook draft board

10-team ESPN PPR. Rank players the way a sharp book would, then convert that
into draft value for *this* league.

```bash
pip install -r requirements.txt
python3 test_nfl.py          # scoring / juice / VORP / sim
python3 nfl.py               # -> nfl_rankings_2026.csv
python3 nfl.py --fetch-dk    # live DraftKings (works on a home IP; blocked here)
```

## Why this, not analyst rankings

Last year a sportsbook-based board got you to the championship. Books are
the market: real money on both sides of every passing-yard, rushing-yard,
reception, and TD total. We take those season-long lines as expected stats,
score them as ESPN PPR, and rank by **points above replacement** in a
10-team league (1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, 1 K, 1 DST).

Raw fantasy points overrate quarterbacks in 1QB. VORP is the entire edge
in a 10-team draft. Josh Allen can be QB1 and still go in the late 2nd.

## Pipeline

1. **Lines** — your DraftKings offering workbook (`nfl/dk_offering.csv`)
   is the source of truth. Balanced O/Us are de-vigged (`nfl_lines.py`)
   so a -120 / +100 over sits a bit above the printed number. Milestones
   and IDP sacks are ignored. Duplicate names, error rows (`10+` tickets),
   or anyone DK never posted who *is* on the previous Vegas snapshot
   (`nfl/vegas_2026.csv`) use that book line. Hist does not overwrite a book.
2. **Everyone else** — players (and missing stats) with no DK ticket are
   filled by a 2k-draw Monte Carlo of 2024+2025 regular-season rates
   (`nfl_hist.py`). 2025 is weighted 65%. Companion TDs/receptions are
   scaled to any DK yardage so Gibbs's 1199.5 rush line is not sitting on
   last year's TD count. Hist-only names with no 2026 team are dropped.
   `line_source` is `dk+hist`, `vegas`, or `hist`.
3. **Score** — ESPN PPR: 0.04 pass yd, 4 pass TD, -2 INT, 0.1 rush/rec yd,
   6 rush/rec TD, 1 PPR, -2 fumble lost.
4. **Sim** — 4,000 seasons around those means with a shared team-offense
   shock plus player residual. Rank on the market mean; the sim only
   produces **floor (10th) / ceiling (90th)** so you can take upside in
   the double-digit rounds.
5. **VORP** — replacement is the first player at each position who does
   not start (dedicated slots, then FLEX). TEs are then floored against a
   FLEX RB/WR so TE11 being terrible does not stuff nine TEs in the top 70.
   ESPN ADP is a sidecar column only (`adp` / `adp_gap`).

## How to actually draft with it

- Sort the CSV by `rank` (already VORP). Ignore raw `proj_points` for pick
  order.
- In a 10-team PPR, the board will push RB/WR in the first four rounds and
  let QB slide unless a dual-threat is being drafted behind his VORP.
- `adp` is the room, not the model. Ignore it for pick order.
- `ceil - floor` is volatility. Prefer high ceiling after pick 80.
- K and DST are streamed. The board ranks them; do not spend a pick before
  the last two rounds.
- Injuries after the snapshot: edit the DK workbook or drop the row and rerun.

## What this is not

- Not a week-by-week lineup tool. Season totals are the draft object.
- Not a play-by-play NFL simulator. Game-level sim would need a play-calling
  model and would mostly rediscover the same season totals the books already
  posted.
- Not a 12-team / superflex board. Change `TEAMS` / `SLOTS` / `FLEX` in
  `nfl.py` if the league isn't 10-team 1QB PPR.
