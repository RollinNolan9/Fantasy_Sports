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

1. **Lines** — `nfl/vegas_2026.csv` is a 2026 season-long snapshot built
   from DraftKings-style player props (yards, TDs, receptions, INTs). Live
   DK is `--fetch-dk` when their sportsbook is reachable. Juice is removed
   (`nfl_lines.py`) so a -120 / +100 over sits a bit above the printed number.
2. **Missing stats** — if a book lists receiving yards but not receptions,
   fill recs from position yards-per-catch. QBs without an INT total get
   ~2.3% of pass attempts. Season-long lines already price missed games;
   we do not haircut them again.
3. **Score** — ESPN PPR: 0.04 pass yd, 4 pass TD, -2 INT, 0.1 rush/rec yd,
   6 rush/rec TD, 1 PPR, -2 fumble lost.
4. **Sim** — 4,000 seasons around those means with a shared team-offense
   shock plus player residual. Rank on the market mean; the sim only
   produces **floor (10th) / ceiling (90th)** so you can take upside in
   the double-digit rounds.
5. **VORP + ADP** — replacement is the first player at each position who
   does not start (dedicated slots, then FLEX). ESPN PPR ADP is joined for
   **adp_gap**: positive means we rank them earlier than the room, i.e. a
   steal if the board is right.

## How to actually draft with it

- Sort the CSV by `rank` (already VORP). Ignore raw `proj_points` for pick
  order.
- In a 10-team PPR, the board will push RB/WR in the first four rounds and
  let QB slide unless a dual-threat is being drafted behind his VORP.
- `adp_gap >= 12` inside the top 140 is the steal list printed at the end
  of `nfl.py`. Those are the names to sit on.
- `ceil - floor` is volatility. Prefer high ceiling after pick 80.
- K and DST are streamed. The board ranks them; do not spend a pick before
  the last two rounds.
- Injuries after the snapshot: delete or zero the row in
  `nfl/vegas_2026.csv` and rerun. Do not hand-edit projections.

## Refreshing lines

DraftKings' public sportsbook API is IP-blocked from this cloud machine
(Akamai 403). On your laptop:

```bash
python3 nfl.py --fetch-dk --lines nfl/dk_lines.csv
```

If that still 403s, paste season O/Us into `nfl/vegas_2026.csv` (same
columns) and rerun. The ranking math does not care which book the numbers
came from as long as they are season-long, two-way markets.

## What this is not

- Not a week-by-week lineup tool. Season totals are the draft object.
- Not a play-by-play NFL simulator. Game-level sim would need a play-calling
  model and would mostly rediscover the same season totals the books already
  posted.
- Not a 12-team / superflex board. Change `TEAMS` / `SLOTS` / `FLEX` in
  `nfl.py` if the league isn't 10-team 1QB PPR.
