# vuza-canons

Exhaustive enumeration of rhythmic tiling canons (Vuza canons) and a systematic test of the
**Coven–Meyerowitz T2 conjecture**. Also renders canons as audio.

Made by MV2 of Munim, Inc., with AI agents. Licensed under Apache-2.0 (notes and results files: CC BY 4.0). Version 0.7.0.

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

## New in 0.7.0: the last route is closed (`phi6close.py`, `notes/phi6_close.md`)

**Theorem.** Let A be a lift of S180 or C180 to Z_{180k} (A ≡ X mod 180), where every prime factor of k is
2, 3 or 5, and let A ⊕ B = Z_{180k}. Then Φ₆ divides B.

**Corollary** (with the 0.6.0 route theorem). **Every tiling of Z_{180k} by a lift of S180 or C180 satisfies
T2, for every k whose prime factors are 2, 3 and 5.** This settles 5400, the period that 0.6.0 left open, and
every larger such period. By KMMS Prop. 6.3 the same holds for lifts of the period-900 dilates. With
Łaba–Londner Cor. 6.2, the least period where a lift of these tiles is not settled is 6300 = 180·35.

The proof adds two folds to the 0.5.1 fold proposition. The complement's residue counts mod 3·2^a and mod
2·3^b turn out to be periodic, because the route theorem forces Φ_{3·2^j} and Φ_{2·3^j} into B. This makes
B₆ divisible by 2^{a−2}·3^{b−2}. Together with the 5-adic fold, it forces the Φ₆-part v of B₃₀ to be a
multiple of k. Nonnegativity then leaves no room for v ≠ 0. At 5400, the 0.5.1 fold allowed 450 candidate
profiles with a Φ₆ failure; after the new divisibility, none are left. `phi6close.py` re-checks every step exactly
for all 26 values of k ≤ 60 with those prime factors, and `test_phi6close.py` asserts that it reproduces
`phi6_close.json`. **No human expert has checked the proof yet.**

## 0.6.0: every route but Φ₆ is closed (`liftroutes.py`, `notes/lift_routes.md`)

A tiling A ⊕ B = Z_M breaks T2 on the B side at an order N only if Φ_N divides A without support (an
*unsupported divisor*). Tan and Zhang's tiles S180 and C180 are the smallest tiles with one (Φ₆), and their
**lifts** A ⊂ Z_{180k} (A ≡ X mod 180) are where our counterexample search looks.

**Theorem.** If every prime factor of k is 2, 3 or 5, then no lift of S180 or C180 has Φ_N | A for any order
N at which T2 for B could fail, except N = 6.

The proof combines three exact steps: splitting a vanishing sum by classes mod p when p² | N, shifting out
a common residue, and the Lam–Leung weight theorem. It also uses two small facts about the tiles. For example,
the class 4 mod 5 of both tiles is 4 + 30·{0..5}. `liftroutes.py` re-derives every case mechanically for
all 26 values of k ≤ 60 with those prime factors (the engine only ever answers "excluded" with a proof).

## 0.5.1: the fold proposition (`foldlemma.py`, `notes/fold_lemma.md`)

**Proposition.** Let A ⊕ B = Z_M with |A| = 30, Φ₅ and Φ₆ dividing A(x), and Φ₂, Φ₃, Φ₁₀, Φ₁₅, Φ₃₀ not
dividing it. Write M/180 = 5^s·k′ with 5 ∤ k′. If Φ₆ does not divide B(x), then k′ ≥ 6.

0.7.0 strengthens this for lifts: no k with prime factors 2, 3 and 5 allows a Φ₆ failure.

`fold6sat.py` (job vuza-fold6-v1) asks CP-SAT about k = 6–9 and k = 30 (M = 5400). After 0.7.0, every case
it asks about has a proven negative answer, so the job can only measure the solver.

## 0.5.0: hunting where the weak counterexamples live (`liftsat.py`)

- **Tan and Zhang** (arXiv:2609.06677) show that 180 is the least period of an unsupported divisor, and
  900 the least for a three-prime one. Their period-180 tiles have size 30, signature {4, 5, 9} and
  unsupported Φ_6:
  - `S180` = {30j + c : j < 6, c ∈ {0, 2, 3, 4, 6}} (periodic);
  - `C180` = the aperiodic set of their §8.2, with complement {0, 20, 40, 45, 65, 85}.
  Their Theorem 7.4 classifies every complement of one specific periodic set at the periods 180·5^j and
  shows that each one satisfies T2. 0.7.0 covers **arbitrary** lifts, at every 5-smooth period.
- **Kiss, Marshall, Matolcsi and Somlai** (arXiv:2611.13593) prove that tiles like these have
  nonnegative rational **weak** complements that fail T2. But "no such set complement is constructed
  here". Dilation does not change the set question (their Prop. 6.3).

`liftsat.py` lets A run over every lift of X to Z_M, M = 180k, and asks CP-SAT for a set B with
A ⊕ B = Z_M in which B (or A) fails T2. After 0.7.0, every one of its cases is a proven negative.

## Where T2 is really open (since 0.3.0)

- **Łaba–Londner, Corollary 6.2** (arXiv:2106.14042; Lemma 6.2 in arXiv:2407.11374): in a tiling
  A ⊕ B = Z_M, T2 can only fail if **at least three primes divide both |A| and |B|**.
- The three-shared-primes case is proven for M = p²q²r² (Łaba–Londner, Invent. Math. 2023; even case,
  Res. Math. Sci. 2025) and for the families of their splitting theorem (arXiv:2407.11374, Thm 1.2).
