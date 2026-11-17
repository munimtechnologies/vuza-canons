# vuza-canons

Exhaustive enumeration of rhythmic tiling canons (Vuza canons) and a systematic test of the
**Coven–Meyerowitz T2 conjecture** on every rhythm found. Also renders canons as audio.

Made by MV2 of Munim, Inc., with AI agents. Licensed under Apache-2.0. Version 0.3.0.

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
theory of integer tilings. Amiot showed that any counterexample can be collapsed to a **Vuza canon** that
fails T2, so Vuza canons are where a counterexample would have to show up.

## Correction in 0.3.0: where T2 is really open

Version 0.2.0 said T2 was open at periods 360, 420, 504, 540, 600, 630, 660, 840 and 924. **That was
wrong.** It overlooked a published reduction:

- **Łaba–Londner, Corollary 6.2** ("Combinatorial and harmonic-analytic methods for integer tilings",
  arXiv:2106.14042; restated as Lemma 6.2 in "Splitting for integer tilings", arXiv:2407.11374).
  A prime that divides only one of |A| and |B| can be removed from the problem. So in a tiling
  A ⊕ B = Z_M, T2 can only fail if **at least three primes divide both |A| and |B|**.
- Since |A|·|B| = M, every such prime needs p² | M. At 360 = 2³·3²·5 only 2 and 3 qualify, at
  420 = 2²·3·5·7 only 2 does, and so on. T2 is therefore already a theorem at every 0.2.0 period.
- The three-shared-primes case is proven for M = p²q²r² (Łaba–Londner, Invent. Math. 2023; even case,
  Res. Math. Sci. 2025). It is also proven for the families of their splitting theorem
  (arXiv:2407.11374, Thm 1.2: M = pⁿM₁ with p > M₁/rad(M₁)).

`t2open.py` encodes exactly these published results. By our reading of them:

- **The smallest period where some tiling is not covered is M = 1800 = 2³·3²·5².** The only open factor
  sizes there are {30, 60}.
- Below 5000 the open periods are **1800, 2700, 3528, 3600 and 4500**.
- `python t2open.py --limit 20000` lists every open period up to 20000 with its open size pairs.

