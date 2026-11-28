# Lifts of the Tan–Zhang Apéry tiles: T2 at every period, and the one route that stays open

vuza-canons 0.8.0, 2026-11-28. Made by MV2 of Munim, Inc., with AI agents. Text CC BY 4.0, code Apache-2.0.
**Not yet checked by a human expert.** `aperylifts.py` re-checks every finite step exactly, and
`test_aperylifts.py` asserts that it reproduces `aperylifts.json`.

## Summary

1. **S180 and C180, every period.** Every tiling of ℤ_{180k} by a lift of S180 or C180 satisfies T2, for
   **every** k. 0.7.0 proved this for k with prime factors 2, 3, 5. A known reduction removes every other
   prime. This corrects our own 0.7.0 remark that 6300 was the least unsettled period: it is settled.
2. **The whole standard family.** For primes p < q < r with r ∈ ⟨p, q⟩, Tan and Zhang's standard tile
   X_{p,q,r} has the unsupported divisor Φ_pq. We prove that **Φ_pq divides every complement of every lift,
   and every such tiling satisfies T2**, under three explicit conditions C1–C3 on how the Apéry set falls
   modulo pq. The conditions are exact. When one fails, a lift really carries the matching cyclotomic factor.
3. **p = 2, q = 3: all primes r.** C1 and C2 hold for every prime r ≥ 5, so Φ₆ divides every complement. C3
   holds exactly for r ∈ {5, 7, 11, 13}. For r ≥ 17 the route Φ_{2^α3^β} (α, β ≥ 3) is open. We exhibit a
   lift of X_{2,3,17} that carries Φ₂₁₆ and still tiles. That route is where a set counterexample to T2
   built from these tiles would have to live. The least period at which it is not settled is
   2³·3³·17² = 62424.

## Setting

Tan and Zhang (arXiv:2609.06677, Thm 7.1 with L = r, h = 1): let p < q < r be primes with r ∈ S = ⟨p, q⟩, and
let Ap = Ap(S; r) be the least element of S in each residue class mod r. Put K = pqr and M₀ = p²q²r, and define

  X = {K·j + s : 0 ≤ j < pq, s ∈ Ap} ⊂ ℤ_{M₀},  B₀ = r·{0, …, pq − 1}.

Then Σ_{s∈Ap} x^s = [r]_x·Φ_pq(x) (their Lemma 2.2). Hence X(x) = (x^{M₀} − 1)/(x^K − 1)·Φ_r(x)·Φ_pq(x),
X ⊕ B₀ = ℤ_{M₀}, S_X = {p², q², r}, X satisfies T2, and Φ_pq is unsupported. For d | K, Φ_d | X iff
d ∈ {r, pq}. The case (2, 3, 5) is S180 = {30j + c : c ∈ {0, 2, 3, 4, 6}}.

A **lift** of X to ℤ_M, M = M₀k, is a set A with A ≡ X (mod M₀): each x ∈ X moves to x + M₀t_x. Seen mod a
divisor N of M, each point may sit at any residue y ≡ x (mod g), g = gcd(M₀, N), independently. Every lift
tiles (with B₀ + M₀ℤ_k). The question is whether some complement B breaks T2.

Write N(u, t) = #{s ∈ Ap : s ≡ u (mod p), s ≡ t (mod q)}, a p × q table summing to r.

- **C1:** for some u ∈ ℤ_p, the values N(u, t), t ∈ ℤ_q, are not all congruent mod p.
- **C2:** for some t ∈ ℤ_q, the values N(u, t), u ∈ ℤ_p, are not all congruent mod q.
- **C3:** some N(u, t) is not in ⟨p, q⟩ (as a count; for p = 2, q = 3 this means some N(u, t) = 1).

## Theorem

Let A be a lift of X_{p,q,r} to ℤ_{M₀k} and A ⊕ B = ℤ_{M₀k}.

- (i) If C1 and C2 hold, then Φ_pq | B.
- (ii) If in addition C3 holds, or pq ∤ k, or r ∤ k, then A and B satisfy T2.
- (iii) Each condition is necessary for its route. If C1 fails, then for each j ≥ 3 (with p^j | M) some lift
  has Φ_{q·p^j} | A. If C2 fails, the same holds for Φ_{p·q^j}. If C3 fails, the same holds for Φ_{p^αq^β}
  with α, β ≥ 3.

## Step 0: only {p, q, r}-smooth k matter

