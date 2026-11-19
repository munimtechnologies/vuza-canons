# The fold proposition: when can Φ₆ witness a T2 failure?

vuza-canons 0.5.1, 2026-11-19. Made by MV2 of Munim, Inc., with AI agents. Text CC BY 4.0, code Apache-2.0.
**Not yet checked by a human expert.** The computational steps are checked exactly by `foldlemma.py`
(`python -m unittest test_foldlemma`), and the committed numbers are in `fold_lemma.json`.

## Setting

A tiling A ⊕ B = ℤ_M fails the Coven–Meyerowitz condition T2 on the B side when, for some product N of
prime powers in S_B (powers of distinct primes, at least two of them), Φ_N does not divide B(x). Tiling then
forces Φ_N | A(x) with no prime power of N in S_A: an *unsupported divisor* of A (Kiss–Łaba–Marshall–Somlai).
Tan and Zhang (arXiv:2609.06677) found the smallest tiles with an unsupported divisor: two sets of size 30 and
period 180, S180 and C180, with S_A = {4, 5, 9} and Φ₆ unsupported. Kiss, Marshall, Matolcsi and Somlai
(arXiv:2611.13593) proved that such tiles have *weak* (nonnegative rational) complements failing T2. Their
Prop. 6.2 shows that every normalized nonnegative T1 weak complement of S180 *itself* satisfies T2. Their paper
constructs no *set* complement that fails T2.

The natural place to look for a set counterexample is therefore among **lifts**: sets A ⊂ ℤ_{180k} with
A ≡ X (mod 180) for X = S180 or C180, at periods where no theorem settles T2 (1800, 2700, 3600, …). KMMS
Prop. 6.2 does not apply to lifts: a complement B of a lift folds mod 180 to a weak complement of X whose
value at 0 is |B ∩ 180ℤ|/k, which is not 1 in general. Our 0.5.0 prediction L5 ("lifts of S180 never miss Φ₆")
had leaned on Prop. 6.2. The proposition below proves L5 at every period that the search covers, and
it also covers C180.

## Proposition

Let A ⊕ B = ℤ_M with |A| = 30, such that Φ₅ and Φ₆ divide A(x), while Φ₂, Φ₃, Φ₁₀, Φ₁₅ and Φ₃₀ do not.
Then 180 | M. Write M/180 = 5^s·k′ with 5 ∤ k′. **If Φ₆ ∤ B(x), then k′ ≥ 6.**

These hypotheses depend only on A mod 30, so they hold for **every lift of S180 and of C180** to every period
(checked exactly in `foldlemma.py`).

**Corollary.** For lifts of S180 or C180 to M = 180k, no set complement misses Φ₆ when k ∈ {1, …, 5, 10, 15,
20, 25}. In particular, at the three open lift periods 1800, 2700 and 3600, a T2 failure would have to be
witnessed by an order that involves 8, 16, 25 or 27 (at 1800: N ∈ {24, 50, 150, 200, 600}). For 5 ∤ k the
case is already closed by Łaba–Londner Cor. 6.2 (only the primes 2 and 3 divide both |A| and |B| = 6k). So
**5400 = 2³·3³·5² is the least period at which a lift of these tiles could have a set complement that misses
Φ₆.**

## Proof

Write X_m for the residue-count function of a set X modulo m, and use Fourier analysis on ℤ_m. The
coefficient of X_m at a frequency of order d | m vanishes if and only if Φ_d | X(x).

**0. Profiles.** Every tile satisfies T1 (Coven–Meyerowitz), and for prime powers s | M exactly one of A, B is
divisible by Φ_s. Since |A| = 30 = ∏_{s∈S_A} Φ_s(1), Φ₂ and Φ₃ do not divide A, and Φ₅ does, S_A holds one
power 2^i with i ≥ 2, one power 3^j with j ≥ 2, and the power 5 itself. Hence 4·9·5 = 180 divides M. With
5^e ∥ M (e ≥ 1), every Φ_{5^j} for 2 ≤ j ≤ e divides B, and Φ₅ does not divide B.

**1. Fold mod 30.** Folding A ⊕ B = ℤ_M gives A₃₀ ∗ B₃₀ = M/30 (constant) on ℤ₃₀. So for every frequency ξ ≠ 0,
Â₃₀(ξ)·B̂₃₀(ξ) = 0. By hypothesis Â₃₀ is nonzero at every frequency of order 2, 3, 10, 15 or 30. Hence B̂₃₀ is
supported on frequencies of order 1, 5 and 6.