- `t2open.py` encodes exactly these published results. By our reading, **the smallest period where some
  tiling is not covered is M = 1800 = 2³·3²·5²** (sizes {30, 60}), and below 5000 the open periods are
  1800, 2700, 3528, 3600 and 4500. 0.6.0 and 0.7.0 settle the lifts of the Tan–Zhang tiles there, **not**
  every tiling at those periods.
- A preprint (Prajapati, arXiv:2609.22280) claims a proof of T2 for all integer tiles. It is unrefereed, and
  we treat T2 as open.

## 0.4.0: every tiling at once (`profsat.py`)

`profsat.py` asks the question for all tilings A ⊕ B = Z_1800 with |A| = 30, |B| = 60 at once, as 132
CP-SAT cases (12 T1 profiles × 11 T2 conditions). Pre-registered P13–P16 (2026-11-17).

## Everything in the repo

- `vuza.py`, `tilec.c`, `closure.py`: Vuza canons, every complement by exact cover (Python and C), closures.
- `t2open.py`: the map of where T2 is still open.
- `profsat.py`: the all-tilings profile search (0.4.0).
- `liftsat.py`: the lift search over tiles with unsupported divisors (0.5.0).
- `foldlemma.py`, `notes/fold_lemma.md`, `fold_lemma.json`: the fold proposition (0.5.1).
- `fold6sat.py`: the solver on the hard negatives and on 5400 (0.5.1).
- `liftroutes.py`, `notes/lift_routes.md`, `lift_routes.json`: every route but Φ₆ closed (0.6.0).
- `phi6close.py`, `notes/phi6_close.md`, `phi6_close.json`: Φ₆ closed, T2 for every lift at 5-smooth
  periods (0.7.0).
- WAV rendering of a canon, one pitch per voice, so the interlocking can be heard.

## Earlier pre-registered predictions

- **0.1.0** (`run_cases.py`): P1 published complement counts reproduced (Auricchio et al., arXiv
  2112.05249); P2 T1 never fails; P3 no complement fails T2; P4 incomplete cases reported as incomplete.
- **0.2.0** (`closure.py`): P5 C and Python agree; P6 closures for N ≤ 168 match Jedrzejewski's Table 1;
  P7 no T1/T2 failure; P8 every complete closure is complete bipartite (an open guess); P9 complement
  counts match the published SAT counts.
- **0.3.0** (`closure.py --only open1800`): P10 no T2 failure in the explored 1800 blocks; P11 most blocks
  incomplete; P12 all 24 standard seeds are Vuza canons.
- **0.5.0 / 0.5.1**: L1–L5 (liftsat) and F1–F4 (fold6sat). F3 predicted "no verified failure at 5400"; it
  is now a theorem.

The "wow" outcome would be a tile that fails T2: a counterexample to a 27-year-old conjecture. For the lifts
of the smallest unsupported tiles, the answer is now no at every period whose prime factors are 2, 3 and 5.

## Run

```
pip install -r requirements.txt        # numpy is optional (speed only)
pip install -r requirements-sat.txt    # OR-Tools, only for profsat.py, liftsat.py and fold6sat.py
python -m unittest -v test_vuza test_closure test_t2open test_profsat test_liftsat test_foldlemma test_fold6sat test_liftroutes test_phi6close
python phi6close.py --out-dir out
python liftroutes.py --out-dir out
python foldlemma.py --out out/fold_lemma_computed.json
python t2open.py --limit 20000 --out out/t2_open_periods.json
python liftsat.py --out-dir out --workers 4 --total-minutes 320
python fold6sat.py --out-dir out --workers 2 --total-minutes 225
```

## Honest limits

- The fold proposition, the route theorem and the Φ₆ theorem are hand proofs with machine-checked finite
  steps. No human expert has refereed them yet.
- They cover only lifts of two source tiles (and their dilates), not every tiling at these periods.
- CP-SAT answers INFEASIBLE without a proof certificate; UNKNOWN means the time limit ran out.
- `t2open.py` is only as complete as the list of results it encodes. It can only err toward calling a
  period open, never toward calling an open one closed.

## References

- E. M. Coven, A. Meyerowitz, *Tiling the integers with translates of one finite set*, J. Algebra 212 (1999).
- T. Y. Lam, K. H. Leung, *On vanishing sums of roots of unity*, J. Algebra 224 (2000).
- I. Łaba, I. Londner, *Combinatorial and harmonic-analytic methods for integer tilings*, arXiv:2106.14042.
- I. Łaba, I. Londner, *The Coven–Meyerowitz tiling conditions for 3 odd prime factors*, Invent. Math. 232 (2023); *… the even case*, Res. Math. Sci. 12 (2025).
- I. Łaba, I. Londner, *Splitting for integer tilings*, arXiv:2407.11374.
- G. Kiss, I. Łaba, C. Marshall, G. Somlai, *Lower bounds for mask polynomials with many cyclotomic divisors*, arXiv:2507.11672.
- G. Kiss, C. Marshall, M. Matolcsi, G. Somlai, *Nonnegative weak tilings and the Coven–Meyerowitz condition (T2)*, arXiv:2611.13593.
- H. Tan, Y. Zhang, *Unsupported cyclotomic divisors in three-prime integer tilings*, arXiv:2609.06677.
- E. Amiot, *New perspectives on rhythmic canons and the spectral conjecture*, J. Math. Music 3 (2009).
- F. Jedrzejewski, *Enumeration of Vuza canons*, arXiv:1304.6609.
- G. Auricchio, L. Ferrarini, S. Gualandi, L. Pernazza, *Computing aperiodic tiling rhythmic canons via SAT models*, Constraints (2024); arXiv:2112.05249.
