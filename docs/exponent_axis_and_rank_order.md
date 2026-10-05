# Exponent axis, rank order and Hardy descent

This page records what the repository checks about the exponents of omega**omega,
and, separately, statements made by the project owner that are **not** checked
here. The boundary between the two is the point of the page. Nothing here changes
the exact domain (`Ordinal` is strictly below `omega**omega`), the separation of
ordinary and natural operations, or the meaning of `rational_power_image`.

Executable surfaces behind this page:

- `ordinatics.fundamental`: fundamental sequences and the Hardy hierarchy with an explicit step budget
  (`tests/test_fundamental.py`);
- `rational_power_image` on rational exponents, checked exactly with SymPy
  (`tests/test_exponent_axis.py`, needs the `scientific` extra);
- the rank order of the omegas on a bounded grid of `Ordinal` values
  (`tests/test_rank_order.py`).

## Owner statements, recorded verbatim

These are quoted as recorded in the owner's program notes. They are the owner's
words, not results of this repository. Dates are the dates of the statements.

### USER-STATED, 2026-10-04: ranking the omegas, and the three forms of omega**omega

> Ordinals "have a real component and an imaginary component, both working backwards reach either normals imaginary or normals normal"; imaginary ordinals work backwards to form the reals, ω^ω forms "a third form like a primal backwards down the transfinites into irrational and surreals", with imaginary ω^ω for surreals, real ω^ω for irrationals, and normal ω^ω backwards "might be unsolvable ... harder to prove because of discrete omega^k jumps". Requirement: "prove that omegas naturally rank order in the tower of omega^omega".

