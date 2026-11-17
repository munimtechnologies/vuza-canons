# SPDX-License-Identifier: Apache-2.0
# Closure search over Vuza canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""Closure of a Vuza canon under "take every complement".

Start from a canon S (+) R = Z_N with S and R both aperiodic. Enumerate every
aperiodic complement of S (new inner rhythms), then every aperiodic
complement of each of those (new outer rhythms), and so on until nothing new
appears. The result is the whole connected block of Vuza canons that contains
the seed, counted up to translation as in the literature (Fripertinger,
Amiot, Kolountzakis-Matolcsi, Jedrzejewski). Every set found is tested for
the Coven-Meyerowitz conditions T1 and T2 (vuza.Cyclo, exact), and T2
failures are re-checked with integer polynomial division.

Where T2 is still open (0.3.0): t2open.py maps which tilings published
theorems already cover. At every period of the 0.2.0 list (360-924) they all
are, so T2 checks there are consistency checks. The smallest period with an
open case is 1800 = 2^3 3^2 5^2, with factor sizes {30, 60}; the group
"open1800" searches the Vuza blocks of exactly those sizes.

Two search back-ends give the same answers:
  * PyBackend: vuza.enumerate_complements (pure Python, used by the tests),
  * CBackend: tilec.c (about 100x faster), checked against PyBackend at start.

Usage: python closure.py --out-dir out [--case-minutes 20] [--total-minutes 420]
       [--only open1800] [--per-set-seconds 60] [--dump-max 400000]