Let ℓ be a prime with ℓ | k and ℓ ∉ {p, q, r}. Then ℓ ∤ |A| = pqr. By Tijdeman's dilation theorem, ℓA ⊕ B =
ℤ_M. Since ℓA(x) = A′(x^ℓ) with A′ = A mod M/ℓ, the subgroup reduction (Coven–Meyerowitz Lemma 2.5;
Łaba–Londner arXiv:2106.14042, Thm 6.1 and the proof of Cor. 6.2) gives B = ⋃_ν (ν + ℓB_ν) with A′ ⊕ B_ν =
ℤ_{M/ℓ}. It also shows that A and B satisfy T2 once A′ and every B_ν do. Their proof uses T2 only for these
particular tilings. A′ is again a lift of X, now to ℤ_{M/ℓ}, so induction on the number of such primes
reduces everything to {p, q, r}-smooth k. If r ∤ k, Łaba–Londner Cor. 6.2 applies directly, because only p
and q divide both |A| and |B| = pqk.

From now on M = p^a q^b r^e with a, b ≥ 2, e ≥ 1 and k = p^{a−2}q^{b−2}r^{e−1}. By T1 (|A| = pqr), S_A =
{p², q², r}, and S_B holds every other prime power dividing M. T2 for A involves only orders dividing M₀, so
it is inherited from X. **T2 for B** asks Φ_N | B for N = p^αq^βr^γ with α ∈ {0, 1} ∪ [3, a],
β ∈ {0, 1} ∪ [3, b] and γ ∈ {0} ∪ [2, e], using at least two primes. Since Φ_N | A or Φ_N | B, it suffices
to show that **no lift has Φ_N | A**, except at N = pq, where Φ_pq | A always holds.

## Step 1: the routes, exactly

Tools: (R1) if p² | n, a sum of n-th roots of unity vanishes iff its sub-sum over each class mod p vanishes
(1, ζ_n, …, ζ_n^{p−1} are independent over ℚ(ζ_{n/p})). (R2) points sharing one residue mod p can be shifted
and rescaled. (R0) a vanishing sum of n-th roots has size in ⟨primes of n⟩ (Lam–Leung). (L) since ℚ(ζ_q) and
ℚ(ζ_{p^m}) are linearly disjoint, Σ_t ζ_q^t H_t = 0 with H_t ∈ ℤ[ζ_{p^m}] iff all H_t are equal. Equal H_t
force equal sizes mod p, via ℤ[ζ_{p^m}]/(1 − ζ) ≅ 𝔽_p. Conversely, if m ≥ 1 and the sizes are congruent,
ρ points at 0 per t plus p-cycles make them equal.

Two counts drive everything. For fixed s ∈ Ap, the points Kj + s (j ∈ ℤ_pq) meet each residue z ≡ s (mod pq)
of ℤ_{p²q²} exactly once, since K·j ≡ pq·(rj) and r is invertible mod pq. Hence:
- the class z mod p²q² of X has N(z mod p, z mod q) points;
- the class c mod p² of X has q·N(c mod p, t) points with residue t mod q.

**γ ≥ 2 (always closed, any p < q < r).** Split by r. The class c mod r is {Kj + s_c : j ∈ ℤ_pq}, all ≡ s_c
mod pqr. After removing the common offset and shifting out p and q (or applying a Galois automorphism when
p ∤ N or q ∤ N), the class becomes pq points j + pq·t_j of ℤ_{n′}, n′ = p^{α″}q^{β″}r^{γ−1} with
α″ = max(α − 1, 0) ∈ {0} ∪ [2, ∞), and β″ likewise.
- α″ = β″ = 0: pq free points of ℤ_{r^{γ−1}}, and pq ∉ ℕr.
- α″ ≥ 2, β″ = 0: split by p into classes of q free points, and q ∉ ℕp + ℕr since p ∤ q < r.
- α″ = 0, β″ ≥ 2: classes of p free points, and p ∉ ℕq + ℕr.
- α″, β″ ≥ 2: split by p, then by q, into single points.

**γ = 0, α ≥ 3, β = 1 (C1).** Split by p twice. Class c mod p² keeps n_t = q·N(c mod p, t) points at residue
t mod q, each free mod p^{α−2}. By (L) the class can vanish iff the n_t are congruent mod p. So the route is
closed for every lift iff C1 holds. If C1 fails, then for each α ≥ 3 some lift carries Φ_{q p^α}.

**γ = 0, α = 1, β ≥ 3 (C2).** The same argument with p and q exchanged.

**γ = 0, α, β ≥ 3 (C3).** Split by p twice and by q twice. Class z mod p²q² holds N(z mod p, z mod q) points
free in ℤ_{p^{α−2}q^{β−2}}. It can vanish iff its size lies in ⟨p, q⟩. The route is closed iff C3 holds. This
route exists only when p | k and q | k.

## Step 2: Φ_pq | B (generalising 0.7.0)

Fold mod pqr: A_{pqr} ∗ B_{pqr} is constant, and A_{pqr} = X_{pqr} has nonzero Fourier coefficients at the
orders p, q, pr, qr and pqr. Hence B_{pqr}(x) = c + f(x mod r) + v(x mod pq), where v has only order-pq
frequencies (zero sums along every row and column of ℤ_p × ℤ_q). Differences of B_{pqr} are integers, so
q·v and p·v are integers, so v is integral. Write w = c + f, also integral. Then Σw = |B|/pq = k,
**B_pq(y) = k + r·v(y)**, and Φ_pq | B iff v = 0.