(This paragraph is as recorded in the notes: quoted fragments of the owner's words joined by the
notes' own connecting prose.)

### USER-STATED, 2026-10-04: the classification of omega**omega representations, by exponent axis and coefficient axis

Verbatim:

> exponent axis of normal representations of omega^omega is unsolvable due to discontinuities
> exponent axis of real representations of omega^omega is surreal omega
> exponent axis of irrational representations of omega^omega is irrational omega
> exponent axis of imaginary normal representations of omega^omega is normal omega (I think we can prove finite imaginary exponents of omega^omega solvability into a normal pre omega^omega class)
> exponent of imaginary rational is rational omega
> exponent of imaginary irrational is primal omega (infers new math about primes through prime localized ordinals)
> exponent of surreal omega^omega is real omega^omega
> exponent of imaginary surreal omega^omega is surreal omega^omega * imaginary omega^omega think like the complex numbers but with multiplication between the surreal component and the imaginary component so omega^omega is separatable in this regime and may be composable though a dont know if it works bidirectionally like that, we would need to prove a bijection which is difficult because here the imaginary omega^omega is the class of normal, rational, and irrational
>
> coefficient of normal representations of omega^omega is normal finite
> coefficient of real rational representations of omega^omega is rational finite
> coefficient of real irrational representations of omega^omega is irrational finite
> coefficient of imaginary normal representations of omega^omega is imaginary finite
> coefficient of imaginary irrational omega^omega is irrational omega^omega
> coefficient of surreal omega^omega is surreal omega
> coefficient of imaginary surreal omega^omega is the additive equivalent of the multiplicative complex number analog of the exponent of this class ie surreal omega^omega + imaginary omega^omega allowing you to fully separate this class into seperable components which then allow working like I said backwards to find I believe all classes and having the closure unsolvability of the normal omega^omega is the base meta-induction which allows a full proof of the existence of omega and finites from omega^omega class

## What is checked here

| Statement | Status | Where |
|---|---|---|
| Exponents add and values multiply under `rational_power_image` (rational exponents) | Checked exactly (SymPy) on a rational grid | `tests/test_exponent_axis.py` |
| The modulus is `2**(-r)`, strictly decreasing, so the map is injective on the exponent axis | Checked exactly on the grid; the argument is one line | `tests/test_exponent_axis.py` |
| Phase classes: integer `r` on the real axis, half-odd `r` on the imaginary axis, other rationals of finite phase order | Checked exactly on the grid | `tests/test_exponent_axis.py` |
| The image of this exponent map is one-dimensional (a logarithmic spiral: modulus and phase are both functions of `r`) | Checked (exact modulus, numeric phase to 1e-9) | `tests/test_exponent_axis.py` |
| Rank order below `omega**omega`: strict total order, `omega**j < omega**j'` for `j < j'`, banding, cofinality of the omegas | Checked on bounded grids of coefficient tuples; proved in Lean elsewhere (see below) | `tests/test_rank_order.py` |
| Descent into the naturals: fundamental sequences and Hardy descent terminate and produce the closed forms `H_omega(n) = 2n`, `H_(omega*2)(n) = 4n`, `H_(omega**2)(n) = n*2**n`, `H_(omega**3)(2) = 2048` | Checked; `H_(omega**4)(2)` is reported as exceeding the budget `10**7`, not computed | `tests/test_fundamental.py` |
| A rewrite game on pairs (a, b) = `omega*a + b` terminates from every infinite position although its run length is unbounded over the adversary's choices | Checked on bounded grids and random runs; every step strictly lowers the exact `Ordinal` | `tests/test_descent_game.py` |

Grids are evidence for the grid. Irrational exponents are not testable by this
code: that their phase has infinite order follows from an argument (a finite order
`n` would force `n*r` to be an even integer, so `r` rational), not from computation.

### The Lean statement

The rank-order statements (strict total order on the tower below `omega**omega`,
strict monotonicity of the omega powers, banding, cofinality) are proved and
kernel-checked in Lean in the `lean4` directory of the hypermath repository, on its
branch `claude/translator-and-ladder`. Ordinatics contains no Lean and does not link
to that file; the Python property test is an independent re-check on this repository's
own `Ordinal` type, not a transcription of the proof. Zero is the only element below
`omega**0`; every nonzero element lies in exactly one band
`[omega**k, omega**(k+1))`.

## The one stated objection: solvable, not boundable

The owner's statement says the exponent axis of normal omega**omega representations is
"unsolvable due to discontinuities". The backward descent along it is computable and
terminating: the fundamental sequence is `omega**omega[n] = omega**n`, and below it
`omega**k[n] = omega**(k-1)*n`, down to the naturals, and every such descent ends
(transfinite induction below `omega**omega`). What fails is a bound: the length of the
descent is not controlled by any simple function of the data, `H_(omega**3)(2) = 2048`
while `H_(omega**4)(2)` exceeds `10**7` steps. The accurate summary is therefore
**solvable, not boundable**, not "unsolvable". This is why `ordinatics.fundamental`
takes an explicit step budget and raises `HardyBudgetError` rather than returning a
partial value.

## OPEN / HYPOTHETICAL

The following are the owner's statements, or hypotheses made while reading them. They
are not established by anything in this repository.

- **OPEN**: the exponent axis for surreal (Hahn-series) exponents, and any surreal
  component multiplied with an independent imaginary component. The checked image
  here is one-dimensional; an independent second component would need a complex
  exponent `omega**(a+bi)` with `a`, `b` independent, which is outside `rational_power_image`.
- **HYPOTHETICAL**: that the real, imaginary and normal reading of omega**omega
  representations matches the three classes found by phase order (integer, half-odd,
  other rational). The phase partition is checked; the identification with the owner's
  classes is a reading, not a theorem.
- **HYPOTHETICAL**: prime-localized ordinals and the "primal omega" class for imaginary
  irrational exponents.
- **OPEN**: the owner's belief that solvability of finite imaginary exponents of omega**omega into a
  "normal pre omega^omega class" can be proved. Nothing here addresses imaginary exponents beyond
  the rational phase classes above.
- **OPEN**: a bijection between the owner's classes of representations (the statement that
  the classification composes in both directions).
- **OPEN**: towers of towers (`omega**omega**omega`, epsilon-zero and beyond). Nothing here
  goes beyond `omega**omega`.

No claim here is stronger than its row in the table above. The test names are the
falsification conditions: a map without the imaginary branch, or with increasing
modulus, is rejected by the exponent-axis checker; a weakened or non-transitive order
is rejected by the rank-order checker.
