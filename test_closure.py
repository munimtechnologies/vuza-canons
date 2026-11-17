# SPDX-License-Identifier: Apache-2.0
# Tests for closure.py. Made by MV2 of Munim, Inc., with AI agents.
import itertools
import os
import tempfile
import unittest

import closure
import vuza


def brute(S, N):
    """(solutions with 0, translation classes, sorted aperiodic class reps) by brute force."""
    k = N // len(S)
    sols = [(0,) + rest for rest in itertools.combinations(range(1, N), k - 1)
            if vuza.is_tiling(S, (0,) + rest, N)]
    classes = {closure.lexmin(R, N) for R in sols}
    aper = sorted(c for c in classes if not vuza.is_periodic(c, N))
    return len(sols), len(classes), aper


class Helpers(unittest.TestCase):
    def test_lexmin(self):
        self.assertEqual(closure.lexmin([3, 5, 9], 12), (0, 2, 6))
        self.assertEqual(closure.lexmin([0, 6], 12), (0, 6))
        self.assertEqual(closure.lexmin([15, 9], 12), (0, 6))  # 15 = 3 mod 12

    def test_pack_roundtrip(self):
        t = (0, 5, 700, 2047)
        self.assertEqual(closure.unpack(closure.pack(t)), t)

    def test_param_tuples_72(self):
        self.assertEqual(closure.param_tuples(72), [(2, 2, 3, 3, 2), (3, 3, 2, 2, 2)])

    def test_param_tuples_valid(self):
        for N in (120, 180, 420):
            ts = closure.param_tuples(N)
            self.assertTrue(ts)
            for t in ts:
                self.assertEqual(vuza.check_params(*t), N)
        self.assertIn((5, 7, 2, 3, 2), closure.param_tuples(420))
        self.assertIn((2, 2, 3, 5, 2), closure.param_tuples(120))

    def test_proven_periods(self):
        for N in (72, 108, 144, 180, 900):
            self.assertTrue(closure.t2_proven_period(N), N)
        for N in (120, 360, 420, 840):
            self.assertFalse(closure.t2_proven_period(N), N)


class PyBackendTests(unittest.TestCase):
    def test_matches_brute_force(self):
        be = closure.PyBackend()
        for N, S in closure.SMALL_CASES:
            got = []
            st = be.run(N, [S], None, lambda i, t: got.append(t))[0]
            sols, classes, aper = brute(S, N)
            self.assertTrue(st["complete"])
            self.assertEqual(st["sols"], sols, (N, S))
            self.assertEqual(st["classes"], classes, (N, S))
            self.assertEqual(st["aper_classes"], len(aper))
            self.assertEqual(sorted(got), aper)

    def test_batch_indices(self):
        be = closure.PyBackend()
        seen = {}
        stats = be.run(12, [[0, 1], [0, 1, 6, 7]], None, lambda i, t: seen.setdefault(i, []).append(t))
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["sols"], brute([0, 1], 12)[0])
        self.assertEqual(stats[1]["sols"], brute([0, 1, 6, 7], 12)[0])


class ClosureTests(unittest.TestCase):
    def test_closure_72(self):
        N, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        _, R = vuza.vuza_inner(2, 2, 3, 3, 2)
        cl = closure.Closure(N, [(S, R)], closure.PyBackend())
        res = cl.run(900)
        self.assertTrue(res["complete"])
        self.assertEqual(res["sizes"], [6, 12])
        self.assertEqual(res["t1_failures"], [0, 0])
        self.assertEqual(res["t2_failure_classes"], [0, 0])  # 72 has two primes: T2 is a theorem
        self.assertTrue(res["edges_consistent"])
        self.assertTrue(res["t2_proven_for_period"])
        # every aperiodic complement of the standard S is in side 1
        direct = []
        closure.PyBackend().run(N, [S], None, lambda i, t: direct.append(t))
        self.assertEqual(res["seed_complements"][0], len(direct))
        self.assertTrue(set(direct) <= set(cl.classes(1)))
        self.assertIn(closure.lexmin(S, N), cl.classes(0))
        self.assertIn(closure.lexmin(R, N), cl.classes(1))
        # every class tiles with the class it was found from
        for side in (0, 1):
            other = cl.classes(1 - side)
            for i, t in enumerate(cl.classes(side)):
                p = cl.parent[side][i]
                if p >= 0:
                    self.assertTrue(vuza.is_tiling(other[p], t, N))
                self.assertFalse(vuza.is_periodic(t, N))
        with tempfile.TemporaryDirectory() as d:
            cl.dump(os.path.join(d, "x"))
            self.assertTrue(os.path.exists(os.path.join(d, "x_side1.txt.gz")))

    def test_time_budget(self):
        N, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        _, R = vuza.vuza_inner(2, 2, 3, 3, 2)
        cl = closure.Closure(N, [(S, R)], closure.PyBackend())
        res = cl.run(0)  # no time: nothing processed, reported incomplete
        self.assertFalse(res["complete"])
        self.assertEqual(res["classes"], [1, 1])

    def test_cap(self):
        N, S = vuza.vuza_outer(2, 2, 3, 3, 2)
        _, R = vuza.vuza_inner(2, 2, 3, 3, 2)
        cl = closure.Closure(N, [(S, R)], closure.PyBackend(), max_classes=3)
        res = cl.run(600)
        self.assertTrue(res["capped"])
        self.assertFalse(res["complete"])
        self.assertLessEqual(sum(res["classes"]), 3)


@unittest.skipUnless(os.environ.get("VUZA_TEST_C") == "1", "set VUZA_TEST_C=1 to compile and test tilec.c")
class CBackendTests(unittest.TestCase):
    def test_c_matches_python(self):
        with tempfile.TemporaryDirectory() as d:
            exe, msg = closure.compile_c(os.path.join(closure.HERE, "tilec.c"), os.path.join(d, "tilec"))
            self.assertIsNotNone(exe, msg)
            ok, rep = closure.crosscheck(closure.CBackend(exe))
            self.assertTrue(ok, rep)


if __name__ == "__main__":
    unittest.main()
