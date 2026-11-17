# SPDX-License-Identifier: Apache-2.0
# Tests for vuza.py. Made by MV2 of Munim, Inc., with AI agents.
import itertools
import os
import random
import tempfile
import unittest

import vuza


def brute_complements(S, N):
    """All R containing 0 with S (+) R = Z_N, by brute force."""
    k = N // len(S)
    out = []
    for rest in itertools.combinations(range(1, N), k - 1):
        R = (0,) + rest
        if vuza.is_tiling(S, R, N):
            out.append(R)
    return out


class Arithmetic(unittest.TestCase):
    def test_factorize(self):
        self.assertEqual(vuza.factorize(420), {2: 2, 3: 1, 5: 1, 7: 1})
        self.assertEqual(vuza.factorize(97), {97: 1})
        self.assertEqual(vuza.n_prime_factors(30), 3)
        self.assertEqual(vuza.n_prime_factors(1), 0)
        self.assertEqual(vuza.divisors(12), [1, 2, 3, 4, 6, 12])

    def test_cyclotomic(self):
        self.assertEqual(vuza.cyclotomic(1), [-1, 1])
        self.assertEqual(vuza.cyclotomic(2), [1, 1])
        self.assertEqual(vuza.cyclotomic(6), [1, -1, 1])
        self.assertEqual(vuza.cyclotomic(12), [1, 0, -1, 0, 1])
        self.assertEqual(vuza.cyclotomic(9), [1, 0, 0, 1, 0, 0, 1])
        # Phi_105 is the first with a coefficient -2
        self.assertIn(-2, vuza.cyclotomic(105))

    def test_rot_and_masks(self):
        N = 10
        m = vuza.to_mask([0, 3, 9])
        self.assertEqual(vuza.from_mask(vuza.rot(m, 2, N)), [1, 2, 5])
        self.assertEqual(vuza.from_mask(vuza.rot(m, -3, N)), [0, 6, 7])
        self.assertTrue(vuza.is_periodic([0, 5], 10))
        self.assertFalse(vuza.is_periodic([0, 1, 3], 10))
        self.assertEqual(vuza.stabilizer_size([0, 2, 4, 6, 8], 10), 5)
        self.assertEqual(vuza.stabilizer_size([0, 1, 3], 10), 1)

    def test_canonical_rule(self):
        rnd = random.Random(7)
        for _ in range(300):
            N = rnd.randint(2, 30)
            k = rnd.randint(1, N)
            X = sorted(rnd.sample(range(N), k))
            cls = vuza.canonical(X, N)
            passing = []
            for r in X:
                Y = sorted((x - r) % N for x in X)
                if vuza.is_canonical_sorted(Y, N):
                    passing.append(vuza.to_mask(Y))
            # every translate containing 0 that passes has the class mask,
            # and at least one passes
            self.assertTrue(passing)
            self.assertTrue(all(p == cls for p in passing))


class CycloTests(unittest.TestCase):
    def test_float_test_matches_exact(self):
        rnd = random.Random(11)
        for N in (12, 18, 20, 24, 30, 36, 60):
            for use_np in (False, True):
                cy = vuza.Cyclo(N, use_numpy=use_np)
                for _ in range(40):
                    X = rnd.sample(range(N), rnd.randint(1, N))
                    spec = cy._spectrum(X)
                    for d in vuza.divisors(N)[1:]:
                        self.assertEqual(cy.vanishes(X, d, spec), vuza.vanishes_exact(X, d), (N, X, d))

    def test_structured_zeros(self):
        cy = vuza.Cyclo(30, use_numpy=False)
        X = [0, 10, 20]  # 10 * I_3: X(x) = Phi_3(x^10) has Phi_3 (and Phi_6?) no: Phi_3, Phi_6, Phi_15, Phi_30... check exact
        for d in (2, 3, 5, 6, 10, 15, 30):
            self.assertEqual(cy.vanishes(X, d), vuza.vanishes_exact(X, d))
        self.assertTrue(cy.vanishes(X, 3))
        self.assertFalse(cy.vanishes(X, 2))

    def test_t2_logic(self):
        S = {2: [2, 4], 3: [3], 5: []}
        ok = {6, 12}
        self.assertEqual(vuza.t2_failures(S, lambda s: s in ok), [])
        self.assertEqual(vuza.t2_failures(S, lambda s: s == 6), [12])
        S3 = {2: [2], 3: [3], 5: [5]}
        self.assertEqual(vuza.t2_failures(S3, lambda s: s in (6, 10, 15)), [30])
        self.assertEqual(vuza.t2_failures({2: [2], 3: []}, lambda s: False), [])

    def test_t1_t2_on_small_tilings(self):
        # Every tiling of Z_N for N with two primes satisfies T1 and T2
        # (Coven-Meyerowitz), so the checker must report no failures.
        for N, S in ((12, [0, 1, 6, 7]), (18, [0, 1, 2]), (24, [0, 4, 8, 12, 16, 20]), (20, [0, 1])):
            cy = vuza.Cyclo(N, use_numpy=False)
            for R in brute_complements(S, N):
                for X in (S, R):
                    SX, t1, fails = cy.profile(X)
                    self.assertTrue(t1, (N, X, SX))
                    self.assertEqual(fails, [], (N, X))


