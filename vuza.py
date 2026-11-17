# SPDX-License-Identifier: Apache-2.0
# vuza-canons: exhaustive complements of Vuza rhythms and Coven-Meyerowitz checks.
# Made by MV2 of Munim, Inc., with AI agents. Licensed under the Apache License 2.0.
"""Rhythmic tiling canons (Vuza canons) and the Coven-Meyerowitz conditions.

A rhythmic canon of period N is a tiling Z_N = S (+) R: the outer rhythm S
(entry offsets of the voices) plus the inner rhythm R (the rhythm every voice
plays) covers every pulse exactly once. It is a Vuza canon when neither S nor R
is periodic.

Coven and Meyerowitz (1999) proved that a finite set A tiles the integers if
it satisfies their conditions T1 and T2, that T1 is necessary, and that T2 is
necessary when |A| has at most two prime factors. Whether T2 is always
necessary is open. Amiot showed that a counterexample would collapse to a Vuza
canon that fails T2, so Vuza canons are where to look.

This module:
  * builds the standard Vuza rhythms (Jedrzejewski 2013, Theorems 12/14;
    after Vuza, Hajos and de Bruijn),
  * enumerates EVERY complement R of a rhythm S in Z_N by exact-cover search,
    one representative per translation class,
  * tests T1 and T2 on every class with an exact cyclotomic-zero test.

Cyclotomic-zero test: for d | N, Phi_d divides X(x) iff X(zeta_d) = 0. If the
algebraic integer X(zeta_d) is nonzero its norm (the product of its Galois
conjugates X(zeta_d^j), gcd(j, d) = 1) is a nonzero integer, so some conjugate
has absolute value >= 1. Hence X(zeta_d) = 0 iff every conjugate has absolute
value < 0.5 in floating point (rounding error here is below 1e-9). This is
exact, not a heuristic threshold.
"""
import cmath
import itertools
import math
import time

VERSION = "0.1.0"

try:  # optional speed-up; every result is also computable in pure Python
    import numpy as _np
except Exception:  # pragma: no cover
    _np = None


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


def is_prime(n):
    return n >= 2 and factorize(n) == {n: 1}


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def prod(xs):
    p = 1
    for x in xs:
        p *= x
    return p


def n_prime_factors(n):
    """Number of DISTINCT primes dividing n."""
    return len(factorize(n)) if n > 1 else 0


# ---------------------------------------------------------------- bit masks
def to_mask(xs):
    m = 0
    for x in xs:
        m |= 1 << x
    return m


def from_mask(m):
    out = []
    i = 0
    while m:
        if m & 1:
            out.append(i)
        m >>= 1
        i += 1
    return out


def rot(m, r, N):
    """Mask of (X + r) mod N, where m is the mask of X."""
    r %= N
    if r == 0:
        return m
    full = (1 << N) - 1
    return ((m << r) | (m >> (N - r))) & full


