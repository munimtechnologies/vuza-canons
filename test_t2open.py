# SPDX-License-Identifier: Apache-2.0
# Tests for t2open.py. Made by MV2 of Munim, Inc., with AI agents.
import unittest

import t2open


class T2OpenTests(unittest.TestCase):
    def test_rad_D(self):
        self.assertEqual(t2open.rad(1), 1)
        self.assertEqual(t2open.rad(72), 6)
        self.assertEqual(t2open.D(72), 12)
        self.assertEqual(t2open.D(225), 15)
        self.assertEqual(t2open.D(900), 30)

    def test_known_periods(self):
        # two primes (CM), at most one prime with exponent >= 2 (LL6), p^2q^2r^2 (LL3)
        for M in (72, 108, 120, 144, 168, 180, 360, 420, 504, 540, 600, 630, 660, 840, 900, 924,
                  1764, 4356, 4900, 6300):
            self.assertTrue(t2open.known_all(M), M)

    def test_open_periods(self):
        self.assertEqual(t2open.open_periods(1799), [])
        self.assertEqual(t2open.open_periods(5000), [1800, 2700, 3528, 3600, 4500])

    def test_splitting(self):
        # 2^3 3^2 13^2: 13 > D(72) = 12, so Theorem 1.2 covers it
        self.assertTrue(t2open.known_all(12168))
        # 2^3 3^2 11^2: 11 < 12, 3 < D(968) = 44, 2 < D(1089) = 33
        self.assertFalse(t2open.known_all(8712))
        # 2^2 3^2 5^2 7^2: every triple is p^2q^2r^2, but 7 < D(900) = 30
        self.assertFalse(t2open.known_all(44100))
        # 2^2 3^2 5^2 37^2: 37 > 30
        self.assertTrue(t2open.known_all(1232100))

    def test_sizes(self):
        self.assertTrue(t2open.known_for_sizes(420, 12, 35))
        self.assertTrue(t2open.known_for_sizes(1800, 20, 90))
        self.assertFalse(t2open.known_for_sizes(1800, 30, 60))
        self.assertEqual(t2open.shared_part(1800, 30, 60), 1800)
        self.assertEqual(t2open.shared_part(1800, 20, 90), 200)
        self.assertEqual(t2open.open_size_pairs(1800), [(30, 60), (60, 30)])
        self.assertEqual(t2open.open_size_pairs(420), [])
        with self.assertRaises(ValueError):
            t2open.known_for_sizes(1800, 30, 30)


if __name__ == "__main__":
    unittest.main()
