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
            rows += get("/stats/player/season", year=year, category=cat)
        if rows:  # empty for seasons not yet played
            pd.DataFrame(rows).to_csv(players, index=False)
            pd.DataFrame(get("/stats/season", year=year)).to_csv(f"data/teams_{year}.csv", index=False)
        print(f"{year}: {len(rows)} player stat rows")
    roster = f"data/roster_{year}.csv"
    if not os.path.exists(roster):
        df = pd.DataFrame(get("/roster", year=year))
        if len(df):
            df.to_csv(roster, index=False)
        print(f"{year}: {len(df)} roster rows")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    years = [int(a) for a in sys.argv[1:]] or range(2019, 2027)
    for y in years:
        fetch_year(y)
