# SPDX-License-Identifier: Apache-2.0
# Which cyclotomic orders can witness a T2 failure for a lift of the Tan-Zhang tiles?
# Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""liftroutes: every route but one is closed for lifts of S180 and C180.

Setting. X is S180 or C180 (Tan-Zhang, arXiv:2609.06677): 30 points of period
L = 180 with S_X = {4, 5, 9} and the unsupported divisor Phi_6. A LIFT of X to
Z_M, M = 180k, is any set A with A = X mod 180 (each of the 30 points may be
moved by any multiple of 180). Suppose A (+) B = Z_M.

* T1 holds for every tile (Coven-Meyerowitz), and Phi_4, Phi_9, Phi_5 already
  divide A with Phi_4(1)Phi_9(1)Phi_5(1) = 30 = |A|, so S_A = {4, 9, 5} and S_B
  is every other prime power dividing M.
* T2 for A only involves orders 20, 36, 45, 180, which divide 180, so it is
  decided by X alone (it holds).
* T2 for B fails at a product N of elements of S_B (distinct primes, at least
  two) only if Phi_N does not divide B, hence (tiling) Phi_N divides A.

So a lift can only break T2 at orders N where SOME lift A has Phi_N | A. This
module decides that question with a sound recursive test (below). The result,
for every k whose prime factors are 2, 3 and 5: the only such N is 6. Phi_6
divides every lift, and the fold proposition (notes/fold_lemma.md) shows that a
complement missing Phi_6 needs k' >= 6, where k = 5^s k' with 5 not dividing
k'. Together with Laba-Londner Cor. 6.2 (5 not dividing k), every tiling of a
lift satisfies T2 unless 5 | k and k' >= 6; the least such period is 5400.

The test. Phi_N | A depends on A mod N. A lift places x in X at any residue
y = x mod g of Z_N, g = gcd(180, N), independently for each x. For a list of
such constrained points ((b, h): y = b mod h, h | n) in Z_n, "some choice has
sum of zeta_n^y = 0" is decided by three exact rules:
  R1 (split)  if p^2 | n and every h is divisible by p: the sum vanishes iff
              the sum over each class mod p, rescaled to Z_{n/p}, vanishes
              (1, z, ..., z^{p-1} are independent over Q(zeta_{n/p}), z = zeta_n).
  R2 (shift)  if p | n, every h is divisible by p and all points share the
              same residue i mod p: sum zeta_n^y = zeta_n^i sum zeta_{n/p}^w,
              w = (y - i)/p in Z_{n/p}.
  R0 (weight) Lam-Leung (2000): a vanishing sum of n-th roots of unity has a
              weight that is a nonnegative integer combination of the primes
              dividing n. For n = 1 a nonempty sum never vanishes.
R1 and R2 are equivalences and R0 is a necessary condition, so "excluded" is a
proof; "not_excluded" only means these rules found no obstruction.
test_liftroutes.py also checks soundness against brute force on random cases.

Usage:
  python liftroutes.py --out-dir out
