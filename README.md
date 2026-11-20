# vuza-canons

Exhaustive enumeration of rhythmic tiling canons (Vuza canons) and a systematic test of the
**Coven–Meyerowitz T2 conjecture**. Also renders canons as audio.

Made by MV2 of Munim, Inc., with AI agents. Licensed under Apache-2.0 (notes and results files: CC BY 4.0). Version 0.6.0.

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

## New in 0.6.0: every route but Φ₆ is closed (`liftroutes.py`, `notes/lift_routes.md`)

A tiling A ⊕ B = Z_M breaks T2 on the B side at an order N only if Φ_N divides A without support (an
*unsupported divisor*). Tan and Zhang's tiles S180 and C180 are the smallest tiles with one (Φ₆), and their
**lifts** A ⊂ Z_{180k} (A ≡ X mod 180) are where our counterexample search looks.

**Theorem.** If every prime factor of k is 2, 3 or 5, then no lift of S180 or C180 has Φ_N | A for any order
N at which T2 for B could fail, except N = 6.

**Corollary** (with the 0.5.1 fold proposition and Łaba–Londner Cor. 6.2). Every tiling of a lift of either
tile satisfies T2 unless 5 | k and k′ ≥ 6 (k = 5^s·k′, 5 ∤ k′), and then the only possible failure is Φ₆ ∤ B.
- At **1800, 2700, 3600 and 4500**, the open periods that our search targets, all lifts of both tiles satisfy
  T2 in every tiling. At 1800 the closed orders are 24, 50, 75, 150, 200 and 600.
- The lift question is now **one question**: at 5400 (then 7200, 8100, 10800, …), does a lift have a set
  complement B with Φ₆ ∤ B? Job vuza-fold6-v1 asks exactly that at 5400.
- By KMMS Prop. 6.3, the same holds for lifts of the period-900 dilates 5·S180 and 5·C180.

The proof combines three exact steps: splitting a vanishing sum by classes mod p when p² | N, shifting out
a common residue, and the Lam–Leung weight theorem. It also uses two small facts about the tiles. For example,
the class 4 mod 5 of both tiles is 4 + 30·{0..5}. `liftroutes.py` re-derives every case mechanically for
all 26 values of k ≤ 60 with those prime factors (the engine only ever answers "excluded" with a proof).
`test_liftroutes.py` checks the engine against brute force on random cases and asserts that the code
reproduces the hand-written `lift_routes.json`. **No human expert has checked the proof yet.**

## 0.5.1: a proof that closes the Φ₆ route below 5400 (`foldlemma.py`, `notes/fold_lemma.md`)

**Proposition.** Let A ⊕ B = Z_M with |A| = 30, Φ₅ and Φ₆ dividing A(x), and Φ₂, Φ₃, Φ₁₀, Φ₁₅, Φ₃₀ not
dividing it. Write M/180 = 5^s·k′ with 5 ∤ k′. If Φ₆ does not divide B(x), then k′ ≥ 6.

The hypotheses only depend on A mod 30, so they hold for **every lift** of S180 and C180. Together with
Łaba–Londner Cor. 6.2, 5400 = 2³·3³·5² is the least period at which a lift of these tiles could have a set
complement missing Φ₆. The proof folds the tiling mod 30, where the complement's counts must have the form
w(x mod 5) + v(x mod 6), and mod 5^e, where Φ₂₅ | B forces 5^{e−1} | w. `foldlemma.py` checks its
computational steps exactly, and `test_foldlemma.py` asserts that it reproduces `fold_lemma.json`.

`fold6sat.py` (job vuza-fold6-v1) puts the solver where the cheap argument is silent:
- **hard negatives** k = 6–9 (M = 1080–1620): the folds allow a Φ₆ failure, but Łaba–Londner forbids
  it. These test whether CP-SAT can find the deeper obstruction on its own;
- **frontier** k = 30 (M = 5400): after 0.6.0, the only place a lift could still break T2 below 7200.

Pre-registered (2026-11-19, before any run): F1 every configuration tiles; F2 no FEASIBLE among the hard
negatives; F3 no verified failure at 5400 (we expect UNKNOWN there); F4 the lemma checks reproduce
`fold_lemma.json` inside the job.

## 0.5.0: hunting where the weak counterexamples live (`liftsat.py`)

- **Tan and Zhang** (arXiv:2609.06677) show that 180 is the least period of an unsupported divisor, and
  900 the least for a three-prime one. Their period-180 tiles have size 30, signature {4, 5, 9} and
  unsupported Φ_6:
  - `S180` = {30j + c : j < 6, c ∈ {0, 2, 3, 4, 6}} (periodic);
  - `C180` = the aperiodic set of their §8.1, with complement {0, 20, 40, 45, 65, 85}.
- **Kiss, Marshall, Matolcsi and Somlai** (arXiv:2611.13593) prove that tiles like these have
  nonnegative rational **weak** complements that fail T2, for example at period 180. But "no such set
  complement is constructed here". Dilation does not change the set question (their Prop. 6.3).

