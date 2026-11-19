# SPDX-License-Identifier: Apache-2.0
# Tests for foldlemma.py (vuza-canons 0.5.1). Made by MV2 of Munim, Inc., with AI agents.
import json
import os
import unittest

import foldlemma as fl

HERE = os.path.dirname(os.path.abspath(__file__))


class TestArithmetic(unittest.TestCase):
    def test_cyclotomic(self):
        self.assertEqual(fl.cyclotomic(1), [-1, 1])
        self.assertEqual(fl.cyclotomic(5), [1, 1, 1, 1, 1])
        self.assertEqual(fl.cyclotomic(6), [1, -1, 1])
        self.assertEqual(fl.cyclotomic(10), [1, -1, 1, -1, 1])

    def test_E_is_phi5_phi6(self):
        e = fl.fold(fl.E, 30)
        self.assertTrue(fl.phi_divides(e, 5))
        self.assertTrue(fl.phi_divides(e, 6))
        for d in (2, 3, 10, 15, 30):
            self.assertFalse(fl.phi_divides(e, d))

    def test_vp(self):
        self.assertEqual(fl.vp(1800, 5), 2)
        self.assertEqual(fl.vp(4500, 5), 3)
        self.assertEqual(fl.vp(1080, 5), 1)


class TestHypotheses(unittest.TestCase):
    def test_sources_tile(self):
        for n in fl.SOURCES:
            self.assertTrue(fl.is_tiling(fl.SOURCES[n], fl.COMPLEMENTS[n], 180), n)
            self.assertEqual(len(set(fl.SOURCES[n])), 30)

    def test_hypotheses_hold(self):
        for n, xs in fl.SOURCES.items():
            self.assertTrue(fl.hypotheses(xs)["ok"], n)

    def test_lift_keeps_hypotheses(self):
        # moving points by multiples of 180 never changes the fold mod 30
        xs = fl.SOURCES["C180"]
        lifted = [x + 180 * ((7 * i) % 10) for i, x in enumerate(xs)]
        self.assertEqual(fl.fold(lifted, 30), fl.fold(xs, 30))
        self.assertTrue(fl.hypotheses(lifted)["ok"])

    def test_kernel_is_u_plus_v(self):
        for n, xs in fl.SOURCES.items():
            r = fl.kernel_report(xs)
            self.assertEqual(r["kernel_dim"], 6, n)
            self.assertTrue(r["ok"], n)


class TestProfiles(unittest.TestCase):
    def test_none_at_open_lift_periods(self):
        for k in (1, 2, 3, 4, 5, 10, 15, 20, 25):
            self.assertEqual(fl.admissible_profiles(k), [], k)

    def test_k6(self):
        profs = fl.admissible_profiles(6)
        self.assertEqual(len(profs), 30)
        self.assertTrue(fl.check_profiles(6, profs))

    def test_five_adic_step_matters(self):
        # without step 5 the fold mod 30 alone would allow 750 profiles at M = 1800
        profs = fl.admissible_profiles(10, five_adic=False)
        self.assertEqual(len(profs), 750)
        self.assertTrue(fl.check_profiles(10, profs))

    def test_results_file_matches(self):
        with open(os.path.join(HERE, "fold_lemma.json")) as f:
            saved = json.load(f)
        self.assertEqual(fl.compute(), saved)


if __name__ == "__main__":
    unittest.main()