"""
import argparse
import cmath
import functools
import itertools
import json
import math
import os
import sys

VERSION = "0.6.0"
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


# every k <= 60 whose prime factors are among 2, 3 and 5
KS = [k for k in range(1, 61) if set(factorize(k)) <= {2, 3, 5}]


def prime_of(q):
    f = factorize(q)
    if len(f) != 1:
        raise ValueError("not a prime power: %d" % q)
    return next(iter(f))


def prime_powers(M):
    f = factorize(M)
    return sorted(p ** e for p in f for e in range(1, f[p] + 1))


def t2_products(S):
    """Products of elements of S that use powers of at least two distinct primes
    (at most one power of each prime)."""
    by = {}
    for q in S:
        by.setdefault(prime_of(q), []).append(q)
    out = []
    for combo in itertools.product(*[[1] + sorted(by[p]) for p in sorted(by)]):
        parts = [c for c in combo if c != 1]
        if len(parts) >= 2:
            p = 1
            for c in parts:
                p *= c
            out.append(p)
    return sorted(out)


def kprime(k):
    while k % 5 == 0:
        k //= 5
    return k


def is_tiling(A, B, M):
    seen = [0] * M
    for a in A:
        for b in B:
            seen[(a + b) % M] += 1
    return all(c == 1 for c in seen)


def vanishes_residues(ys, n):
    """Exact test of sum zeta_n^y = 0 for a multiset ys of residues mod n.
    The sum is an algebraic integer; if it is nonzero, some conjugate has
    modulus >= 1, so 'every conjugate below 0.5' means zero."""
    ys = list(ys)
    s = sum(cmath.exp(2j * math.pi * (y % n) / n) for y in ys)
    if abs(s) > 1e-6:
        return False
    for u in range(1, n + 1):
        if math.gcd(u, n) != 1:
            continue
        t = sum(cmath.exp(2j * math.pi * ((u * y) % n) / n) for y in ys)
        if abs(t) >= 0.5:
            return False
    return True


@functools.lru_cache(maxsize=None)
def in_semigroup(c, gens):
    ok = [False] * (c + 1)
    ok[0] = True
    for v in range(1, c + 1):
        ok[v] = any(v >= g and ok[v - g] for g in gens)
    return ok[c]


# ------------------------------------------------------------ the sound test
def _canon(elems):
    return tuple(sorted((b % h, h) for b, h in elems))


@functools.lru_cache(maxsize=None)
def _excluded(n, elems):
    if not elems:
        return False
    if n == 1:
        return True
    ps = tuple(sorted(factorize(n)))
    if not in_semigroup(len(elems), ps):  # R0
        return True
    for p in ps:
        if any(h % p for _, h in elems):
            continue
        classes = {}
        for b, h in elems:
            i = b % p
            classes.setdefault(i, []).append(((b - i) // p, h // p))
        if len(classes) > 1 and n % (p * p):
            continue  # neither R1 nor R2 applies for this p
        for i in sorted(classes):  # R1 (several classes) or R2 (one class)
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


# ---------------------------------------------------------------- the tiles
def source_report(name):
    X, B0 = SOURCES[name]["A"], SOURCES[name]["B"]
    S_A = [q for q in prime_powers(PERIOD) if vanishes_residues(X, q)]
    prods = t2_products(S_A)
    return {
        "name": name,
        "size": len(set(X)),
        "tiling": len(set(X)) * len(set(B0)) == PERIOD and is_tiling(X, B0, PERIOD),
        "S_A": S_A,
        "t1": math.prod(prime_of(q) for q in S_A) == len(set(X)),
        "A_t2_products": prods,
        "A_satisfies_T2": all(vanishes_residues(X, s) for s in prods),
        "phi6_divides": vanishes_residues(X, 6),
    }


def lift_points(name, N):
    """Constrained points of a lift, seen mod N: x may sit at any y = x mod g."""
    g = math.gcd(PERIOD, N)
    return [(x % g, g) for x in SOURCES[name]["A"]]


def period_routes(name, k):
    X = SOURCES[name]["A"]
    M = PERIOD * k
    S_A = [q for q in prime_powers(M) if PERIOD % q == 0 and vanishes_residues(X, q)]
    if math.prod(prime_of(q) for q in S_A) != len(X):
        raise AssertionError("T1 bookkeeping failed for %s" % name)
    S_B = [q for q in prime_powers(M) if q not in S_A]
    routes = {}
    for N in t2_products(S_B):
        if PERIOD % N == 0:
            routes[str(N)] = "divides_every_lift" if vanishes_residues(X, N) else "excluded_fixed"
        else:
            routes[str(N)] = "excluded" if excluded(N, lift_points(name, N)) else "not_excluded"
    open_routes = sorted(int(N) for N, v in routes.items() if v in ("divides_every_lift", "not_excluded"))
    kp = kprime(k)
    ll = k % 5 != 0
    fold = kp <= 5
    # T2 is forced if Laba-Londner Cor. 6.2 applies (5 does not divide |B| = 6k), or if
    # Phi_6 is the only open route and the fold proposition closes it.
    forced = ll or (all(N == 6 for N in open_routes) and fold)
    return {"k": k, "M": M, "S_A": S_A, "S_B": S_B, "routes": routes, "open": open_routes,
            "kprime": kp, "laba_londner_cor62": ll, "phi6_closed_by_fold": fold, "t2_forced": forced}


def compute(ks=None):
    ks = list(KS if ks is None else ks)
    sources = {n: source_report(n) for n in SOURCE_NAMES}
    table = {n: {} for n in SOURCE_NAMES}
    for n in SOURCE_NAMES:
        for k in ks:
            row = period_routes(n, k)
            table[n][str(row["M"])] = row
    rows = [r for n in SOURCE_NAMES for r in table[n].values()]
    summary = {
        "ks": ks,
        "every_open_route_is_6": all(r["open"] == [6] for r in rows),
        "t2_forced_k": {n: [r["k"] for r in table[n].values() if r["t2_forced"]] for n in SOURCE_NAMES},
        "phi6_route_open_k": {n: [r["k"] for r in table[n].values() if not r["t2_forced"]] for n in SOURCE_NAMES},
        "least_open_period": {n: min([r["M"] for r in table[n].values() if not r["t2_forced"]] or [None])
                              for n in SOURCE_NAMES},
    }
    counts = {
        "periods": len(ks),
        "routes_checked": sum(len(r["routes"]) for r in rows),
        "routes_excluded": sum(1 for r in rows for v in r["routes"].values() if v.startswith("excluded")),
    }
    return {"version": VERSION, "sources": sources, "summary": summary, "counts": counts, "table": table}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    doc = compute()
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "lift_routes_full.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print(json.dumps({"summary": doc["summary"], "counts": doc["counts"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