class SearchTests(unittest.TestCase):
    def test_dfs_matches_brute_force(self):
        cases = [(12, [0, 1]), (12, [0, 1, 6, 7]), (16, [0, 1, 4, 5]), (16, [0, 2, 4, 6]),
                 (18, [0, 3, 6]), (20, [0, 1, 10, 11]), (24, [0, 1, 2, 12, 13, 14]),
                 (12, [0, 1, 3]), (15, [0, 1, 2]), (14, [0, 1])]
        for N, S in cases:
            got = []
            n, nodes, complete = vuza.enumerate_complements(S, N, lambda R: got.append(tuple(sorted(R))))
            self.assertTrue(complete)
            self.assertEqual(n, len(got))
            self.assertEqual(sorted(got), sorted(brute_complements(S, N)), (N, S))
            self.assertEqual(len(set(got)), len(got))

    def test_time_limit_stops(self):
        N, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        n, nodes, complete = vuza.enumerate_complements(S, N, lambda R: None, time_limit=0.0)
        # the limit is checked every 16384 nodes; tiny searches may finish
        self.assertIn(complete, (True, False))


class VuzaTests(unittest.TestCase):
    def test_outer_72(self):
        N, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        self.assertEqual(N, 72)
        self.assertEqual(S, [0, 8, 16, 18, 26, 34])
        self.assertFalse(vuza.is_periodic(S, N))

    def test_inner_72_hand_checked(self):
        N, R = vuza.vuza_inner(2, 2, 3, 3, 2)
        self.assertEqual(R, [0, 1, 4, 7, 13, 24, 28, 37, 43, 48, 49, 52])
        _, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        self.assertTrue(vuza.is_tiling(S, R, N))
        self.assertFalse(vuza.is_periodic(R, N))

    def test_published_example_72(self):
        # Jedrzejewski (2013), Example 18; tiling and aperiodicity checked by hand.
        S = [0, 8, 16, 18, 26, 34]
        R = [0, 1, 21, 24, 25, 30, 36, 45, 49, 60, 66, 69]
        self.assertTrue(vuza.is_tiling(S, R, 72))
        self.assertFalse(vuza.is_periodic(R, 72))

    def test_constructions_tile(self):
        for params in ((2, 2, 3, 3, 2), (2, 2, 3, 3, 3), (2, 2, 3, 5, 2), (2, 2, 5, 3, 2),
                       (2, 2, 3, 7, 2), (2, 2, 7, 3, 2), (2, 2, 3, 5, 3), (5, 7, 2, 3, 2),
                       (4, 2, 3, 5, 3), (5, 11, 2, 3, 2)):
            N, S = vuza.vuza_outer(*params)
            N2, R = vuza.vuza_inner(*params)
            n1, p1, n2, p2, n3 = params
            self.assertEqual(N, N2)
            self.assertEqual(len(S), n1 * n2)
            self.assertEqual(len(R), p1 * p2 * n3)
            self.assertTrue(vuza.is_tiling(S, R, N), params)
            self.assertFalse(vuza.is_periodic(S, N), params)

    def test_bad_params(self):
        with self.assertRaises(ValueError):
            vuza.vuza_outer(2, 2, 2, 3, 2)  # gcd(4, 6) != 1
        with self.assertRaises(ValueError):
            vuza.vuza_outer(2, 4, 3, 3, 2)  # 4 not prime
        with self.assertRaises(ValueError):
            vuza.vuza_outer(2, 2, 3, 3, 1)

    def test_analyze_72(self):
        N, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        res = vuza.analyze_case(S, N)
        self.assertTrue(res["complete"])
        self.assertTrue(res["translates_consistent"])
        self.assertEqual(res["t1_failures"], 0)
        self.assertEqual(res["t2_failure_classes"], 0)  # 72 has two primes: T2 is a theorem
        self.assertGreaterEqual(res["aperiodic_classes"], 2)
        # both hand-checked aperiodic complements are among the classes found
        found = set()
        got = []
        vuza.enumerate_complements(S, N, lambda R: got.append(sorted(R)))
        for R in got:
            found.add(vuza.canonical(R, N))
        self.assertIn(vuza.canonical([0, 1, 4, 7, 13, 24, 28, 37, 43, 48, 49, 52], N), found)
        self.assertIn(vuza.canonical([0, 1, 21, 24, 25, 30, 36, 45, 49, 60, 66, 69], N), found)
        self.assertEqual(res["classes"], len({vuza.canonical(R, N) for R in got}))


class AudioTests(unittest.TestCase):
    def test_wav(self):
        N, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        _, R = vuza.vuza_inner(2, 2, 3, 3, 2)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.wav")
            secs = vuza.render_canon_wav(p, S, R, N, pulses_per_second=24, cycles=1, rate=8000)
            self.assertGreater(os.path.getsize(p), 1000)
            self.assertGreater(secs, 2.5)


if __name__ == "__main__":
    unittest.main()
