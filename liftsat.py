# SPDX-License-Identifier: Apache-2.0
# Lift search for a set complement that fails the Coven-Meyerowitz condition T2.
# Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""liftsat: hunt for a set counterexample to T2 where weak ones are known to live.

Background (all published):
  * A tiling A (+) B = Z_M fails T2 on the B side exactly when, for some
    product N of B's prime powers (two or more primes), Phi_N does not divide
    B(x). Tiling then forces Phi_N | A(x) while no prime power of N divides
    A(x): Phi_N is an UNSUPPORTED divisor of A (Kiss-Laba-Marshall-Somlai,
    Def. 1.5). So every counterexample is a tile with an unsupported divisor.
  * Kiss-Marshall-Matolcsi-Somlai (arXiv:2611.13593, Thm 1.4) show that such
    tiles have nonnegative rational WEAK complements failing T2, e.g. at period
    180, but construct no SET complement that fails T2 ("No such set complement
    is constructed here").
  * Tan-Zhang (arXiv:2609.06677) show 180 is the least period of an
    unsupported divisor and 900 the least for a three-prime one. Their period
    180 tiles, both of size 30 with signature {4, 5, 9} and Phi_6 unsupported:
      S180 = {30j + c : j < 6, c in {0,2,3,4,6}}   (periodic; = KMMS's T)
      C180 = the aperiodic set of their Sec. 8.1, complement {0,20,40,45,65,85}
    Their period-900 examples are 5*S180 and 5*C180.
  * Dilation does not change the answer: A has a set complement failing T2 iff
    qA in Z_{qM} has (KMMS Prop. 6.3).

The search here: fix a source tile X of period L, a dilation q and a lift
factor k, and let A range over every set in Z_M (M = qLk) with A = qX mod qL
(k choices for each of the |X| points). Ask CP-SAT for a tiling A (+) B = Z_M
in which B (or A) fails T2. With A fixed modulo qL, every cyclotomic order
dividing qL is decided in Python, so the models are small.

Configurations:
  theorem  M is covered by a theorem (k <= 5, or a dilation that reduces to
           one), so every T2 case must come back INFEASIBLE. These measure the
           method on the same model sizes as the open runs.
  open     k = 10, 15, 20: M = 1800, 2700, 3600 with sizes 30 / 60, 90, 120,
           where no published theorem covers every tiling.

A verified FEASIBLE T2 case in an open configuration would be a counterexample
to the Coven-Meyerowitz conjecture; it is written to
T2_COUNTEREXAMPLE_CANDIDATES.json and must be re-verified independently. All
INFEASIBLE would be the first search showing that these weak-counterexample
tiles have no T2-failing set complement at these periods (solver-dependent;
CP-SAT gives no proof certificate). This is a targeted search, not all tilings.

Usage:
  python liftsat.py --list
  python liftsat.py --out-dir out --workers 4 --total-minutes 320
"""
import argparse
import cmath
import functools
import itertools
import json
import math
import os
import sys
import time
import traceback

VERSION = "0.5.0"

C5 = (0, 2, 3, 4, 6)  # Apery core: 1 + x^2 + x^3 + x^4 + x^6 = Phi_5 Phi_6

SOURCES = {
    "S180": {
        "period": 180,
        "A": sorted(30 * j + c for j in range(6) for c in C5),
        "B": [0, 5, 10, 15, 20, 25],
        "ref": "Tan-Zhang arXiv:2609.06677 (period 180, m=1, e=0); = T of Kiss-Marshall-Matolcsi-Somlai arXiv:2611.13593 Thm 1.5",
    },
    "C180": {
        "period": 180,
        "A": [0, 2, 4, 12, 21, 34, 36, 38, 48, 51, 60, 62, 64, 72, 75, 90, 94, 98, 108, 111,
              122, 124, 126, 132, 141, 150, 154, 158, 165, 168],
        "B": [0, 20, 40, 45, 65, 85],
        "ref": "Tan-Zhang arXiv:2609.06677 Sec. 8.1 (aperiodic; 5*C180 is their period-900 example)",
    },
}

THM_SMALL = "Laba-Londner Cor. 6.2: |B| has only the primes 2 and 3 in common with |A|"
THM_900 = "M = 900 = (2*3*5)^2: T2 holds for every tiling (Laba-Londner, Invent. Math. 2023; Res. Math. Sci. 2025)"
DIL = "every lift is a dilate of a lift at a smaller period (KMMS Prop. 6.3), where T2 is a theorem"

# name, source, q (dilation), k (lift factor), label, seconds per T2 case, why
CONFIGS = [
    ("S180-k1", "S180", 1, 1, "theorem", 30, "M=180; " + THM_SMALL),
    ("C180-k1", "C180", 1, 1, "theorem", 30, "M=180; " + THM_SMALL),
    ("S180-k2", "S180", 1, 2, "theorem", 30, "M=360; " + THM_SMALL),
    ("C180-k2", "C180", 1, 2, "theorem", 30, "M=360; " + THM_SMALL),
    ("S180-k3", "S180", 1, 3, "theorem", 30, "M=540; " + THM_SMALL),
    ("S180-k4", "S180", 1, 4, "theorem", 30, "M=720; " + THM_SMALL),
    ("S180-k5", "S180", 1, 5, "theorem", 60, THM_900),
    ("C180-k5", "C180", 1, 5, "theorem", 60, THM_900),
    ("S180-q5k2", "S180", 5, 2, "theorem", 120, "M=1800 but " + DIL + " (360)"),
    ("C180-q5k2", "C180", 5, 2, "theorem", 120, "M=1800 but " + DIL + " (360)"),
    ("S180-q2k5", "S180", 2, 5, "theorem", 120, "M=1800 but " + DIL + " (900)"),
    ("S180-k10", "S180", 1, 10, "open", 240, "M=1800 = 2^3 3^2 5^2, sizes 30/60: no theorem covers it"),
    ("C180-k10", "C180", 1, 10, "open", 240, "M=1800 = 2^3 3^2 5^2, sizes 30/60: no theorem covers it"),
    ("S180-k15", "S180", 1, 15, "open", 300, "M=2700 = 2^2 3^3 5^2, sizes 30/90: no theorem covers it"),
    ("C180-k15", "C180", 1, 15, "open", 300, "M=2700 = 2^2 3^3 5^2, sizes 30/90: no theorem covers it"),
    ("S180-k20", "S180", 1, 20, "open", 300, "M=3600 = 2^4 3^2 5^2, sizes 30/120: no theorem covers it"),
    ("C180-k20", "C180", 1, 20, "open", 300, "M=3600 = 2^4 3^2 5^2, sizes 30/120: no theorem covers it"),
]


# ---------------------------------------------------------------- arithmetic
def factorize(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def prod(xs):
    p = 1
    for x in xs:
        p *= x
    return p


def rad(n):
    return prod(factorize(n))


def prime_of(q):
    f = factorize(q)
    if len(f) != 1:
        raise ValueError("not a prime power: %d" % q)
    return next(iter(f))


def mixed_divisors(M):
    return [d for d in divisors(M) if d > 1 and len(factorize(d)) >= 2]


def prime_power_list(M):
    f = factorize(M)
    return {p: [p ** k for k in range(1, f[p] + 1)] for p in sorted(f)}


def all_prime_powers(M):
    return sorted(q for qs in prime_power_list(M).values() for q in qs)


def parent_prime(M, d):
    for p in sorted(factorize(M)):
        if (M // d) % p == 0:
            return p
    raise ValueError("d must be a proper divisor of M")


# ------------------------------------------------------- integer polynomials
def poly_exact_div(a, b):
    a = list(a)
    db = len(b) - 1
    q = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i] // b[-1]
        q[i - db] = c
        for j in range(db + 1):
            a[i - db + j] -= c * b[j]
    if any(a[:db]):
        raise ArithmeticError("not exact")
    return q


def poly_rem_monic(a, b):
    a = list(a)
    db = len(b) - 1
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        if c:
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
    return a[:db]


_CYC = {}


def cyclotomic(d):
    if d in _CYC:
        return _CYC[d]
    num = [-1] + [0] * (d - 1) + [1]
    for e in divisors(d):
        if e < d:
            num = poly_exact_div(num, cyclotomic(e))
    _CYC[d] = num
    return num


@functools.lru_cache(maxsize=None)
def rem_table(m):
    phi = cyclotomic(m)
    deg = len(phi) - 1
    rows = []
    for j in range(m):
        a = [0] * max(m, deg + 1)
        a[j] = 1
        rows.append(poly_rem_monic(a, phi))
    return rows


@functools.lru_cache(maxsize=None)
def vanish_rows(d):
    """phi(d) integer linear forms on the residue counts mod d whose common
    vanishing is equivalent to Phi_d | X(x) (Phi_d(x) = Phi_m(x^(d/m)),
    m = rad(d))."""
    m = rad(d)
    k = d // m
    T = rem_table(m)
    ph = len(T[0])
    rows = []
    for t in range(k):
        for i in range(ph):
            rows.append(tuple((t + k * j, T[j][i]) for j in range(m) if T[j][i] != 0))
    return tuple(rows)


def residues(xs, d):
    c = [0] * d
    for x in xs:
        c[x % d] += 1
    return c


def vanishes_rows(xs, d):
    c = residues(xs, d)
    for row in vanish_rows(d):
        if sum(v * c[r] for r, v in row) != 0:
            return False
    return True


def vanishes_numeric(xs, d):
    """Independent exact test: X(zeta_d^u) = 0 for every unit u. A nonzero
    algebraic integer has a conjugate of modulus >= 1, so 'all below 0.5' is
    exact."""
    xs = list(xs)
    for u in range(1, d):
        if math.gcd(u, d) != 1:
            continue
        s = 0j
        for x in xs:
            s += cmath.exp(2j * math.pi * ((u * x) % d) / d)
        if abs(s) >= 0.5:
            return False
    return True


def is_tiling(A, B, M):
    seen = [0] * M
    for a in A:
        for b in B:
            seen[(a + b) % M] += 1
    return all(c == 1 for c in seen)


# ------------------------------------------------------------ T1/T2 helpers
def profiles(M, a):
    pp = prime_power_list(M)
    fa = factorize(a)
    choices = [list(itertools.combinations(pp[p], fa.get(p, 0))) for p in sorted(pp)]
    return [tuple(sorted(q for part in combo for q in part)) for combo in itertools.product(*choices)]


def complement_profile(M, SA):
    return tuple(sorted(set(all_prime_powers(M)) - set(SA)))


def t2_products(S):
    by = {}
    for q in S:
        by.setdefault(prime_of(q), []).append(q)
    primes = sorted(by)
    out = []
    for combo in itertools.product(*[[1] + sorted(by[p]) for p in primes]):
        parts = [c for c in combo if c != 1]
        if len(parts) >= 2:
            out.append(prod(parts))
    return sorted(out)


def t2_report(X, M):
    S = [q for q in all_prime_powers(M) if vanishes_rows(X, q)]
    S_num = [q for q in all_prime_powers(M) if vanishes_numeric(X, q)]
    t1 = len(set(X)) == prod(prime_of(q) for q in S)
    fails = [s for s in t2_products(S) if not vanishes_rows(X, s)]
    fails_num = [s for s in t2_products(S) if not vanishes_numeric(X, s)]
    return {"S": S, "S_numeric_agrees": S == S_num, "t1": t1, "t2_failures": fails,
            "t2_numeric_agrees": fails == fails_num}


def unsupported_orders(X, M):
    """Mixed orders s | M with Phi_s | X, every prime of s dividing |X|, and
    Phi_{p^a} not dividing X for every p^a || s (KLMS Def. 1.5)."""
    n = len(set(X))
    out = []
    for s in mixed_divisors(M):
        f = factorize(s)
        if any(n % p for p in f):
            continue
        if not vanishes_rows(X, s):
            continue
        if any(vanishes_rows(X, p ** e) for p, e in f.items()):
            continue
        out.append(s)
    return out


def source_report(name):
    src = SOURCES[name]
    M, A, B = src["period"], src["A"], src["B"]
    rep = {"name": name, "period": M, "size_A": len(set(A)), "size_B": len(set(B)), "ref": src["ref"]}
    rep["tiling"] = len(set(A)) * len(set(B)) == M and is_tiling(A, B, M)
    rep["A"] = t2_report(A, M)
    rep["B"] = t2_report(B, M)
    rep["unsupported_A"] = unsupported_orders(A, M)
    rep["ok"] = bool(rep["tiling"] and rep["A"]["t1"] and not rep["A"]["t2_failures"]
                     and rep["A"]["S_numeric_agrees"] and rep["unsupported_A"])
    return rep


# ------------------------------------------------------------------ planning
def config_dict(row):
    name, src, q, k, label, secs, why = row
    L = SOURCES[src]["period"] * q
    return {"name": name, "src": src, "q": q, "k": k, "L": L, "M": L * k, "label": label,
            "seconds": secs, "why": why}


def base_set(cfg):
    return sorted(cfg["q"] * x for x in SOURCES[cfg["src"]]["A"])


@functools.lru_cache(maxsize=None)
def _known(src, q):
    L = SOURCES[src]["period"] * q
    base = sorted(q * x for x in SOURCES[src]["A"])
    return {d: vanishes_rows(base, d) for d in divisors(L) if d > 1}


def known_orders(cfg):
    """{d: Phi_d | A} for every d > 1 dividing L; fixed because A = base mod L."""
    return _known(cfg["src"], cfg["q"])


def config_cases(cfg):
    """Every tile control and T2 case of one configuration."""
    M, L = cfg["M"], cfg["L"]
    base = base_set(cfg)
    a = len(base)
    known = known_orders(cfg)
    out = []
    for SA in profiles(M, a):
        if any((qq in SA) != known[qq] for qq in all_prime_powers(M) if L % qq == 0):
            continue
        SB = complement_profile(M, SA)
        common = {"cfg": cfg["name"], "label": cfg["label"], "src": cfg["src"], "q": cfg["q"], "k": cfg["k"],
                  "L": L, "M": M, "a": a, "b": M // a, "SA": list(SA), "SB": list(SB)}
        out.append(dict(common, mode="tile", side=None, s=None, decided=None))
        for side, S in (("B", SB), ("A", SA)):
            for s in t2_products(S):
                decided = None
                if L % s == 0:
                    if side == "B" and not known[s]:
                        decided = "Phi_%d does not divide A (fixed mod L), so every complement B has it" % s
                    if side == "A" and known[s]:
                        decided = "Phi_%d divides A (fixed mod L)" % s
                out.append(dict(common, mode="t2", side=side, s=s, decided=decided))
    return out


# ------------------------------------------------------------ CP-SAT model
def _lin(row, c):
    return sum(v * c[r] for r, v in row)


def _tree(model, xs, M, tag, size, L=None):
    """Residue counts c[d] for divisors d of M (c[d][r] = sum of c[dp][r + d i]).
    With L given, only divisors not dividing L are built (the rest are fixed)."""
    c = {M: xs}
    for d in sorted(divisors(M), reverse=True):
        if d == M or d == 1:
            continue
        if L is not None and L % d == 0:
            continue
        p = parent_prime(M, d)
        par = c[d * p]
        cur = []
        for r in range(d):
            v = model.new_int_var(0, min(M // d, size), "%s_c%d_%d" % (tag, d, r))
            model.add(v == sum(par[r + d * i] for i in range(p)))
            cur.append(v)
        c[d] = cur
    return c


def verify(case, base, A, B):
    """Re-check a solver answer from scratch."""
    M, L = case["M"], case["L"]
    errs = []
    if len(set(A)) != case["a"] or len(set(B)) != case["b"]:
        errs.append("sizes")
    if sorted(x % L for x in A) != sorted(base):
        errs.append("A is not a lift of the source")
    if not is_tiling(A, B, M):
        errs.append("not a tiling")
    for sd, X, S in (("A", A, case["SA"]), ("B", B, case["SB"])):
        for qq in S:
            if not (vanishes_rows(X, qq) and vanishes_numeric(X, qq)):
                errs.append("profile %s Phi_%d" % (sd, qq))
    out = {}
    if case["mode"] == "t2":
        X = A if case["side"] == "A" else B
        r, n = vanishes_rows(X, case["s"]), vanishes_numeric(X, case["s"])
        out["s_vanishes_rows"], out["s_vanishes_numeric"] = r, n
        if r or n:
            errs.append("Phi_%d divides %s after all" % (case["s"], case["side"]))
    out["errors"] = errs
    out["verified"] = not errs
    return out


def solve_case(case, cfg, seconds, workers=1, seed=1):
    from ortools.sat.python import cp_model  # imported here: tests stay pure Python

    M, L, k = case["M"], case["L"], case["k"]
    a, b = case["a"], case["b"]
    base = base_set(cfg)
    bset = set(base)
    known = known_orders(cfg)
    mode, side, s = case["mode"], case["side"], case["s"]
    model = cp_model.CpModel()

    xb = [model.new_bool_var("b%d" % x) for x in range(M)]
    model.add(sum(xb) == b)
    model.add(xb[0] == 1)
    cb = _tree(model, xb, M, "B", b)
    if k > 1:
        xa = [model.new_bool_var("a%d" % x) for x in range(M)]
        for r in range(L):
            model.add(sum(xa[r + L * i] for i in range(k)) == (1 if r in bset else 0))
        model.add(xa[0] == 1)  # translate by a multiple of L: 0 is in every lift's base
        ca = _tree(model, xa, M, "A", a, L)
    else:
        xa, ca = None, {}

    def need(c, d, lit=None):
        for row in vanish_rows(d):
            ct = model.add(_lin(row, c[d]) == 0)
            if lit is not None:
                ct.only_enforce_if(lit)

    def fail(c, d):
        lits = []
        for i, row in enumerate(vanish_rows(d)):
            w = model.new_bool_var("w%d_%d" % (d, i))
            model.add(_lin(row, c[d]) != 0).only_enforce_if(w)
            lits.append(w)
        model.add_bool_or(lits)

    for qq in case["SA"]:
        if L % qq:
            need(ca, qq)
    for qq in case["SB"]:
        need(cb, qq)
    for d in mixed_divisors(M):
        if mode == "t2" and d == s:
            continue
        if L % d == 0:
            if not known[d]:
                need(cb, d)
        else:
            z = model.new_bool_var("z%d" % d)  # 1: Phi_d | A required
            y = model.new_bool_var("y%d" % d)  # 1: Phi_d | B required
            model.add(z + y == 1)
            need(ca, d, z)
            need(cb, d, y)
    if mode == "t2":
        if side == "B":
            if L % s:
                need(ca, s)
            fail(cb, s)
        else:
            need(cb, s)
            if L % s:
                fail(ca, s)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(seconds)
    try:
        solver.parameters.num_workers = int(workers)
    except (AttributeError, ValueError):
        solver.parameters.num_search_workers = int(workers)
    solver.parameters.random_seed = int(seed)
    t0 = time.time()
    status = solver.solve(model)
    name = solver.status_name(status)
    rec = dict(case, time_limit=seconds, wall=round(time.time() - t0, 2), solver_status=name)
    if name in ("OPTIMAL", "FEASIBLE"):
        B = [x for x in range(M) if solver.value(xb[x])]
        A = base if xa is None else [x for x in range(M) if solver.value(xa[x])]
        chk = verify(case, base, A, B)
        rec["check"], rec["sets"] = chk, {"A": A, "B": B}
        rec["status"] = "FEASIBLE" if chk["verified"] else "FEASIBLE_UNVERIFIED"
        if chk["verified"]:
            rec["t2_report"] = {"A": t2_report(A, M), "B": t2_report(B, M)}
    else:
        rec["status"] = name
    return rec


# ------------------------------------------------------------------ runner
def summarize(records, sources, configs, meta):
    per = {}
    for r in records:
        P = per.setdefault(r["cfg"], {"label": r["label"], "M": r["M"], "tile": {}, "t2": {}})
        P[r["mode"]][r["status"]] = P[r["mode"]].get(r["status"], 0) + 1
    t2 = [r for r in records if r["mode"] == "t2"]
    feas = ("FEASIBLE", "FEASIBLE_UNVERIFIED")
    ran = [c["name"] for c in configs]
    tile_ok = all(any(r["cfg"] == n and r["mode"] == "tile" and r["status"] == "FEASIBLE" for r in records)
                  for n in ran if any(r["cfg"] == n for r in records))
    s6 = [r for r in t2 if r["src"] == "S180" and r["q"] == 1 and r["side"] == "B" and r["s"] == 6]
    strength = {}
    for lab in ("theorem", "open"):
        rs = [r for r in t2 if r["label"] == lab]
        strength[lab] = {st: sum(1 for r in rs if r["status"] == st) for st in sorted({r["status"] for r in rs})}
    cands = [r for r in t2 if r["label"] == "open" and r["status"] == "FEASIBLE"]
    return {
        "version": VERSION, **meta,
        "sources": sources,
        "per_config": per,
        "t2_status_by_label": strength,
        "predictions": {
            "L1_sources_verified_with_unsupported_divisor": all(v["ok"] for v in sources.values()),
            "L2_every_config_has_a_verified_tiling": tile_ok,
            "L3_no_feasible_t2_case_where_T2_is_a_theorem": not any(
                r["label"] == "theorem" and r["status"] in feas for r in t2),
            "L4_no_verified_T2_failure_in_open_configs": not cands,
            "L5_S180_Phi6_cases_all_infeasible": bool(s6) and all(
                r["status"] in ("INFEASIBLE", "DECIDED_INFEASIBLE") for r in s6),
        },
        "bug_flags": {
            "unverified_feasible": sum(1 for r in records if r["status"] == "FEASIBLE_UNVERIFIED"),
            "model_invalid_or_error": sum(1 for r in records if r["status"] in ("MODEL_INVALID", "ERROR")),
            "theorem_violations": sum(1 for r in t2 if r["label"] == "theorem" and r["status"] == "FEASIBLE"),
        },
        "T2_COUNTEREXAMPLE_CANDIDATES": len(cands),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--configs", default="", help="comma-separated config names (default: all)")
    ap.add_argument("--control-seconds", type=float, default=60.0)
    ap.add_argument("--time-scale", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--total-minutes", type=float, default=320.0)
    ap.add_argument("--list", action="store_true", help="print the plan and exit (no solver needed)")
    args = ap.parse_args(argv)

    configs = [config_dict(r) for r in CONFIGS]
    if args.configs:
        want = set(args.configs.split(","))
        configs = [c for c in configs if c["name"] in want]
    sources = {n: source_report(n) for n in sorted({c["src"] for c in configs})}
    plan = []
    for c in configs:
        cs = config_cases(c)
        plan.append({"cfg": c["name"], "M": c["M"], "label": c["label"], "why": c["why"],
                     "profiles": len([x for x in cs if x["mode"] == "tile"]),
                     "t2_to_solve": [(x["side"], x["s"]) for x in cs if x["mode"] == "t2" and not x["decided"]],
                     "t2_decided": len([x for x in cs if x["mode"] == "t2" and x["decided"]])})
    if args.list:
        print(json.dumps({"sources": sources, "plan": plan}, indent=1))
        return 0

    os.makedirs(args.out_dir, exist_ok=True)
    jpath = os.path.join(args.out_dir, "liftsat_results.jsonl")
    spath = os.path.join(args.out_dir, "liftsat_summary.json")
    cpath = os.path.join(args.out_dir, "T2_COUNTEREXAMPLE_CANDIDATES.json")
    with open(os.path.join(args.out_dir, "liftsat_plan.json"), "w") as f:
        json.dump({"sources": sources, "plan": plan}, f, indent=1)
    t_start = time.time()
    budget = args.total_minutes * 60.0
    records = []
    meta = {"started_unix": t_start, "workers": args.workers, "seed": args.seed,
            "time_scale": args.time_scale, "control_seconds": args.control_seconds}

    def emit(rec):
        records.append(rec)
        with open(jpath, "a") as f:
            f.write(json.dumps(rec) + "\n")
        with open(spath, "w") as f:
            json.dump(summarize(records, sources, configs, dict(meta, elapsed_s=round(time.time() - t_start, 1))),
                      f, indent=1)
        if rec["mode"] == "t2" and rec["status"] in ("FEASIBLE", "FEASIBLE_UNVERIFIED"):
            found = [r for r in records if r["mode"] == "t2" and r["status"] in ("FEASIBLE", "FEASIBLE_UNVERIFIED")]
            with open(cpath, "w") as f:
                json.dump(found, f, indent=1)
        print("%-10s %-4s M=%d SA=%s side=%s s=%s -> %s (%.1fs)" % (
            rec["cfg"], rec["mode"], rec["M"], rec["SA"], rec["side"], rec["s"], rec["status"],
            rec.get("wall", 0.0)), flush=True)

    print("liftsat %s" % VERSION, flush=True)
    for c in configs:
        if not sources[c["src"]]["ok"]:
            print("source %s failed verification; skipping %s" % (c["src"], c["name"]), flush=True)
            continue
        for case in config_cases(c):
            if case["decided"]:
                emit(dict(case, status="DECIDED_INFEASIBLE", wall=0.0))
                continue
            limit = args.control_seconds if case["mode"] == "tile" else c["seconds"] * args.time_scale
            if time.time() - t_start > budget:
                emit(dict(case, status="SKIPPED_BUDGET", wall=0.0))
                continue
            try:
                rec = solve_case(case, c, limit, args.workers, args.seed)
            except Exception:
                rec = dict(case, status="ERROR", wall=0.0, error=traceback.format_exc()[-2000:])
            emit(rec)
    doc = summarize(records, sources, configs, dict(meta, elapsed_s=round(time.time() - t_start, 1), finished=True))
    with open(spath, "w") as f:
        json.dump(doc, f, indent=1)
    print(json.dumps(doc["predictions"]), flush=True)
    print(json.dumps(doc["t2_status_by_label"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
