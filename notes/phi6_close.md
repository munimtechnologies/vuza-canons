# The last route is closed: lifts of the Tan–Zhang tiles never break T2 at 5-smooth periods

vuza-canons 0.7.0, 2026-11-26. Made by MV2 of Munim, Inc., with AI agents. Text CC BY 4.0, code Apache-2.0.
**Not yet checked by a human expert.** `phi6close.py` re-checks every finite step exactly, and
`test_phi6close.py` asserts that it reproduces `phi6_close.json`.

## Statement

Let X be S180 or C180 (Tan–Zhang, arXiv:2609.06677): 30 points of period 180, S_X = {4, 5, 9}, with Φ₆ as an
unsupported divisor. Let M = 180k, where k has no prime factor other than 2, 3 and 5. Write M = 2^a·3^b·5^e
(a, b ≥ 2, e ≥ 1, and k = 2^{a−2}·3^{b−2}·5^{e−1}). Let A ⊂ ℤ_M be a **lift** of X (A ≡ X mod 180) and
A ⊕ B = ℤ_M.

**Theorem.** Φ₆ divides B(x).

**Corollary.** With the route theorem of 0.6.0 (`notes/lift_routes.md`), **every tiling of ℤ_{180k} by a lift
of S180 or C180 satisfies T2, for every k whose prime factors are 2, 3 and 5.** In particular this settles
5400, which 0.6.0 left open, and every larger 5-smooth period (7200, 8100, 10800, …). By KMMS Prop. 6.3
(arXiv:2611.13593) the same holds for lifts of the dilates 5·S180 and 5·C180 (Tan–Zhang's period-900
examples). With Łaba–Londner Cor. 6.2, which settles every k not divisible by 5, the least period at which a
lift of these tiles is not covered is 180·35 = **6300**.

The 0.5.1 fold proposition needed k′ ≥ 6 for a Φ₆ failure, and only folded mod 30 and mod 5^e. The new
ingredient is to fold also mod 3·2^a and mod 2·3^b, where the route theorem supplies the vanishing that
makes these folds periodic.

## Notation

For a multiset Y of integers and m ≥ 1, Y_m(x) is the number of y ∈ Y with y ≡ x (mod m). The Fourier
coefficient of Y_m at a frequency of order d | m vanishes iff Φ_d | Y(x).

**Periodicity lemma.** Let P | m. If the Fourier coefficient of f: ℤ_m → ℂ vanishes at every frequency ξ
with m ∤ Pξ, then f(x + P) = f(x). (The coefficient of f(· + P) − f is f̂(ξ)(e^{2πiPξ/m} − 1).) If f = Y_m
is P-periodic, then Y_P(x) = (m/P)·Y_m(x), so **m/P divides every value of Y_P.**

## Step 1: the mod-30 fold (0.5.1)

Folding the tiling gives A₃₀ ∗ B₃₀ = M/30 on ℤ₃₀. Since Φ₂, Φ₃, Φ₁₀, Φ₁₅, Φ₃₀ ∤ X and Φ₅, Φ₆ | X (these depend
only on X mod 30), the 0.5.1 proposition (`notes/fold_lemma.md`, steps 1–3) gives

  B₃₀(x) = w(x mod 5) + v(x mod 6),  v = (p, p+r, r, −p, −p−r, −r),

with w and v integer valued, Σ w = |B|/6 = k, and **Φ₆ | B iff v = 0**. Summing over the five x with a given
residue y mod 6 (they cover every residue mod 5):

  B₆(y) = k + 5·v(y).

By step 6 of 0.5.1 (Φ_{5^l} | B for 2 ≤ l ≤ e), 5^{e−1} | w(a) for every a.

## Step 2: which Φ_N divide B

Because A ⊕ B = ℤ_M, every Φ_N with 1 < N | M divides A or B. T1 bookkeeping (|A| = 30 = Φ₄(1)Φ₉(1)Φ₅(1))
puts every prime power other than 4, 9 and 5 in S_B. The route theorem of 0.6.0 shows that **no lift**
has Φ_N | A for N = 3·2^j (j ≥ 3), N = 2·3^j (j ≥ 3), or N = m·5^l (m ∈ {2, 3, 6}, l ≥ 2). So all of these divide B.
We only use these three families. Their proofs are short. With g = gcd(180, N), a lift may put each point
x at any y ≡ x (mod g):

