"""Convert sportsbook over/unders + American odds into expected stats.

The O/U is treated as the median. Juice is removed so P(over) is fair, then
the mean is shifted under a normal assumption: mean = line + sigma * z(p_over).

Season-long yards are close to normal; TDs are right-skewed so a small extra
mean bump is applied when we don't have a better sigma.
"""
from statistics import NormalDist

_N = NormalDist()


def american_to_prob(odds):
    odds = int(odds)
    if odds == 0:
        return 0.5
    if odds < 0:
        return abs(odds) / (abs(odds) + 100.0)
    return 100.0 / (odds + 100.0)


def fair_over_prob(over_odds, under_odds):
    p_o = american_to_prob(over_odds)
    p_u = american_to_prob(under_odds)
    s = p_o + p_u
    return 0.5 if s <= 0 else p_o / s


def default_sigma(stat, line):
    m = abs(float(line))
    if stat.endswith("_yds"):
        return max(80.0, 0.20 * m)
    if stat in ("receptions", "pass_att", "pass_cmp", "rush_att"):
        return max(6.0, 0.18 * m)
    if stat.endswith("_td") or stat in ("interceptions", "fumbles"):
        return max(1.2, m ** 0.5 * 1.15)
    return max(1.0, 0.20 * m)


def expected_from_ou(line, over_odds, under_odds, stat="rec_yds", sigma=None):
    """Fair expected value of a two-way O/U market."""
    line = float(line)
    sig = default_sigma(stat, line) if sigma is None else float(sigma)
    p = fair_over_prob(over_odds, under_odds)
    # clip so extreme juice can't send z to inf
    p = min(max(p, 0.02), 0.98)
    z = _N.inv_cdf(p)
    mean = line + sig * z
    # counting stats can't go negative
    return max(0.0, mean)


# DK / sportsbook market labels -> our columns
MARKET_ALIASES = {
    "pass_yds": ("passing yards", "pass yards", "passing yds"),
    "pass_td": ("passing tds", "pass tds", "passing touchdowns", "pass td"),
    "interceptions": ("interceptions", "ints thrown", "pass ints"),
    "rush_yds": ("rushing yards", "rush yards", "rushing yds"),
    "rush_td": ("rushing tds", "rush tds", "rushing touchdowns", "rush td"),
    "rec_yds": ("receiving yards", "rec yards", "receiving yds"),
    "receptions": ("receptions", "recpts"),
    "rec_td": ("receiving tds", "rec tds", "receiving touchdowns", "rec td"),
}


def classify_market(label):
    s = (label or "").lower().replace("-", " ")
    # skip alt / weekly / first-td noise
    if any(w in s for w in ("alt ", "anytime", "first td", "longest", "combo")):
        return None
    for col, keys in MARKET_ALIASES.items():
        if any(k in s for k in keys):
            return col
    return None


def looks_season_long(label, event_name=""):
    blob = f"{label} {event_name}".lower()
    if any(w in blob for w in ("week ", "wk ", "game ", "1h", "1st half")):
        return False
    return any(w in blob for w in ("season", "regular season", "2026", "2025/26", "2026/27"))
