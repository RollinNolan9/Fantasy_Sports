"""10-team ESPN PPR draft board from sportsbook season-long lines + Monte Carlo.

python3 nfl.py                 # -> nfl_rankings_2026.csv
python3 nfl.py --fetch-dk      # try live DraftKings (often blocked off-home IPs)
python3 nfl.py --lines PATH    # use a different lines CSV
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

from nfl_fetch import attach_espn, fetch_draftkings, fetch_espn, name_key
from nfl_scoring import SKILL, complete_stats, skill_points
from nfl_sim import simulate

TEAMS = 10
SLOTS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "K": 1, "DST": 1}
FLEX = 1
FLEX_ELIGIBLE = {"RB", "WR", "TE"}
DEFAULT_LINES = Path("nfl/dk_offering.csv")
OUT = Path("nfl_rankings_2026.csv")


def replacement_points(df):
    leftover = {p: n * TEAMS for p, n in SLOTS.items()}
    flex_left = FLEX * TEAMS
    repl = {}
    for r in df.sort_values("proj_points", ascending=False).itertuples():
        pos = r.position
        if leftover.get(pos, 0) > 0:
            leftover[pos] -= 1
        elif pos in FLEX_ELIGIBLE and flex_left > 0:
            flex_left -= 1
        elif pos not in repl:
            repl[pos] = r.proj_points
    for pos, g in df.groupby("position"):
        repl.setdefault(pos, g["proj_points"].min())
    return repl


def load_lines(path):
    peek = pd.read_csv(path, nrows=1)
    if "Market" in peek.columns and "Player" in peek.columns:
        from nfl_dk import overlay_vegas, parse_offering
        from nfl_hist import expected_from_hist, fill_from_hist, load_hist
        _, wide, dirty = parse_offering(path)
        wide = overlay_vegas(wide, dirty)
        n_vegas = int((wide.get("line_source", "") == "vegas").sum())
        hist = load_hist()
        filled = fill_from_hist(wide, expected_from_hist(hist))
        n_dk = int((filled.get("n_dk", 0) > 0).sum())
        n_hist = int((filled.get("line_source", "") == "hist").sum())
        print(f"DK: {n_dk} clean markets; Vegas fallback: {n_vegas} "
              f"(dup/error); hist MC: {n_hist} others")
        df = filled
    else:
        df = pd.read_csv(path)
    df["position"] = df["position"].replace({"DEF": "DST", "D/ST": "DST", "FB": "RB"})
    df = complete_stats(df)
    skill = df["position"].isin(SKILL)
    df.loc[skill, "_det"] = df.loc[skill].apply(skill_points, axis=1)
    return df


def drop_unsigned_hist(board, espn=None):
    """Hist-only names need a 2026 ESPN team. Unsigned/retired stay off the board."""
    hist = board["line_source"].fillna("").eq("hist")
    if not hist.any():
        return board
    if espn is None or getattr(espn, "empty", True):
        keep = ~hist | board["team"].fillna("").astype(str).str.strip().ne("")
        return board.loc[keep].copy()
    e = espn[espn["position"].isin(list(SKILL))].copy()
    rostered = {
        name_key(n)
        for n, t in zip(e["name"], e["team"].fillna(""))
        if str(t).strip()
    }
    keys = board["name"].map(name_key)
    return board.loc[~hist | keys.isin(rostered)].copy()


def pick_replacement(repl):
    """TE11 is a wasteland, so mediocre TEs look like top-40 picks vs that.

    In 10-team 1TE they actually compete with a FLEX RB/WR. Floor TE
    replacement there so only McBride/Bowers-level TEs stay early.
    """
    out = dict(repl)
    rb, wr = out.get("RB"), out.get("WR")
    if "TE" in out and rb is not None and wr is not None:
        out["TE"] = max(out["TE"], min(rb, wr))
    return out


def rank(df):
    df = df.sort_values("proj_points", ascending=False)
    repl = replacement_points(df)
    pick = pick_replacement(repl)
    df["draft_value"] = (df["proj_points"] - df["position"].map(pick)).round(1)
    skill = df["position"].isin(SKILL)
    df = pd.concat([
        df.loc[skill].sort_values(["draft_value", "proj_points"], ascending=False),
        df.loc[~skill].sort_values(["draft_value", "proj_points"], ascending=False),
    ])
    df["rank"] = range(1, len(df) + 1)
    df["pos_rank"] = (
        df["position"]
        + df.groupby("position")["proj_points"]
            .rank(ascending=False, method="first").astype(int).astype(str)
    )
    if "adp" in df.columns:
        df["adp_gap"] = (pd.to_numeric(df["adp"], errors="coerce") - df["rank"]).round(1)
    return df, pick


def run(lines_path=DEFAULT_LINES, n_sims=4000, use_espn=True):
    board = load_lines(lines_path)
    espn = None
    if use_espn:
        try:
            espn = fetch_espn()
            board = attach_espn(board, espn)
            before = len(board)
            board = drop_unsigned_hist(board, espn)
            dropped = before - len(board)
            if dropped:
                print(f"Dropped {dropped} hist-only players with no 2026 team")
            print(f"ESPN room ADP attached for {board['adp'].notna().sum()} "
                  f"players (not used in rank)")
        except Exception as e:
            print(f"ESPN ADP skipped: {e}", file=sys.stderr)
            board["team"] = board.get("team", pd.Series("", index=board.index))
        kdst = espn[espn["position"].isin(["K", "DST"])].copy() if espn is not None else pd.DataFrame()
        if len(kdst):
            have = set(board["name"].map(name_key))
            kdst["_k"] = [
                name_key(t if p == "DST" else n)
                for n, p, t in zip(kdst["name"], kdst["position"], kdst["team"])
            ]
            kdst = kdst[~kdst["_k"].isin(have)].drop(columns=["_k"])
            kdst["source_points"] = pd.to_numeric(kdst["espn_proj"], errors="coerce")
            kdst["line_source"] = "espn"
            board = pd.concat([board, kdst], ignore_index=True, sort=False)
    if "team" not in board.columns:
        board["team"] = ""
    board["team"] = board["team"].fillna("")
    board = simulate(board, n_sims=n_sims)
    board, repl = rank(board)
    cols = [
        "rank", "pos_rank", "name", "position", "team",
        "proj_points", "floor", "ceil", "draft_value",
        "adp", "adp_gap", "espn_proj", "injury", "line_source",
        "pass_yds", "pass_td", "interceptions",
        "rush_yds", "rush_td", "receptions", "rec_yds", "rec_td", "fumbles",
    ]
    for c in cols:
        if c not in board.columns:
            board[c] = ""
    out = board[cols].copy()
    for c in ("proj_points", "floor", "ceil", "draft_value", "adp", "adp_gap", "espn_proj"):
        out[c] = pd.to_numeric(out[c], errors="coerce").round(1)
    return out, repl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", default=str(DEFAULT_LINES))
    ap.add_argument("--fetch-dk", action="store_true")
    ap.add_argument("--no-espn", action="store_true")
    ap.add_argument("--sims", type=int, default=4000)
    args = ap.parse_args()

    if args.fetch_dk:
        try:
            from nfl_fetch import name_key
            long, wide = fetch_draftkings()
            Path("nfl").mkdir(exist_ok=True)
            long.to_csv("nfl/dk_markets.csv", index=False)
            espn = fetch_espn()
            wide["_key"] = wide["name"].map(name_key)
            espn["_key"] = espn["name"].map(name_key)
            merged = wide.merge(
                espn[["_key", "position", "team"]].drop_duplicates("_key"),
                on="_key", how="left").drop(columns=["_key"])
            merged.to_csv("nfl/dk_lines.csv", index=False)
            print(f"DraftKings: {len(wide)} players, {len(long)} markets -> nfl/dk_lines.csv")
            if merged["position"].notna().sum() > 50:
                args.lines = "nfl/dk_lines.csv"
                print("Using live DK lines for this run.")
        except Exception as e:
            print(f"DraftKings fetch failed ({e}). "
                  f"Their sportsbook blocks datacenter IPs; "
                  f"using {args.lines}.", file=sys.stderr)

    out, repl = run(Path(args.lines), n_sims=args.sims, use_espn=not args.no_espn)
    out.to_csv(OUT, index=False)
    print(out.head(40).to_string(index=False))
    print("\nreplacement:", {p: round(float(v), 1) for p, v in repl.items()})
    print(f"\n{len(out)} players -> {OUT}")


if __name__ == "__main__":
    main()
