# SPDX-License-Identifier: Apache-2.0
# Tests for aperylifts.py (vuza-canons 0.8.0). Made by MV2 of Munim, Inc., with AI agents.
import json
import os
import random
import unittest

import aperylifts as al

HERE = os.path.dirname(os.path.abspath(__file__))

S180 = sorted(30 * j + c for j in range(6) for c in (0, 2, 3, 4, 6))


class TestBasics(unittest.TestCase):
    def test_semigroup(self):
        self.assertTrue(al.in_semigroup2(0, 2, 3))
        self.assertFalse(al.in_semigroup2(1, 2, 3))
        self.assertTrue(al.in_semigroup2(7, 2, 5))
        self.assertFalse(al.in_semigroup2(3, 2, 5))
        self.assertFalse(al.in_semigroup2(7, 3, 5))

    def test_apery(self):
        self.assertEqual(al.apery_set(2, 3, 5), [0, 2, 3, 4, 6])
        self.assertEqual(al.apery_set(2, 3, 7), [0, 2, 3, 4, 5, 6, 8])
        self.assertEqual(al.apery_set(2, 5, 7), [0, 2, 4, 5, 6, 8, 10])
        for r in (5, 7, 11, 13, 17, 19, 23):
            self.assertEqual(al.apery_set(2, 3, r), [n for n in range(r + 2) if n not in (1, r)])
        with self.assertRaises(ValueError):
            al.apery_set(3, 5, 7)   # 7 is not in <3, 5>

    def test_tile_is_s180(self):
        X, B0, M0 = al.tile(2, 3, 5)
        self.assertEqual(X, S180)
        self.assertEqual(B0, [0, 5, 10, 15, 20, 25])
        self.assertEqual(M0, 180)

    def test_cyclotomic(self):
        self.assertEqual(al.cyclotomic(6), (1, -1, 1))
        self.assertEqual(al.cyclotomic(10), (1, -1, 1, -1, 1))
        self.assertIn(-2, al.cyclotomic(105))

    def test_closed_form(self):
        self.assertEqual(al.closed_form_23(5), [[2, 1, 1], [1, 0, 0]])
        self.assertEqual(al.closed_form_23(7), [[2, 1, 2], [1, 0, 1]])
        self.assertEqual(al.closed_form_23(17), [[4, 3, 3], [3, 2, 2]])

    def test_compositions(self):
        self.assertEqual(len(list(al.compositions(3, 2))), 4)
        self.assertEqual(len(list(al.compositions(2, 6))), 21)
        self.assertEqual(list(al.compositions(0, 3)), [(0, 0, 0)])

    def test_class_can_vanish(self):
        # two points at t = 0, free mod 2, in Z_6: 1 + zeta^3 = 0
        self.assertTrue(al.class_can_vanish([2, 0, 0], 2, 3))
        self.assertTrue(al.class_can_vanish([1, 1, 1], 2, 3))
        self.assertTrue(al.class_can_vanish([3, 1, 1], 2, 3))
        self.assertFalse(al.class_can_vanish([1, 0, 0], 2, 3))
        self.assertFalse(al.class_can_vanish([6, 3, 3], 2, 3))
        # free points in Z_6: sizes in <2, 3> vanish, size 1 does not
        self.assertTrue(al.class_can_vanish([2], 6, 1))
        self.assertTrue(al.class_can_vanish([3], 6, 1))
        self.assertFalse(al.class_can_vanish([1], 6, 1))
        # free points in Z_10: 1 and 3 are not in <2, 5>
        self.assertFalse(al.class_can_vanish([3], 10, 1))
        self.assertTrue(al.class_can_vanish([5], 10, 1))


class TestRandomLifts(unittest.TestCase):
    """Closed routes stay closed on random lifts of genuine tilings."""

    def test_237_at_k42(self):
        rng = random.Random(20261128)
        X, B0, M0 = al.tile(2, 3, 7)
        k = 42                         # M = 10584 = 2^3 3^3 7^2: every route family occurs
        M = M0 * k
        B = [b + M0 * i for b in B0 for i in range(k)]
        routes = [24, 54, 216, 98, 147, 294, 392, 1176, 1323]
        for _ in range(3):
            A = [x + M0 * rng.randrange(k) for x in X]
            self.assertTrue(al.is_tiling(A, B, M))
            for N in routes:
                self.assertFalse(al.phi_divides(N, A), N)
            self.assertTrue(al.phi_divides(6, A))     # the unsupported divisor itself

    def test_2317_closed_families(self):
        rng = random.Random(3672)
        X, B0, M0 = al.tile(2, 3, 17)
        for _ in range(3):
            A = [x + M0 * rng.randrange(6) for x in X]
            for N in (24, 54):                        # C1 and C2 hold for r = 17
                self.assertFalse(al.phi_divides(N, A), N)


class TestResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(json.dumps(al.compute()))
        with open(os.path.join(HERE, "aperylifts.json")) as f:
            cls.ref = json.load(f)

    def test_summary(self):
        self.assertEqual(self.doc["summary"], self.ref["summary"])

    def test_family(self):
        self.assertEqual(self.doc["family_23"], self.ref["family_23"])

    def test_triples(self):
        for k, want in self.ref["triples"].items():
            for field, value in want.items():
                self.assertEqual(self.doc["triples"][k][field], value, (k, field))

    def test_version(self):
        self.assertEqual(self.doc["version"], self.ref["version"])


if __name__ == "__main__":
    unittest.main()
