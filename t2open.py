# SPDX-License-Identifier: Apache-2.0
# Where is the Coven-Meyerowitz condition T2 still open?
# Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""Which tilings A (+) B = Z_M are NOT yet covered by a published T2 theorem?

T2 for a set A depends only on the polynomial A(x). So a tiling of Z_M' with
M' | M lifts to a tiling of Z_M (take B + M' Z_M), and "T2 is known for every
tiling of Z_M" passes down to divisors of M.

Published results used (as read on 2026-11-17):

  CM   Coven-Meyerowitz, J. Algebra 212 (1999): T2 holds for A if |A| has at
       most two distinct prime factors.
  LL6  Laba-Londner, "Combinatorial and harmonic-analytic methods for integer
       tilings" (arXiv:2106.14042), Corollary 6.2, restated as Lemma 6.2 of
       "Splitting for integer tilings" (arXiv:2407.11374). Primes that divide
       at most one of |A|, |B| can be removed: let M0 be the part of M on the
       primes dividing BOTH |A| and |B|; if every tiling of Z_M0 satisfies
       T2, then A and B satisfy T2. A prime p with p^2 not dividing M can never
       divide both sizes, because |A| |B| = M.
  LL3  Laba-Londner, Invent. Math. 232 (2023) (odd primes) and Res. Math. Sci.
       12 (2025) (the even case): T2 for every tiling of period p^2 q^2 r^2.
  LLS  Laba-Londner, "Splitting for integer tilings", Theorem 1.2: if
       M = p^n M1 with p not dividing M1, T2 is known for every tiling of
       Z_M' for every M' | M1, and p > D(M1) = M1 / rad(M1), then T2 holds
       for every tiling of Z_M. (Their Corollary 1.5 is a special case.)

Together: a tiling can fail T2 only if at least three primes divide both
|A| and |B|, and the part M0 of M on those primes is not covered by LL3 or
LLS. The smallest such period is 1800 = 2^3 3^2 5^2, where the only open
size pair is {30, 60}.

Not used: unrefereed 2026 preprints that claim T2 in full (for example
arXiv:2609.22280). If a newer theorem covers more, this map is too cautious,
never too bold: every period it calls "known" really is covered by the
results above.

Usage: python t2open.py [--limit 20000] [--out t2_open_periods.json]
"""
import argparse
import functools
import itertools
import json
import sys

import vuza

VERSION = "0.3.0"


def rad(n):
    """Product of the distinct primes dividing n (rad(1) = 1)."""
    return vuza.prod(vuza.factorize(n))


def D(n):
    """D(n) = n / rad(n), as in Laba-Londner."""
    return n // rad(n)


@functools.lru_cache(maxsize=None)
def known_core(M0):
    """True if T2 is known for every tiling of Z_M0, where every prime of M0
    may divide both factor sizes (the case LL6 cannot reduce further)."""
    f = vuza.factorize(M0)
    if len(f) <= 2:
        return True  # CM: every factor size has at most two primes
    if len(f) == 3 and all(e <= 2 for e in f.values()):
        return True  # LL3
    for p in sorted(f):  # LLS
        M1 = M0 // p ** f[p]
        if p > D(M1) and all(known_all(d) for d in vuza.divisors(M1)):
            return True
    return False


@functools.lru_cache(maxsize=None)
def known_all(M):
    """True if the results above give T2 for both factors of EVERY tiling
    A (+) B = Z_M."""
    f = vuza.factorize(M)
    shareable = sorted(p for p, e in f.items() if e >= 2)
    for k in range(3, len(shareable) + 1):
        for P in itertools.combinations(shareable, k):
            if not known_core(vuza.prod(p ** f[p] for p in P)):
                return False
    return True


def shared_part(M, a, b):
    """Part of M on the primes dividing both a and b."""
    f = vuza.factorize(M)
    return vuza.prod(p ** f[p] for p in sorted(f) if a % p == 0 and b % p == 0)


def known_for_sizes(M, a, b):
    """True if T2 is known for both factors of every tiling of Z_M with
    |A| = a and |B| = b (LL6, then known_all of the shared part)."""
    if a * b != M:
        raise ValueError("sizes must multiply to M")
    return known_all(shared_part(M, a, b))


def open_size_pairs(M):
    """All (|A|, |B|) with |A| |B| = M for which T2 is not yet a theorem."""
    return [(a, M // a) for a in vuza.divisors(M) if not known_for_sizes(M, a, M // a)]


def open_periods(limit, start=2):
    """Periods M in [start, limit] with at least one tiling not covered."""
    return [M for M in range(max(2, start), limit + 1) if not known_all(M)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20000)
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    rows = []
    for M in open_periods(args.limit):
        rows.append({"M": M, "factorization": {str(p): e for p, e in sorted(vuza.factorize(M).items())},
                     "open_size_pairs": open_size_pairs(M)})
    doc = {"version": VERSION, "limit": args.limit, "count": len(rows),
           "rules": ["CM 1999", "Laba-Londner Cor. 6.2 / Lemma 6.2", "Laba-Londner p^2q^2r^2 (2023, 2025)",
                     "Laba-Londner splitting Thm 1.2"],
           "open_periods": rows}
    text = json.dumps(doc, indent=1)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
    print("open periods up to %d: %d; first: %s" % (args.limit, len(rows), [r["M"] for r in rows[:12]]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
