# Every route but Φ₆ is closed for lifts of the Tan–Zhang tiles

vuza-canons 0.6.0, 2026-11-20. Made by MV2 of Munim, Inc., with AI agents. Text CC BY 4.0, code Apache-2.0.
**Not yet checked by a human expert.** `liftroutes.py` re-derives every case below with three exact rules,
and `test_liftroutes.py` asserts that it reproduces `lift_routes.json`.

## Statement

Let X be S180 or C180 (Tan–Zhang, arXiv:2609.06677), M = 180k, and let A ⊂ ℤ_M be a **lift** of X
(A ≡ X mod 180, one point over each point of X). Suppose A ⊕ B = ℤ_M.

**Theorem.** If every prime factor of k is 2, 3 or 5, then for every order N at which T2 for B could fail,
other than N = 6, no lift A has Φ_N | A. Hence Φ_N | B for all of them.

**Corollary.** Write k = 5^s·k′ with 5 ∤ k′. Every tiling of a lift of S180 or C180 satisfies T2, except
possibly when 5 | k and k′ ≥ 6, and then only through Φ₆ ∤ B. At the open periods 1800, 2700, 3600 and 4500,
all lifts of both tiles satisfy T2 in every tiling. The least period where a lift could still break T2 is
**5400**, and only through Φ₆.

Proof of the corollary. T2 for A involves 20, 36, 45 and 180, which divide 180, so it is decided by X, and it
holds. For B, the theorem leaves only N = 6. The fold proposition (`notes/fold_lemma.md`) shows that
Φ₆ ∤ B forces k′ ≥ 6. If 5 ∤ k, Łaba–Londner Cor. 6.2 applies, because only 2 and 3 divide both |A| = 30
and |B| = 6k. ∎

By the dilation invariance of KMMS Prop. 6.3, the same holds for lifts of the dilates 5·S180 and 5·C180,
which are Tan–Zhang's period-900 examples. A lift of qX to ℤ_{900k} is q times a lift of X to ℤ_{180k}.

## Which N matter

Every tile satisfies T1. Φ₄, Φ₉ and Φ₅ divide X, so they divide A, and Φ₄(1)Φ₉(1)Φ₅(1) = 30 = |A|. So
S_A = {4, 9, 5}, and S_B is every other prime power dividing M: 2, 3, the powers 2^a with a ≥ 3, the powers
3^b with b ≥ 3, and the powers 5^e with e ≥ 2. T2 for B asks that Φ_N | B for every N = 2^a·3^b·5^e with
a ∈ {0, 1} ∪ [3, ∞), b ∈ {0, 1} ∪ [3, ∞), e ∈ {0} ∪ [2, ∞), using at least two primes. Since A ⊕ B = ℤ_M,
Φ_N ∤ B forces Φ_N | A. So it is enough to show that **Φ_N ∤ A for every lift**. At 1800 this means
N ∈ {24, 50, 75, 150, 200, 600}. Only N = 6 divides 180, and Φ₆ divides X.

## Three exact tools

Write ζ_n for a primitive n-th root of unity. Φ_N | A means Σ_{a∈A} ζ_N^a = 0, which depends on A mod N. A
lift may put each x ∈ X at any residue y ≡ x mod g of ℤ_N, where g = gcd(180, N), independently for each x.

- **(R1) Split.** If p² | n, then 1, ζ_n, …, ζ_n^{p−1} are linearly independent over ℚ(ζ_{n/p}). So a sum of
  n-th roots vanishes iff, for each class i mod p, the sum of ζ_{n/p}^{(y−i)/p} over the points y ≡ i vanishes.
- **(R2) Shift.** If all points are ≡ i mod p (p | n), then Σ ζ_n^y = ζ_n^i·Σ ζ_{n/p}^{(y−i)/p}.
- **(R0) Weight (Lam–Leung 2000).** A vanishing sum of n-th roots of unity has weight in ℕp₁ + … + ℕp_r,
  where p₁, …, p_r are the primes dividing n. A nonempty sum of 1st roots never vanishes.

## Proof of the theorem

Two facts about the tiles do the work:
- **(F1)** The class 4 mod 5 of both tiles is 4 + 30·{0, …, 5} = {4, 34, 64, 94, 124, 154}.
- **(F2)** The odd points ≡ 1 mod 4 of C180 are {21, 141, 165}, and those ≡ 3 mod 4 of S180 are {3, 63, 123}.
  The points ≡ 1 mod 3 of both tiles are again {4, 34, 64, 94, 124, 154}.

