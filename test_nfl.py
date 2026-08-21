"""Sanity checks for ESPN PPR scoring, juice conversion, VORP, and the sim."""
import unittest

import pandas as pd

from nfl_lines import american_to_prob, expected_from_ou, fair_over_prob
from nfl_scoring import complete_stats, skill_points
from nfl_sim import simulate
from nfl import rank


class Scoring(unittest.TestCase):
    def test_ppr_receiver(self):
        # 100 rec, 1200 yds, 8 TD, 1 fumble lost
        pts = skill_points({
            "pass_yds": 0, "pass_td": 0, "interceptions": 0,
            "rush_yds": 0, "rush_td": 0,
            "receptions": 100, "rec_yds": 1200, "rec_td": 8, "fumbles": 1,
        })
        self.assertAlmostEqual(pts, 100 + 120 + 48 - 2, places=4)

    def test_qb(self):
        pts = skill_points({
            "pass_yds": 4000, "pass_td": 30, "interceptions": 10,
            "rush_yds": 400, "rush_td": 5,
            "receptions": 0, "rec_yds": 0, "rec_td": 0, "fumbles": 3,
        })
        self.assertAlmostEqual(pts, 160 + 120 - 20 + 40 + 30 - 6, places=4)

    def test_fill_receptions_from_yards(self):
        df = complete_stats(pd.DataFrame([
            {"name": "X", "position": "WR", "rec_yds": 1280,
             "receptions": None, "pass_yds": None, "pass_td": None,
             "interceptions": None, "rush_yds": None, "rush_td": None,
             "rec_td": 8, "fumbles": None},
        ]))
        self.assertAlmostEqual(df.loc[0, "receptions"], 100.0, places=1)


class Lines(unittest.TestCase):
    def test_even_juice_mean_is_the_line(self):
        mu = expected_from_ou(999.5, -110, -110, "rec_yds", sigma=200)
        self.assertAlmostEqual(mu, 999.5, places=2)

    def test_juiced_over_lifts_mean(self):
        mu = expected_from_ou(3799.5, -120, 100, "pass_yds", sigma=500)
        self.assertGreater(mu, 3799.5)
        self.assertLess(mu, 3799.5 + 200)

    def test_american_favorite(self):
        self.assertAlmostEqual(american_to_prob(-110), 110 / 210, places=6)
        self.assertAlmostEqual(fair_over_prob(-110, -110), 0.5, places=6)


class Vorp(unittest.TestCase):
    def test_flex_eats_skill_before_replacement(self):
        rows = []
        # 10 QBs above replacement, 11th is replacement
        for i in range(12):
            rows.append({"name": f"QB{i}", "position": "QB", "proj_points": 300 - i})
        # 20 RB starters + some flex: 30 WR/RB/TE flex pool starts with RBs first
        for i in range(25):
            rows.append({"name": f"RB{i}", "position": "RB", "proj_points": 250 - i})
        for i in range(25):
            rows.append({"name": f"WR{i}", "position": "WR", "proj_points": 240 - i})
        for i in range(12):
            rows.append({"name": f"TE{i}", "position": "TE", "proj_points": 180 - i})
        for i in range(12):
            rows.append({"name": f"K{i}", "position": "K", "proj_points": 100 - i})
        for i in range(12):
            rows.append({"name": f"D{i}", "position": "DST", "proj_points": 90 - i})
        df = pd.DataFrame(rows)
        ranked, repl = rank(df.assign(floor=0, ceil=0))
        self.assertEqual(repl["QB"], 290)  # 11th QB (300, 299, ... 290)
        self.assertGreater(repl["RB"], 0)
        # top QB draft value should be less than top RB in this toy (QB VORP = 10, RB VORP larger)
        top_qb = ranked.loc[ranked.position.eq("QB")].iloc[0]
        top_rb = ranked.loc[ranked.position.eq("RB")].iloc[0]
        self.assertGreater(top_rb.draft_value, top_qb.draft_value)


class Sim(unittest.TestCase):
    def test_mean_tracks_deterministic(self):
        df = pd.DataFrame([{
            "name": "Test WR", "position": "WR", "team": "CIN",
            "pass_yds": 0, "pass_td": 0, "interceptions": 0,
            "rush_yds": 20, "rush_td": 0,
            "receptions": 100, "rec_yds": 1200, "rec_td": 8, "fumbles": 1,
            "source_points": None,
        }])
        det = skill_points(df.iloc[0])
        out = simulate(df, n_sims=3000, seed=0)
        self.assertAlmostEqual(out.loc[0, "proj_points"], round(det, 1), places=1)
        self.assertLess(out.loc[0, "floor"], out.loc[0, "proj_points"])
        self.assertGreater(out.loc[0, "ceil"], out.loc[0, "proj_points"])


if __name__ == "__main__":
    unittest.main()