`liftsat.py` lets A run over **every lift** of X to Z_M, M = 180k, and asks CP-SAT for a set B with
A ⊕ B = Z_M in which B (or A) fails T2.

| configs | M | sizes | status |
|---|---|---|---|
| k = 1, 2, 3, 4 | 180–720 | 30 / 6k | theorem (Łaba–Londner Cor. 6.2): controls |
| k = 5 | 900 | 30 / 30 | theorem (Łaba–Londner, p²q²r²): control |
| 5·X lifted ×2, 2·X lifted ×5 | 1800 | 30 / 60 | theorem via dilation: same-size controls |
| k = 10 | 1800 | 30 / 60 | **now a theorem for lifts (0.6.0)**: exact negative controls |
| k = 15 | 2700 | 30 / 90 | **now a theorem for lifts (0.6.0)** |
| k = 20 | 3600 | 30 / 120 | **now a theorem for lifts (0.6.0)** |

Pre-registered predictions L1–L5 (2026-11-18, before any run) are unchanged. After 0.6.0, every T2 case
in liftsat's open configurations is known to be INFEASIBLE, so any FEASIBLE answer there is a bug, and
the job measures solver strength on cases with known answers.

## Where T2 is really open (since 0.3.0)

- **Łaba–Londner, Corollary 6.2** (arXiv:2106.14042; Lemma 6.2 in arXiv:2407.11374): in a tiling
  A ⊕ B = Z_M, T2 can only fail if **at least three primes divide both |A| and |B|**.
- The three-shared-primes case is proven for M = p²q²r² (Łaba–Londner, Invent. Math. 2023; even case,
  Res. Math. Sci. 2025) and for the families of their splitting theorem (arXiv:2407.11374, Thm 1.2).
- `t2open.py` encodes exactly these published results. By our reading, **the smallest period where some
  tiling is not covered is M = 1800 = 2³·3²·5²** (sizes {30, 60}), and below 5000 the open periods are
  1800, 2700, 3528, 3600 and 4500. 0.6.0 settles the lifts of the Tan–Zhang tiles there, **not** every
  tiling at those periods.

## 0.4.0: every tiling at once (`profsat.py`)

`profsat.py` asks the question for all tilings A ⊕ B = Z_1800 with |A| = 30, |B| = 60 at once, as 132
CP-SAT cases (12 T1 profiles × 11 T2 conditions). Pre-registered P13–P16 (2026-11-17).

## Everything in the repo

- `vuza.py`, `tilec.c`, `closure.py`: Vuza canons, every complement by exact cover (Python and C), closures.
- `t2open.py`: the map of where T2 is still open.
- `profsat.py`: the all-tilings profile search (0.4.0).
- `liftsat.py`: the lift search over tiles with unsupported divisors (0.5.0).
- `foldlemma.py`, `notes/fold_lemma.md`, `fold_lemma.json`: the fold proposition (0.5.1).
- `fold6sat.py`: the solver on the hard negatives and on the 5400 frontier (0.5.1).
- `liftroutes.py`, `notes/lift_routes.md`, `lift_routes.json`: every route but Φ₆ closed (0.6.0).
- WAV rendering of a canon, one pitch per voice, so the interlocking can be heard.

## Earlier pre-registered predictions

- **0.1.0** (`run_cases.py`): P1 published complement counts reproduced (Auricchio et al., arXiv
  2112.05249); P2 T1 never fails; P3 no complement fails T2; P4 incomplete cases reported as incomplete.
- **0.2.0** (`closure.py`): P5 C and Python agree; P6 closures for N ≤ 168 match Jedrzejewski's Table 1;
  P7 no T1/T2 failure; P8 every complete closure is complete bipartite (an open guess); P9 complement
  counts match the published SAT counts.
- **0.3.0** (`closure.py --only open1800`): P10 no T2 failure in the explored 1800 blocks; P11 most blocks
  incomplete; P12 all 24 standard seeds are Vuza canons.

The "wow" outcome would be a tile that fails T2: a counterexample to a 27-year-old conjecture. For the lifts
of the smallest unsupported tiles, that question now sits entirely at Φ₆ and period 5400 or above.

## Run

```
pip install -r requirements.txt        # numpy is optional (speed only)
pip install -r requirements-sat.txt    # OR-Tools, only for profsat.py, liftsat.py and fold6sat.py
python -m unittest -v test_vuza test_closure test_t2open test_profsat test_liftsat test_foldlemma test_fold6sat test_liftroutes
python liftroutes.py --out-dir out
python foldlemma.py --out out/fold_lemma_computed.json
python t2open.py --limit 20000 --out out/t2_open_periods.json
python liftsat.py --out-dir out --workers 4 --total-minutes 320
python fold6sat.py --out-dir out --workers 2 --total-minutes 225
```

## Honest limits

- The fold proposition and the route theorem are hand proofs with machine-checked case analysis. No human
  expert has refereed them yet.
- They cover only lifts of two source tiles (and their dilates), not every tiling at 1800–4500.
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