"""
import argparse
import array
import gzip
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

import t2open
import vuza

VERSION = "0.3.0"
HERE = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------ helpers
def lexmin(xs, N):
    """Least translate of X that contains 0, as a sorted tuple (lexicographic
    order). The same class representative as tilec.c uses."""
    xs = sorted(set(x % N for x in xs))
    return min(tuple(sorted((x - t) % N for x in xs)) for t in xs)


def pack(t):
    return array.array("H", t).tobytes()


def unpack(b):
    a = array.array("H")
    a.frombytes(b)
    return tuple(a)


def param_tuples(N):
    """All (n1, p1, n2, p2, n3) with n1 p1 n2 p2 n3 = N, p1 != p2 prime,
    n1, n2, n3 >= 2 and gcd(n1 p1, n2 p2) = 1 (Jedrzejewski's order)."""
    out = set()
    for a in vuza.divisors(N):
        if a < 2:
            continue
        rest = N // a
        for p1 in sorted(vuza.factorize(a)):
            n1 = a // p1
            if n1 < 2:
                continue
            for b in vuza.divisors(rest):
                if b < 2 or math.gcd(a, b) != 1:
                    continue
                for p2 in sorted(vuza.factorize(b)):
                    n2 = b // p2
                    n3 = rest // b
                    if n2 >= 2 and n3 >= 2:
                        out.add((n1, p1, n2, p2, n3))
    return sorted(out)


def seed_sizes(params):
    """(|S|, |R|) of the standard canon: (n1 n2, p1 p2 n3)."""
    n1, p1, n2, p2, n3 = params
    return n1 * n2, p1 * p2 * n3


def open_tuples(N):
    """Parameter tuples at N whose standard canon has factor sizes for which
    T2 is not yet a theorem (t2open.known_for_sizes is False)."""
    out = []
    for t in param_tuples(N):
        a, b = seed_sizes(t)
        if not t2open.known_for_sizes(N, a, b):
            out.append(t)
    return out


def t2_proven_period(N):
    """True if published theorems give T2 for every tiling of period N
    (see t2open.py). 0.2.0 used a narrower test (two primes or N | p^2q^2r^2)
    and wrongly listed 360-924 as open."""
    return t2open.known_all(N)


# ------------------------------------------------------------ back-ends
class PyBackend:
    name = "python"

    def run(self, N, sets, time_limit, on_complement):
        """For each set X (index i): call on_complement(i, tuple) once per
        translation class of aperiodic complements (lexmin form). Returns a
        list of stats dicts. time_limit applies to each set."""
        stats = []
        for i, X in enumerate(sets):
            st = {"sols": 0, "classes": 0, "aper_classes": 0}

            def on(R, i=i, st=st):
                rs = tuple(sorted(R))
                if lexmin(rs, N) != rs:
                    return
                st["classes"] += 1
                if vuza.is_periodic(rs, N):
                    return
                st["aper_classes"] += 1
                on_complement(i, rs)

            t0 = time.time()
            sols, nodes, complete = vuza.enumerate_complements(X, N, on, time_limit)
            st.update(sols=sols, nodes=nodes, complete=complete, seconds=time.time() - t0)
            stats.append(st)
        return stats


class CBackend:
    name = "c"

    def __init__(self, exe):
        self.exe = exe

    def run(self, N, sets, time_limit, on_complement):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write("%d %.3f\n" % (N, float(time_limit or 0)))
            for i, X in enumerate(sets):
                f.write("%d %d %s\n" % (i, len(X), " ".join(str(int(x)) for x in X)))
        stats = [None] * len(sets)
        try:
            with open(path) as fin:
                p = subprocess.Popen([self.exe], stdin=fin, stdout=subprocess.PIPE, text=True)
                for line in p.stdout:
                    parts = line.split()
                    if not parts:
                        continue
                    if parts[0] == "C":
                        on_complement(int(parts[1]), tuple(int(x) for x in parts[2:]))
                    elif parts[0] == "D":
                        stats[int(parts[1])] = {
                            "sols": int(parts[2]), "classes": int(parts[3]), "aper_classes": int(parts[4]),
                            "complete": parts[5] == "1", "nodes": int(parts[6]), "seconds": float(parts[7])}
                rc = p.wait()
        finally:
            os.unlink(path)
        if rc != 0 or any(s is None for s in stats):
            raise RuntimeError("tilec failed (exit %s)" % rc)
        return stats


def compile_c(src, out_path):
    """Compile tilec.c. Returns (path or None, message)."""
    for cc in ("gcc", "cc", "clang"):
        exe = shutil.which(cc)
        if not exe:
            continue
        p = subprocess.run([exe, "-O2", "-o", out_path, src], capture_output=True, text=True)
        if p.returncode == 0:
            return out_path, cc
        return None, (cc + ": " + p.stderr[-3000:])
    return None, "no C compiler found"


SMALL_CASES = [(12, [0, 1]), (12, [0, 1, 6, 7]), (16, [0, 1, 4, 5]), (18, [0, 3, 6]),
               (24, [0, 1, 2, 12, 13, 14])]


def crosscheck(cbackend, pybackend=None, cases=None):
    """Compare two back-ends set by set. Sets with the same N go in one batch
    (this also tests the batch protocol)."""
    py = pybackend or PyBackend()
    if cases is None:
        cases = list(SMALL_CASES)
        for params in ((2, 2, 3, 3, 2), (2, 2, 3, 5, 2)):
            N, S = vuza.vuza_outer(*params)
            _, R = vuza.vuza_inner(*params)
            if params == (2, 2, 3, 3, 2):
                cases.append((N, S))
            cases.append((N, R))
        # 0.3.0: a 29-word bit set (N = 1800); an interval has exactly one complement
        cases.append((1800, list(range(30))))
    by_n = {}
    for N, X in cases:
        by_n.setdefault(N, []).append(X)
    ok = True
    report = []
    for N, sets in sorted(by_n.items()):
        got = {"py": [[] for _ in sets], "c": [[] for _ in sets]}
        st_py = py.run(N, sets, None, lambda i, t: got["py"][i].append(tuple(t)))
        st_c = cbackend.run(N, sets, None, lambda i, t: got["c"][i].append(tuple(t)))
        for i, X in enumerate(sets):
            a, b = st_py[i], st_c[i]
            same = (a["sols"] == b["sols"] and a["classes"] == b["classes"]
                    and a["aper_classes"] == b["aper_classes"] and b["complete"]
                    and sorted(got["py"][i]) == sorted(got["c"][i]))
            ok = ok and same
            report.append({"N": N, "size": len(X), "same": same,
                           "py": [a["sols"], a["classes"], a["aper_classes"]],
                           "c": [b["sols"], b["classes"], b["aper_classes"]]})
    return ok, report


# ------------------------------------------------------------ closure
class Closure:
    """Side 0 holds outer rhythms (the seed S), side 1 inner rhythms (seed R)."""

    def __init__(self, N, seeds, backend, max_classes=1000000, per_set_seconds=None):
        self.N = N
        self.backend = backend
        self.cy = vuza.Cyclo(N)
        self.max_classes = max_classes
        self.per_set = per_set_seconds
        self.capped = False
        self.index = [{}, {}]
        self.keys = [[], []]
        self.parent = [[], []]
        self.done = [0, 0]
        self.edges = [0, 0]
        self.sols = [0, 0]
        self.nodes = [0, 0]
        self.avg = [None, None]
        self.batch = [1, 1]
        self.incomplete_enums = 0
        self.first_stats = [None, None]
        self.t1_failures = [0, 0]
        self.t2_fail = [0, 0]
        self.t2_examples = []
        self.profiles = [{}, {}]
        self.seconds = 0.0
        self.error = None
        for S, R in seeds:
            i = self.add(0, lexmin(S, N), -1)
            self.add(1, lexmin(R, N), i)

    def classes(self, side):
        return [unpack(k) for k in self.keys[side]]

    def add(self, side, tup, parent):
        k = pack(tup)
        idx = self.index[side].get(k)
        if idx is not None:
            return idx
        if len(self.keys[0]) + len(self.keys[1]) >= self.max_classes:
            self.capped = True
            return -1
        idx = len(self.keys[side])
        self.index[side][k] = idx
        self.keys[side].append(k)
        self.parent[side].append(parent)
        self._check(side, tup, parent)
        return idx

    def _check(self, side, xs, parent):
        SX, t1, fails = self.cy.profile(xs)
        key = ",".join(map(str, SX))
        d = self.profiles[side]
        if key in d or len(d) < 300:
            d[key] = d.get(key, 0) + 1
        else:
            d["other"] = d.get("other", 0) + 1
        if not t1:
            self.t1_failures[side] += 1
        if fails:
            self.t2_fail[side] += 1
            if len(self.t2_examples) < 20:
                ptup = unpack(self.keys[1 - side][parent]) if parent >= 0 else None
                exact = (all(vuza.vanishes_exact(xs, q) for q in SX)
                         and not any(vuza.vanishes_exact(xs, s) for s in fails)
                         and (ptup is None or vuza.is_tiling(ptup, xs, self.N)))
                self.t2_examples.append({"side": side, "X": list(xs), "S_X": SX, "missing": fails,
                                         "partner": list(ptup) if ptup else None, "exact_confirmed": exact})

    def pending(self, side):
        return len(self.keys[side]) - self.done[side]

    def run(self, budget_s, log=None):
        t_start = time.time()
        N = self.N
        while True:
            pend = [self.pending(0), self.pending(1)]
            if not any(pend) or self.capped:
                break
            left = budget_s - (time.time() - t_start)
            if left <= 1:
                break
            cands = [s for s in (0, 1) if pend[s]]
            side = min(cands, key=lambda s: (self.avg[s] if self.avg[s] is not None else -1.0, s))
            other = 1 - side
            n = min(pend[side], self.batch[side])
            lo = self.done[side]
            idxs = list(range(lo, lo + n))
            sets = [unpack(self.keys[side][i]) for i in idxs]
            tl = left
            if self.per_set:
                tl = min(float(self.per_set), max(1.0, left / n))

            def on_comp(j, tup):
                self.add(other, tup, idxs[j])

            try:
                stats = self.backend.run(N, sets, tl, on_comp)
            except Exception as e:  # keep what was found; report the error
                self.error = repr(e)
                break
            secs = 0.0
            for j, st in enumerate(stats):
                if idxs[j] == 0 and self.first_stats[side] is None:
                    self.first_stats[side] = dict(st)
                self.edges[side] += st["aper_classes"]
                self.sols[side] += st["sols"]
                self.nodes[side] += st["nodes"]
                if not st["complete"]:
                    self.incomplete_enums += 1
                secs += st["seconds"]
            self.done[side] += n
            avg = secs / n
            self.avg[side] = avg if self.avg[side] is None else 0.5 * (self.avg[side] + avg)
            self.batch[side] = max(1, min(512, int(20.0 / max(self.avg[side], 1e-3))))
            if log:
                log("  side %d: %d/%d done, classes %d/%d, %.2fs/set" % (
                    side, self.done[side], len(self.keys[side]), len(self.keys[0]), len(self.keys[1]),
                    self.avg[side]))
        self.seconds += time.time() - t_start
        return self.result()

    def result(self):
        N = self.N
        sizes = [len(unpack(self.keys[s][0])) for s in (0, 1)]
        counts = [len(self.keys[0]), len(self.keys[1])]
        complete = (self.pending(0) == 0 and self.pending(1) == 0 and self.incomplete_enums == 0
                    and not self.capped and self.error is None)
        proven = t2_proven_period(N)
        open_sizes = None
        if sizes[0] * sizes[1] == N:
            open_sizes = not t2open.known_for_sizes(N, sizes[0], sizes[1])
        return {
            "N": N, "sizes": sizes, "classes": counts, "processed": list(self.done),
            "complete": complete, "capped": self.capped, "error": self.error,
            "incomplete_enumerations": self.incomplete_enums,
            "edges_from_side": list(self.edges),
            "edges_consistent": (self.edges[0] == self.edges[1]) if complete else None,
            "complete_bipartite": (self.edges[0] == self.edges[1] == counts[0] * counts[1]) if complete else None,
            "seed_complements": [s["aper_classes"] if s else None for s in self.first_stats],
            "seed_complements_complete": [s["complete"] if s else None for s in self.first_stats],
            "t1_failures": list(self.t1_failures), "t2_failure_classes": list(self.t2_fail),
            "t2_examples": self.t2_examples,
            "size_distinct_primes": [vuza.n_prime_factors(s) for s in sizes],
            "t2_proven_for_period": proven,
            "t2_open_for_sizes": open_sizes,
            "profiles": self.profiles, "solutions_with_0": list(self.sols), "nodes": list(self.nodes),
            "seconds": round(self.seconds, 1),
        }

    def dump(self, path_prefix, limit=None):
        """Write the classes of each side, one per line (at most limit each)."""
        for side in (0, 1):
            with gzip.open("%s_side%d.txt.gz" % (path_prefix, side), "wt") as f:
                for i, k in enumerate(self.keys[side]):
                    if limit is not None and i >= limit:
                        break
                    f.write(" ".join(map(str, unpack(k))) + "\n")


# ------------------------------------------------------------ the case list
# Jedrzejewski (arXiv 1304.6609) Table 1, a complete classification for
# N <= 168 (#S, #R up to translation); a closure must equal one of the rows.
TABLE1 = {
    (2, 2, 3, 3, 2): [(3, 6)],
    (2, 2, 3, 3, 3): [(3, 252)],
    (2, 2, 3, 5, 2): [(8, 18)],
    (2, 2, 5, 3, 2): [(16, 20)],
    (2, 2, 3, 3, 4): [(3, 8640), (6, 36)],
    (4, 2, 3, 3, 2): [(6, 60), (162, 12), (324, 6)],
    (2, 2, 3, 7, 2): [(16, 54)],
    (2, 2, 7, 3, 2): [(104, 42)],
}
# Jedrzejewski Table 2: lower bounds (#S, #R).
TABLE2 = {
    (2, 2, 3, 5, 3): (8, 2052), (2, 5, 3, 3, 2): (3, 84), (2, 2, 5, 3, 3): (16, 1800),
    (3, 3, 5, 2, 2): (9, 105), (2, 2, 3, 3, 5): (3, 77760),
}
# Aperiodic complements of the standard outer rhythm, Auricchio-Ferrarini-
# Gualandi-Pernazza (arXiv 2112.05249), in Jedrzejewski's parameter order.
SAT_COUNTS = {
    (2, 2, 3, 3, 2): 6, (2, 2, 3, 3, 3): 252, (2, 2, 3, 5, 2): 18, (2, 2, 5, 3, 2): 20,
    (2, 2, 3, 7, 2): 54, (2, 2, 7, 3, 2): 42, (2, 2, 3, 5, 3): 2052, (2, 2, 5, 3, 3): 1800,
    (3, 3, 2, 5, 2): 96, (5, 2, 3, 3, 2): 120, (2, 2, 3, 3, 4): 8640, (2, 2, 3, 3, 5): 281232,
    (5, 7, 2, 3, 2): 720, (7, 5, 2, 3, 2): 672, (3, 7, 2, 5, 2): 864, (7, 3, 2, 5, 2): 6720,
    (2, 7, 3, 5, 2): 1872, (2, 7, 5, 3, 2): 22320, (5, 7, 3, 2, 2): 3120, (7, 5, 3, 2, 2): 1008,
    (3, 7, 5, 2, 2): 33480, (7, 3, 5, 2, 2): 840, (7, 2, 3, 5, 2): 10080, (7, 2, 5, 3, 2): 1120,
}

CASES = [
    ("validate", (2, 2, 3, 3, 2)), ("validate", (2, 2, 3, 3, 3)), ("validate", (2, 2, 3, 5, 2)),
    ("validate", (2, 2, 5, 3, 2)), ("validate", (2, 2, 3, 7, 2)), ("validate", (2, 2, 7, 3, 2)),
    ("validate", (4, 2, 3, 3, 2)), ("validate", (2, 2, 3, 3, 4)),
    # N = 420 = 2^2 3 5 7 (T2 is a theorem here by Laba-Londner Cor. 6.2; see t2open.py)
    ("open420", (5, 7, 2, 3, 2)), ("open420", (7, 5, 2, 3, 2)), ("open420", (3, 7, 2, 5, 2)),
    ("open420", (7, 3, 2, 5, 2)), ("open420", (2, 7, 3, 5, 2)), ("open420", (2, 7, 5, 3, 2)),
    # periods with no published enumeration (T2 is a theorem at all of them; see t2open.py)
    ("new", (4, 2, 3, 5, 3)), ("new", (4, 2, 3, 7, 3)), ("new", (2, 2, 9, 5, 3)),
    ("new", (7, 5, 3, 3, 2)), ("new", (3, 3, 7, 5, 2)), ("new", (5, 11, 2, 3, 2)),
    ("new", (11, 5, 2, 3, 2)), ("new", (7, 11, 2, 3, 2)), ("new", (11, 7, 2, 3, 2)),
    ("new", (4, 2, 5, 3, 5)), ("new", (5, 7, 2, 3, 4)),
    # lower bounds at 180 (T2 is a theorem there: validation of block sizes)
    ("t180", (2, 2, 3, 5, 3)), ("t180", (2, 5, 3, 3, 2)), ("t180", (2, 2, 5, 3, 3)), ("t180", (3, 3, 5, 2, 2)),
]


def full_case_list():
    cases = list(CASES)
    listed = set(p for _, p in cases)
    # 0.3.0: the smallest period where T2 is open (factor sizes 30 and 60)
    for t in open_tuples(1800):
        cases.append(("open1800", t))
        listed.add(t)
    for t in param_tuples(420):
        if t not in listed:
            cases.append(("all420", t))
            listed.add(t)
    cases += [("heavy", (2, 2, 3, 3, 5)), ("heavy", (2, 2, 15, 7, 2))]
    return cases


# ------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--case-minutes", type=float, default=20.0)
    ap.add_argument("--total-minutes", type=float, default=420.0)
    ap.add_argument("--only", default="", help="comma list of groups")
    ap.add_argument("--no-c", action="store_true")
    ap.add_argument("--max-classes", type=int, default=1000000)
    ap.add_argument("--per-set-seconds", type=float, default=0.0, help="0 = no per-set limit")
    ap.add_argument("--dump-max", type=int, default=400000,
                    help="dump every class if a block has at most this many, else this many per side")
    args = ap.parse_args(argv)
    out = args.out_dir
    os.makedirs(os.path.join(out, "classes"), exist_ok=True)
    t_start = time.time()
    meta = {"version": VERSION, "python": sys.version.split()[0], "numpy": vuza._np is not None,
            "case_minutes": args.case_minutes, "total_minutes": args.total_minutes,
            "per_set_seconds": args.per_set_seconds, "max_classes": args.max_classes, "only": args.only}

    backend = PyBackend()
    if not args.no_c:
        exe, msg = compile_c(os.path.join(HERE, "tilec.c"), os.path.join(tempfile.gettempdir(), "tilec"))
        meta["compile"] = msg
        if exe:
            cb = CBackend(exe)
            t0 = time.time()
            try:
                ok, rep = crosscheck(cb)
            except Exception as e:
                ok, rep = False, [{"error": repr(e)}]
            meta["crosscheck_ok"] = ok
            meta["crosscheck"] = rep
            meta["crosscheck_seconds"] = round(time.time() - t0, 1)
            print("crosscheck C vs Python:", ok, flush=True)
            if ok:
                backend = cb
    meta["backend"] = backend.name

    groups = set(g for g in args.only.split(",") if g)
    results = []
    seen_blocks = []  # (N, sizes, params, side0 key set or None, side1 key set or None)
    wav_done = set()
    per_set = args.per_set_seconds if args.per_set_seconds > 0 else None

    def save():
        with open(os.path.join(out, "closure_results.json"), "w") as f:
            json.dump({"meta": meta, "results": results}, f, indent=1)

    for group, params in full_case_list():
        if groups and group not in groups:
            continue
        left = args.total_minutes * 60 - (time.time() - t_start)
        if left < 90:
            results.append({"group": group, "params": list(params), "skipped": "total time budget used"})
            continue
        N, S = vuza.vuza_outer(*params)
        _, R = vuza.vuza_inner(*params)
        base = {"group": group, "params": list(params), "params_order": "n1,p1,n2,p2,n3", "N": N}
        if not (vuza.is_tiling(S, R, N) and not vuza.is_periodic(S, N) and not vuza.is_periodic(R, N)):
            base["skipped"] = "seed is not a Vuza canon"
            results.append(base)
            continue
        kS, kR = pack(lexmin(S, N)), pack(lexmin(R, N))
        same = [b for b in seen_blocks if b[0] == N and b[1] == (len(S), len(R))
                and ((b[3] is not None and kS in b[3]) or (b[4] is not None and kR in b[4]))]
        if same:
            base["same_block_as"] = list(same[0][2])
            results.append(base)
            print("case", group, params, "N =", N, ": same block as", same[0][2], flush=True)
            continue
        print("case", group, params, "N =", N, "|S| =", len(S), "|R| =", len(R), flush=True)
        cl = Closure(N, [(S, R)], backend, max_classes=args.max_classes, per_set_seconds=per_set)
        budget = min(args.case_minutes * 60, left - 60)
        if group == "heavy":
            budget = left - 60
        res = cl.run(budget, log=lambda s: print(s, flush=True))
        res.update(base)
        res["backend"] = backend.name
        if params in TABLE1:
            res["table1_rows"] = [list(r) for r in TABLE1[params]]
            if res["complete"]:
                res["matches_table1"] = tuple(res["classes"]) in TABLE1[params]
        if params in TABLE2:
            res["table2_lower_bound"] = list(TABLE2[params])
        if params in SAT_COUNTS:
            res["sat_count"] = SAT_COUNTS[params]
            if res["seed_complements_complete"][0]:
                res["matches_sat_count"] = res["seed_complements"][0] == SAT_COUNTS[params]
        prefix = os.path.join(out, "classes", "N%d_%s" % (N, "-".join(map(str, params))))
        if sum(res["classes"]) <= args.dump_max:
            cl.dump(prefix)
        else:
            cl.dump(prefix + "_first", limit=max(1, args.dump_max // 2))
            res["dump_truncated"] = True
        seen_blocks.append((N, (len(S), len(R)), params,
                            set(cl.index[0]) if len(cl.index[0]) <= 100000 else None,
                            set(cl.index[1]) if len(cl.index[1]) <= 100000 else None))
        # audio: one canon per new period, a non-standard outer rhythm if there is one
        if (group in ("new", "open420") or group.startswith("open")) and N not in wav_done:
            i0 = 1 if len(cl.keys[0]) > 1 else 0
            Sx = unpack(cl.keys[0][i0])
            p = cl.parent[0][i0]
            Rx = unpack(cl.keys[1][p]) if p >= 0 else unpack(cl.keys[1][0])
            if vuza.is_tiling(Sx, Rx, N):
                path = prefix + "_canon.wav"
                try:
                    secs = vuza.render_canon_wav(path, Sx, Rx, N, pulses_per_second=14.0,
                                                 cycles=2 if N <= 500 else 1)
                    res["wav"] = os.path.basename(path)
                    res["wav_seconds"] = round(secs, 1)
                    res["wav_canon"] = {"S": list(Sx), "R": list(Rx)}
                    wav_done.add(N)
                except Exception as e:
                    res["wav_error"] = repr(e)
        print(json.dumps({k: res.get(k) for k in ("N", "classes", "complete", "complete_bipartite",
                                                    "seed_complements", "t1_failures", "t2_failure_classes",
                                                    "t2_open_for_sizes", "matches_table1", "matches_sat_count",
                                                    "seconds")}),
              flush=True)
        results.append(res)
        save()

    # pre-registered predictions (README, P5-P12)
    done = [r for r in results if "classes" in r]
    opened = [r for r in done if r.get("t2_open_for_sizes")]
    pred = {
        "P5_crosscheck": meta.get("crosscheck_ok"),
        "P6_table1": [[r["params"], r["classes"], r.get("matches_table1")] for r in done if "table1_rows" in r],
        "P7_t1_failures": sum(sum(r["t1_failures"]) for r in done),
        "P7_t2_failure_classes": sum(sum(r["t2_failure_classes"]) for r in done),
        "P8_complete_bipartite": [[r["params"], r["complete_bipartite"]] for r in done if r["complete"]],
        "P9_sat_counts": [[r["params"], r["seed_complements"][0], r["sat_count"], r.get("matches_sat_count")]
                          for r in done if "sat_count" in r],
        "P10_open_rhythms_checked": sum(sum(r["classes"]) for r in opened),
        "P10_open_t2_failure_classes": sum(sum(r["t2_failure_classes"]) for r in opened),
        "P11_open_blocks": [[r["params"], r["sizes"], r["classes"], r["complete"]] for r in opened],
        "P12_open_seeds_skipped": [[r["params"], r.get("skipped")] for r in results
                                   if r.get("group", "").startswith("open1800") and r.get("skipped")],
    }
    summary = []
    for r in results:
        summary.append({k: r.get(k) for k in ("group", "params", "N", "sizes", "classes", "complete",
                                              "complete_bipartite", "seed_complements", "t2_open_for_sizes",
                                              "t1_failures", "t2_failure_classes", "same_block_as",
                                              "skipped", "seconds")})
    meta["elapsed_minutes"] = round((time.time() - t_start) / 60, 1)
    save()
    with open(os.path.join(out, "closure_summary.json"), "w") as f:
        json.dump({"meta": meta, "predictions": pred, "summary": summary}, f, indent=1)
    if pred["P7_t2_failure_classes"]:
        print("T2 FAILURES FOUND: verify independently before any claim", flush=True)
    print("done in", meta["elapsed_minutes"], "minutes", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