- **N = 3·2^j.** Split by 2 twice (R1). The class 3 mod 4 of S180 is {3, 63, 123} (for C180 the class 1 mod 4
  is {21, 141, 165}). All of these points are ≡ 3 (resp. 9) mod 12, so they share one residue mod 3. Shift it out (R2). This leaves three free
  points of ℤ_{2^{j−2}}, and 3 ∉ ℕ·2 (Lam–Leung).
- **N = 2·3^j.** Split by 3 (R1). The class 1 mod 3 of both tiles is {4, 34, 64, 94, 124, 154}, which is ≡ 4, 16,
  10, 4, 16, 10 mod 18. After rescaling, all points are odd, so shift out 2 (R2). They then lie two in each class mod 3, so split by 3 (R1).
  This leaves classes of two free points of ℤ_{3^{j−2}}, and 2 ∉ ℕ·3.
- **N = m·5^l.** Split by 5 (R1). The class 4 mod 5 of both tiles is 4 + 30·{0, …, 5}, all ≡ 4 mod 30. After
  rescaling, shift out 2 and 3 where they divide m (R2). This leaves six free points of ℤ_{5^{l−1}}, and 6 ∉ ℕ·5.

## Step 3: three periodic folds

- **2-adic.** On ℤ_{3·2^a}, the frequencies with m ∤ 12ξ are those of order 2^j or 3·2^j with 3 ≤ j ≤ a. All of
  these Φ divide B (step 2), so B_{3·2^a} is 12-periodic and **2^{a−2} | B₁₂(y)**, hence 2^{a−2} | B₆(y).
- **3-adic.** On ℤ_{2·3^b}, the frequencies with m ∤ 18ξ have order 3^j or 2·3^j with 3 ≤ j ≤ b. So B_{2·3^b} is
  18-periodic and **3^{b−2} | B₁₈(y)**, hence 3^{b−2} | B₆(y).
- **5-adic.** On ℤ_{6·5^e}, the frequencies with m ∤ 30ξ have order m·5^l with m | 6 and 2 ≤ l ≤ e. So B_{6·5^e} is
  30-periodic and **5^{e−1} | B₃₀(x)** for every x.

## Step 4: counting

From B₆(y) = k + 5v(y), with 2^{a−2} | k and 5 invertible mod 2, we get 2^{a−2} | v(y). In the same way
3^{b−2} | v(y). From 5^{e−1} | B₃₀(x) = w(a) + v(y) and 5^{e−1} | w(a) we get 5^{e−1} | v(y). Hence

  **k | v(y) for every y.**

Suppose v ≠ 0. By antisymmetry (v(y+3) = −v(y)), min v ≤ −k. Every pair (a, y) occurs as (x mod 5, x mod 6),
so B₃₀ ≥ 0 gives w(a) ≥ k for all five residues a, and Σ w ≥ 5k > k = Σ w. This is a contradiction. So v = 0 and
Φ₆ | B. ∎

## Where the argument stops

- It uses that 2, 3 and 5 are the only primes of M. If k = k_s·m with gcd(m, 30) = 1 and m > 1, the same
  steps give k_s | v. This is a contradiction only when 5k_s > k_s·m, that is m < 5, which is impossible.
  New primes also open new T2 routes (for example Φ_{6p} can divide a lift). The first such period that
  Łaba–Londner do not cover is k = 35, M = 6300.
- It is about lifts of two tiles, not about every tiling at these periods. Other tiles with unsupported
  divisors (Tan–Zhang's p²q²r³ family, the KMMS four-prime construction) are untouched.
- The integrality is essential. KMMS build *weak* (rational) complements of these tiles that fail T2. Our
  argument breaks for them at step 4, because v need not be integral and k | v means nothing there.

## What the code checks (`phi6_close.json`)

For all 26 values of k ≤ 60 with prime factors 2, 3 and 5, and for both tiles:

- every order that step 3 needs is either a prime power in S_B or is excluded for every lift by the sound
  R0–R2 engine (copied from `liftroutes.py`);
- each periodicity statement holds exactly on ℤ_m;
- no mod-30 profile with v ≠ 0 survives the new divisibility. Before it, the 0.5.1 fold allowed 450 such
  profiles at 5400 (and 30 at 1080). After it, none survive at any k;
- the tile facts are checked by exact division by cyclotomic polynomials, and the necessary conditions hold
  on genuine tilings by random lifts.

This replaces the solver searches at 5400 (`fold6sat.py`, job vuza-fold6-v1). Every case they ask about now
has a proven answer, so they can only measure the solver.