def is_periodic(xs, N):
    """True iff X + g = X for some g != 0 in Z_N."""
    m = to_mask(xs)
    for p in factorize(N):
        if rot(m, N // p, N) == m:
            return True
    return False


def stabilizer_size(xs, N):
    """Number of g in Z_N with X + g = X."""
    m = to_mask(xs)
    for g in divisors(N):
        if rot(m, g, N) == m:
            return N // g
    return 1  # unreachable: g = N always works


def is_tiling(A, B, N):
    seen = [0] * N
    for a in A:
        for b in B:
            seen[(a + b) % N] += 1
    return all(c == 1 for c in seen)


def canonical(xs, N):
    """Least mask over all translates of X (a translation-class id)."""
    xs = sorted(set(x % N for x in xs))
    m = to_mask(xs)
    return min(rot(m, -x, N) for x in xs)


def is_canonical_sorted(rs, N):
    """rs: sorted list containing 0. True iff its mask is the least among all
    translates of the set (so exactly one member of each class passes).

    The translate X - r has largest element N - gap(r), where gap(r) is the
    cyclic gap ending at r, so the least mask must come from a largest gap;
    ties are settled by comparing masks."""
    k = len(rs)
    g0 = N - rs[-1] if k > 1 else N
    ties = []
    for i in range(1, k):
        g = rs[i] - rs[i - 1]
        if g > g0:
            return False
        if g == g0:
            ties.append(rs[i])
    if not ties:
        return True
    m0 = to_mask(rs)
    for r in ties:
        if to_mask([(x - r) % N for x in rs]) < m0:
            return False
    return True


# ---------------------------------------------------------- Vuza rhythms
def check_params(n1, p1, n2, p2, n3):
    if not (is_prime(p1) and is_prime(p2) and p1 != p2):
        raise ValueError("p1, p2 must be distinct primes")
    if min(n1, n2, n3) < 2:
        raise ValueError("n1, n2, n3 must be >= 2")
    if math.gcd(n1 * p1, n2 * p2) != 1:
        raise ValueError("n1*p1 and n2*p2 must be coprime")
    return n1 * p1 * n2 * p2 * n3


def vuza_outer(n1, p1, n2, p2, n3):
    """Standard outer rhythm S = A + B, A = n1 p1 n3 I_{n2}, B = n2 p2 n3 I_{n1}
    (Jedrzejewski 2013, Thm 14; parameters in his order n1, p1, n2, p2, n3)."""
    N = check_params(n1, p1, n2, p2, n3)
    A = [(n1 * p1 * n3 * i) % N for i in range(n2)]
    B = [(n2 * p2 * n3 * j) % N for j in range(n1)]
    S = sorted({(a + b) % N for a in A for b in B})
    return N, S


def vuza_inner(n1, p1, n2, p2, n3):
    """Standard inner rhythm R = (U + V' + K1) u (U' + V + K2) with alpha =
    beta = 1, K1 = {0}, K2 = {1..n3-1} (Jedrzejewski 2013, Thm 12)."""
    N = check_params(n1, p1, n2, p2, n3)
    U = [n1 * n2 * n3 * p1 * i for i in range(p2)]
    V = [n1 * n2 * n3 * p2 * i for i in range(p1)]
    U2 = [n2 * n3 * i for i in range(p2)]
    V2 = [n1 * n3 * i for i in range(p1)]
    R = set()
    for u in U:
        for v in V2:
            R.add((u + v) % N)
    for k in range(1, n3):
        for u in U2:
            for v in V:
                R.add((u + v + k) % N)
    return N, sorted(R)


# ------------------------------------------------------- exact-cover search
class _Stop(Exception):
    pass


def enumerate_complements(S, N, on_solution, time_limit=None):
    """Call on_solution(R) for every R containing 0 with S (+) R = Z_N.

    Exact cover: the least uncovered pulse x must be covered by s + r for
    exactly one s in S, so r = x - s; every complement containing 0 is
    produced exactly once. R is passed as a list that is reused; copy it.
    Returns (number_of_solutions, nodes, complete)."""
    S = sorted(set(x % N for x in S))
    full = (1 << N) - 1
    smask = to_mask(S)
    masks = [rot(smask, r, N) for r in range(N)]
    if (N % len(S)) != 0:
        return 0, 0, True
    t0 = time.time()
    state = {"sols": 0, "nodes": 0}
    R = [0]

    def dfs(covered):
        state["nodes"] += 1
        if time_limit is not None and (state["nodes"] & 0x3FFF) == 0:
            if time.time() - t0 > time_limit:
                raise _Stop()
        if covered == full:
            state["sols"] += 1
            on_solution(R)
            return
        free = full & ~covered
        x = (free & -free).bit_length() - 1
        for s in S:
            r = x - s
            if r < 0:
                r += N
            m = masks[r]
            if not (m & covered):
                R.append(r)
                dfs(covered | m)
                R.pop()

    complete = True
    try:
        dfs(smask)
    except _Stop:
        complete = False
    return state["sols"], state["nodes"], complete


# ------------------------------------------------- cyclotomic conditions
class Cyclo:
    """Cyclotomic-divisor tests for subsets of Z_N."""

    def __init__(self, N, use_numpy=True):
        self.N = N
        self.f = factorize(N)
        self.primes = sorted(self.f)
        self.pp = {p: [p ** e for e in range(1, self.f[p] + 1)] for p in self.primes}
        self.units = {}
        self.w = [cmath.exp(2j * math.pi * k / N) for k in range(N)]
        self.use_numpy = bool(use_numpy and _np is not None)

    def _units(self, d):
        u = self.units.get(d)
        if u is None:
            u = [j for j in range(1, d) if math.gcd(j, d) == 1]
            self.units[d] = u
        return u

    def _spectrum(self, xs):
        if not self.use_numpy:
            return None
        v = _np.zeros(self.N)
        v[list(xs)] = 1.0
        return _np.abs(_np.fft.fft(v))

    def vanishes(self, xs, d, spec=None):
        """Exact test of X(zeta_d) = 0 for d | N, d > 1 (see module doc)."""
        N = self.N
        step = N // d
        if spec is not None:
            for j in self._units(d):
                if spec[(j * step) % N] >= 0.5:
                    return False
            return True
        w = self.w
        for j in self._units(d):
            js = j * step
            v = 0j
            for x in xs:
                v += w[(js * x) % N]
            if abs(v) >= 0.5:
                return False
        return True

    def profile(self, xs):
        """Return (S_X as sorted prime powers, T1 holds, list of T2 failures).

        S_X = prime powers q | N with Phi_q | X. T1: |X| = prod of the primes
        of S_X. T2: for prime powers of distinct primes in S_X, their product
        s has Phi_s | X. A T2 failure is such a product s with Phi_s not
        dividing X."""
        xs = sorted(set(x % self.N for x in xs))
        spec = self._spectrum(xs)
        S = {p: [q for q in self.pp[p] if self.vanishes(xs, q, spec)] for p in self.primes}
        SX = sorted(q for p in self.primes for q in S[p])
        t1 = len(xs) == prod(p for p in self.primes for _ in S[p])
        fails = t2_failures(S, lambda s: self.vanishes(xs, s, spec))
        return SX, t1, fails


def t2_failures(S_by_prime, vanishes):
    """S_by_prime: {p: [prime powers of p in S_X]}. vanishes(s) -> bool.
    Returns the products (over >= 2 distinct primes) that do NOT vanish."""
    primes = sorted(S_by_prime)
    options = [[1] + list(S_by_prime[p]) for p in primes]
    fails = []
    for combo in itertools.product(*options):
        parts = [c for c in combo if c != 1]
        if len(parts) < 2:
            continue
        s = prod(parts)
        if not vanishes(s):
            fails.append(s)
    return sorted(fails)


# ------------------------------------------- exact polynomial cross-check
def poly_divmod_monic(a, b):
    """Remainder of integer polynomial a by monic b (coeff lists, low first)."""
    a = list(a)
    db = len(b) - 1
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        if c:
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
    r = a[:db] if db > 0 else []
    return r


def cyclotomic(d, _cache={}):
    """Coefficients (low first) of the d-th cyclotomic polynomial."""
    if d in _cache:
        return _cache[d]
    num = [-1] + [0] * (d - 1) + [1]  # x^d - 1
    for e in divisors(d):
        if e < d:
            num = poly_exact_div(num, cyclotomic(e))
    _cache[d] = num
    return num


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


def vanishes_exact(xs, d):
    """Phi_d divides X(x)? Exponents reduced mod d (x^d = 1 mod Phi_d)."""
    c = [0] * d
    for x in xs:
        c[x % d] += 1
    return not any(poly_divmod_monic(c, cyclotomic(d)))


# ------------------------------------------------------ case analysis
def analyze_case(S, N, time_limit=None, keep_examples=3, keep_failures=50):
    """Enumerate every complement of S in Z_N; classify translation classes."""
    cy = Cyclo(N)
    sizeR = N // len(S)
    res = {
        "N": N, "S": list(S), "size_S": len(S), "size_R": sizeR,
        "solutions_with_0": 0, "classes": 0, "aperiodic_classes": 0,
        "periodic_classes": 0, "aperiodic_classes_mod_reflection": 0,
        "translates_check": 0, "t1_failures": 0, "t2_failure_classes": 0,
        "aperiodic_t2_failure_classes": 0, "t2_failure_examples": [],
        "SR_profiles": {}, "aperiodic_examples": [],
    }
    t0 = time.time()

    def on_solution(R):
        rs = sorted(R)
        if not is_canonical_sorted(rs, N):
            return
        res["classes"] += 1
        stab = stabilizer_size(rs, N)
        res["translates_check"] += sizeR // stab
        aper = stab == 1
        if aper:
            res["aperiodic_classes"] += 1
            c = to_mask(rs)
            if c <= canonical([(-x) % N for x in rs], N):
                res["aperiodic_classes_mod_reflection"] += 1
            if len(res["aperiodic_examples"]) < keep_examples:
                res["aperiodic_examples"].append(list(rs))
        else:
            res["periodic_classes"] += 1
        SX, t1, fails = cy.profile(rs)
        if not t1:
            res["t1_failures"] += 1
        key = ("A" if aper else "P") + ":" + ",".join(map(str, SX))
        res["SR_profiles"][key] = res["SR_profiles"].get(key, 0) + 1
        if fails:
            res["t2_failure_classes"] += 1
            if aper:
                res["aperiodic_t2_failure_classes"] += 1
            if len(res["t2_failure_examples"]) < keep_failures:
                # confirm with exact integer polynomial arithmetic
                exact = (all(vanishes_exact(rs, q) for q in SX)
                         and not any(vanishes_exact(rs, s) for s in fails)
                         and is_tiling(S, rs, N))
                res["t2_failure_examples"].append({"R": list(rs), "S_R": SX, "missing": fails,
                                                   "aperiodic": aper, "exact_confirmed": exact})

    sols, nodes, complete = enumerate_complements(S, N, on_solution, time_limit)
    SX, t1, fails = cy.profile(S)
    res.update({
        "solutions_with_0": sols, "nodes": nodes, "complete": complete,
        "seconds": round(time.time() - t0, 2),
        "S_profile": {"S_S": SX, "t1": t1, "t2_missing": fails, "periodic": is_periodic(S, N)},
        "translates_consistent": res["translates_check"] == sols,
        "R_has_3plus_primes": n_prime_factors(sizeR) >= 3,
        "S_has_3plus_primes": n_prime_factors(len(S)) >= 3,
    })
    return res


# ------------------------------------------------------------ audio
def render_canon_wav(path, S, R, N, pulses_per_second=14.0, cycles=2, rate=22050):
    """Write a mono 16-bit WAV of the canon: voice i enters at S[i] and plays
    rhythm R; every pulse of the cycle is struck by exactly one voice. Each
    voice gets its own pitch (a pentatonic ladder), so the interlocking is
    audible. Pure Python (wave + array)."""
    import array
    import wave
    S = sorted(S)
    ratios = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3]
    pitches = [220.0 * ratios[i % 5] * (2 ** ((i // 5) % 4)) for i in range(len(S))]
    voice_at = {}
    for i, s in enumerate(S):
        for r in R:
            voice_at[(s + r) % N] = i
    dt = 1.0 / pulses_per_second
    total = int(rate * dt * N * cycles) + rate // 2
    buf = [0.0] * total
    note_len = int(rate * min(0.25, 2.5 * dt))
    for c in range(cycles):
        for t in range(N):
            i = voice_at[t]
            f = pitches[i]
            start = int(rate * dt * (c * N + t))
            for k in range(note_len):
                idx = start + k
                if idx >= total:
                    break
                env = math.exp(-k / (rate * 0.06))
                buf[idx] += 0.35 * env * math.sin(2 * math.pi * f * k / rate)
    peak = max(1e-9, max(abs(x) for x in buf))
    data = array.array("h", (int(32767 * 0.9 * x / peak) for x in buf))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())
    return total / rate
