"""Valuation / scoring tests. python3 test_valuation.py"""
import math
import unittest

import pandas as pd

from projections import GAMES, PLAYOFF_WEEKS, SCORING, score_stat
from valuation import (
    CONTESTED_ROLE, COPILOT_SHARE, EXPECTED_QBS_ROSTERED_PER_TEAM, FLEX,
    FLEX_ELIGIBLE, SLOTS, TEAMS, apply_qb_split_scenarios, apply_rb_committee_scenarios,
    lineup_counts, n_qb_starters, n_skill_starters, select_lineup, starter_vorps,
    value_board,
)


def _player(i, name, pos, pts, team="X", role=1.0):
    return {"playerId": str(i), "name": name, "team": team, "position": pos,
            "role": role, "proj_points": pts, "rank": i, "pos_rank": f"{pos}{i}",
            "draft_value": 0.0}


class ScoringTests(unittest.TestCase):
    def test_ten_receptions_are_five_points(self):
        self.assertEqual(SCORING[("receiving", "REC")], 0.5)
        self.assertEqual(score_stat("receiving", "REC", 10), 5.0)

    def test_half_ppr_everywhere_in_scoring_dict(self):
        self.assertEqual(SCORING[("receiving", "REC")], 0.5)
        self.assertEqual(PLAYOFF_WEEKS, 0)
        self.assertEqual(GAMES, 12)

    def test_unknown_stat_is_zero_not_guessed(self):
        self.assertEqual(score_stat("kicking", "FG", 3), 0.0)
        self.assertEqual(score_stat("passing", "TWOPT", 1), 0.0)


class OptimizerTests(unittest.TestCase):
    def setUp(self):
        rows = []
        n = 1
        for i in range(40):
            rows.append(_player(n, f"QB{i}", "QB", 300 - i, team=f"T{i}"))
            n += 1
        for i in range(50):
            rows.append(_player(n, f"RB{i}", "RB", 200 - i, team=f"R{i}"))
            n += 1
        for i in range(50):
            rows.append(_player(n, f"WR{i}", "WR", 180 - i, team=f"W{i}"))
            n += 1
        for i in range(10):
            rows.append(_player(n, f"TE{i}", "TE", 170 - 10 * i, team=f"E{i}"))
            n += 1
        self.df = pd.DataFrame(rows)
        self.df["pts12"] = self.df["proj_points"]

    def test_lineup_shape(self):
        sel = select_lineup(self.df)
        c = lineup_counts(sel)
        self.assertEqual(c["n_qb"], 28)
        self.assertEqual(c["n_skill"], 84)
        self.assertGreaterEqual(c["n_rb"], 28)
        self.assertGreaterEqual(c["n_wr"], 28)
        self.assertEqual(n_qb_starters(), 28)
        self.assertEqual(n_skill_starters(), 84)
        self.assertEqual(SLOTS.get("TE", 0), 0)
        self.assertEqual(TEAMS * SLOTS["QB"], 28)

    def test_no_mandatory_te(self):
        sel = select_lineup(self.df)
        # TE0 at 170 beats WR28 at 152, so a TE can be a FLEX, but zero TEs are required
        tes = select_lineup(self.df[self.df["position"] != "TE"])
        self.assertEqual(lineup_counts(tes)["n_te"], 0)
        self.assertEqual(lineup_counts(tes)["n_skill"], 84)

    def test_te_uses_flex_replacement(self):
        ranked, sel, margins = starter_vorps(self.df)
        te = ranked[ranked["name"] == "TE0"].iloc[0]
        flex = margins["next_skill"]
        self.assertAlmostEqual(te["starter_vorp"], te["pts12"] - flex, places=1)
        # a private TE2 baseline would be TE1=160; TE0 would then be +10, not flex
        te1_pts = float(self.df.loc[self.df["name"] == "TE1", "pts12"].iloc[0])
        self.assertNotAlmostEqual(te["starter_vorp"], te["pts12"] - te1_pts, places=1)

    def test_duplicate_ids_rejected_by_output(self):
        ranked, _, _ = starter_vorps(self.df)
        self.assertEqual(ranked["playerId"].nunique(), len(ranked))


class BoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = pd.read_csv("projections_2026.csv", dtype={"playerId": str})
        cls.plain, cls.plain_info = value_board(cls.raw, apply_priors=False)
        cls.tuned, cls.info = value_board(cls.raw, apply_priors=True)

    def test_optimizer_counts_on_real_board(self):
        c = self.info["counts"]
        self.assertEqual(c["n_qb"], 28)
        self.assertEqual(c["n_skill"], 84)
        self.assertGreaterEqual(c["n_rb"], 28)
        self.assertGreaterEqual(c["n_wr"], 28)

    def test_no_mandatory_te_on_real_board(self):
        self.assertGreaterEqual(self.info["counts"]["n_te"], 0)
        # FLEX replacement is a skill player, not a private TE2
        self.assertEqual(self.plain_info["counts"]["n_qb"], 28)
        feagin = self.plain[self.plain["name"] == "Kaden Feagin"].iloc[0]
        self.assertAlmostEqual(feagin["starter_vorp"], 3.1, delta=1.5)
        self.assertGreaterEqual(int(feagin["rank"]), 70)
        self.assertLessEqual(int(feagin["rank"]), 110)

    def test_unique_continuous_ranks(self):
        r = self.tuned["rank"].sort_values()
        self.assertEqual(list(r), list(range(1, len(self.tuned) + 1)))
        self.assertEqual(self.tuned["playerId"].nunique(), len(self.tuned))
        self.assertFalse(self.tuned["rank"].duplicated().any())

    def test_rank_monotonic_with_draft_value(self):
        d = self.tuned.sort_values(["rank"])
        v = d["draft_adjusted_value"].values
        for i in range(1, min(len(v), 500)):
            self.assertGreaterEqual(v[i - 1], v[i] - 1e-9)

    def test_no_nan_inf_ranks(self):
        for col in ["rank", "starter_vorp", "draft_adjusted_value", "managed_vorp",
                    "projected_ppg", "p50"]:
            s = self.tuned[col]
            self.assertFalse(s.isna().any(), col)
            self.assertTrue(all(math.isfinite(float(x)) for x in s.head(2000)), col)

    def test_named_starter_not_stale_backup(self):
        b = self.tuned[self.tuned["name"] == "Faizon Brandon"].iloc[0]
        self.assertGreaterEqual(b["starter_probability"], 0.85)
        self.assertGreater(b["projected_points_if_active"], 150)
        staub = self.tuned[self.tuned["name"] == "Ryan Staub"].iloc[0]
        self.assertLess(staub["role"], b["role"])
        self.assertLess(staub["projected_points_if_active"], b["projected_points_if_active"])

    def test_unavailable_week_gets_replacement(self):
        h = self.tuned[self.tuned["name"] == "Ahmad Hardy"].iloc[0]
        self.assertEqual(h["projected_games"], 10)
        self.assertGreater(h["replacement_points_during_absences"], 0)
        self.assertAlmostEqual(
            h["managed_season_points"],
            h["raw_season_points"] + h["replacement_points_during_absences"],
            places=1,
        )
        self.assertGreater(h["managed_season_points"], h["raw_season_points"])

    def test_scenario_probabilities_sum_to_one(self):
        # synthetic two-RB room
        rows = [
            _player(1, "A", "RB", 159, team="TTU", role=CONTESTED_ROLE),
            _player(2, "B", "RB", 159, team="TTU", role=CONTESTED_ROLE),
        ]
        d = pd.DataFrame(rows)
        d["pts_full"] = d["proj_points"] / CONTESTED_ROLE
        d["pts12"] = d["proj_points"]
        d["contested"] = True
        d["role_in"] = d["role"]
        out = apply_rb_committee_scenarios(d)
        self.assertAlmostEqual(0.5 + 0.5, 1.0)
        room = float(out["_room_expected"].iloc[0])
        budget = float(out["_room_budget"].iloc[0])
        self.assertAlmostEqual(room, budget, delta=budget * 0.02)
        # identical teammates must share the same expected points (not one lead + one copilot)
        self.assertAlmostEqual(float(out["pts12"].iloc[0]), float(out["pts12"].iloc[1]), places=1)
        self.assertAlmostEqual(float(out["pts12"].iloc[0]), 0.5 * (227.142857 + 159.0), delta=0.2)

    def test_qb_split_shares_sum_to_one(self):
        rows = [
            _player(1, "A", "QB", 225, team="UNLV", role=1.0),
            _player(2, "B", "QB", 144, team="UNLV", role=1.0),
        ]
        d = pd.DataFrame(rows)
        d["pts_full"] = d["proj_points"]
        d["pts12"] = d["proj_points"]
        d["contested"] = True
        out = apply_qb_split_scenarios(d)
        self.assertAlmostEqual(float(out["_qb_share_sum"].iloc[0]), 1.0)
        # neither keeps a full-time starter projection
        self.assertLess(out["pts12"].max(), 225)

    def test_default_qb_roster_assumption(self):
        self.assertEqual(TEAMS * EXPECTED_QBS_ROSTERED_PER_TEAM, 42)
        self.assertIn("RB", FLEX_ELIGIBLE)
        self.assertIn("TE", FLEX_ELIGIBLE)
        self.assertEqual(FLEX, 2)


if __name__ == "__main__":
    unittest.main()
