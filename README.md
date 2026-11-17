# vuza-canons

Exhaustive enumeration of rhythmic tiling canons (Vuza canons) and a systematic test of the
**Coven–Meyerowitz T2 conjecture**. Also renders canons as audio.

Made by MV2 of Munim, Inc., with AI agents. Licensed under Apache-2.0. Version 0.4.0.

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

## Where T2 is really open (since 0.3.0)

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
  sizes there are {30, 60}. (Splitting needs 2 > 15, 3 > 20 or 5 > 12; none holds.)
- Below 5000 the open periods are **1800, 2700, 3528, 3600 and 4500**.
- `python t2open.py --limit 20000` lists every open period up to 20000 with its open size pairs.

## New in 0.4.0: every tiling at once (`profsat.py`)

`closure.py` samples Vuza canons one rhythm at a time. At 1800 the blocks are far too big to finish.
`profsat.py` asks the question for **all tilings A ⊕ B = Z_1800 with |A| = 30, |B| = 60 at once**, as
constraint problems solved with CP-SAT (Google OR-Tools):

- A ⊕ B = Z_M exactly when |A|·|B| = M and every Φ_d (d | M, d > 1) divides A(x) or B(x).
- "Φ_d divides X(x)" is a **linear** condition on the residue counts of X mod d. With m = rad(d),
  Φ_d(x) = Φ_m(x^{d/m}), so only remainders modulo Φ_2, …, Φ_30 are needed.
- T1 holds for every tile, so the prime powers {2, 4, 8, 3, 9, 5, 25} split between A and B in one of
  only **12 profiles**. A T2 failure means that one side misses some product s of its own prime powers.
  That gives 12 × (4 + 7) = **132 cases**, each one 0/1 model with 3600 set variables.
- **All 132 INFEASIBLE** would mean that T2 holds for every tiling of period 1800, the smallest open
  case. That would be a computer-assisted claim that depends on the solver, and it needs an independent
  second check before anyone should call it a theorem. **A verified FEASIBLE case** would be a
  counterexample to the Coven–Meyerowitz conjecture. Every solver answer is re-checked from scratch
  (direct tiling count, plus exact divisibility by two independent methods).

### Pre-registered predictions for 0.4.0 (2026-11-17, before any run)

Run: `python profsat.py --periods 360:30,900:30,1800:30 --seconds 20,40,90 --control-seconds 20 --workers 2`.
- **P13 (validation):** at 360 (sizes 30/12) and 900 (sizes 30/30), where T2 is a theorem, no T2 case is
  FEASIBLE. A FEASIBLE case there would mean a bug. The share proven INFEASIBLE within the time limit
  measures how strong the method is (reported as `validation_strength`).
- **P14 (positive control):** for every profile at every period, the model without the failure condition
  finds a real tiling, verified by direct counting. Coven–Meyerowitz standard sets show that one exists.
- **P15 (encoding control):** one side alone with the failure condition always finds a set, verified
  exactly. This shows the "Φ_s does not divide" encoding is not vacuous.
- **P16:** no verified T2 failure at 1800. We expect a mix of INFEASIBLE and UNKNOWN in this first pilot
  (90 seconds per case on 2 CPUs), and we will report the counts as they come out.
- If a T2 failure is ever verified, it will be re-verified independently and sent privately to
  specialists before any public claim.

## Everything in the repo

- `vuza.py` builds the standard Vuza rhythms (Jedrzejewski 2013, Theorems 12/14, after Vuza, Hajós and
  de Bruijn) and enumerates **every** complement of a rhythm by exact-cover search. It checks T1 and T2
  with an exact cyclotomic-zero test. Any T2 failure is re-checked with exact integer polynomial division.
- `closure.py` computes the **closure** of a Vuza canon: all aperiodic complements of S, then all aperiodic
  complements of each of those, and so on until nothing new appears. The `open1800` group covers the 24
  standard Vuza canons of period 1800 with rhythm sizes 30 and 60.
- `tilec.c` is the same exact-cover search in C, roughly 100× faster, cross-checked against Python.
- `t2open.py` is the map of where T2 is still open (see above).
- `profsat.py` is the all-tilings profile search (see above).
- WAV rendering of a canon, one pitch per voice, so the interlocking can be heard.

## Earlier pre-registered predictions

### 0.1.0 (2026-11-17, before any run): complements of the standard rhythm (`run_cases.py`)
- **P1:** every completed validation case matches the published count (Auricchio, Ferrarini, Gualandi,
  Pernazza, arXiv 2112.05249).
- **P2:** T1 never fails. This is a theorem, so a failure means a bug.
- **P3:** no complement fails T2.
- **P4:** cases that hit the time budget are reported as incomplete, never as complete.

### 0.2.0 (2026-11-17, before any run): closures (`closure.py`)
- **P5:** the C and Python searches agree on every cross-check case.
- **P6:** for N ≤ 168 every completed closure equals a row of Jedrzejewski's Table 1 (arXiv 1304.6609).
- **P7:** no T1 failure anywhere (a theorem), and no T2 failure. *Since 0.3.0: at every 0.2.0 period T2
  is a theorem, so a failure there would be a bug.*
- **P8:** every completed closure is complete bipartite. This is an open guess, not a theorem.
- **P9:** the number of complements of the standard outer rhythm equals the published SAT counts.

### 0.3.0 (2026-11-17, before any run): the smallest open period, 1800 (`closure.py --only open1800`)
- **P10:** no rhythm in the explored part of the 1800 blocks fails T2.
- **P11:** most 1800 blocks are reported `"complete": false`; the result is a sample.
- **P12:** all 24 standard seeds are genuine Vuza canons.

The "wow" outcome would be a tile that fails T2: a counterexample to a 27-year-old conjecture. The other
strong outcome is a computer-assisted proof that T2 holds at 1800, the smallest period no theorem covers.

## Run

```
pip install -r requirements.txt        # numpy is optional (speed only)
pip install -r requirements-sat.txt    # OR-Tools, only for profsat.py
python -m unittest -v test_vuza test_closure test_t2open test_profsat
python t2open.py --limit 20000 --out out/t2_open_periods.json
python profsat.py --out-dir out --periods 360:30,900:30,1800:30 --seconds 20,40,90 --workers 2
python closure.py --out-dir out1800 --only open1800 --case-minutes 12 --per-set-seconds 60 --max-classes 300000
```

`profsat.py` writes `profsat_results.jsonl` (one line per model, with every tiling it found),
`profsat_summary.json` (the predictions and counts) and, only if a T2 failure appears,
`T2_COUNTEREXAMPLE_CANDIDATES.json`.

## Honest limits

- CP-SAT answers INFEASIBLE without a proof certificate. Until a second, independent solver (ideally one
  that emits a checkable proof) agrees, an all-INFEASIBLE result at 1800 is strong evidence, not a theorem.
- UNKNOWN means the time limit ran out; it says nothing either way.
- A closure is one connected block, not necessarily every Vuza canon of its period.
- `t2open.py` is only as complete as the list of results it encodes. It can only err toward calling a
  period open, never toward calling an open one closed.

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