So the 0.2.0 job at 360–924 is still useful, as the first complete Vuza-canon blocks at those periods
(Jedrzejewski's complete table stops at 168). But its T2 checks there are consistency checks of a
theorem: any "failure" would mean a bug. The search for a counterexample moves to 1800.

Unrefereed 2026 preprints that claim a full proof of T2 (for example arXiv:2609.22280) are not used.
If they hold up, the question is closed.

## What it does

- `vuza.py` builds the standard Vuza rhythms (Jedrzejewski 2013, Theorems 12/14, after Vuza, Hajós and
  de Bruijn) and enumerates **every** complement of a rhythm by exact-cover search.
  - It checks T1 and T2 with an exact cyclotomic-zero test. X(ζ_d) = 0 if and only if every Galois
    conjugate X(ζ_d^j) has absolute value below 1/2, because a nonzero algebraic integer has a norm of at
    least 1.
  - Any T2 failure is re-checked with exact integer polynomial division.
- `closure.py` computes the **closure** of a Vuza canon: all aperiodic complements of S, then all
  aperiodic complements of each of those, and so on until nothing new appears.
  - The result is the whole connected block of Vuza canons containing the seed, counted up to
    translation as in the literature. Every rhythm in it is tested for T1 and T2.
  - Each result now records `t2_open_for_sizes`: whether published theorems leave T2 open for a tiling
    with these factor sizes.
  - The new `open1800` group covers the 24 standard Vuza canons of period 1800 whose two rhythms have
    sizes 30 and 60. Those are exactly the sizes where T2 is open.
  - `--per-set-seconds` caps the time spent on one rhythm, so a block too large to finish is explored
    in breadth instead of getting stuck on its first rhythm.
- `tilec.c` is the same exact-cover search in C, roughly 100× faster. Each run first cross-checks it
  against the Python search (0.3.0 adds a check at N = 1800), and falls back to Python if they ever
  disagree.
- `t2open.py` is the map of where T2 is still open (see above).
- Renders a canon as a WAV file, one pitch per voice, so the interlocking can be heard.

## Pre-registered plans and predictions

### 0.1.0 (2026-11-17, before any run): complements of the standard rhythm (`run_cases.py`)
- **P1:** every completed validation case matches the published count (Auricchio, Ferrarini, Gualandi,
  Pernazza, arXiv 2112.05249).
- **P2:** T1 never fails. This is a theorem, so a failure means a bug.
- **P3:** no complement fails T2.
- **P4:** cases that hit the time budget are reported as incomplete, never as complete.

### 0.2.0 (2026-11-17, before any run): closures (`closure.py`)
- **P5:** the C and Python searches agree on every cross-check case.
- **P6:** for N ≤ 168 every completed closure equals a row of Jedrzejewski's Table 1 (arXiv 1304.6609),
  a complete classification. For example, 72 gives (3 outer, 6 inner), 108 gives (3, 252), 120 gives
  (8, 18) and (16, 20), and 168 gives (16, 54) and (104, 42).
- **P7:** no T1 failure anywhere (a theorem), and no T2 failure. *Corrected in 0.3.0: at every 0.2.0
  period T2 is a theorem, so a failure there would be a bug.*
- **P8:** every completed closure is complete bipartite. This is an open guess, not a theorem.
- **P9:** the number of complements of the standard outer rhythm equals the SAT counts of Auricchio et
  al. wherever those were published (including 22320 and 33480 at N = 420).

### 0.3.0 (2026-11-17, before any run): the smallest open period, 1800
Run: `python closure.py --only open1800 --case-minutes 12 --per-set-seconds 60 --max-classes 300000`.
- **P10:** no rhythm in the explored part of the 1800 blocks fails T2. The job reports how many
  rhythms were checked (`P10_open_rhythms_checked`).
  - A confirmed failure would be a counterexample to the Coven–Meyerowitz conjecture. It would be
    re-verified independently (exact polynomial division, a fresh tiling check) and sent privately to
    specialists before any public claim.
- **P11:** these blocks are far too large to finish in 12 minutes each, so we expect most to be
  reported `"complete": false`. The result is a large sample, not a classification.
- **P12:** all 24 standard seeds are genuine Vuza canons (both rhythms aperiodic), as Jedrzejewski's
  theorem says. Any seed reported as "not a Vuza canon" means a bug in our construction.

The "wow" outcome would be a tile that fails T2, which is a counterexample to a 27-year-old conjecture.
The realistic outcome is a clean negative result at the smallest period where the question is open,
plus the first complete Vuza-canon blocks at 360–924, a dataset of canons that composers can use.

## Run

```
pip install -r requirements.txt   # numpy is optional (speed only)
python -m unittest -v test_vuza test_closure test_t2open   # VUZA_TEST_C=1 also tests tilec.c (needs gcc)
python t2open.py --limit 20000 --out out/t2_open_periods.json
python closure.py --out-dir out --case-minutes 20 --total-minutes 420
python closure.py --out-dir out1800 --only open1800 --case-minutes 12 --per-set-seconds 60 --max-classes 300000 --dump-max 20000
```

Outputs:
- `out/closure_summary.json` (prediction checks) and `out/closure_results.json` (counts, cyclotomic
  profiles, any T2 failures);
- `out/classes/N<N>_<params>_side{0,1}.txt.gz`, every rhythm found, one per line (`_first` files hold
  only the first part when a block is too large);
- WAV renderings of canons;
- `t2_open_periods.json`, the open periods and their open size pairs.

## Honest limits

- A closure is one connected block. It is not necessarily every Vuza canon of its period, because other
  constructions can start other blocks.
- A clean result (no T2 failure) is evidence, not a proof. At 1800 it is a partial search.
- `t2open.py` is only as complete as the list of results it encodes. A newer theorem could close more
  periods. It can only err toward calling a period open, never toward calling an open one closed.
- Search time grows quickly with N. Anything cut by a budget is marked `"complete": false`.

## References

- E. M. Coven, A. Meyerowitz, *Tiling the integers with translates of one finite set*, J. Algebra 212 (1999).
- I. Łaba, I. Londner, *Combinatorial and harmonic-analytic methods for integer tilings*, arXiv:2106.14042.
- I. Łaba, I. Londner, *The Coven–Meyerowitz tiling conditions for 3 odd prime factors*, Invent. Math. 232 (2023); *… the even case*, Res. Math. Sci. 12 (2025).
- I. Łaba, I. Londner, *Splitting for integer tilings*, arXiv:2407.11374.
- G. Kiss, C. Marshall, M. Matolcsi, G. Somlai, *Nonnegative weak tilings and the Coven–Meyerowitz condition (T2)*, arXiv:2611.13593 (weak tilings that fail T2; no set counterexample).
- E. Amiot, *New perspectives on rhythmic canons and the spectral conjecture*, J. Math. Music 3 (2009).
- F. Jedrzejewski, *Enumeration of Vuza canons*, arXiv:1304.6609.
- M. N. Kolountzakis, M. Matolcsi, *Algorithms for translational tiling*, J. Math. Music 3 (2009).
- G. Auricchio, L. Ferrarini, S. Gualandi, L. Pernazza, *Computing aperiodic tiling rhythmic canons via SAT models*, Constraints (2024); arXiv:2112.05249.
