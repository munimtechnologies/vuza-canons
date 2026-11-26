# SPDX-License-Identifier: Apache-2.0
# Tests for phi6close.py (vuza-canons 0.7.0). Made by MV2 of Munim, Inc., with AI agents.
import itertools
import json
import os
import random
import unittest

import phi6close as pc

HERE = os.path.dirname(os.path.abspath(__file__))


class TestArithmetic(unittest.TestCase):
    def test_ks(self):
        self.assertEqual(pc.KS, [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 27, 30, 32,
                                 36, 40, 45, 48, 50, 54, 60])

    def test_exps(self):
        self.assertEqual(pc.exps(1), (2, 2, 1))
        self.assertEqual(pc.exps(30), (3, 3, 2))
        self.assertEqual(pc.exps(40), (5, 2, 2))
        with self.assertRaises(ValueError):
            pc.exps(7)

    def test_cyclotomic(self):
        self.assertEqual(pc.cyclotomic(1), (-1, 1))
        self.assertEqual(pc.cyclotomic(2), (1, 1))
        self.assertEqual(pc.cyclotomic(6), (1, -1, 1))
        self.assertEqual(pc.cyclotomic(12), (1, 0, -1, 0, 1))
        self.assertEqual(pc.cyclotomic(9), (1, 0, 0, 1, 0, 0, 1))
        for n in (8, 24, 30, 54, 105, 150):
            self.assertEqual(len(pc.cyclotomic(n)) - 1,
                             sum(1 for t in range(1, n + 1) if pc.math.gcd(t, n) == 1), n)
        # Phi_105 is the first with a coefficient -2
        self.assertIn(-2, pc.cyclotomic(105))

    def test_phi_divides(self):
        self.assertTrue(pc.phi_divides(6, [0, 2, 4]))
        self.assertTrue(pc.phi_divides(6, [0, 3]))
        self.assertFalse(pc.phi_divides(6, [0, 1]))
        core = [0, 2, 3, 4, 6]
        self.assertTrue(pc.phi_divides(5, core))
        self.assertTrue(pc.phi_divides(6, core))
        self.assertFalse(pc.phi_divides(2, core))
        self.assertFalse(pc.phi_divides(3, core))
        self.assertFalse(pc.phi_divides(10, core))

    def test_periodicity(self):
        self.assertTrue(pc.periodicity(24, 12, {8, 24}))
        self.assertFalse(pc.periodicity(24, 12, {8}))      # order-24 frequencies left alive
        self.assertTrue(pc.periodicity(150, 30, {25, 50, 75, 150}))
        self.assertFalse(pc.periodicity(150, 30, {25, 50, 75}))
        self.assertTrue(pc.periodicity(54, 18, {27, 54}))
        self.assertTrue(pc.periodicity(12, 12, set()))

    def test_profile_counts_match_fold_lemma(self):
        # 0.5.1 fold_lemma.json: 30 admissible mod-30 profiles at k = 6, 450 at k = 30, 0 at k = 10
        self.assertEqual(pc.profile_count(6, False), (30, 6))
        self.assertEqual(pc.profile_count(30, False), (450, 90))
        self.assertEqual(pc.profile_count(10, False)[0], 0)
        self.assertEqual(pc.count_w(30, 5, 5), 5)
        self.assertEqual(pc.count_w(30, 6, 5), 0)
        self.assertEqual(pc.count_w(10, 1, 1), 125)   # C(9,4) - 1 (the constant w = 2)


class TestSources(unittest.TestCase):
    def test_sources(self):
        for name in pc.SOURCE_NAMES:
            rep = pc.source_report(name)
            self.assertEqual(rep["size"], 30, name)
            self.assertTrue(rep["tiling"], name)
            self.assertEqual(rep["S_A"], [4, 5, 9], name)
            self.assertTrue(rep["A_t2"], name)
            self.assertEqual(rep["phi_divides_mod30"],
                             {"2": False, "3": False, "5": True, "6": True,
                              "10": False, "15": False, "30": False}, name)


class TestEngine(unittest.TestCase):
    def test_sound_against_brute_force(self):
        rng = random.Random(20261126)
        ns = [4, 6, 8, 9, 10, 12, 15, 18, 20, 24, 25, 30, 36]
        checked = proved = 0
        for _ in range(300):
            n = rng.choice(ns)
            divs = [d for d in range(1, n + 1) if n % d == 0]
            pts = []
            for _ in range(rng.randint(1, 5)):
                h = rng.choice(divs)
                pts.append((rng.randrange(h), h))
            space = 1
            for _, h in pts:
                space *= n // h
            if space > 1500:
                continue
            ex = pc.excluded(n, pts)
            found = any(pc.phi_divides(n, ys)
                        for ys in itertools.product(*[range(b, n, h) for b, h in pts]))
            if ex:
                self.assertFalse(found, (n, pts))
            checked += 1
            proved += ex
        self.assertGreater(checked, 80)
        self.assertGreater(proved, 5)


class TestRealTilings(unittest.TestCase):
    """Necessary conditions of the proof hold on genuine tilings by random lifts."""

    def test_random_lifts(self):
        rng = random.Random(5400)
        for name in pc.SOURCE_NAMES:
            X, B0 = pc.SOURCES[name]["A"], pc.SOURCES[name]["B"]
            for k in (2, 6, 10):
                M = 180 * k
                A = [x + 180 * rng.randrange(k) for x in X]
                B = [b + 180 * j for b in B0 for j in range(k)]
                self.assertTrue(pc.is_tiling(A, B, M), (name, k))
                a, b, e = pc.exps(k)
                for fam in pc.needed_orders(k).values():
                    for N in fam:
                        self.assertTrue(pc.phi_divides(N, B), (name, k, N))
                        if not pc.is_prime_power(N):
                            self.assertFalse(pc.phi_divides(N, A), (name, k, N))
                self.assertTrue(pc.phi_divides(6, B))
                self.assertTrue(all(c % 2 ** (a - 2) == 0 for c in pc.fold(B, 12)))
                self.assertTrue(all(c % 3 ** (b - 2) == 0 for c in pc.fold(B, 18)))
                self.assertTrue(all(c % 5 ** (e - 1) == 0 for c in pc.fold(B, 30)))


class TestTheorem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = pc.compute()
        with open(os.path.join(HERE, "phi6_close.json")) as f:
            cls.ref = json.load(f)

    def test_summary_matches_committed(self):
        self.assertEqual(self.doc["summary"], self.ref["summary"])

    def test_named_periods(self):
        for k, want in self.ref["named_periods"].items():
            row = self.doc["table"][k]
            for key, value in want.items():
                self.assertEqual(row[key], value, (k, key))

    def test_every_period_forced(self):
        for row in self.doc["table"].values():
            self.assertTrue(row["phi6_forced"], row["k"])
            for name in pc.SOURCE_NAMES:
                self.assertNotIn("not_excluded", row["status"][name].values(), (name, row["k"]))
                self.assertNotIn("in_S_A", row["status"][name].values(), (name, row["k"]))


if __name__ == "__main__":
    unittest.main()
