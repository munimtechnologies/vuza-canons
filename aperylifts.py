# SPDX-License-Identifier: Apache-2.0
# Lifts of the Tan-Zhang Apery tiles: when every tiling satisfies T2, and where a route stays open.
# Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""aperylifts: T2 for every lift of the standard Tan-Zhang tiles X_{p,q,r}.

Setting (Tan-Zhang, arXiv:2609.06677, Thm 7.1 with L = r, h = 1). Let p < q < r be
primes with r in the numerical semigroup <p, q>, Ap = Ap(<p,q>; r) the Apery set
(the least element of <p,q> in each class mod r), K = pqr and M0 = pqK = p^2 q^2 r.
    X = {K j + s : 0 <= j < pq, s in Ap}  (pqr points of Z_M0),
    X(x) = (x^M0 - 1)/(x^K - 1) * Phi_r(x) * Phi_pq(x),  S_X = {p^2, q^2, r},
and Phi_pq is an unsupported divisor. For (2, 3, 5) this is S180.

Let N(u, t) = #{s in Ap : s = u mod p, s = t mod q}. Three exact conditions:
  C1  some u in Z_p has t -> N(u, t) not constant mod p;
  C2  some t in Z_q has u -> N(u, t) not constant mod q;
  C3  some N(u, t) is not in the semigroup <p, q> (as a count).

Theorem (notes/apery_lifts.md). Let A be a lift of X to Z_{M0 k} (A = X mod M0)
and A (+) B = Z_{M0 k}.
  (i)  If C1 and C2 hold, Phi_pq divides B.
  (ii) If moreover C3 holds, or p q r does not divide k, A and B satisfy T2.
  (iii) The conditions are exact: if C1 (C2, C3) fails, some lift A has
       Phi_N | A for N = q p^3 (p q^3, p^3 q^3).
Primes of k outside {p, q, r} are removed by Tijdeman's dilation theorem and the
subgroup reduction (Coven-Meyerowitz Lemma 2.5; Laba-Londner arXiv:2106.14042,
Thm 6.1), so only {p, q, r}-smooth k need the new argument.

This module checks exactly: the Apery sets and the identity sum x^s = [r]_x Phi_pq;
the tile facts by division by cyclotomic polynomials; C1-C3 and, by brute force at
the least exponent, that each is equivalent to the route being closed; the closed
form of N for p = 2, q = 3 and every prime r < 200; and, where C3 fails, an
explicit lift that carries Phi_{p^3 q^3} and still tiles.

Usage:
  python aperylifts.py --out-dir out [--scan 60]
