# vuza-canons

Exhaustive enumeration of rhythmic tiling canons (Vuza canons) and a systematic test of the
**Coven–Meyerowitz T2 conjecture**. Also renders canons as audio.

Made by MV2 of Munim, Inc., with AI agents. Licensed under Apache-2.0 (notes: CC BY 4.0). Version 0.5.1.

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

## New in 0.5.1: a proof that closes the Φ₆ route below 5400 (`foldlemma.py`, `notes/fold_lemma.md`)

**Proposition.** Let A ⊕ B = Z_M with |A| = 30, Φ₅ and Φ₆ dividing A(x), and Φ₂, Φ₃, Φ₁₀, Φ₁₅, Φ₃₀ not
dividing it. Write M/180 = 5^s·k′ with 5 ∤ k′. If Φ₆ does not divide B(x), then k′ ≥ 6.

The hypotheses only depend on A mod 30, so they hold for **every lift** of the Tan–Zhang tiles S180 and
C180. Consequences:
- At the open lift periods **1800, 2700 and 3600** (and at 4500), no set complement of such a lift misses
  Φ₆. Prediction L5 of 0.5.0 is therefore a theorem for both tiles. A T2 failure there would have to be
  witnessed by an order involving 8, 16, 25 or 27 (at 1800: 24, 50, 150, 200 or 600).
- Together with Łaba–Londner Cor. 6.2, **5400 = 2³·3³·5² is the least period at which a lift of these
  tiles could have a set complement missing Φ₆**.
- The proof folds the tiling mod 30, where the complement's counts must have the form w(x mod 5) + v(x mod 6),
  and mod 5^e, where Φ₂₅ | B forces 5^{e−1} | w. The second step does the work: the fold mod 30 alone
  would allow 750 profiles at 1800.

Why this was needed: KMMS Prop. 6.2 (every normalized weak complement of S180 *itself* satisfies T2) does
not apply to lifts, because a lift's complement folds to a weak complement that is not normalized. 0.5.0
had leaned on it for L5. The full proof is in `notes/fold_lemma.md`. `foldlemma.py` checks its
computational steps exactly (cyclotomic remainders, the kernel over ℚ, and every surviving profile), and
`test_foldlemma.py` asserts that it reproduces `fold_lemma.json`. **No human expert has checked the proof yet.**

`fold6sat.py` (job vuza-fold6-v1) then puts the solver where the cheap argument is silent:
- **hard negatives** k = 6–9 (M = 1080–1620): the folds allow a Φ₆ failure, but Łaba–Londner forbids
  it. These test whether CP-SAT can find the deeper obstruction on its own;
- **frontier** k = 30 (M = 5400): the least period the proposition leaves open for Φ₆.

Pre-registered (2026-11-19, before any run): F1 every configuration tiles; F2 no FEASIBLE among the hard
negatives; F3 no verified failure at 5400 (we expect UNKNOWN there); F4 the lemma checks reproduce
`fold_lemma.json` inside the job.

## 0.5.0: hunting where the weak counterexamples live (`liftsat.py`)

Two 2026 preprints sharpen where a counterexample could be:

- A tiling A ⊕ B = Z_M fails T2 on the B side exactly when some product N of B's prime powers has
  Φ_N ∤ B. Tiling then forces Φ_N | A while no prime power of N divides A. Kiss, Łaba, Marshall and
  Somlai call such a Φ_N an **unsupported divisor** of A. So every counterexample is a tile with an
  unsupported divisor.
- **Tan and Zhang** (arXiv:2609.06677) show that 180 is the least period of an unsupported divisor, and
  900 the least for a three-prime one. Their period-180 tiles have size 30, signature {4, 5, 9} and
  unsupported Φ_6:
  - `S180` = {30j + c : j < 6, c ∈ {0, 2, 3, 4, 6}} (periodic);
  - `C180` = the aperiodic set of their §8.1, with complement {0, 20, 40, 45, 65, 85}.

  Their period-900 examples are 5·S180 and 5·C180.
- **Kiss, Marshall, Matolcsi and Somlai** (arXiv:2611.13593) prove that tiles like these have
  nonnegative rational **weak** complements that fail T2, for example at period 180. But "no such set
  complement is constructed here". Dilation does not change the set question (their Prop. 6.3).

`liftsat.py` asks the set question directly. Fix a source tile X of period 180, and let A run over
**every lift** of X to Z_M, M = 180k: every set with A ≡ X mod 180, giving k choices for each of the 30
points. Then CP-SAT searches for a set B with A ⊕ B = Z_M in which B (or A) fails T2. Because A is fixed
mod 180, every cyclotomic order dividing 180 is decided in plain Python, so the models stay small.

