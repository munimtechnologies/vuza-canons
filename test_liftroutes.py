# SPDX-License-Identifier: Apache-2.0
# Tests for liftroutes.py (vuza-canons 0.6.0). Made by MV2 of Munim, Inc., with AI agents.
import itertools
import json
import os
import random
import unittest

import liftroutes as lr

HERE = os.path.dirname(os.path.abspath(__file__))


class TestBasics(unittest.TestCase):
    def test_ks(self):
        self.assertEqual(lr.KS, [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 27, 30, 32,
                                 36, 40, 45, 48, 50, 54, 60])

    def test_t2_products(self):
        self.assertEqual(lr.t2_products([2, 8, 3, 25]), [6, 24, 50, 75, 150, 200, 600])
        self.assertEqual(lr.t2_products([4, 5, 9]), [20, 36, 45, 180])

    def test_kprime(self):
        self.assertEqual([lr.kprime(k) for k in (10, 15, 20, 25, 30, 40, 45, 50, 60)],
                         [2, 3, 4, 1, 6, 8, 9, 2, 12])

    def test_vanishing(self):
        self.assertTrue(lr.vanishes_residues([0, 2, 4], 6))
        self.assertTrue(lr.vanishes_residues([0, 3], 6))
        self.assertFalse(lr.vanishes_residues([0, 1], 6))
        # Phi_5 Phi_6 = 1 + x^2 + x^3 + x^4 + x^6 vanishes at order 5 and 6, not 2 or 3
        core = [0, 2, 3, 4, 6]
        self.assertTrue(lr.vanishes_residues(core, 5))
        self.assertTrue(lr.vanishes_residues(core, 6))
        self.assertFalse(lr.vanishes_residues(core, 2))
        self.assertFalse(lr.vanishes_residues(core, 3))

    def test_semigroup(self):
        self.assertFalse(lr.in_semigroup(1, (2, 3)))
        self.assertTrue(lr.in_semigroup(5, (2, 3)))
        self.assertFalse(lr.in_semigroup(3, (2, 5)))
        self.assertFalse(lr.in_semigroup(6, (5,)))
        self.assertTrue(lr.in_semigroup(0, (5,)))


class TestSources(unittest.TestCase):
    def test_sources(self):
        for name in lr.SOURCE_NAMES:
            rep = lr.source_report(name)
            self.assertEqual(rep["size"], 30)
            self.assertTrue(rep["tiling"], name)
            self.assertEqual(rep["S_A"], [4, 5, 9], name)
            self.assertTrue(rep["t1"], name)
            self.assertEqual(rep["A_t2_products"], [20, 36, 45, 180])
            self.assertTrue(rep["A_satisfies_T2"], name)
            self.assertTrue(rep["phi6_divides"], name)

    def test_class_four_mod_five(self):
        # the proof uses: the class 4 mod 5 of both tiles is 4 + 30*{0..5}
        for name in lr.SOURCE_NAMES:
            cls = sorted(x for x in lr.SOURCES[name]["A"] if x % 5 == 4)
            self.assertEqual(cls, [4, 34, 64, 94, 124, 154], name)

    def test_odd_points(self):
        # the proof uses the odd points that are 1 mod 4 (C180) or 3 mod 4 (S180)
        c = sorted(x for x in lr.SOURCES["C180"]["A"] if x % 4 == 1)
        s = sorted(x for x in lr.SOURCES["S180"]["A"] if x % 4 == 3)
        self.assertEqual(c, [21, 141, 165])
        self.assertEqual(s, [3, 63, 123])


class TestEngine(unittest.TestCase):
    def test_simple_cases(self):
        self.assertFalse(lr.excluded(6, [(0, 6), (2, 6), (4, 6)]))  # a 3-cycle
        self.assertTrue(lr.excluded(6, [(0, 3), (0, 3), (0, 3)]))   # same residue mod 3
        self.assertFalse(lr.excluded(6, [(0, 3), (1, 3), (2, 3)]))
        self.assertTrue(lr.excluded(10, [(0, 2)] * 6))               # 6 points, one parity
        self.assertTrue(lr.excluded(7, [(0, 1)]))                    # one point never vanishes
        self.assertFalse(lr.excluded(12, []))

    def test_sound_against_brute_force(self):
        rng = random.Random(20261120)
        ns = [4, 6, 8, 9, 10, 12, 15, 18, 20, 24, 25, 30, 36]
        checked = proved = 0
        for _ in range(400):
            n = rng.choice(ns)
            divs = [d for d in range(1, n + 1) if n % d == 0]
            pts = []
            for _ in range(rng.randint(1, 5)):
                h = rng.choice(divs)
                pts.append((rng.randrange(h), h))
            space = 1
            for _, h in pts:
                space *= n // h
            if space > 2000:
                continue
            ex = lr.excluded(n, pts)
            found = any(lr.vanishes_residues(ys, n)
                        for ys in itertools.product(*[range(b, n, h) for b, h in pts]))
            if ex:
                self.assertFalse(found, (n, pts))
            checked += 1
            proved += ex
        self.assertGreater(checked, 100)
        self.assertGreater(proved, 10)


class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = lr.compute()
        with open(os.path.join(HERE, "lift_routes.json")) as f:
            cls.ref = json.load(f)

    def test_summary_matches_committed(self):
        self.assertEqual(self.doc["summary"], self.ref["summary"])

    def test_named_periods(self):
        for name in lr.SOURCE_NAMES:
            for M, routes in self.ref["named_periods"].items():
                self.assertEqual(self.doc["table"][name][M]["routes"], routes, (name, M))
                n_ex = sum(1 for v in routes.values() if v.startswith("excluded"))
                self.assertEqual(self.ref["named_period_route_counts"][M], {"routes": len(routes), "excluded": n_ex})

    def test_no_route_left_unproved(self):
        for name in lr.SOURCE_NAMES:
            for row in self.doc["table"][name].values():
                self.assertNotIn("not_excluded", row["routes"].values(), (name, row["M"]))
                self.assertEqual(row["S_A"], [4, 5, 9])


if __name__ == "__main__":
    unittest.main()
