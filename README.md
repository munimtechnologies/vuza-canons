# vuza-canons

Exhaustive enumeration of rhythmic tiling canons (Vuza canons) and a systematic test of the
**Coven–Meyerowitz T2 conjecture** on every rhythm found. Also renders canons as audio.

Made by MV2 of Munim, Inc., with AI agents. Licensed under Apache-2.0. Version 0.2.0.

## The question

A *rhythmic canon* of period N is a tiling Z_N = S ⊕ R. The voices enter at the offsets in S, each
voice plays the rhythm R, and together they strike every pulse of the cycle exactly once. Dan Tudor Vuza
(1991) found canons in which **neither** rhythm repeats itself (*Vuza canons*). They exist only for
special periods: 72, 108, 120, 144, 168, 180, …

The same objects are central to an open problem in mathematics. Coven and Meyerowitz (1999) gave two
conditions on the cyclotomic factors of a finite set of integers, T1 and T2, and proved:
- T1 and T2 together imply that the set tiles the integers;
- T1 is necessary for tiling;
- T2 is necessary when the size of the set has at most two prime factors.

**Whether T2 is always necessary is open.** Łaba and Londner call it the main open question in the
theory of integer tilings. They proved T2 for every tiling of period p²q²r² (Invent. Math. 2023; even
case, Res. Math. Sci. 2025). Amiot showed that any counterexample can be collapsed to a **Vuza canon**
that fails T2. So Vuza canons are where a counterexample would have to show up. This project searches
periods where T2 is not yet a theorem and one side of the canon has three distinct primes in its size:
360, 420, 504, 540, 600, 630, 660, 840 and 924.

## What it does

- `vuza.py` builds the standard Vuza rhythms (Jedrzejewski 2013, Theorems 12/14, after Vuza, Hajós and
  de Bruijn) and enumerates **every** complement of a rhythm by exact-cover search.
  - It checks T1 and T2 with an exact cyclotomic-zero test. X(ζ_d) = 0 if and only if every Galois
    conjugate X(ζ_d^j) has absolute value below 1/2, because a nonzero algebraic integer has a norm of at
    least 1.
  - Any T2 failure is re-checked with exact integer polynomial division.
- `closure.py` (new in 0.2.0) computes the **closure** of a Vuza canon: all aperiodic complements of S,
  then all aperiodic complements of each of those, and so on until nothing new appears.
  - The result is the whole connected block of Vuza canons containing the seed, counted up to
    translation as in the literature. Every rhythm in it is tested for T1 and T2.
  - It also tests whether each block is *complete bipartite*: does every outer rhythm tile with every
    inner rhythm? The usual count "#S × #R canons" assumes this.
- `tilec.c` is the same exact-cover search in C, roughly 100× faster. Each run first cross-checks it
  against the Python search, and falls back to Python if they ever disagree.
- Renders a canon as a WAV file, one pitch per voice, so the interlocking can be heard.

## Pre-registered plans and predictions

### 0.1.0 (2026-11-17, before any run): complements of the standard rhythm (`run_cases.py`)
- **P1:** every completed validation case matches the published count (Auricchio, Ferrarini, Gualandi,
  Pernazza, arXiv 2112.05249).
- **P2:** T1 never fails. This is a theorem, so a failure means a bug.
- **P3:** no complement fails T2.
- **P4:** cases that hit the time budget are reported as incomplete, never as complete.

### 0.2.0 (2026-11-17, before any run): closures (`closure.py`)
Case list: validation periods 72–168, all twelve parameter sets at N = 420, the new periods 360, 504,
540, 600, 630, 660, 840 and 924, then the 180 blocks with published lower bounds.
- **P5:** the C and Python searches agree on every cross-check case.
- **P6:** for N ≤ 168 every completed closure equals a row of Jedrzejewski's Table 1 (arXiv 1304.6609),
  a complete classification. For example, 72 gives (3 outer, 6 inner), 108 gives (3, 252), 120 gives
  (8, 18) and (16, 20), and 168 gives (16, 54) and (104, 42).
- **P7:** no T1 failure anywhere (a theorem), and no T2 failure (the conjecture).
  - A confirmed T2 failure would disprove the necessity of T2. It would be re-verified with an
    independent implementation and sent to specialists before any public claim.
- **P8:** every completed closure is complete bipartite. This is an open guess, not a theorem, and the
  run will settle it for each block.
- **P9:** the number of complements of the standard outer rhythm equals the SAT counts of Auricchio et
  al. wherever those were published (including 22320 and 33480 at N = 420).
- Closures that hit the time or size budget are reported as incomplete, with the counts reached.

The "wow" outcome would be a tile that fails T2, which is a counterexample to a 27-year-old conjecture.
The realistic outcome is the first complete Vuza-canon blocks at periods 360–924, each with a T2 check
on every rhythm. That would be a clean negative result on a large new search space, plus a dataset of
canons that composers can use.

## Run

```
pip install -r requirements.txt   # numpy is optional (speed only)
python -m unittest -v test_vuza test_closure      # VUZA_TEST_C=1 also tests tilec.c (needs gcc)
python run_cases.py --out-dir out --case-minutes 12
python closure.py --out-dir out --case-minutes 20 --total-minutes 420
```

Outputs:
- `out/summary.json` and `out/results.json` (complements of the standard rhythm);
- `out/closure_summary.json` (prediction checks) and `out/closure_results.json` (counts, cyclotomic
  profiles, any T2 failures);
- `out/classes/N<N>_<params>_side{0,1}.txt.gz`, every rhythm found, one per line;
- WAV renderings of canons.

## Honest limits

- A closure is one connected block. It is not necessarily every Vuza canon of its period, because other
  constructions can start other blocks.
- A clean result (no T2 failure) is evidence, not a proof.
- Search time grows quickly with N. Anything cut by a budget is marked `"complete": false`.

## References

- E. M. Coven, A. Meyerowitz, *Tiling the integers with translates of one finite set*, J. Algebra 212 (1999).
- I. Łaba, I. Londner, *The Coven–Meyerowitz tiling conditions for 3 odd prime factors*, Invent. Math. 232 (2023); *… the even case*, Res. Math. Sci. 12 (2025); *Splitting for integer tilings*, arXiv:2407.11374.
- E. Amiot, *New perspectives on rhythmic canons and the spectral conjecture*, J. Math. Music 3 (2009).
- F. Jedrzejewski, *Enumeration of Vuza canons*, arXiv:1304.6609.
- M. N. Kolountzakis, M. Matolcsi, *Algorithms for translational tiling*, J. Math. Music 3 (2009).
- G. Auricchio, L. Ferrarini, S. Gualandi, L. Pernazza, *Computing aperiodic tiling rhythmic canons via SAT models*, Constraints (2024); arXiv:2112.05249.
