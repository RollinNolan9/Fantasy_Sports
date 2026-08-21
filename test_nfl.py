"""Sanity checks for ESPN PPR scoring, juice conversion, VORP, and the sim."""
import unittest

import pandas as pd

from nfl_dk import overlay_vegas, parse_current_line, parse_offering
from nfl_hist import fill_from_hist
from nfl_lines import american_to_prob, expected_from_ou, fair_over_prob
from nfl_scoring import complete_stats, skill_points
from nfl_sim import simulate
from nfl import drop_unsigned_hist, rank


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

    def test_mid_te_ranks_like_flex_not_vs_te11(self):
        rows = []
        for i in range(12):
            rows.append({"name": f"QB{i}", "position": "QB", "proj_points": 300 - i})
        for i in range(30):
            rows.append({"name": f"RB{i}", "position": "RB", "proj_points": 250 - i})
        for i in range(30):
            rows.append({"name": f"WR{i}", "position": "WR", "proj_points": 240 - i})
        rows.append({"name": "Elite TE", "position": "TE", "proj_points": 240})
        rows.append({"name": "Good TE", "position": "TE", "proj_points": 220})
        for i in range(12):
            rows.append({"name": f"TE{i}", "position": "TE", "proj_points": 175 - i})
        for i in range(12):
            rows.append({"name": f"K{i}", "position": "K", "proj_points": 100 - i})
        for i in range(12):
            rows.append({"name": f"D{i}", "position": "DST", "proj_points": 90 - i})
        ranked, _ = rank(pd.DataFrame(rows).assign(floor=0, ceil=0))
        tes_in_70 = ranked.query("rank <= 70 and position == 'TE'")
        self.assertLessEqual(len(tes_in_70), 3)
        self.assertEqual(ranked.loc[ranked.name.eq("Elite TE")].iloc[0].pos_rank, "TE1")
        mid = ranked.loc[ranked.name.eq("TE0")].iloc[0]
        self.assertGreater(mid["rank"], 40)


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


class Offering(unittest.TestCase):
    def test_parse_juiced_and_partial_odds(self):
        line, over, under = parse_current_line("799.5  -120 / 100")
        self.assertEqual(line, 799.5)
        self.assertEqual(over, -120)
        self.assertEqual(under, 100)
        line, over, under = parse_current_line("924.5  -110 /")
        self.assertEqual((line, over, under), (924.5, -110, -110))

    def test_open_line_fallback(self):
        parsed = parse_current_line(None, open_line=68.5, open_o=-110, open_u=-110)
        self.assertEqual(parsed[0], 68.5)

    def test_ticket_id_does_not_use_open_line(self):
        self.assertIsNone(parse_current_line("10+ 701", open_line=799.5,
                                            open_o=-110, open_u=-110))

    def test_real_offering_locks_gibbs(self):
        _, wide, _ = parse_offering("nfl/dk_offering.csv")
        g = wide[wide.name.eq("Jahmyr Gibbs")].iloc[0]
        self.assertAlmostEqual(g.rush_yds, 1199.5, places=1)

    def test_hist_does_not_clobber_dk(self):
        dk = pd.DataFrame([{"name": "Jahmyr Gibbs", "team": "DET", "position": "RB",
                            "rush_yds": 1199.5, "n_dk": 1, "line_source": "dk"}])
        hist = pd.DataFrame([{
            "key": "jahmyr gibbs", "name": "Jahmyr Gibbs", "position": "RB", "team": "DET",
            "pass_yds": 0, "pass_td": 0, "interceptions": 0,
            "rush_yds": 800, "rush_td": 8, "rush_att": 200,
            "receptions": 50, "rec_yds": 400, "rec_td": 3, "fumbles": 1,
            "pass_att": 0, "pass_cmp": 0,
        }])
        out = fill_from_hist(dk, hist)
        row = out[out.name.eq("Jahmyr Gibbs")].iloc[0]
        self.assertAlmostEqual(row.rush_yds, 1199.5, places=1)
        self.assertGreater(row.receptions, 0)
        # TDs scaled toward the 1199.5 / 800 workload
        self.assertGreater(row.rush_td, 8)

    def test_dup_or_error_falls_back_to_vegas(self):
        _, wide, dirty = parse_offering("nfl/dk_offering.csv")
        self.assertIn("Brock Bowers", dirty)
        self.assertIn("Stefon Diggs", dirty)
        self.assertTrue(wide[wide.name.eq("Brock Bowers")].empty)
        self.assertTrue(wide[wide.name.eq("Stefon Diggs")].empty)
        out = overlay_vegas(wide, dirty)
        b = out[out.name.eq("Brock Bowers")].iloc[0]
        self.assertEqual(b.position, "TE")
        self.assertAlmostEqual(b.rec_yds, 924.5, places=1)
        self.assertAlmostEqual(b.rec_td, 7.5, places=1)
        self.assertEqual(b.line_source, "vegas")
        d = out[out.name.eq("Stefon Diggs")].iloc[0]
        self.assertAlmostEqual(d.rec_yds, 774.5, places=1)
        self.assertLess(d.rush_yds if pd.notna(d.rush_yds) else 0, 50)

    def test_vegas_beats_hist_when_dk_omits(self):
        _, wide, dirty = parse_offering("nfl/dk_offering.csv")
        self.assertTrue(wide[wide.name.eq("Jauan Jennings")].empty)
        out = overlay_vegas(wide, dirty)
        j = out[out.name.eq("Jauan Jennings")].iloc[0]
        self.assertEqual(j.line_source, "vegas")
        self.assertAlmostEqual(j.rec_yds, 487.0, places=1)
        self.assertAlmostEqual(j.rec_td, 3.0, places=1)

    def test_unsigned_hist_dropped(self):
        board = pd.DataFrame([
            {"name": "Jahmyr Gibbs", "team": "DET", "position": "RB",
             "line_source": "dk+hist"},
            {"name": "Joe Mixon", "team": "HOU", "position": "RB",
             "line_source": "hist"},
            {"name": "Ghost RB", "team": "", "position": "RB",
             "line_source": "hist"},
        ])
        espn = pd.DataFrame([
            {"name": "Jahmyr Gibbs", "position": "RB", "team": "DET"},
            {"name": "Joe Mixon", "position": "RB", "team": ""},
        ])
        out = drop_unsigned_hist(board, espn)
        names = set(out.name)
        self.assertIn("Jahmyr Gibbs", names)
        self.assertNotIn("Joe Mixon", names)
        self.assertNotIn("Ghost RB", names)


if __name__ == "__main__":
    unittest.main()
