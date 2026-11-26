# SPDX-License-Identifier: Apache-2.0
# The last route is closed: no lift of the Tan-Zhang tiles has a complement missing Phi_6.
# Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""phi6close: Phi_6 divides every complement of every lift (5-smooth periods).

Setting. X is S180 or C180 (Tan-Zhang, arXiv:2609.06677), |X| = 30, period 180,
S_X = {4, 5, 9}, unsupported divisor Phi_6. A lift of X to Z_M, M = 180k, is a
set A with A = X mod 180. Suppose A (+) B = Z_M and write M = 2^a 3^b 5^e
(so k = 2^(a-2) 3^(b-2) 5^(e-1): k has no prime factor other than 2, 3, 5).

Theorem (notes/phi6_close.md). Phi_6 divides B. With the 0.6.0 route theorem
(notes/lift_routes.md) every tiling of a lift then satisfies T2.

Proof in one paragraph. Fold mod 30: B_30(x) = w(x mod 5) + v(x mod 6) with
integer w, v, sum of w = k, v = (p, p+r, r, -p, -p-r, -r), and Phi_6 | B iff
v = 0 (0.5.1 fold proposition). Three periodicity lemmas:
  (2) Phi_N | B for N = 2^j and 3*2^j (3 <= j <= a)  =>  B_{3*2^a} is
      12-periodic  =>  2^(a-2) divides every value of B_12, hence of B_6;
  (3) Phi_N | B for N = 3^j and 2*3^j (3 <= j <= b)  =>  B_{2*3^b} is
      18-periodic  =>  3^(b-2) divides every value of B_18, hence of B_6;
  (5) Phi_N | B for N = 5^l, 2*5^l, 3*5^l, 6*5^l (2 <= l <= e)  =>
      B_{6*5^e} is 30-periodic  =>  5^(e-1) divides every value of B_30.
The prime powers lie in S_B (T1 bookkeeping); the other orders are T2 routes
that no lift can carry (0.6.0), so tiling puts them in B. Since
B_6(y) = k + 5 v(y) and 5^(e-1) | w(a), this gives k | v(y) for every y. If
v != 0 then min v <= -k, so w(a) >= k for all five a (B_30 >= 0), and
sum w >= 5k > k: a contradiction. So v = 0 and Phi_6 | B.

This module re-checks every finite step exactly:
  * the tile facts (S_X, the fold-30 kernel hypotheses) by exact polynomial
    division by cyclotomic polynomials;
  * that every order the proof needs in B is a prime power in S_B or is
    excluded for every lift by the sound engine of liftroutes.py (copied here,
    so the module is self-contained);
  * each periodicity lemma, as an exact statement about frequencies of Z_m;
  * the profile arithmetic: the mod-30 profiles allowed before (0.5.1 counts:
    30 at k = 6, 450 at k = 30) and after the new divisibility (none).

Usage:
  python phi6close.py --out-dir out
