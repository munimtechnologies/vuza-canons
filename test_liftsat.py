# SPDX-License-Identifier: Apache-2.0
# Tests for liftsat.py (pure Python; the CP-SAT solver is not needed).
# Made by MV2 of Munim, Inc., with AI agents. Licensed under the Apache License 2.0.
import unittest

import liftsat as L


def cfg(name):
    return next(L.config_dict(r) for r in L.CONFIGS if r[0] == name)


class TestSources(unittest.TestCase):
    def test_s180_is_the_apery_tile(self):
        S = L.SOURCES["S180"]["A"]
        self.assertEqual(len(set(S)), 30)
        self.assertTrue(L.is_tiling(S, L.SOURCES["S180"]["B"], 180))

    def test_c180_tiles(self):
        C, D = L.SOURCES["C180"]["A"], L.SOURCES["C180"]["B"]
        self.assertEqual(len(set(C)), 30)
        self.assertEqual(len(set(D)), 6)
        self.assertTrue(L.is_tiling(C, D, 180))

    def test_core_mask_is_phi5_phi6(self):
        core = [0] * 7
        for c in L.C5:
            core[c] = 1
        five_six = [0] * 7
        for i, a in enumerate(L.cyclotomic(5)):
            for j, b in enumerate(L.cyclotomic(6)):
                five_six[i + j] += a * b
        self.assertEqual(core, five_six)

    def test_two_exact_tests_agree(self):
        for name in ("S180", "C180"):
            X = L.SOURCES[name]["A"]
            for d in L.divisors(180):
                if d > 1:
                    self.assertEqual(L.vanishes_rows(X, d), L.vanishes_numeric(X, d), (name, d))

    def test_signature_and_unsupported(self):
        S = L.SOURCES["S180"]["A"]
        self.assertEqual([q for q in L.all_prime_powers(180) if L.vanishes_rows(S, q)], [4, 5, 9])
        self.assertEqual(L.unsupported_orders(S, 180), [6])
        self.assertIn(6, L.unsupported_orders(L.SOURCES["C180"]["A"], 180))

    def test_source_reports_ok(self):
        for name in ("S180", "C180"):
            rep = L.source_report(name)
            self.assertTrue(rep["tiling"], name)
            self.assertTrue(rep["A"]["t1"], name)
            self.assertEqual(rep["A"]["t2_failures"], [], name)
            self.assertTrue(rep["ok"], name)


class TestPlan(unittest.TestCase):
    def test_config_periods(self):
        self.assertEqual(cfg("S180-k10")["M"], 1800)
        self.assertEqual(cfg("S180-k15")["M"], 2700)
        self.assertEqual(cfg("S180-k20")["M"], 3600)
        self.assertEqual(cfg("S180-q5k2")["M"], 1800)
        self.assertEqual(cfg("S180-q2k5")["M"], 1800)
        for r in L.CONFIGS:
            c = L.config_dict(r)
            self.assertEqual(c["M"] % 30, 0)
            self.assertEqual(c["label"] == "open", c["k"] >= 10 and c["q"] == 1)

    def test_lift_x10_cases(self):
        cs = L.config_cases(cfg("S180-k10"))
        tiles = [c for c in cs if c["mode"] == "tile"]
        self.assertEqual([t["SA"] for t in tiles], [[4, 5, 9]])
        self.assertEqual(tiles[0]["SB"], [2, 3, 8, 25])
        todo = [(c["side"], c["s"]) for c in cs if c["mode"] == "t2" and not c["decided"]]
        self.assertEqual(todo, [("B", s) for s in (6, 24, 50, 75, 150, 200, 600)])
        decided = sorted(c["s"] for c in cs if c["mode"] == "t2" and c["decided"])
        self.assertEqual(decided, [20, 36, 45, 180])

    def test_dilated_lift_cases(self):
        cs = L.config_cases(cfg("S180-q5k2"))
        tiles = [c for c in cs if c["mode"] == "tile"]
        self.assertEqual([t["SA"] for t in tiles], [[4, 9, 25]])
        todo = [(c["side"], c["s"]) for c in cs if c["mode"] == "t2" and not c["decided"]]
        self.assertEqual(todo, [("B", s) for s in (6, 24, 30, 40, 120)])

    def test_every_config_has_a_profile(self):
        for r in L.CONFIGS:
            cs = L.config_cases(L.config_dict(r))
            self.assertTrue(any(c["mode"] == "tile" for c in cs), r[0])


class TestVerify(unittest.TestCase):
    def test_trivial_lift_verifies(self):
        c = cfg("S180-k10")
        case = [x for x in L.config_cases(c) if x["mode"] == "tile"][0]
        A = L.base_set(c)
        B = sorted(b + 180 * i for b in L.SOURCES["S180"]["B"] for i in range(10))
        chk = L.verify(case, A, A, B)
        self.assertTrue(chk["verified"], chk["errors"])

    def test_wrong_lift_rejected(self):
        c = cfg("S180-k10")
        case = [x for x in L.config_cases(c) if x["mode"] == "tile"][0]
        A = L.base_set(c)
        bad = [1] + A[1:]
        B = sorted(b + 180 * i for b in L.SOURCES["S180"]["B"] for i in range(10))
        self.assertFalse(L.verify(case, A, bad, B)["verified"])


if __name__ == "__main__":
    unittest.main()
