"""Download CFBD season stats to data/*.csv. Usage: python3 fetch.py [years...]"""
import os
import sys

import pandas as pd
import requests

API = "https://api.collegefootballdata.com"
CATEGORIES = ["passing", "rushing", "receiving", "fumbles"]


def api_key():
    k = os.environ.get("CFBD_API_KEY")
    if not k and os.path.exists(".env"):
        for line in open(".env"):
            if line.startswith("CFBD_API_KEY="):
                k = line.split("=", 1)[1].strip()
    if not k:
        sys.exit("Set CFBD_API_KEY as an env var or in a .env file")
    return k


def get(path, **params):
    r = requests.get(API + path, params=params,
                     headers={"Authorization": f"Bearer {api_key()}"}, timeout=60)
    r.raise_for_status()
    return r.json()


def fetch_year(year):
    players = f"data/players_{year}.csv"
    if not os.path.exists(players):
        rows = []
        for cat in CATEGORIES:
            # regular season only: bowls/playoffs/CCGs aren't part of the fantasy season
            rows += get("/stats/player/season", year=year, category=cat, seasonType="regular")
        if rows:  # empty for seasons not yet played
            pd.DataFrame(rows).to_csv(players, index=False)
            pd.DataFrame(get("/stats/season", year=year)).to_csv(f"data/teams_{year}.csv", index=False)
            games = get("/games", year=year, seasonType="regular")
            counts = pd.Series([g["homeTeam"] for g in games] + [g["awayTeam"] for g in games])
            (counts.value_counts().rename_axis("team").rename("games").reset_index()
             .to_csv(f"data/teamgames_{year}.csv", index=False))
        print(f"{year}: {len(rows)} player stat rows")
    roster = f"data/roster_{year}.csv"
    if not os.path.exists(roster):
        df = pd.DataFrame(get("/roster", year=year))
        if len(df):
            df.to_csv(roster, index=False)
        print(f"{year}: {len(df)} roster rows")
    recruits = f"data/recruits_{year}.csv"
    if not os.path.exists(recruits):
        df = pd.DataFrame(get("/recruiting/players", year=year))
        if len(df):
            df.to_csv(recruits, index=False)
        print(f"{year}: {len(df)} recruits")
    sp = f"data/sp_{year}.csv"
    if not os.path.exists(sp):
        df = pd.json_normalize(get("/ratings/sp", year=year))
        if len(df):
            df.to_csv(sp, index=False)
        print(f"{year}: {len(df)} SP+ ratings")


GAMES_SINCE = 2020  # games-played only needed for post-COVID training + 1 feature lag


def fetch_games(year):
    """Count games each player recorded an offensive stat in (per-week box scores)."""
    out = f"data/games_{year}.csv"
    if os.path.exists(out):
        return
    seen = set()
    for wk in range(0, 17):
        try:
            games = get("/games/players", year=year, week=wk, seasonType="regular")
        except requests.HTTPError:
            continue
        for g in games:
            for t in g["teams"]:
                for cat in t["categories"]:
                    if cat["name"] in ("passing", "rushing", "receiving"):
                        for ty in cat["types"]:
                            for a in ty["athletes"]:
                                seen.add((str(a["id"]), g["id"]))
    df = pd.DataFrame(sorted(seen), columns=["playerId", "gameId"])
    df.groupby("playerId").size().rename("games").reset_index().to_csv(out, index=False)
    print(f"{year}: games played for {df['playerId'].nunique()} players")


def fetch_coaches(min_year):
    out = "data/coach_seasons.csv"
    if os.path.exists(out):
        return
    rows = [{"coach": f"{c['firstName']} {c['lastName']}", "team": s["school"],
             "year": s["year"], "games": s["games"]}
            for c in get("/coaches", minYear=min_year) for s in c["seasons"]]
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"coaches: {len(rows)} coach-seasons")


def fetch_abbr():
    out = "data/team_abbr.csv"
    if os.path.exists(out):
        return
    rows = [{"team": t["school"], "abbr": t["abbreviation"]}
            for t in get("/teams/fbs", year=2026)]
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"team abbreviations: {len(rows)}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    years = [int(a) for a in sys.argv[1:]] or range(2014, 2027)
    for y in years:
        fetch_year(y)
        if y >= GAMES_SINCE and os.path.exists(f"data/players_{y}.csv"):
            fetch_games(y)
    fetch_coaches(min(years))
    fetch_abbr()
