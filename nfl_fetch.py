"""Pull ESPN ADP/projections and (when unblocked) DraftKings season-long lines."""
import json
import re
import time
import unicodedata

import pandas as pd
import requests

from nfl_lines import classify_market, expected_from_ou, looks_season_long

ESPN_POS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}
ESPN_TEAMS = {
    1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL", 7: "DEN",
    8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC", 13: "LV", 14: "LAR",
    15: "MIA", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ", 21: "PHI",
    22: "ARI", 23: "PIT", 24: "LAC", 25: "SF", 26: "SEA", 27: "TB", 28: "WAS",
    29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU",
}

DK_NFL = 88808
DK_BASE = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


def name_key(name):
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return " ".join(s.split())


def _get(url, headers=None, timeout=45):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    r = requests.get(url, headers=h, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_espn(season=2026):
    """PPR ADP + ESPN's own season projection for comparison."""
    url = (f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/"
           f"{season}/segments/0/leaguedefaults/3?view=kona_player_info")
    filt = {"players": {"limit": 2000,
                        "sortPercOwned": {"sortPriority": 1, "sortAsc": False}}}
    data = _get(url, headers={"X-Fantasy-Filter": json.dumps(filt)})
    rows = []
    for item in data.get("players") or []:
        p = item.get("player") or {}
        pos = ESPN_POS.get(p.get("defaultPositionId"))
        if not pos:
            continue
        own = p.get("ownership") or {}
        ranks = (p.get("draftRanksByRankType") or {}).get("PPR") or {}
        espn_proj = None
        for st in p.get("stats") or []:
            if (st.get("seasonId") == season and st.get("statSourceId") == 1
                    and st.get("statSplitTypeId") == 0 and st.get("scoringPeriodId") == 0):
                espn_proj = st.get("appliedTotal")
                break
        team = ESPN_TEAMS.get(p.get("proTeamId"), "")
        name = p.get("fullName") or ""
        if pos == "DST" and team:
            name = team  # match LAR / PHI snapshot names
        rows.append({
            "espn_id": p.get("id"),
            "name": p.get("fullName") or "",
            "key": name_key(name if pos != "DST" else team),
            "position": pos,
            "team": team,
            "adp": own.get("averageDraftPosition"),
            "espn_rank": ranks.get("rank"),
            "espn_proj": espn_proj,
            "injured": p.get("injured") or False,
            "injury": p.get("injuryStatus") or "",
        })
    return pd.DataFrame(rows)


def _dk_get(url):
    try:
        from curl_cffi import requests as cr
        r = cr.get(url, impersonate="chrome", timeout=30,
                   headers={"Accept": "application/json", "User-Agent": UA})
        r.raise_for_status()
        return r.json()
    except Exception:
        return _get(url)


def fetch_draftkings(sleep=0.25):
    """Walk DK NFL categories for season-long player O/Us. Raises on 403."""
    root = _dk_get(f"{DK_BASE}/{DK_NFL}?format=json")
    eg = root.get("eventGroup") or {}
    events = {e.get("eventId"): e.get("name", "") for e in eg.get("events") or []}
    cats = eg.get("offerCategories") or []
    rows = []
    for cat in cats:
        cid = cat.get("offerCategoryId")
        cname = cat.get("name") or ""
        try:
            cjson = _dk_get(f"{DK_BASE}/{DK_NFL}/categories/{cid}?format=json")
        except Exception:
            continue
        subs = ((cjson.get("eventGroup") or {}).get("offerCategories") or [{}])
        descriptors = []
        for sc in subs:
            if sc.get("offerCategoryId") == cid or len(subs) == 1:
                descriptors = sc.get("offerSubcategoryDescriptors") or []
                break
        if not descriptors:
            descriptors = cat.get("offerSubcategoryDescriptors") or []
        for sub in descriptors:
            sid = sub.get("subcategoryId")
            sname = sub.get("name") or ""
            try:
                sjson = _dk_get(
                    f"{DK_BASE}/{DK_NFL}/categories/{cid}/subcategories/{sid}?format=json")
            except Exception:
                continue
            time.sleep(sleep)
            for oc in (sjson.get("eventGroup") or {}).get("offerCategories") or []:
                for desc in oc.get("offerSubcategoryDescriptors") or []:
                    offers = ((desc.get("offerSubcategory") or {}).get("offers") or [])
                    for group in offers:
                        for offer in (group if isinstance(group, list) else [group]):
                            label = offer.get("label") or sname
                            event = events.get(offer.get("eventId"), "")
                            if not looks_season_long(f"{label} {cname} {sname}", event):
                                # still keep if the category itself is futures-like
                                blob = f"{cname} {sname} {event}".lower()
                                if not any(w in blob for w in
                                           ("future", "season", "wins", "player")):
                                    continue
                            stat = classify_market(f"{label} {sname} {cname}")
                            if not stat:
                                continue
                            outs = offer.get("outcomes") or []
                            over = next((o for o in outs if str(o.get("label", "")).lower().startswith("over")), None)
                            under = next((o for o in outs if str(o.get("label", "")).lower().startswith("under")), None)
                            if not over or over.get("line") is None:
                                continue
                            player = (over.get("participant") or offer.get("label") or "").strip()
                            if not player:
                                continue
                            oo = over.get("oddsAmerican") or -110
                            uo = (under or {}).get("oddsAmerican") or -110
                            try:
                                oo, uo = int(str(oo).replace("+", "")), int(str(uo).replace("+", ""))
                            except ValueError:
                                oo, uo = -110, -110
                            line = float(over["line"])
                            rows.append({
                                "name": player,
                                "stat": stat,
                                "line": line,
                                "over_odds": oo,
                                "under_odds": uo,
                                "expected": round(expected_from_ou(line, oo, uo, stat), 2),
                                "market": f"{cname}/{sname}",
                                "event": event,
                            })
    if not rows:
        raise RuntimeError("DraftKings returned no season-long player markets")
    long = pd.DataFrame(rows)
    wide = (long.sort_values("name")
            .drop_duplicates(["name", "stat"])
            .pivot(index="name", columns="stat", values="expected")
            .reset_index())
    return long, wide


def attach_espn(vegas, espn):
    """Join ESPN ADP by name. ESPN position/team win (fantasy slot, current roster)."""
    v = vegas.copy()
    v["_key"] = v["name"].map(name_key)
    e = espn.copy()
    e["_key"] = [
        name_key(t if p == "DST" else n)
        for n, p, t in zip(e["name"], e["position"], e["team"])
    ]
    keep = (e.drop_duplicates("_key")
            [["_key", "position", "team", "adp", "espn_rank", "espn_proj", "injury"]]
            .rename(columns={"position": "position_espn", "team": "team_espn"}))
    merged = v.merge(keep, on="_key", how="left")
    merged["position"] = merged["position_espn"].combine_first(merged["position"])
    merged["team"] = merged["team_espn"].combine_first(merged["team"])
    return merged.drop(columns=["_key", "position_espn", "team_espn"])