**Case 25 | N.** Split by 5 (R1; 5 | g). The class 4 rescales to the points 6j + 36t_j (j = 0..5, t_j free) of
ℤ_{N/5}. Shift out 2 if 2 | N and 3 if 3 | N (R2; every point is ≡ 0). What remains are points j + 6t_j of
ℤ_n with n = 2^{a′}3^{b′}5^{e−1}, where a′ = max(a−1, 0) ∈ {0} ∪ [2, ∞) and b′ likewise. Their residue mod 6
is j, so it is fixed. (If 2 ∤ N or 3 ∤ N, multiplying by the missing factor is a Galois automorphism, and the
same counts apply.)
- a′ = b′ = 0: six points, and 6 ∉ ℕ·5 (R0).
- a′ ≥ 2, b′ = 0: split by 2 into classes of 3. Then 3 ∉ ℕ2 + ℕ5 (R0).
- a′ = 0, b′ ≥ 2: split by 3 into classes of 2. Then 2 ∉ ℕ3 + ℕ5 (R0).
- a′, b′ ≥ 2: split by 2, then by 3 (the three points of each parity are distinct mod 3). Each class has one
  point (R0).

**Case 8 | N, 5 ∤ N.** Split by 2 twice (R1). By (F2), the class 1 mod 4 of C180 rescales to {5, 35, 41} + 45t
in ℤ_{N/4}, and the class 3 mod 4 of S180 to {0, 15, 30} + 45t. All of these points are fixed mod 3 and equal mod 3.
Shift out 3 (R2).
- b = 1: three points remain in ℤ_{2^{a−2}}, and 3 ∉ ℕ2 (R0).
- b ≥ 3: the remaining points are distinct mod 3 (C180: 1, 2, 1, so one class is a single point; S180: 0, 1, 2).
  Split by 3 (9 | N/12) to reach a class of one point (R0).

**Case 2 ∥ N, 27 | N, 5 ∤ N.** Split by 3 (R1). By (F2), the class 1 mod 3 rescales to six points that are all
odd mod 6. Shift out 2 (R2), then split by 3 (9 | 3^{b−1}) into classes of 2, and 2 ∉ ℕ3 (R0).

These cases cover every N except 6. ∎

## What this changes

- The lift search `liftsat.py` (job vuza-liftsat-v1, still queued) asks CP-SAT about these routes at 1800,
  2700 and 3600. Every one of those cases is now a **proven negative**. A FEASIBLE answer there is a bug, and
  the job measures how strong the solver is.
- `notes/fold_lemma.md` had said that a fold mod 150 does not exclude Φ₁₅₀. That remains true of the B side.
  The A side closes it: **no lift has Φ₁₅₀ | A**, because the class 4 mod 5 would reduce to six points of ℤ₅
  whose fifth roots of unity sum to zero, and 6 is not a multiple of 5.
- The whole lift question is now one question: **at M = 5400 (and 7200, 8100, 10800, …), does some lift of
  S180 or C180 have a set complement B with Φ₆ ∤ B?** `fold6sat.py` (job vuza-fold6-v1) asks exactly this at
  5400. A yes would be a counterexample to the Coven–Meyerowitz T2 conjecture.

## Numbers (from `lift_routes.json`)

| M | k | routes N for B | excluded | left |
|---|---|---|---|---|
| 1800 | 10 | 6, 24, 50, 75, 150, 200, 600 | 6 | Φ₆, closed by the fold proposition |
| 2700 | 15 | 6, 50, 54, 75, 150, 675, 1350 | 6 | Φ₆, closed |
| 3600 | 20 | 6, 24, 48, 50, 75, 150, 200, 400, 600, 1200 | 9 | Φ₆, closed |
| 4500 | 25 | 6, 50, 75, 150, 250, 375, 750 | 6 | Φ₆, closed |
| 5400 | 30 | 6, 24, 50, 54, 75, 150, 200, 216, 600, 675, 1350, 5400 | 11 | **Φ₆, open** |

Across all 26 values of k ≤ 60 with prime factors 2, 3 and 5, Φ₆ is the only route left for both tiles. T2 is
forced except at k = 30, 40, 45 and 60.