| configs | M | sizes | status |
|---|---|---|---|
| k = 1, 2, 3, 4 | 180–720 | 30 / 6k | theorem (Łaba–Londner Cor. 6.2): controls |
| k = 5 | 900 | 30 / 30 | theorem (Łaba–Londner, p²q²r²): control |
| 5·X lifted ×2, 2·X lifted ×5 | 1800 | 30 / 60 | theorem via dilation: **same-size controls** |
| **k = 10** | **1800** | 30 / 60 | **open** (Φ₆ case closed by the 0.5.1 proposition) |
| **k = 15** | **2700** | 30 / 90 | **open** (Φ₆ case closed) |
| **k = 20** | **3600** | 30 / 120 | **open** (Φ₆ case closed) |

Every solver answer is re-checked from scratch: the lift, a direct tiling count, and the failing
divisibility by two independent exact tests. `python liftsat.py --list` prints the full plan without
the solver.

### Pre-registered predictions for 0.5.0 (2026-11-18, before any run)

Run: `python liftsat.py --out-dir out --workers 4 --total-minutes 320`.
- **L1 (sources):** S180 and C180 each tile Z_180 with the published complement, satisfy T1 and T2, and
  have Φ_6 as an unsupported divisor. Hand-checked; also in the unit tests.
- **L2 (positive control):** every configuration finds a verified tiling without the failure condition.
- **L3 (validation):** no T2 case is FEASIBLE in a theorem configuration. The INFEASIBLE share of the
  three same-size 1800 controls measures whether the method is strong enough to trust at 1800.
- **L4:** no verified T2 failure in the open configurations. We expect mostly INFEASIBLE, with some
  UNKNOWN at 2700 and 3600.
- **L5:** every case where a lift of S180 asks B to miss Φ_6 is INFEASIBLE. This is the case KMMS
  Prop. 6.2 rules out for weak complements of S180 itself. *(Added 2026-11-19: L5 is unchanged, but its
  justification was wrong, because Prop. 6.2 does not cover lifts. The 0.5.1 proposition proves L5 for
  k = 10, 15 and 20, so these cases are now exact negative controls. Any FEASIBLE among them is a bug.)*
- A verified FEASIBLE case in an open configuration would be a counterexample to the Coven–Meyerowitz
  conjecture. It would be written to `T2_COUNTEREXAMPLE_CANDIDATES.json`, re-verified in a fresh job and
  sent privately to specialists before any public claim.
- **All INFEASIBLE** would be the first evidence that the known weak-counterexample tiles have no
  T2-failing *set* complement at 1800, 2700 and 3600. This is a targeted search, not all tilings, and
  it depends on the solver.

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

## 0.4.0: every tiling at once (`profsat.py`)

`profsat.py` asks the question for **all tilings A ⊕ B = Z_1800 with |A| = 30, |B| = 60 at once**, as
constraint problems solved with CP-SAT (Google OR-Tools):

- A ⊕ B = Z_M exactly when |A|·|B| = M and every Φ_d (d | M, d > 1) divides A(x) or B(x).
- "Φ_d divides X(x)" is a **linear** condition on the residue counts of X mod d. With m = rad(d),
  Φ_d(x) = Φ_m(x^{d/m}), so only remainders modulo Φ_2, …, Φ_30 are needed.
- T1 holds for every tile, so the prime powers {2, 4, 8, 3, 9, 5, 25} split between A and B in one of
  only **12 profiles**. That gives 12 × (4 + 7) = **132 cases**, each one 0/1 model with 3600 set
  variables.
- Pre-registered P13–P16 (2026-11-17): no FEASIBLE case at 360 or 900 (validation), every profile tiles,
  the "does not divide" encoding is not vacuous, and no verified failure at 1800.

`liftsat.py` (0.5.0) is the targeted complement to this: profsat asks about every tiling, which is
harder to settle, while liftsat concentrates on the tiles where weak counterexamples are known to exist.

## Everything in the repo

- `vuza.py` builds the standard Vuza rhythms (Jedrzejewski 2013, Theorems 12/14, after Vuza, Hajós and
  de Bruijn) and enumerates **every** complement of a rhythm by exact-cover search. It checks T1 and T2
  with an exact cyclotomic-zero test.
- `closure.py` computes the **closure** of a Vuza canon: all aperiodic complements of S, then all aperiodic
  complements of each of those, and so on until nothing new appears.
- `tilec.c` is the same exact-cover search in C, roughly 100× faster, cross-checked against Python.
- `t2open.py` is the map of where T2 is still open (see above).
- `profsat.py` is the all-tilings profile search (0.4.0).
- `liftsat.py` is the lift search over tiles with unsupported divisors (0.5.0).
- `foldlemma.py`, `notes/fold_lemma.md` and `fold_lemma.json` are the fold proposition: proof, exact checks and numbers (0.5.1).
- `fold6sat.py` runs the solver on the hard negatives and on the 5400 frontier (0.5.1).
- WAV rendering of a canon, one pitch per voice, so the interlocking can be heard.