**2. Shape.** By the Chinese remainder theorem ℤ₃₀ ≅ ℤ₅ × ℤ₆. Order-5 frequencies give functions of x mod 5 and
order-6 frequencies give functions of x mod 6, so
  B₃₀(x) = w(x mod 5) + v(x mod 6),
where v has only order-6 frequencies on ℤ₆: v(y+3) = −v(y) and v(y) + v(y+2) + v(y+4) = 0. Writing
v = (p, p+r, r, −p, −p−r, −r) covers all such v. (`foldlemma.py` checks over ℚ that the kernel of g ↦ A₃₀ ∗ g has
dimension exactly 6 for both tiles, spanned by the four mean-zero functions of x mod 5 and the two waves.)

**3. Integrality.** B₃₀ takes integer values. Differences v(y) − v(y′) = B₃₀(x) − B₃₀(x′) (same x mod 5) are
integers, so v = c + (integers). Then 2c ∈ ℤ from v(0) + v(3) = 0 and 3c ∈ ℤ from v(0) + v(2) + v(4) = 0, so c ∈ ℤ.
Hence v and w are integer valued.

**4. Φ₆ fails ⇒ w ≥ 1.** Φ₆ ∤ B means v ≠ 0. By antisymmetry, min v ≤ −1. Since (x mod 5, x mod 6) takes every
pair, B₃₀ ≥ 0 gives w(a) ≥ −min v ≥ 1 for every a.

**5. Φ₅ ∤ B ⇒ w not constant.** B₅(a) = Σ_{y∈ℤ₆} (w(a) + v(y)) = 6w(a). Φ₅ ∤ B means B₅ is not constant.

**6. The 5-adic step.** All Φ_{5^j} with 2 ≤ j ≤ e divide B, so B_{5^e} has Fourier support only at orders 1 and 5.
Then B_{5^e} is 5-periodic, and B₅(a) = 5^{e−1}·B_{5^e}(a). So 5^{e−1} | 6w(a), that is, 5^{e−1} | w(a).

**7. Counting.** Σ_a w(a) = |B|/6 = M/180 = 5^{e−1}·k′, because v_5(M/180) = e − 1. Every w(a) is a positive multiple of
5^{e−1}, and they are not all equal, so Σ w ≥ 4·5^{e−1} + 2·5^{e−1} = 6·5^{e−1}. Hence k′ ≥ 6. ∎

## What the proof does not say

- It says nothing about the other candidate orders (24, 50, 150, 200, 600 at M = 1800). Folding mod 150 does
  *not* rule out a Φ₁₅₀ failure in the same way (we found nonnegative integer profiles of the right shape by hand),
  so those cases are left to the solver (`liftsat.py`, job vuza-liftsat-v1).
- At k′ ≥ 6 the folds allow a Φ₆ failure, but that does not mean one exists. At k = 6, …, 9 one cannot exist
  (Łaba–Londner). Those periods are useful *hard negatives* for the solver (`fold6sat.py`).
- Step 6 is what does the work at 1800. The fold mod 30 alone would allow 750 profiles there
  (`k10_profiles_without_5adic_step` in `fold_lemma.json`).

## Numbers (from `fold_lemma.json`)

| k | M | e | k′ | fold allows Φ₆ failure | admissible mod-30 profiles |
|---|---|---|---|---|---|
| 1–4 | 180–720 | 1 | 1–4 | no | 0 |
| 5 | 900 | 2 | 1 | no | 0 |
| 6 | 1080 | 1 | 6 | yes (but Łaba–Londner forbids) | 30 |
| 10 | 1800 | 2 | 2 | no | 0 |
| 15 | 2700 | 2 | 3 | no | 0 |
| 20 | 3600 | 2 | 4 | no | 0 |
| 25 | 4500 | 3 | 1 | no | 0 |
| 30 | 5400 | 2 | 6 | yes, open | 450 |

Each of the 30 and 450 profiles is checked to be a genuine nonnegative integer weak complement of both tiles'
mod-30 folds (A₃₀ ∗ f = 6k), with Φ₅ ∤ f and Φ₆ ∤ f.
