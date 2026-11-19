# SPDX-License-Identifier: Apache-2.0
# Exact checks for the fold proposition of vuza-canons 0.5.1.
# Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""foldlemma: when can the unsupported divisor Phi_6 witness a T2 failure?

Proposition (proof in notes/fold_lemma.md). Let A (+) B = Z_M be a tiling with
|A| = 30, Phi_5 and Phi_6 dividing A(x), and Phi_2, Phi_3, Phi_10, Phi_15,
Phi_30 not dividing A(x). Then 180 | M. Write M/180 = 5^s * k' with 5 not
dividing k'. If Phi_6 does not divide B(x) (so B fails T2 at 6), then k' >= 6.

Every lift of the Tan-Zhang tiles S180 and C180 to Z_{180k} (any A with
A = X mod 180) satisfies the hypotheses, because they only depend on A mod 30.
So at M = 1800, 2700, 3600 and 4500 (k' = 2, 3, 4, 1) no set complement of
such a tile misses Phi_6. The least M where the proposition allows it is 5400.

Proof sketch:
 1. A_30 * B_30 = M/30 on Z_30, so B_30 has Fourier support on orders 1, 5, 6.
 2. Hence B_30(x) = w(x mod 5) + v(x mod 6), v a pure order-6 wave.
 3. Integrality forces v to be integer valued; Phi_6 not dividing B means v != 0,
    so min v <= -1 and w(a) >= 1 for every a.
 4. Phi_5 | A, so Phi_5 does not divide B and w is not constant.
 5. With 5^e || M, Phi_25, ..., Phi_{5^e} all divide B (T1 for |A| = 30), so
    B mod 5^e is 5-periodic and 5^(e-1) divides B_5(a) = 6 w(a).
 6. sum(w) = M/180, every w(a) >= 5^(e-1), one w(a) >= 2*5^(e-1): k' >= 6.

This module checks the computational parts exactly: the hypotheses for both
source tiles (exact cyclotomic remainders), the kernel of convolution by A_30
over the rationals (step 2), and an enumeration of every mod-30 profile that
survives steps 3-6 (with a direct check that each one is a weak complement).

Usage:
  python foldlemma.py --out fold_lemma_computed.json
"""
import argparse
import json
import sys
from fractions import Fraction

VERSION = "0.5.1"

E = (0, 2, 3, 4, 6)  # 1 + x^2 + x^3 + x^4 + x^6 = Phi_5 Phi_6
SOURCES = {
    "S180": sorted(30 * j + c for j in range(6) for c in E),
    "C180": [0, 2, 4, 12, 21, 34, 36, 38, 48, 51, 60, 62, 64, 72, 75, 90, 94, 98, 108, 111,
             122, 124, 126, 132, 141, 150, 154, 158, 165, 168],
}
COMPLEMENTS = {"S180": [0, 5, 10, 15, 20, 25], "C180": [0, 20, 40, 45, 65, 85]}

ORDERS_30 = (2, 3, 5, 6, 10, 15, 30)
MUST_DIVIDE = (5, 6)
MUST_NOT_DIVIDE = (2, 3, 10, 15, 30)

# integer basis of the pure order-6 waves on Z_6: v = (p, p+r, r, -p, -p-r, -r)
V_BASIS = ((1, 1, 0, -1, -1, 0), (0, 1, 1, 0, -1, -1))

TABLE_K = (1, 2, 3, 4, 5, 6, 10, 15, 20, 25, 30)


# ---------------------------------------------------------------- arithmetic
def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def vp(n, p):
    e = 0
    while n % p == 0:
        n //= p
        e += 1
    return e


def _pdiv(a, b):
    """Exact division by a monic integer polynomial (coefficients low to high)."""
    a = list(a)
    db = len(b) - 1
    q = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        q[i - db] = c
        for j in range(db + 1):
            a[i - db + j] -= c * b[j]
    if any(a[:db]):
        raise ArithmeticError("not exact")
    return q


_CYC = {}


def cyclotomic(d):
    if d not in _CYC:
        num = [-1] + [0] * (d - 1) + [1]
        for e in divisors(d):
            if e < d:
                num = _pdiv(num, cyclotomic(e))
        _CYC[d] = num
    return _CYC[d]


def _prem(a, b):
    a = list(a)
    db = len(b) - 1
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        if c:
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
    return a[:db]


def phi_divides(counts, d):
    """Exact: Phi_d divides sum_r counts[r] x^r."""
    return not any(_prem(counts, cyclotomic(d)))


def fold(xs, m):
    c = [0] * m
    for x in xs:
        c[x % m] += 1
    return c


def is_tiling(A, B, M):
    seen = [0] * M
    for a in A:
        for b in B:
            seen[(a + b) % M] += 1
    return all(c == 1 for c in seen)


def convolve(f, g, m):
    return [sum(f[y] * g[(x - y) % m] for y in range(m)) for x in range(m)]


# ---------------------------------------------------------------- hypotheses
def hypotheses(xs):
    f = fold(xs, 30)
    div = {d: phi_divides(f, d) for d in ORDERS_30}
    ok = (len(set(xs)) == 30 and all(div[d] for d in MUST_DIVIDE)
          and not any(div[d] for d in MUST_NOT_DIVIDE))
    return {"size": len(set(xs)), "fold30": f, "phi_divides": {str(d): div[d] for d in ORDERS_30}, "ok": ok}


def rank(rows):
    """Rank over Q by exact Gaussian elimination."""
    m = [[Fraction(x) for x in r] for r in rows]
    rk, ncol = 0, len(m[0]) if m else 0
    for c in range(ncol):
        piv = next((i for i in range(rk, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][c] != 0:
                t = m[i][c] / m[rk][c]
                m[i] = [a - t * b for a, b in zip(m[i], m[rk])]
        rk += 1
    return rk


def kernel_basis():
    """Mean-zero functions of x mod 5 (4) and pure order-6 waves (2) on Z_30."""
    out = []
    for a in range(1, 5):
        out.append([(1 if x % 5 == a else 0) - (1 if x % 5 == 0 else 0) for x in range(30)])
    for v in V_BASIS:
        out.append([v[x % 6] for x in range(30)])
    return out


def kernel_report(xs):
    """Step 2: g -> A_30 * g has kernel exactly span(kernel_basis())."""
    f = fold(xs, 30)
    conv = [[f[(x - y) % 30] for y in range(30)] for x in range(30)]
    r = rank(conv)
    basis = kernel_basis()
    in_kernel = all(not any(convolve(f, g, 30)) for g in basis)
    return {"rank": r, "kernel_dim": 30 - r, "basis_in_kernel": in_kernel,
            "basis_rank": rank(basis), "ok": r == 24 and in_kernel and rank(basis) == 6}


# ------------------------------------------------------------------ profiles
def _comps(total, parts, step):
    """Tuples of `parts` nonnegative multiples of `step` summing to `total`."""
    if parts == 1:
        if total % step == 0:
            yield (total,)
        return
    for x in range(0, total + 1, step):
        for rest in _comps(total - x, parts - 1, step):
            yield (x,) + rest


def admissible_profiles(k, five_adic=True):
    """Every mod-30 profile f(x) = w(x mod 5) + v(x mod 6) that survives steps
    3-6 for M = 180k with v != 0: w integer, not constant, multiples of
    5^(e-1) (if five_adic), sum k, and f >= 0."""
    M = 180 * k
    e = vp(M, 5)
    step = 5 ** (e - 1) if five_adic else 1
    out = []
    for w in _comps(k, 5, step):
        if len(set(w)) == 1:
            continue
        bound = max(w)  # |p| or |r| above max(w) makes some f(x) negative
        for p in range(-bound, bound + 1):
            for r in range(-bound, bound + 1):
                if p == 0 and r == 0:
                    continue
                v = (p, p + r, r, -p, -p - r, -r)
                if min(w) + min(v) >= 0:  # CRT: f takes every value w(a) + v(b)
                    out.append((w, v))
    return out


def profile_function(w, v):
    return [w[x % 5] + v[x % 6] for x in range(30)]


def check_profiles(k, profs):
    """Each profile must be a nonnegative integer weak complement: A_30 * f = 6k
    for both sources, with Phi_5 and Phi_6 not dividing f."""
    folds = [fold(xs, 30) for xs in SOURCES.values()]
    for w, v in profs:
        f = profile_function(w, v)
        if min(f) < 0 or sum(f) != 6 * k:
            return False
        if phi_divides(f, 5) or phi_divides(f, 6):
            return False
        for a30 in folds:
            if any(c != 6 * k for c in convolve(a30, f, 30)):
                return False
    return True


def table_row(k):
    M = 180 * k
    e = vp(M, 5)
    kp = k // 5 ** (e - 1)
    profs = admissible_profiles(k)
    return {"k": k, "M": M, "e": e, "k_prime": kp, "fold_allows_phi6_failure": kp >= 6,
            "only_two_shared_primes": k % 5 != 0, "admissible_profiles": len(profs)}


def compute():
    hyp = {n: hypotheses(xs) for n, xs in SOURCES.items()}
    ker = {n: kernel_report(xs) for n, xs in SOURCES.items()}
    tiles = {n: is_tiling(SOURCES[n], COMPLEMENTS[n], 180) for n in SOURCES}
    table = [table_row(k) for k in TABLE_K]
    checks = {str(k): check_profiles(k, admissible_profiles(k)) for k in (6, 30)}
    return {
        "version": VERSION,
        "sources_tile_Z180": tiles,
        "hypotheses": {n: {"phi_divides": h["phi_divides"], "ok": h["ok"]} for n, h in hyp.items()},
        "kernel": {n: {"kernel_dim": r["kernel_dim"], "ok": r["ok"]} for n, r in ker.items()},
        "table": table,
        "profiles_are_weak_complements": checks,
        "k10_profiles_without_5adic_step": len(admissible_profiles(10, five_adic=False)),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    doc = compute()
    txt = json.dumps(doc, indent=1)
    print(txt)
    if args.out:
        with open(args.out, "w") as f:
            f.write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
