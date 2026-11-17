# SPDX-License-Identifier: Apache-2.0
# Cyclotomic-profile search for counterexamples to the Coven-Meyerowitz
# condition T2 at a fixed period. Part of vuza-canons.
# Made by MV2 of Munim, Inc., with AI agents. Licensed under the Apache License 2.0.
"""profsat: search EVERY tiling of Z_M with given factor sizes for a T2 failure.

closure.py samples Vuza canons one rhythm at a time. This module asks the
question for all tilings at once, as a constraint problem.

Facts used (all standard):
  F1  A (+) B = Z_M  iff  |A| |B| = M and, for every d | M with d > 1, the
      cyclotomic polynomial Phi_d divides A(x) or B(x). (Fourier: the
      convolution 1_A * 1_B is constant iff A^(xi) B^(xi) = 0 for xi != 0.)
  F2  Phi_d | X(x) depends only on the residue counts c_r = #{x in X : x = r
      mod d}, and is LINEAR in them: with m = rad(d) and k = d / m,
      Phi_d(x) = Phi_m(x^k), so Phi_d | X iff for every t < k the polynomial
      sum_j c_{t+kj} y^j (j < m) has zero remainder mod Phi_m(y). Every
      remainder coefficient is an integer linear form in the c's
      (vanish_rows). m is squarefree and divides M, so Phi_m is tiny.
  F3  T1 holds for every tile (Coven-Meyerowitz). So for each prime p,
      exactly v_p(|A|) of the prime powers p, p^2, ..., p^e dividing M have
      Phi_{p^k} | A, and the other ones divide B. We call such a split a
      PROFILE. At M = 1800 = 2^3 3^2 5^2 with |A| = 30 there are 12 profiles.
  F4  T2 for A with profile S_A asks Phi_s | A for every product s of powers
      of distinct primes taken from S_A (at least two primes).

So a counterexample to T2 at (M, |A|) exists iff, for some profile and some
T2 product s of one side, the following has a 0/1 solution: A, B subsets of
Z_M containing 0 with the given sizes, the profile's prime powers dividing
the right side, every mixed divisor d (two or more primes) dividing A or B
(a boolean z_d chooses), and Phi_s NOT dividing the side that should have
it. Translations are free, so 0 in A and 0 in B loses nothing.

Each such case is one CP-SAT model (OR-Tools). INFEASIBLE for every case would
mean T2 holds for every tiling of Z_M with these sizes. That is a
computer-assisted claim that depends on the solver; it would need an
independent second check (a different solver, ideally with a proof
certificate) before being called a theorem. UNKNOWN is reported as UNKNOWN.

Controls run before the open period:
  tile   the model without the T2-failure part must find a real tiling for
         every profile (the Coven-Meyerowitz standard sets show one exists);
         every tiling found is re-checked by direct counting.
  aonly  one side alone with the failure part must find a set that fails the
         divisibility, re-checked exactly: proves the "!= 0" encoding works.
  t2     at periods where T2 is a theorem (360 with sizes 30/12, 900 with
         30/30), no case may be FEASIBLE. How many come back INFEASIBLE
         within the time limit measures how strong the method is.

Usage:
  python profsat.py --out-dir out --periods 360:30,900:30,1800:30 \
      --seconds 20,40,90 --control-seconds 20 --workers 2 --total-minutes 300
Needs: pip install -r requirements-sat.txt (ortools). Everything except the
solver itself is pure Python and tested in test_profsat.py.
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

VERSION = "0.4.0"

# Periods where T2 is a published theorem for these factor sizes (validation).
KNOWN_BY_THEOREM = {
    (360, 30): "Laba-Londner Cor. 6.2 (only 2 and 3 divide both 30 and 12) + Coven-Meyerowitz",
    (900, 30): "Laba-Londner, T2 for every tiling of period p^2 q^2 r^2 (2023, 2025)",
}


# ---------------------------------------------------------------- arithmetic
def factorize(n):
    """Prime factorisation as {prime: exponent}."""
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
    """Product of the distinct primes dividing n."""
    return prod(factorize(n))


def euler_phi(n):
    r = n
    for p in factorize(n):
        r = r // p * (p - 1)
    return r


def prime_of(q):
    """The prime of a prime power q > 1."""
    f = factorize(q)
    if len(f) != 1:
        raise ValueError("not a prime power: %d" % q)
    return next(iter(f))


def mixed_divisors(M):
    """Divisors of M with at least two distinct prime factors."""
    return [d for d in divisors(M) if d > 1 and len(factorize(d)) >= 2]


def prime_power_list(M):
    """{p: [p, p^2, ..., p^e]} for p^e || M."""
    f = factorize(M)
    return {p: [p ** k for k in range(1, f[p] + 1)] for p in sorted(f)}


def all_prime_powers(M):
    return sorted(q for qs in prime_power_list(M).values() for q in qs)


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
    """Remainder of integer polynomial a by monic b (coefficient lists, low
    degree first). len(a) must be at least len(b)."""
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
    """Coefficients (low first) of the d-th cyclotomic polynomial."""
    if d in _CYC:
        return _CYC[d]
    num = [-1] + [0] * (d - 1) + [1]  # x^d - 1
    for e in divisors(d):
        if e < d:
            num = poly_exact_div(num, cyclotomic(e))
    _CYC[d] = num
    return num


@functools.lru_cache(maxsize=None)
def rem_table(m):
    """Row j (j = 0..m-1) holds the phi(m) coefficients of x^j mod Phi_m."""
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
    """Linear forms on residue counts c (length d) whose simultaneous
    vanishing is equivalent to Phi_d | X (fact F2). Each form is a tuple of
    (residue r, integer coefficient). There are phi(d) forms."""
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
    """Exact integer test of Phi_d | X(x) through the linear forms."""
    c = residues(xs, d)
    for row in vanish_rows(d):
        if sum(v * c[r] for r, v in row) != 0:
            return False
    return True


def vanishes_numeric(xs, d):
    """Independent test: X(zeta_d^u) = 0 for every unit u. A nonzero algebraic
    integer has a conjugate of absolute value >= 1 (its norm is a nonzero
    integer), so 'every conjugate below 0.5' is exact, not a threshold."""
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


def parent_prime(M, d):
    """Smallest prime p with d * p | M (d a proper divisor of M)."""
    for p in sorted(factorize(M)):
        if (M // d) % p == 0:
            return p
    raise ValueError("d must be a proper divisor of M")


def residue_tree(xs, M):
    """Residue counts for every divisor d > 1 of M, built the same way the
    model builds them: c_d[r] = sum_{i < p} c_{dp}[r + d i]."""
    c = {M: residues(xs, M)}
    for d in sorted(divisors(M), reverse=True):
        if d == M or d == 1:
            continue
        p = parent_prime(M, d)
        par = c[d * p]
        c[d] = [sum(par[r + d * i] for i in range(p)) for r in range(d)]
    return c


# ------------------------------------------------------------------ profiles
def profiles(M, a):
    """Every T1-consistent profile for |A| = a: A gets v_p(a) of the powers of
    each prime p of M; B gets the rest (fact F3). Sorted tuples S_A."""
    if a < 1 or M % a:
        raise ValueError("a must divide M")
    pp = prime_power_list(M)
    fa = factorize(a)
    choices = [list(itertools.combinations(pp[p], fa.get(p, 0))) for p in sorted(pp)]
    return [tuple(sorted(q for part in combo for q in part)) for combo in itertools.product(*choices)]


def complement_profile(M, SA):
    return tuple(sorted(set(all_prime_powers(M)) - set(SA)))


def t2_products(S):
    """Products of powers of at least two distinct primes, at most one power
    per prime, taken from the prime-power set S (fact F4)."""
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


def standard_set(S, M):
    """Coven-Meyerowitz standard set: prod over q = p^k in S of
    Phi_p(x^(p^(k-1) t_p)), t_p = M / p^(v_p M). A genuine set of size
    prod(p) that satisfies T1 and T2."""
    f = factorize(M)
    pts = [0]
    for q in sorted(S):
        p = prime_of(q)
        k = factorize(q)[p]
        step = p ** (k - 1) * (M // p ** f[p])
        pts = [(x + i * step) % M for x in pts for i in range(p)]
    return sorted(pts)


def make_case(M, a, SA, side=None, s=None):
    return {"M": M, "a": a, "b": M // a, "SA": list(SA), "SB": list(complement_profile(M, SA)),
            "side": side, "s": s}


def cases(M, a):
    """Every (profile, failing side, missing T2 product) for sizes a, M/a."""
    out = []
    for SA in profiles(M, a):
        SB = complement_profile(M, SA)
        for side, S in (("A", SA), ("B", SB)):
            for s in t2_products(S):
                out.append(make_case(M, a, SA, side, s))
    return out


def t2_report(X, M):
    """Independent T1/T2 status of a set: prime powers it vanishes at, T1,
    and every failing T2 product (both exact tests must agree)."""
    S = [q for q in all_prime_powers(M) if vanishes_rows(X, q)]
    S_num = [q for q in all_prime_powers(M) if vanishes_numeric(X, q)]
    t1 = len(set(X)) == prod(prime_of(q) for q in S)
    fails = [s for s in t2_products(S) if not vanishes_rows(X, s)]
    fails_num = [s for s in t2_products(S) if not vanishes_numeric(X, s)]
    return {"S": S, "S_numeric_agrees": S == S_num, "t1": t1, "t2_failures": fails,
            "t2_numeric_agrees": fails == fails_num}


def check_sets(case, sets, mode):
    """Re-check a solver answer from scratch. sets: {"A": list or None,
    "B": list or None}."""
    M = case["M"]
    size = {"A": case["a"], "B": case["b"]}
    prof = {"A": case["SA"], "B": case["SB"]}
    out = {"errors": []}
    for side in ("A", "B"):
        X = sets.get(side)
        if X is None:
            continue
        if len(set(X)) != size[side] or 0 not in X:
            out["errors"].append("size or 0 wrong on %s" % side)
        for q in prof[side]:
            r, n = vanishes_rows(X, q), vanishes_numeric(X, q)
            if not (r and n):
                out["errors"].append("profile %s: Phi_%d rows=%s numeric=%s" % (side, q, r, n))
    if sets.get("A") is not None and sets.get("B") is not None:
        out["tiling"] = is_tiling(sets["A"], sets["B"], M)
        if not out["tiling"]:
            out["errors"].append("not a tiling")
    if mode in ("t2", "aonly"):
        X = sets.get(case["side"])
        r, n = vanishes_rows(X, case["s"]), vanishes_numeric(X, case["s"])
        out["s_vanishes_rows"], out["s_vanishes_numeric"] = r, n
        if r or n:
            out["errors"].append("Phi_%d divides %s after all" % (case["s"], case["side"]))
    out["verified"] = not out["errors"]
    return out


# ------------------------------------------------------------ CP-SAT model
def _lin(row, c):
    return sum(v * c[r] for r, v in row)


def solve_case(case, mode, seconds, workers=1, seed=1):
    """Build and solve one model. Returns a result record (dict)."""
    from ortools.sat.python import cp_model  # imported here: tests stay pure Python

    M = case["M"]
    size = {"A": case["a"], "B": case["b"]}
    prof = {"A": case["SA"], "B": case["SB"]}
    sides = ["A", "B"] if mode in ("t2", "tile") else [case["side"]]
    model = cp_model.CpModel()
    X, C, z = {}, {}, {}
    for side in sides:
        xs = [model.new_bool_var("%s%d" % (side, x)) for x in range(M)]
        model.add(sum(xs) == size[side])
        model.add(xs[0] == 1)
        c = {M: xs}
        for d in sorted(divisors(M), reverse=True):
            if d == M or d == 1:
                continue
            p = parent_prime(M, d)
            par = c[d * p]
            cur = []
            for r in range(d):
                v = model.new_int_var(0, min(M // d, size[side]), "%s_c%d_%d" % (side, d, r))
                model.add(v == sum(par[r + d * i] for i in range(p)))
                cur.append(v)
            c[d] = cur
        X[side], C[side] = xs, c
        for q in prof[side]:
            for row in vanish_rows(q):
                model.add(_lin(row, c[q]) == 0)
    if mode in ("t2", "tile"):
        for d in mixed_divisors(M):
            zd = model.new_bool_var("z%d" % d)  # 1: Phi_d | A required; 0: Phi_d | B required
            yd = model.new_bool_var("y%d" % d)
            model.add(zd + yd == 1)
            for row in vanish_rows(d):
                model.add(_lin(row, C["A"][d]) == 0).only_enforce_if(zd)
                model.add(_lin(row, C["B"][d]) == 0).only_enforce_if(yd)
            z[d] = zd
    if mode in ("t2", "aonly"):
        side, s = case["side"], case["s"]
        if mode == "t2":
            model.add(z[s] == (0 if side == "A" else 1))
        lits = []
        for i, row in enumerate(vanish_rows(s)):
            w = model.new_bool_var("w%d_%d" % (s, i))
            model.add(_lin(row, C[side][s]) != 0).only_enforce_if(w)
            lits.append(w)
        model.add_bool_or(lits)

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
    rec = {"mode": mode, "M": M, "a": case["a"], "b": case["b"], "SA": case["SA"], "SB": case["SB"],
           "side": case["side"], "s": case["s"], "time_limit": seconds,
           "wall": round(time.time() - t0, 2), "solver_status": name}
    if name in ("OPTIMAL", "FEASIBLE"):
        sets = {sd: [x for x in range(M) if solver.value(X[sd][x])] for sd in sides}
        chk = check_sets(case, sets, mode)
        rec["check"] = chk
        rec["sets"] = sets
        rec["status"] = "FEASIBLE" if chk["verified"] else "FEASIBLE_UNVERIFIED"
        if mode == "t2" and chk["verified"]:
            rec["t2_report"] = {sd: t2_report(sets[sd], M) for sd in sides}
    else:
        rec["status"] = name  # INFEASIBLE, UNKNOWN or MODEL_INVALID
    return rec


# ------------------------------------------------------------------ runner
def _count(records, key, mode, status):
    return sum(1 for r in records if (r["M"], r["a"]) == key and r["mode"] == mode and r["status"] == status)


def summarize(records, plan, meta):
    per = {}
    for r in records:
        k = "%d:%d" % (r["M"], r["a"])
        P = per.setdefault(k, {"tile": {}, "aonly": {}, "t2": {}})
        P[r["mode"]][r["status"]] = P[r["mode"]].get(r["status"], 0) + 1
    known = [key for key in plan if key in KNOWN_BY_THEOREM]
    opened = [key for key in plan if key not in KNOWN_BY_THEOREM]
    bad = ("FEASIBLE", "FEASIBLE_UNVERIFIED")
    p13 = all(_count(records, key, "t2", b) == 0 for key in known for b in bad)
    tiles = [r for r in records if r["mode"] == "tile"]
    p14 = bool(tiles) and all(r["status"] == "FEASIBLE" for r in tiles)
    aon = [r for r in records if r["mode"] == "aonly"]
    p15 = bool(aon) and all(r["status"] == "FEASIBLE" for r in aon)
    cands = [r for r in records if r["mode"] == "t2" and r["status"] == "FEASIBLE"]
    p16 = not any((r["M"], r["a"]) in opened for r in cands)
    strength = {}
    for key in known:
        tot = sum(1 for r in records if (r["M"], r["a"]) == key and r["mode"] == "t2")
        inf = _count(records, key, "t2", "INFEASIBLE") + _count(records, key, "t2", "INFEASIBLE_BY_TILE")
        strength["%d:%d" % key] = {"t2_cases_run": tot, "proved_infeasible": inf}
    open_status = {}
    for key in opened:
        n_cases = len(cases(*key))
        tot = sum(1 for r in records if (r["M"], r["a"]) == key and r["mode"] == "t2")
        inf = _count(records, key, "t2", "INFEASIBLE") + _count(records, key, "t2", "INFEASIBLE_BY_TILE")
        open_status["%d:%d" % key] = {"t2_cases_total": n_cases, "t2_cases_run": tot, "proved_infeasible": inf,
                                      "all_cases_infeasible": inf == n_cases}
    return {
        "version": VERSION, **meta,
        "per_period": per,
        "validation_strength": strength,
        "open_periods": open_status,
        "predictions": {
            "P13_no_feasible_t2_case_where_T2_is_a_theorem": p13,
            "P14_every_profile_has_a_verified_tiling": p14,
            "P15_every_aonly_control_feasible_and_verified": p15,
            "P16_no_verified_T2_failure_at_open_periods": p16,
        },
        "bug_flags": {
            "unverified_feasible": sum(1 for r in records if r["status"] == "FEASIBLE_UNVERIFIED"),
            "model_invalid_or_error": sum(1 for r in records if r["status"] in ("MODEL_INVALID", "ERROR")),
        },
        "T2_COUNTEREXAMPLE_CANDIDATES": len([r for r in cands if (r["M"], r["a"]) in opened]),
    }


def parse_periods(text):
    out = []
    for part in text.split(","):
        M, a = part.split(":")
        out.append((int(M), int(a)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--periods", default="360:30,900:30,1800:30")
    ap.add_argument("--seconds", default="20,40,90", help="t2 time limit per case, one per period")
    ap.add_argument("--control-seconds", type=float, default=20.0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--total-minutes", type=float, default=300.0)
    ap.add_argument("--modes", default="tile,aonly,t2")
    args = ap.parse_args(argv)

    plan = parse_periods(args.periods)
    secs = [float(x) for x in args.seconds.split(",")]
    if len(secs) == 1:
        secs = secs * len(plan)
    modes = set(args.modes.split(","))
    os.makedirs(args.out_dir, exist_ok=True)
    jpath = os.path.join(args.out_dir, "profsat_results.jsonl")
    spath = os.path.join(args.out_dir, "profsat_summary.json")
    cpath = os.path.join(args.out_dir, "T2_COUNTEREXAMPLE_CANDIDATES.json")
    t_start = time.time()
    budget = args.total_minutes * 60.0
    records = []
    meta = {"started_unix": t_start, "periods": args.periods, "seconds": args.seconds,
            "control_seconds": args.control_seconds, "workers": args.workers, "seed": args.seed,
            "known_by_theorem": {"%d:%d" % k: v for k, v in KNOWN_BY_THEOREM.items()}}

    def emit(rec):
        records.append(rec)
        with open(jpath, "a") as f:
            f.write(json.dumps(rec) + "\n")
        doc = summarize(records, plan, dict(meta, elapsed_s=round(time.time() - t_start, 1)))
        with open(spath, "w") as f:
            json.dump(doc, f, indent=1)
        if rec["mode"] == "t2" and rec["status"] in ("FEASIBLE", "FEASIBLE_UNVERIFIED"):
            found = [r for r in records if r["mode"] == "t2" and r["status"] in ("FEASIBLE", "FEASIBLE_UNVERIFIED")]
            with open(cpath, "w") as f:
                json.dump(found, f, indent=1)
        print("%-5s M=%d a=%d SA=%s side=%s s=%s -> %s (%.1fs)" % (
            rec["mode"], rec["M"], rec["a"], rec["SA"], rec["side"], rec["s"], rec["status"],
            rec.get("wall", 0.0)), flush=True)

    def run(case, mode, limit):
        if time.time() - t_start > budget:
            rec = dict(case, mode=mode, status="SKIPPED_BUDGET", wall=0.0)
        else:
            try:
                rec = solve_case(case, mode, limit, args.workers, args.seed)
            except Exception:
                rec = dict(case, mode=mode, status="ERROR", wall=0.0, error=traceback.format_exc()[-2000:])
        emit(rec)
        return rec

    print("profsat %s: periods %s" % (VERSION, plan), flush=True)
    for (M, a), limit in zip(plan, secs):
        untilable = set()
        if "tile" in modes:
            for SA in profiles(M, a):
                rec = run(make_case(M, a, SA), "tile", args.control_seconds)
                if rec["status"] == "INFEASIBLE":
                    untilable.add(tuple(SA))
        if "aonly" in modes:
            SA0 = profiles(M, a)[0]
            SB0 = complement_profile(M, SA0)
            for side, S in (("A", SA0), ("B", SB0)):
                for s in t2_products(S):
                    run(make_case(M, a, SA0, side, s), "aonly", args.control_seconds)
        if "t2" in modes:
            for case in cases(M, a):
                if tuple(case["SA"]) in untilable:
                    emit(dict(case, mode="t2", status="INFEASIBLE_BY_TILE", wall=0.0))
                else:
                    run(case, "t2", limit)
    doc = summarize(records, plan, dict(meta, elapsed_s=round(time.time() - t_start, 1), finished=True))
    with open(spath, "w") as f:
        json.dump(doc, f, indent=1)
    print(json.dumps(doc["predictions"]), flush=True)
    print("open periods:", json.dumps(doc["open_periods"]), flush=True)
    print("validation:", json.dumps(doc["validation_strength"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
