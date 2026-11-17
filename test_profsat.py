# SPDX-License-Identifier: Apache-2.0
# Tests for profsat.py (pure Python; the CP-SAT solver itself is not needed).
# Made by MV2 of Munim, Inc., with AI agents. Licensed under the Apache License 2.0.
import unittest

import profsat as ps


def lcg_set(seed, M, k):
    s = seed
    out = set()
    while len(out) < k:
        s = (1103515245 * s + 12345) % (2 ** 31)
        out.add(s % M)
    return sorted(out)


class TestArithmetic(unittest.TestCase):
    def test_basics(self):
        self.assertEqual(ps.factorize(1800), {2: 3, 3: 2, 5: 2})
        self.assertEqual(ps.rad(1800), 30)
        self.assertEqual(ps.euler_phi(1800), 480)
        self.assertEqual(ps.prime_of(25), 5)
        self.assertEqual(len(ps.mixed_divisors(1800)), 28)
        self.assertEqual(ps.all_prime_powers(1800), [2, 3, 4, 5, 8, 9, 25])

    def test_rem_table_small(self):
        self.assertEqual(ps.rem_table(2), [[1], [-1]])
        self.assertEqual(ps.rem_table(3), [[1, 0], [0, 1], [-1, -1]])
        self.assertEqual(ps.rem_table(6), [[1, 0], [0, 1], [-1, 1], [-1, 0], [0, -1], [1, -1]])

    def test_cyclotomic_substitution(self):
        # Phi_d(x) = Phi_rad(d)(x^(d/rad(d))), the identity behind vanish_rows.
        for d in (4, 8, 9, 12, 18, 20, 24, 25, 36, 40, 50, 60, 72):
            m = ps.rad(d)
            k = d // m
            base = ps.cyclotomic(m)
            sub = [0] * (k * (len(base) - 1) + 1)
            for i, v in enumerate(base):
                sub[k * i] = v
            self.assertEqual(ps.cyclotomic(d), sub, d)

    def test_row_count_is_phi(self):
        for d in ps.divisors(1800)[1:]:
            self.assertEqual(len(ps.vanish_rows(d)), ps.euler_phi(d), d)


class TestVanishing(unittest.TestCase):
    def test_small(self):
        self.assertFalse(ps.vanishes_rows([0, 1, 3], 6))
        self.assertTrue(ps.vanishes_rows(range(6), 6))
        self.assertTrue(ps.vanishes_rows([0, 1], 2))
        self.assertTrue(ps.vanishes_rows([0, 3], 6))
        self.assertFalse(ps.vanishes_numeric([0, 1, 3], 6))
        self.assertTrue(ps.vanishes_numeric([0, 3], 6))

    def test_rows_match_numeric(self):
        M = 360
        sets = [ps.standard_set(S, M) for S in ps.profiles(M, 30)]
        sets += [ps.standard_set(S, M) for S in ps.profiles(M, 12)]
        sets += [lcg_set(seed, M, k) for seed, k in ((1, 30), (2, 12), (3, 60), (4, 7))]
        sets.append(list(range(0, M, 6)))
        positives = 0
        for X in sets:
            for d in ps.divisors(M)[1:]:
                r = ps.vanishes_rows(X, d)
                self.assertEqual(r, ps.vanishes_numeric(X, d), (X[:6], d))
                positives += r
        self.assertGreater(positives, 50)

    def test_residue_tree(self):
        for M, k in ((360, 30), (1800, 60)):
            X = lcg_set(7, M, k)
            tree = ps.residue_tree(X, M)
            for d in ps.divisors(M)[1:]:
                self.assertEqual(tree[d], ps.residues(X, d), (M, d))


class TestProfiles(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(ps.profiles(1800, 30)), 12)
        self.assertEqual(len(ps.profiles(900, 30)), 8)
        self.assertEqual(len(ps.profiles(360, 30)), 6)
        self.assertEqual(len(ps.profiles(360, 12)), 6)
        self.assertEqual(len(ps.cases(1800, 30)), 132)
        self.assertEqual(len(ps.cases(900, 30)), 64)
        self.assertEqual(len(ps.cases(360, 30)), 36)

    def test_t2_products(self):
        self.assertEqual(ps.t2_products((2, 3, 5)), [6, 10, 15, 30])
        self.assertEqual(ps.t2_products((4, 8, 9, 25)), [36, 72, 100, 200, 225, 900, 1800])
        self.assertEqual(ps.t2_products((8,)), [])

    def test_complement(self):
        self.assertEqual(ps.complement_profile(1800, (2, 3, 5)), (4, 8, 9, 25))

    def test_standard_sets_tile_and_satisfy_t2(self):
        for M, a in ((360, 30), (900, 30), (1800, 30)):
            for SA in ps.profiles(M, a):
                SB = ps.complement_profile(M, SA)
                A, B = ps.standard_set(SA, M), ps.standard_set(SB, M)
                self.assertEqual(len(set(A)), a)
                self.assertEqual(len(set(B)), M // a)
                self.assertTrue(ps.is_tiling(A, B, M), (M, SA))
                for q in SA:
                    self.assertTrue(ps.vanishes_rows(A, q))
                for q in SB:
                    self.assertTrue(ps.vanishes_rows(B, q))
                for s in ps.t2_products(SA):
                    self.assertTrue(ps.vanishes_rows(A, s))
                for s in ps.t2_products(SB):
                    self.assertTrue(ps.vanishes_rows(B, s))

    def test_check_sets(self):
        M, a = 360, 30
        SA = ps.profiles(M, a)[0]
        case = ps.make_case(M, a, SA)
        sets = {"A": ps.standard_set(case["SA"], M), "B": ps.standard_set(case["SB"], M)}
        self.assertTrue(ps.check_sets(case, sets, "tile")["verified"])
        s = ps.t2_products(case["SA"])[0]
        bad = ps.make_case(M, a, SA, "A", s)
        chk = ps.check_sets(bad, sets, "t2")  # standard sets satisfy T2, so this must fail
        self.assertFalse(chk["verified"])
        self.assertTrue(chk["s_vanishes_rows"])
        broken = {"A": sets["A"], "B": sorted(set(sets["B"][:-1]) | {1})}
        self.assertFalse(ps.check_sets(case, broken, "tile")["verified"])

    def test_t2_report_standard(self):
        M = 900
        A = ps.standard_set((2, 9, 5), M)
        rep = ps.t2_report(A, M)
        self.assertEqual(rep["S"], [2, 5, 9])
        self.assertTrue(rep["t1"])
        self.assertEqual(rep["t2_failures"], [])
        self.assertTrue(rep["S_numeric_agrees"])

    def test_validation_periods_match_t2open(self):
        try:
            import t2open
        except Exception:
            self.skipTest("t2open.py not present")
        self.assertTrue(t2open.known_for_sizes(360, 30, 12))
        self.assertTrue(t2open.known_for_sizes(900, 30, 30))
        self.assertFalse(t2open.known_for_sizes(1800, 30, 60))
        for (M, a) in ps.KNOWN_BY_THEOREM:
            self.assertTrue(t2open.known_for_sizes(M, a, M // a))


if __name__ == "__main__":
    unittest.main()