## Earlier pre-registered predictions

- **0.1.0** (`run_cases.py`): P1 published complement counts reproduced (Auricchio et al., arXiv
  2112.05249); P2 T1 never fails; P3 no complement fails T2; P4 incomplete cases reported as incomplete.
- **0.2.0** (`closure.py`): P5 C and Python agree; P6 closures for N ≤ 168 match Jedrzejewski's Table 1;
  P7 no T1/T2 failure (T2 is a theorem at every 0.2.0 period); P8 every complete closure is complete
  bipartite (an open guess); P9 complement counts match the published SAT counts.
- **0.3.0** (`closure.py --only open1800`): P10 no T2 failure in the explored 1800 blocks; P11 most blocks
  incomplete; P12 all 24 standard seeds are Vuza canons.

The "wow" outcome would be a tile that fails T2: a counterexample to a 27-year-old conjecture. The other
strong outcome is evidence, and eventually a computer-assisted proof, that T2 holds at 1800, the smallest
period that no theorem covers.

## Run

```
pip install -r requirements.txt        # numpy is optional (speed only)
pip install -r requirements-sat.txt    # OR-Tools, only for profsat.py, liftsat.py and fold6sat.py
python -m unittest -v test_vuza test_closure test_t2open test_profsat test_liftsat test_foldlemma test_fold6sat
python foldlemma.py --out out/fold_lemma_computed.json
python t2open.py --limit 20000 --out out/t2_open_periods.json
python liftsat.py --list
python liftsat.py --out-dir out --workers 4 --total-minutes 320
python fold6sat.py --out-dir out --workers 2 --total-minutes 225
python profsat.py --out-dir out --periods 360:30,900:30,1800:30 --seconds 20,40,90 --workers 2
```

`liftsat.py` writes `liftsat_plan.json`, `liftsat_results.jsonl` (one line per model, with every tiling
found), `liftsat_summary.json` (predictions L1–L5 and counts) and, only if a T2 failure appears,
`T2_COUNTEREXAMPLE_CANDIDATES.json`. `profsat.py` and `fold6sat.py` write the same kinds of files under
`profsat_*` and `fold6_*`.

## Honest limits

- The fold proposition is a hand proof with machine-checked arithmetic. No human expert has refereed it yet.
- CP-SAT answers INFEASIBLE without a proof certificate. Until a second, independent solver (ideally one
  that emits a checkable proof) agrees, an all-INFEASIBLE result is strong evidence, not a theorem.
- UNKNOWN means the time limit ran out; it says nothing either way.
- `liftsat.py` covers only lifts of two source tiles (and their dilates), not every tiling.
- A closure is one connected block, not necessarily every Vuza canon of its period.
- `t2open.py` is only as complete as the list of results it encodes. It can only err toward calling a
  period open, never toward calling an open one closed.

## References

- E. M. Coven, A. Meyerowitz, *Tiling the integers with translates of one finite set*, J. Algebra 212 (1999).
- I. Łaba, I. Londner, *Combinatorial and harmonic-analytic methods for integer tilings*, arXiv:2106.14042.
- I. Łaba, I. Londner, *The Coven–Meyerowitz tiling conditions for 3 odd prime factors*, Invent. Math. 232 (2023); *… the even case*, Res. Math. Sci. 12 (2025).
- I. Łaba, I. Londner, *Splitting for integer tilings*, arXiv:2407.11374.
- G. Kiss, I. Łaba, C. Marshall, G. Somlai, *Lower bounds for mask polynomials with many cyclotomic divisors*, arXiv:2507.11672 (Adv. Math. 494, 2026).
- G. Kiss, C. Marshall, M. Matolcsi, G. Somlai, *Nonnegative weak tilings and the Coven–Meyerowitz condition (T2)*, arXiv:2611.13593.
- H. Tan, Y. Zhang, *Unsupported cyclotomic divisors in three-prime integer tilings*, arXiv:2609.06677.
- E. Amiot, *New perspectives on rhythmic canons and the spectral conjecture*, J. Math. Music 3 (2009).
- F. Jedrzejewski, *Enumeration of Vuza canons*, arXiv:1304.6609.
- M. N. Kolountzakis, M. Matolcsi, *Algorithms for translational tiling*, J. Math. Music 3 (2009).
- G. Auricchio, L. Ferrarini, S. Gualandi, L. Pernazza, *Computing aperiodic tiling rhythmic canons via SAT models*, Constraints (2024); arXiv:2112.05249.