"""
import argparse
import functools
import itertools
import json
import os
import sys

VERSION = "0.8.0"

TRIPLES = [(2, 3, 5), (2, 3, 7), (2, 3, 11), (2, 3, 13), (2, 3, 17), (2, 3, 19), (2, 5, 7)]


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


def is_prime(n):
    return n >= 2 and factorize(n) == {n: 1}


def is_prime_power(n):
    return n > 1 and len(factorize(n)) == 1


def in_semigroup2(n, p, q):
    """n in the numerical semigroup <p, q> = {i p + j q : i, j >= 0}."""
    return n >= 0 and any((n - i * p) % q == 0 for i in range(n // p + 1))


# ------------------------------------------------- exact cyclotomic division
def poly_divmod(num, den):
    """Integer polynomials as coefficient lists, lowest degree first; den monic."""
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


def poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def phi_divides(N, pts):
    """Exact test of Phi_N | sum x^y over the multiset pts (residues taken mod N)."""
    poly = [0] * N
    for y in pts:
        poly[y % N] += 1
    _, r = poly_divmod(poly, list(cyclotomic(N)))
    return not any(r)


def is_tiling(A, B, M):
    seen = [0] * M
    for a in A:
        for b in B:
            seen[(a + b) % M] += 1
    return all(c == 1 for c in seen)


# ------------------------------------------------------------ the tiles
def apery_set(p, q, r):
    """Ap(<p,q>; r): the least element of <p,q> in each residue class mod r."""
    if not in_semigroup2(r, p, q):
        raise ValueError("r must lie in the numerical semigroup <p, q>")
    best = {}
    # the largest Apery element is r - 1 + (p-1)(q-1) (Tan-Zhang Lemma 2.2)
    for n in range(r + (p - 1) * (q - 1)):
        c = n % r
        if c not in best and in_semigroup2(n, p, q):
            best[c] = n
    if len(best) != r:
        raise ArithmeticError("Apery set incomplete")
    return sorted(best.values())


def apery_poly_ok(p, q, ap):
    """sum_{s in Ap} x^s == (1 + x + ... + x^(r-1)) * Phi_pq(x), with r = |Ap|."""
    lhs = [0] * (max(ap) + 1)
    for s in ap:
        lhs[s] += 1
    rhs = poly_mul([1] * len(ap), list(cyclotomic(p * q)))
    while len(rhs) > 1 and rhs[-1] == 0:
        rhs.pop()
    return lhs == rhs


def tile(p, q, r):
    """(X, B0, M0): the standard Tan-Zhang tile, its subgroup complement, its period."""
    ap = apery_set(p, q, r)
    K = p * q * r
    M0 = K * p * q
    X = sorted(K * j + s for j in range(p * q) for s in ap)
    B0 = [r * j for j in range(p * q)]
    return X, B0, M0


def tile_report(p, q, r):
    X, B0, M0 = tile(p, q, r)
    K = p * q * r
    pp = [s for s in range(2, M0 + 1) if M0 % s == 0 and is_prime_power(s)]
    return {
        "M0": M0,
        "size": len(set(X)),
        "tiles": is_tiling(X, B0, M0),
        "S_X": [s for s in pp if phi_divides(s, X)],
        "fold": [d for d in range(2, K + 1) if K % d == 0 and phi_divides(d, X)],
        "t2": all(phi_divides(N, X) for N in (p * p * q * q, p * p * r, q * q * r, M0)),
    }


# ------------------------------------------------------- the three conditions
def cells(p, q, ap):
    N = [[0] * q for _ in range(p)]
    for s in ap:
        N[s % p][s % q] += 1
    return N


def conditions(p, q, N):
    c1 = any(len({N[u][t] % p for t in range(q)}) > 1 for u in range(p))
    c2 = any(len({N[u][t] % q for u in range(p)}) > 1 for t in range(q))
    c3 = any(not in_semigroup2(N[u][t], p, q) for u in range(p) for t in range(q))
    return c1, c2, c3


# ---------------------------------------- brute force at the least exponent
def compositions(n, parts):
    if parts == 1:
        yield (n,)
        return
    for first in range(n + 1):
        for rest in compositions(n - first, parts - 1):
            yield (first,) + rest


def class_can_vanish(counts, P, Q):
    """counts[t] points sit at residue t mod Q, each free mod P (gcd(P, Q) = 1).
    Can the sum of the corresponding PQ-th roots of unity be zero? (exhaustive)"""
    n = P * Q
    pos = [[0] * P for _ in range(Q)]
    for e in range(n):
        pos[e % Q][e % P] = e
    den = list(cyclotomic(n))
    options = [list(compositions(c, P)) for c in counts]
    for choice in itertools.product(*options):
        poly = [0] * n
        for t, comp in enumerate(choice):
            for z, c in enumerate(comp):
                poly[pos[t][z]] += c
        _, rem = poly_divmod(poly, den)
        if not any(rem):
            return True
    return False


def brute_checks(p, q, N):
    """Each exact criterion agrees with exhaustive search on every class:
    C1 classes (N = q p^3, class mod p^2): q N(u, t) points at t mod q, free mod p;
    C2 classes (N = p q^3, class mod q^2): p N(u, t) points at u mod p, free mod q;
    C3 classes (N = p^3 q^3, class mod p^2 q^2): N(u, t) points free mod pq."""
    ok = True
    for u in range(p):
        counts = [q * N[u][t] for t in range(q)]
        crit = len({c % p for c in counts}) == 1
        ok = ok and class_can_vanish(counts, p, q) == crit
    for t in range(q):
        counts = [p * N[u][t] for u in range(p)]
        crit = len({c % q for c in counts}) == 1
        ok = ok and class_can_vanish(counts, q, p) == crit
    for u in range(p):
        for t in range(q):
            ok = ok and class_can_vanish([N[u][t]], p * q, 1) == in_semigroup2(N[u][t], p, q)
    return ok


# --------------------------------------------- the open route made explicit
def open_route_witness(p, q, r):
    """If every class of X mod p^2 q^2 has a size in <p, q> (C3 fails), build a lift A
    of X to Z_{M0 pq} with Phi_{p^3 q^3} | A, and check that it still tiles."""
    X, B0, M0 = tile(p, q, r)
    D = p * p * q * q
    Nord = D * p * q
    classes = {}
    for x in X:
        classes.setdefault(x % D, []).append(x)
    target = {}
    for z, pts in classes.items():
        n = len(pts)
        alpha = next((i for i in range(n // p + 1) if (n - i * p) % q == 0), None)
        if alpha is None:
            return None
        beta = (n - alpha * p) // q
        # p-cycles {0, q, .., (p-1)q} and q-cycles {0, p, .., (q-1)p} of Z_pq sum to zero
        ws = [q * i for _ in range(alpha) for i in range(p)] + \
             [p * i for _ in range(beta) for i in range(q)]
        for x, w in zip(sorted(pts), ws):
            target[x] = (z + D * w) % Nord
    k = p * q
    M = M0 * k
    rinv = pow(r, -1, p * q)
    A = []
    for x in X:
        delta = ((target[x] - x) % Nord) // D
        A.append(x + M0 * ((delta * rinv) % (p * q)))
    A.sort()
    B = sorted(b + M0 * i for b in B0 for i in range(k))
    return {
        "N": Nord,
        "M": M,
        "is_lift": sorted(a % M0 for a in A) == X,
        "phi_N_divides": phi_divides(Nord, A),
        "tiles": is_tiling(A, B, M),
    }


# ------------------------------------------------------- p = 2, q = 3 family
def closed_form_23(r):
    """N(u, t) for p = 2, q = 3 and a prime r >= 5, from Ap = {0..r+1} minus {1, r}."""
    if r % 6 == 5:
        m = (r + 1) // 6
        res = [m + 1, m - 1, m, m, m, m - 1]
    else:
        m = (r - 1) // 6
        res = [m + 1, m - 1, m + 1, m, m, m]
    # the residue mod 6 that is u mod 2 and t mod 3 is (3u + 4t) mod 6
    return [[res[(3 * u + 4 * t) % 6] for t in range(3)] for u in range(2)]


def family_23(hi=199):
    rows = []
    for r in range(5, hi + 1):
        if not is_prime(r):
            continue
        N = cells(2, 3, apery_set(2, 3, r))
        c1, c2, c3 = conditions(2, 3, N)
        rows.append((r, N == closed_form_23(r), c1, c2, c3))
    return {
        "primes": len(rows),
        "closed_form_ok": all(x[1] for x in rows),
        "C1_all": all(x[2] for x in rows),
        "C2_all": all(x[3] for x in rows),
        "C3_primes": [x[0] for x in rows if x[4]],
    }


# ------------------------------------------------------------------- report
def key(t):
    return "%d,%d,%d" % t


def triple_row(p, q, r):
    ap = apery_set(p, q, r)
    N = cells(p, q, ap)
    c1, c2, c3 = conditions(p, q, N)
    return {
        "p": p, "q": q, "r": r,
        "apery": ap,
        "apery_poly_ok": apery_poly_ok(p, q, ap),
        "cells": N,
        "C1": c1, "C2": c2, "C3": c3,
        "phi_pq_forced": c1 and c2,
        "t2_every_period": c1 and c2 and c3,
        "brute_ok": brute_checks(p, q, N),
        "tile": tile_report(p, q, r),
        "witness": open_route_witness(p, q, r),
    }


def compute():
    rows = {key(t): triple_row(*t) for t in TRIPLES}

    def tile_ok(row):
        p, q, r = row["p"], row["q"], row["r"]
        tr = row["tile"]
        return (tr["tiles"] and tr["size"] == p * q * r and tr["t2"]
                and tr["S_X"] == sorted([p * p, q * q, r]) and tr["fold"] == sorted([r, p * q]))

    def witness_ok(row):
        w = row["witness"]
        if row["C3"]:
            return w is None
        return w is not None and w["is_lift"] and w["phi_N_divides"] and w["tiles"]

    summary = {
        "phi_pq_forced": [k for k, r in rows.items() if r["phi_pq_forced"]],
        "t2_every_period": [k for k, r in rows.items() if r["t2_every_period"]],
        "open_route": [k for k, r in rows.items() if not r["C3"]],
        "every_apery_poly_ok": all(r["apery_poly_ok"] for r in rows.values()),
        "every_brute_ok": all(r["brute_ok"] for r in rows.values()),
        "every_tile_ok": all(tile_ok(r) for r in rows.values()),
        "every_witness_ok": all(witness_ok(r) for r in rows.values()),
    }
    return {"version": VERSION, "triples": rows, "summary": summary, "family_23": family_23()}


def scan(limit):
    """C1-C3 for every prime triple p < q < r < limit with r in <p, q> (no brute force)."""
    ps = [n for n in range(2, limit) if is_prime(n)]
    out = []
    for p, q, r in itertools.combinations(ps, 3):
        if not in_semigroup2(r, p, q):
            continue
        N = cells(p, q, apery_set(p, q, r))
        c1, c2, c3 = conditions(p, q, N)
        out.append({"triple": key((p, q, r)), "C1": c1, "C2": c2, "C3": c3})
    return {
        "limit": limit,
        "triples": len(out),
        "phi_pq_forced": sum(1 for x in out if x["C1"] and x["C2"]),
        "t2_every_period": sum(1 for x in out if x["C1"] and x["C2"] and x["C3"]),
        "C1_fails": [x["triple"] for x in out if not x["C1"]],
        "C2_fails": [x["triple"] for x in out if not x["C2"]],
        "rows": out,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--scan", type=int, default=0)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    doc = compute()
    with open(os.path.join(args.out_dir, "aperylifts_full.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print(json.dumps(doc["summary"], indent=1))
    if args.scan:
        sc = scan(args.scan)
        with open(os.path.join(args.out_dir, "apery_scan.json"), "w") as f:
            json.dump(sc, f, indent=1)
        print(json.dumps({k: v for k, v in sc.items() if k != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
