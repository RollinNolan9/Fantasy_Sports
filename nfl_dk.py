"""Parse the DraftKings season-long offering workbook into player stat means."""
import re
from pathlib import Path

import pandas as pd

from nfl_fetch import name_key
from nfl_lines import classify_market, expected_from_ou

VEGAS_PATH = Path("nfl/vegas_2026.csv")

# "1199.5  -110 / -110"  |  "799.5  -120 / 100"  |  "924.5  -110 /"
LINE_RE = re.compile(
    r"(?P<line>\d+(?:\.\d+)?)\s*(?:(?P<over>[+-]?\d+)\s*/\s*(?P<under>[+-]?\d+)?)?"
)
SKILL_POS = {"QB", "RB", "WR", "TE"}


def _odds(s, default=-110):
    if s is None or str(s).strip() in ("", "nan"):
        return default
    try:
        return int(str(s).replace("+", "").replace(",", "").strip())
    except ValueError:
        return default


def parse_current_line(text, open_line=None, open_o=None, open_u=None):
    """Return (line, over_odds, under_odds) or None if unusable.

    `10+ NNN` is a ticket id, not a line. Skip the whole row — the Open Line
    on those rows is leftover junk (Diggs 799.5 rush yards). Fall back to
    Open Line only when Current Line is blank.
    """
    s = "" if pd.isna(text) else str(text).strip()
    if re.search(r"\d\+", s):
        return None
    m = LINE_RE.search(s) if s else None
    if m and m.group("line"):
        return (float(m.group("line")),
                _odds(m.group("over")),
                _odds(m.group("under")))
    if open_line is not None and str(open_line).strip() not in ("", "nan"):
        try:
            return float(open_line), _odds(open_o), _odds(open_u)
        except (TypeError, ValueError):
            return None
    return None


def parse_offering(path):
    """Wide player table: one row per skill player, DK means in stat columns.

    Only Balanced O/U skill markets. Sacks / IDP / milestones are ignored.
    """
    raw = pd.read_csv(path, low_memory=False)
    for c in ("Player", "Team", "Pos", "Market", "Balanced/Milestone", "Current Line"):
        if c not in raw.columns:
            raise ValueError(f"{path} missing {c}")
    keep = raw[raw["Balanced/Milestone"].fillna("").str.lower().eq("balanced")].copy()
    keep["pos"] = keep["Pos"].replace({"FB": "RB"}).astype(str).str.upper()
    keep = keep[keep["pos"].isin(SKILL_POS)]

    recs = []
    dirty = set()
    for r in keep.to_dict("records"):
        name = str(r["Player"]).strip()
        stat = classify_market(r.get("Market") or "")
        if not stat:
            continue
        parsed = parse_current_line(
            r.get("Current Line"),
            r.get("Open Line"),
            r.get("Open O Odds"),
            r.get("Open U Odds"),
        )
        if not parsed:
            dirty.add(name)
            continue
        line, over, under = parsed
        recs.append({
            "name": name,
            "team": str(r.get("Team") or "").strip(),
            "position": r["pos"],
            "stat": stat,
            "line": line,
            "over_odds": over,
            "under_odds": under,
            "expected": round(expected_from_ou(line, over, under, stat), 2),
            "market": r.get("Market"),
        })
    if not recs:
        raise ValueError(f"no usable balanced O/Us in {path}")
    long = pd.DataFrame(recs)
    npos = long.groupby("name")["position"].nunique()
    nteam = long.groupby("name")["team"].nunique()
    nstat = long.groupby(["name", "stat"]).size()
    dirty.update(npos[npos > 1].index)
    dirty.update(nteam[nteam > 1].index)
    dirty.update(nstat[nstat > 1].index.get_level_values(0))
    long = long[~long["name"].isin(dirty)].drop_duplicates(["name", "stat"])
    if long.empty:
        wide = pd.DataFrame(columns=["name", "team", "position", "n_dk", "line_source"])
    else:
        wide = (long.pivot(index=["name", "team", "position"], columns="stat", values="expected")
                .reset_index())
        wide.columns.name = None
        wide = wide.merge(long.groupby("name").size().rename("n_dk"),
                          left_on="name", right_index=True, how="left")
        wide["line_source"] = "dk"
    return long, wide, dirty


def overlay_vegas(dk_wide, dirty, vegas_path=VEGAS_PATH):
    """Vegas beats hist. Dirty DK names, plus anyone DK never posted."""
    dirty_keys = {name_key(n) for n in dirty}
    dk = dk_wide.copy()
    if "name" in dk.columns and len(dk):
        dk["_k"] = dk["name"].map(name_key)
        dk = dk[~dk["_k"].isin(dirty_keys)]
    else:
        dk["_k"] = pd.Series(dtype=object)
    have = set(dk["_k"].dropna())
    vegas = pd.read_csv(vegas_path)
    vegas["_k"] = vegas["name"].map(name_key)
    take = vegas[vegas["_k"].isin(dirty_keys) | ~vegas["_k"].isin(have)].drop_duplicates("_k")
    take["line_source"] = "vegas"
    take["n_dk"] = 0
    dk = dk.drop(columns="_k", errors="ignore")
    return pd.concat([dk, take.drop(columns="_k")], ignore_index=True, sort=False)