"""
import argparse
import functools
import json
import math
import os
import sys

VERSION = "0.7.0"
PERIOD = 180

SOURCES = {
    "S180": {
        "A": sorted(30 * j + c for j in range(6) for c in (0, 2, 3, 4, 6)),
        "B": [0, 5, 10, 15, 20, 25],
    },
    "C180": {
        "A": [0, 2, 4, 12, 21, 34, 36, 38, 48, 51, 60, 62, 64, 72, 75, 90, 94, 98, 108, 111,
              122, 124, 126, 132, 141, 150, 154, 158, 165, 168],
        "B": [0, 20, 40, 45, 65, 85],
    },
}
SOURCE_NAMES = ("S180", "C180")


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


# every k <= 60 whose prime factors are among 2, 3 and 5 (26 values)
KS = [k for k in range(1, 61) if set(factorize(k)) <= {2, 3, 5}]


def exps(k):
    """(a, b, e) with 180k = 2^a 3^b 5^e (k must be 5-smooth)."""
    f = factorize(PERIOD * k)
    if set(f) - {2, 3, 5}:
        raise ValueError("k must have no prime factor other than 2, 3, 5")
    return f.get(2, 0), f.get(3, 0), f.get(5, 0)


def is_prime_power(n):
    return n > 1 and len(factorize(n)) == 1


# ------------------------------------------------- exact cyclotomic division
def poly_divmod(num, den):
    """Integer polynomials as coefficient lists, lowest degree first; den monic.
    Returns (quotient, remainder)."""
    num = list(num)
    dd = len(den) - 1
    if den[dd] != 1:
        raise ValueError("divisor must be monic")
    if len(num) - 1 < dd:
        return [0], num
    q = [0] * (len(num) - dd)
    for i in range(len(num) - 1, dd - 1, -1):
        c = num[i]
        if c:
            q[i - dd] = c
            for j in range(dd + 1):
                num[i - dd + j] -= c * den[j]
    return q, num[:dd]


@functools.lru_cache(maxsize=None)
def cyclotomic(n):
    """Phi_n as a tuple of integer coefficients, lowest degree first."""
    p = [-1] + [0] * (n - 1) + [1]  # x^n - 1
    for d in range(1, n):
        if n % d == 0:
            p, r = poly_divmod(p, list(cyclotomic(d)))
            if any(r):
                raise ArithmeticError("cyclotomic recursion failed at %d" % n)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def phi_divides(N, pts):
    """Exact test of Phi_N | sum x^y over the multiset pts (residues taken mod N)."""
    poly = [0] * N
    for y in pts:
        poly[y % N] += 1
    _, r = poly_divmod(poly, list(cyclotomic(N)))
    return not any(r)


def fold(pts, m):
    """Residue counts of a multiset of integers modulo m."""
    out = [0] * m
    for y in pts:
        out[y % m] += 1
    return out


def is_tiling(A, B, M):
    seen = [0] * M
    for a in A:
        for b in B:
            seen[(a + b) % M] += 1
    return all(c == 1 for c in seen)


# ------------------------------------- the sound engine of liftroutes (0.6.0)
@functools.lru_cache(maxsize=None)
def in_semigroup(c, gens):
    ok = [False] * (c + 1)
    ok[0] = True
    for v in range(1, c + 1):
        ok[v] = any(v >= g and ok[v - g] for g in gens)
    return ok[c]


def _canon(elems):
    return tuple(sorted((b % h, h) for b, h in elems))


@functools.lru_cache(maxsize=None)
def _excluded(n, elems):
    if not elems:
        return False
    if n == 1:
        return True
    ps = tuple(sorted(factorize(n)))
    if not in_semigroup(len(elems), ps):  # R0 (Lam-Leung weight)
        return True
    for p in ps:
        if any(h % p for _, h in elems):
            continue
        classes = {}
        for b, h in elems:
            i = b % p
            classes.setdefault(i, []).append(((b - i) // p, h // p))
        if len(classes) > 1 and n % (p * p):
            continue  # neither R1 (split) nor R2 (shift) applies for this p
        for i in sorted(classes):
            if _excluded(n // p, _canon(classes[i])):
                return True
    return False


def excluded(n, elems):
    """True if NO choice of y = b mod h (each point independently, in Z_n) makes
    sum zeta_n^y vanish (proved by R0-R2). False means: not excluded by them."""
    elems = list(elems)
    for b, h in elems:
        if h <= 0 or n % h:
            raise ValueError("each h must divide n")
    return _excluded(n, _canon(elems))


def lift_points(name, N):
    """Constrained points of a lift, seen mod N: x may sit at any y = x mod g."""
    g = math.gcd(PERIOD, N)
    return [(x % g, g) for x in SOURCES[name]["A"]]


# ------------------------------------------------------------ the tile facts
def source_report(name):
    X, B0 = SOURCES[name]["A"], SOURCES[name]["B"]
    pp = [q for q in range(2, PERIOD + 1) if PERIOD % q == 0 and is_prime_power(q)]
    return {
        "name": name,
        "size": len(set(X)),
        "tiling": is_tiling(X, B0, PERIOD),
        "S_A": [q for q in pp if phi_divides(q, X)],
        "A_t2": all(phi_divides(N, X) for N in (20, 36, 45, 180)),
        # fold-30 hypotheses of the 0.5.1 proposition
        "phi_divides_mod30": {str(d): phi_divides(d, X) for d in (2, 3, 5, 6, 10, 15, 30)},
    }


# ------------------------------------------------------- the proof, per period
def needed_orders(k):
    """Orders N with Phi_N | B that the three periodicity lemmas use."""
    a, b, e = exps(k)
    two = [2 ** j for j in range(3, a + 1)] + [3 * 2 ** j for j in range(3, a + 1)]
    three = [3 ** j for j in range(3, b + 1)] + [2 * 3 ** j for j in range(3, b + 1)]
    five = [m * 5 ** l for l in range(2, e + 1) for m in (1, 2, 3, 6)]
    return {"2": two, "3": three, "5": five}


def order_status(name, N):
    if is_prime_power(N):
        # S_A = {4, 9, 5} exactly (T1 bookkeeping), so every other prime power is in S_B
        return "in_S_A" if N in (4, 9, 5) else "in_S_B"
    return "excluded" if excluded(N, lift_points(name, N)) else "not_excluded"


def periodicity(m, P, vanishing):
    """Exact: if f on Z_m has zero Fourier coefficient at every frequency whose
    order lies in `vanishing`, then f(x + P) = f(x). True iff every other
    frequency xi satisfies m | P*xi."""
    for xi in range(m):
        order = m // math.gcd(xi, m)
        if order not in vanishing and (P * xi) % m:
            return False
    return True


def hexagon_vs(bound):
    """Every nonzero v on Z_6 with only order-6 frequencies and max |v| <= bound."""
    out = []
    for p in range(-bound, bound + 1):
        for r in range(-bound, bound + 1):
            v = (p, p + r, r, -p, -p - r, -r)
            if any(v) and max(abs(t) for t in v) <= bound:
                out.append(v)
    return out


def count_w(k, m, q):
    """Number of w: Z_5 -> qZ with every w(a) >= max(m, 1), sum k, not constant."""
    if k % q:
        return 0
    K = k // q
    c = -(-max(m, 1) // q)
    rest = K - 5 * c
    if rest < 0:
        return 0
    n = math.comb(rest + 4, 4)
    if K % 5 == 0 and K // 5 >= c:
        n -= 1
    return n


def profile_count(k, use_new):
    """Mod-30 profiles B_30 = w + v with v != 0 (a Phi_6 failure) allowed by the
    0.5.1 fold (use_new False) or also by the new 2-, 3- and 5-adic divisibility."""
    a, b, e = exps(k)
    q5, d2, d3 = 5 ** (e - 1), 2 ** (a - 2), 3 ** (b - 2)
    total = nv = 0
    for v in hexagon_vs(k // 5):  # min w >= max |v| and sum w = k
        m = max(abs(t) for t in v)
        if use_new:
            if any(t % q5 for t in v):
                continue
            if any((k + 5 * t) % d2 or (k + 5 * t) % d3 for t in v):
                continue
        n = count_w(k, m, q5)
        if n:
            total += n
            nv += 1
    return total, nv


def period_row(k):
    a, b, e = exps(k)
    need = needed_orders(k)
    status = {n: {str(N): order_status(n, N) for fam in ("2", "3", "5") for N in need[fam]}
              for n in SOURCE_NAMES}
    per = {
        "2": periodicity(3 * 2 ** a, 12, set(need["2"])),
        "3": periodicity(2 * 3 ** b, 18, set(need["3"])),
        "5": periodicity(6 * 5 ** e, 30, set(need["5"])),
    }
    old = profile_count(k, False)
    new = profile_count(k, True)
    closed = all(s in ("in_S_B", "excluded") for n in SOURCE_NAMES for s in status[n].values())
    return {
        "k": k, "M": PERIOD * k, "a": a, "b": b, "e": e, "needed": need, "status": status,
        "periodic": per, "divides_B6_or_B30": {"2": 2 ** (a - 2), "3": 3 ** (b - 2), "5": 5 ** (e - 1)},
        "old_profiles": old[0], "old_v": old[1], "new_profiles": new[0], "new_v": new[1],
        "phi6_forced": closed and all(per.values()) and new[0] == 0,
    }


def compute(ks=None):
    ks = list(KS if ks is None else ks)
    rows = {str(k): period_row(k) for k in ks}
    summary = {
        "ks": ks,
        "every_needed_order_closed": all(
            s in ("in_S_B", "excluded") for r in rows.values() for n in SOURCE_NAMES
            for s in r["status"][n].values()),
        "every_periodicity_ok": all(all(r["periodic"].values()) for r in rows.values()),
        "new_profiles_total": sum(r["new_profiles"] for r in rows.values()),
        "phi6_forced_k": [r["k"] for r in rows.values() if r["phi6_forced"]],
    }
    return {"version": VERSION, "sources": {n: source_report(n) for n in SOURCE_NAMES},
            "summary": summary, "table": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    doc = compute()
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "phi6_close_full.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print(json.dumps(doc["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
