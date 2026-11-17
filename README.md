# vuza-canons

Exhaustive enumeration of rhythmic tiling canons (Vuza canons) and a systematic test of the
**Coven–Meyerowitz T2 conjecture** on every complement found. Also renders canons as audio.

Made by MV2 of Munim, Inc., with AI agents. Licensed under Apache-2.0. Version 0.1.0.

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

**Whether T2 is always necessary is open.** It is tied to Fuglede's spectral-set conjecture in cyclic
groups. Łaba and Londner proved T2 for every tiling of period p²q²r² (Invent. Math. 2023, and the even
case). Amiot showed that any counterexample can be collapsed to a **Vuza canon** that fails T2. So Vuza
canons are where a counterexample would have to show up.

## What this does

- Builds the standard Vuza rhythms (Jedrzejewski 2013, Theorems 12/14, after Vuza, Hajós and de Bruijn).
- Enumerates **every** complement R of the outer rhythm S by exact-cover search, keeping one
  representative per translation class. It counts aperiodic and periodic classes, and classes up to
  reflection.
- Checks T1 and T2 on every class. The cyclotomic-zero test is exact: X(ζ_d) = 0 if and only if every
  Galois conjugate X(ζ_d^j) has absolute value below 1/2, because a nonzero algebraic integer has a norm of
  at least 1. Any T2 failure is re-checked with exact integer polynomial division before it is reported.
- Writes a WAV file of a canon, one pitch per voice, so the interlocking can be heard.

## Pre-registered plan (2026-11-17, before any run)

Cases are listed in `run_cases.py`, in this order:
1. **Validation.** Ten periods (72 to 180) whose aperiodic-complement counts were published by Auricchio,
   Ferrarini, Gualandi and Pernazza (arXiv 2112.05249). **Prediction:** every case that completes
   matches the published count, up to translation. A mismatch means either that our reading of their
   count convention is wrong or that there is a bug, and it is reported as such.
2. **N = 420 = 2²·3·5·7.** This period has four primes, so it is outside the p²q²r² theorem. The six cases
   whose complements have three distinct primes in their size are the ones where T2 is not automatic.
3. **New periods with no published complete enumeration that we could find:** 360, 504, 540, 630, 660,
   924, then 600 and 840.

Predictions:
- **P1:** every completed validation case matches the published count.
- **P2:** T1 never fails. This is a theorem, so a failure means a bug.
- **P3:** no complement fails T2. A confirmed failure would be a counterexample to the necessity of T2.
  It would first be re-verified independently, and would be reported to the specialists before any public
  claim.
- **P4:** cases that hit the 12-minute budget are reported as incomplete, never as complete.

## Run

```
pip install -r requirements.txt   # numpy is optional (speed only)
python -m unittest -v test_vuza
python run_cases.py --out-dir out --case-minutes 12
```

Outputs: `out/summary.json`, `out/results.json` (counts, cyclotomic profiles, examples, any T2
failures) and `out/canon_<N>_*.wav`.

## Honest limits

- Only complements of the *standard* outer rhythm are enumerated, not every Vuza canon of a period.
- A clean result (no T2 failure) is evidence, not a proof.
- Search time grows quickly with N. Cases that hit the time budget are marked `"complete": false`.

## References

- E. M. Coven, A. Meyerowitz, *Tiling the integers with translates of one finite set*, J. Algebra 212 (1999).
- I. Łaba, I. Londner, *The Coven–Meyerowitz tiling conditions for 3 odd prime factors*, Invent. Math. 232 (2023); and *… the even case*.
- E. Amiot, *New perspectives on rhythmic canons and the spectral conjecture*, J. Math. Music 3 (2009).
- F. Jedrzejewski, *On the enumeration of Vuza canons*, arXiv:1304.6609.
- G. Auricchio, L. Ferrarini, S. Gualandi, L. Pernazza, *Computing aperiodic tiling rhythmic canons via SAT models*, Constraints (2024); arXiv:2112.05249.
