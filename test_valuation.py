"""Valuation / scoring tests. python3 test_valuation.py"""
import math
import unittest

import pandas as pd

from projections import GAMES, PLAYOFF_WEEKS, SCORING, score_stat
from valuation import (
    CONTESTED_ROLE, EXPECTED_QBS_ROSTERED_PER_TEAM, FLEX,
    FLEX_ELIGIBLE, PRIMARY_SHARE, SCORING_PPR, SLOTS, TEAMS, WAIVER_REPLACEMENT_RANK,
    apply_qb_split_scenarios, apply_rb_committee_scenarios,
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

    def test_fifty_receptions_are_twenty_five_points(self):
        self.assertEqual(score_stat("receiving", "REC", 50), 25.0)

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
                    "projected_ppg", "floor_rank", "ceiling_rank"]:
            s = self.tuned[col]
            self.assertFalse(s.isna().any(), col)
            self.assertTrue(all(math.isfinite(float(x)) for x in s.head(2000)), col)

    def test_floor_ceiling_cover_full_pool(self):
        n = len(self.tuned)
        for col in ("floor_rank", "ceiling_rank"):
            r = self.tuned[col].sort_values()
            self.assertEqual(list(r), list(range(1, n + 1)), col)

    def test_percentiles_null_or_distinct(self):
        d = self.tuned
        identical = d["p10"].notna() & ((d["p90"] - d["p10"]).abs() < 0.5)
        self.assertEqual(int(identical.sum()), 0)
        low_conf = d[d["starter_probability"] < 0.85]
        modeled = low_conf[low_conf["p10"].notna()]
        if len(modeled):
            self.assertTrue(((modeled["p90"] - modeled["p10"]).abs() > 0.5).all())
        locked = d[(d["role"] >= 0.99) & (d["projected_games"] == 12)
                   & ~d["contested"]]
        # no scenario/injury → null percentiles, not a fake distribution
        self.assertTrue(locked["p10"].isna().mean() > 0.8)

    def test_wr_uses_wr29_not_flex(self):
        wrs = self.tuned[self.tuned["position"] == "WR"]
        positive = (wrs["draft_adjusted_value"] > 0).sum()
        self.assertGreaterEqual(int(positive), 25)
        barkate = wrs[wrs["name"] == "Cooper Barkate"]
        if len(barkate):
            self.assertGreater(float(barkate.iloc[0]["draft_adjusted_value"]), 0)
        feagin = self.tuned[self.tuned["name"] == "Kaden Feagin"].iloc[0]
        # TE still vs FLEX, not a private TE baseline
        self.assertLess(abs(float(feagin["draft_adjusted_value"])
                            - (float(feagin["managed_season_points"]) - self.info["flex_repl"])), 1.5)

    def test_scoring_ppr_exported(self):
        self.assertEqual(SCORING_PPR, 0.5)
        self.assertTrue((self.tuned["scoring_ppr"] == 0.5).all())

    def test_waiver_not_flex_for_missed_games(self):
        h = self.tuned[self.tuned["name"] == "Ahmad Hardy"].iloc[0]
        missed = 12 - float(h["projected_games"])
        self.assertEqual(missed, 2)
        expected = missed * float(h["waiver_replacement_ppg"])
        self.assertAlmostEqual(float(h["replacement_points_during_absences"]), expected, delta=1.5)
        self.assertEqual(int(h["waiver_replacement_rank"]), WAIVER_REPLACEMENT_RANK)
        # ramped PPG is below full-workload 21.16
        self.assertLess(float(h["projected_ppg"]), 21.0)

    def test_davison_not_stuck_on_2025_injury(self):
        d = self.tuned[self.tuned["name"] == "Jordon Davison"].iloc[0]
        self.assertEqual(float(d["projected_games"]), 12)

    def test_sp_blank_without_probability_model(self):
        lacy = self.tuned[self.tuned["name"] == "Kewan Lacy"].iloc[0]
        self.assertTrue(pd.isna(lacy["starter_probability"]))
        dickey = self.tuned[self.tuned["name"] == "Cameron Dickey"].iloc[0]
        self.assertGreater(float(dickey["starter_probability"]), 0.3)

    def test_mccomb_named_starter(self):
        m = self.tuned[self.tuned["name"] == "David McComb"].iloc[0]
        g = self.tuned[self.tuned["name"] == "Thomas Gotkowski"].iloc[0]
        self.assertGreaterEqual(float(m["starter_probability"]), 0.85)
        self.assertGreater(float(m["projected_points_if_active"]), float(g["projected_points_if_active"]))
        self.assertEqual(str(m["role_source_date"]), "2026-08-24")
        self.assertNotEqual(str(m.get("source_as_of", "")), "2026-08-25")

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
        d["starter_probability"] = 0.5
        out = apply_rb_committee_scenarios(d)
        shares = out["expected_opportunity_share"]
        self.assertAlmostEqual(float(shares.sum()), 1.0, delta=0.02)
        self.assertTrue((shares < 0.70).all())
        self.assertAlmostEqual(float(out["pts12"].iloc[0]), float(out["pts12"].iloc[1]), places=1)
        room = float(out["_room_expected"].iloc[0])
        budget = float(out["_room_budget"].iloc[0])
        self.assertAlmostEqual(room, budget, delta=budget * 0.02)
        self.assertAlmostEqual(float(out["starter_probability"].sum()), 1.0, delta=0.02)
        self.assertAlmostEqual(float(out["p75"].iloc[0]), float(out["p90"].iloc[0]), delta=0.5)
        self.assertGreater(float(out["p90"].iloc[0]), float(out["p50"].iloc[0]))
        self.assertGreater(float(out["p90"].iloc[0]) - float(out["p10"].iloc[0]), 1)

    def test_committee_includes_every_rb(self):
        rows = [
            _player(1, "A", "RB", 159, team="TTU", role=CONTESTED_ROLE),
            _player(2, "B", "RB", 159, team="TTU", role=CONTESTED_ROLE),
            _player(3, "C", "RB", 80, team="TTU", role=0.84),
        ]
        d = pd.DataFrame(rows)
        d["pts_full"] = [159 / CONTESTED_ROLE, 159 / CONTESTED_ROLE, 80 / 0.84]
        d["pts12"] = d["proj_points"]
        d["contested"] = [True, True, False]
        d["starter_probability"] = [0.5, 0.5, float("nan")]
        out = apply_rb_committee_scenarios(d)
        budget = float(out["_room_budget"].iloc[0])
        self.assertAlmostEqual(float(out["expected_opportunity_share"].sum()), 1.0, delta=0.02)
        self.assertAlmostEqual(float(out["pts12"].sum()), budget, delta=budget * 0.02)
        self.assertAlmostEqual(float(out.loc[out["contested"], "starter_probability"].sum()), 1.0)
        self.assertEqual(float(out.loc[~out["contested"], "starter_probability"].iloc[0]), 0.0)
        self.assertGreater(float(out.loc[out["name"] == "A", "p90"].iloc[0]),
                           float(out.loc[out["name"] == "A", "p50"].iloc[0]))
        c = out.loc[out["name"] == "C"].iloc[0]
        self.assertGreater(float(c["pts12"]), 0)
        self.assertGreater(float(c["expected_opportunity_share"]), 0)
        if pd.notna(c["p90"]):
            self.assertLess(float(c["p90"]), 0.40 * budget)

    def test_ttu_boise_usc_winner_percentiles(self):
        checks = (
            ("TTU", "Cameron Dickey", "J'Koby Williams", "Quinten Joyner"),
            ("BOIS", "Dylan Riley", "Sire Gaines", "Juelz Goff"),
            ("USC", "Waymond Jordan", "King Miller", None),
        )
        for team, lead, second, third in checks:
            room = self.tuned[(self.tuned["team"] == team) & (self.tuned["position"] == "RB")]
            self.assertGreater(len(room), 2, team)
            budget = float(room["_room_budget"].dropna().iloc[0])
            max_full = float(room["pts_full"].max())
            self.assertNotAlmostEqual(budget, max_full, delta=1.0, msg=f"{team} pool must not be max(pts_full)")
            self.assertAlmostEqual(float(room["expected_opportunity_share"].sum()), 1.0, delta=0.02)
            self.assertAlmostEqual(float(room["pts12"].sum()), budget, delta=budget * 0.02)
            self.assertAlmostEqual(float(room["starter_probability"].sum()), 1.0, delta=0.02)
            a = room[room["name"] == lead].iloc[0]
            b = room[room["name"] == second].iloc[0]
            self.assertGreater(float(a["managed_season_points"]), float(b["managed_season_points"]), team)
            self.assertGreater(float(a["starter_probability"]), float(b["starter_probability"]), team)
            for r in (a, b):
                self.assertAlmostEqual(float(r["p75"]), float(r["p90"]), delta=1, msg=r["name"])
                self.assertGreater(float(r["p90"]), float(r["p50"]) + 5, msg=r["name"])
                self.assertAlmostEqual(float(r["p50"]), float(r["managed_season_points"]),
                                       delta=1.5, msg=r["name"])
            if third:
                t = room[room["name"] == third].iloc[0]
                self.assertGreater(float(t["starter_probability"]), 0.05, third)
                self.assertGreater(float(t["managed_season_points"]), 10, third)

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