The periodicity lemma (a function on ℤ_m whose Fourier coefficients vanish at every order not dividing P is
P-periodic, so m/P divides each count mod P) gives the following. The vanishing needed is Step 1 (γ ≥ 2, C1,
C2) together with the prime powers in S_B.
- B_{q·p^a} is p²q-periodic, so p^{a−2} | B_pq(y);
- B_{p·q^b} is pq²-periodic, so q^{b−2} | B_pq(y);
- B_{pq·r^e} is pqr-periodic, so r^{e−1} | B_pqr(x), and B_{r^e} is r-periodic, so r^{e−1} | w(a).

So p^{a−2} | r·v(y), q^{b−2} | r·v(y) and r^{e−1} | v(y): **k | v**. If v ≠ 0, then since Σv = 0, some
v(y) ≤ −k. Every pair (a, y) occurs, and B_{pqr} ≥ 0, so w(a) ≥ k for all r residues a. Then Σw ≥ rk > k,
a contradiction. So v = 0. ∎

With Step 1 this proves (i) and (ii). Part (iii) is the "iff" in Step 1.

## The family p = 2, q = 3

⟨2, 3⟩ = ℕ ∖ {1}, so Ap = {0, …, r + 1} ∖ {1, r}. Counting residues mod 6, with m = ⌊(r + 1)/6⌋:

| r mod 6 | res 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 5 | m+1 | m−1 | m | m | m | m−1 |
| 1 | m+1 | m−1 | m+1 | m | m | m |

Row u = 0 (residues 0, 4, 2) is never constant mod 2, so C1 holds. Column t = 0 (residues 0, 3) holds m + 1 and m,
so C2 holds. A count equal to 1 occurs iff m ≤ 2, that is r ∈ {5, 7, 11, 13}. `aperylifts.py` checks the
closed form against the Apéry sets for all 44 primes 5 ≤ r ≤ 199.

So **Φ₆ divides every complement of every lift of every X_{2,3,r}**. T2 holds for all their tilings at every
period when r ≤ 13, and for r ≥ 17 unless 6r | k. For r = 17 the witness in `aperylifts.json` is a lift A to
ℤ₃₆₇₂ with Φ₂₁₆ | A, checked by exact division, and A still tiles. The same residues work in ℤ₆₂₄₂₄, the
least period where Step 0 and Łaba–Londner leave this route open.

## What the code checks

For (p, q, r) ∈ {(2,3,5), (2,3,7), (2,3,11), (2,3,13), (2,3,17), (2,3,19), (2,5,7)}, `aperylifts.py` checks:
- the Apéry identity, the tiling X ⊕ B₀, S_X, the fold divisors and T2 for X, by exact cyclotomic division;
- C1–C3, and, by exhaustive search at the least exponent, that every class can vanish exactly when the
  criterion says so;
- the open-route witness wherever C3 fails.

Random lifts of X_{2,3,7} to ℤ₁₀₅₈₄ = 2³3³7² never carry any closed route. `--scan L` lists C1–C3 for every
admissible triple below L. That scan is queued as job vuza-apery-scan-v1, and its results are not yet in.

## Prior work and what is new

- Tan–Zhang (arXiv:2609.06677) built these tiles. Their Theorem 7.4 classifies all complements of one
  multiscale **periodic** set. It does not treat arbitrary lifts.
- Kiss–Marshall–Matolcsi–Somlai (arXiv:2611.13593), Theorem 1.5 / Prop. 6.2: for the **fixed** tile
  T = S180 at every period, even every nonnegative weak T1 complement satisfies T2. Their proof uses that all
  cyclotomic factors of T have order dividing 180. A lift changes the mask and can gain new factors (Φ₂₁₆
  above), and their statement does not cover lifts. Their Cor. 7.2 treats dilates of {0, 2, 3, 4, 6} under
  positive definiteness.
- Łaba–Londner give the reduction used in Step 0. Our 0.5.1–0.7.0 notes give the (2, 3, 5) case of Steps 1–2.
- New here: Steps 1–2 for the whole standard family, the exact conditions C1–C3, the (2, 3, r) classification,
  the S180/C180 result at every period, and the open route with an explicit witness.

## Limits

These are hand proofs with machine-checked finite steps, not refereed. They cover lifts of the standard tiles
(L = r, h = 1) and C180, not every tile with an unsupported divisor (for example the multiscale or r^m cores,
or the KMMS four-prime construction). An open route is not a counterexample. A counterexample would further
need a complement B with Φ_{2^α3^β} ∤ B.
