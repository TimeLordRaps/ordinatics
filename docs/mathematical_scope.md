# Mathematical scope

| Surface | Implemented meaning | Boundary |
|---|---|---|
| `Ordinal` | Finite nonnegative integer polynomial coefficients representing ordinals below omega to the omega | No arbitrary ordinal exponentiation, epsilon-zero notation system, or proper class of ordinals |
| `+`, `*`, finite `**` | Ordinary ordinal operations | Addition and multiplication generally do not commute |
| `natural_add`, `natural_mul` | Commutative coefficient/polynomial operations | A separate algebra from ordinary ordinal operations |
| `to_sympy` / `from_sympy` | Exact representation map to/from integer polynomials in one symbol | This does not identify ordinary ordinal operations with field operations |
| `wrap` | Partial specialization of rational functions at minus one-half | Pole rejection; no evaluation on all nonzero field inverses |
| `rational_power_image` | A fixed logarithm branch for rational exponents | Not all algebraic numbers, an ordinal homomorphism, or a canonical consequence of the source ground axioms. Exact tests cover composition, injectivity on rational exponents (modulus `2**(-r)`), phase classes, and a one-dimensional image; surreal, irrational or complex exponents are not covered |
| rank order of `Ordinal` | Strict total order, strictly increasing omega powers, banding and cofinality of the omegas below `omega**omega` | Checked by exhaustive property tests on bounded coefficient grids; the Lean proof lives in the hypermath repository (lean4 directory, branch `claude/translator-and-ladder`) and is not part of this package |
| `hardy_fundamental`, `hardy`, `hardy_descent`, `hardy_omega_omega`, `omega_omega_fundamental` | Fundamental sequences `alpha[n]` (Hardy-indexed: `omega**k[n] = omega**(k-1)*n`) and the Hardy hierarchy `H_alpha(n)` for `alpha` strictly below `omega**omega`, plus the single step `omega**omega[n] = omega**n` | Every descent terminates but its length is unbounded in practice (`H_(omega**4)(2)` exceeds `10**7` steps), so each call takes an explicit step budget and raises `HardyBudgetError` on exhaustion; no partial value is ever returned. `omega**omega` is not an `Ordinal`. Pure standard library |
| `rank` | Static language rank of a finite formula tree | Does not compute infinite truth sets |
| `evaluate` | Natural-number arithmetic with explicit finite quantifier bounds and typed quotations | Not a decision procedure for arbitrary first-order arithmetic truth |

The paper's hierarchy uses unbounded natural-number quantification in an explicit set-theoretic metatheory. The Python evaluator uses a syntactically bounded fragment with finite work budgets. Passing a software test does not prove the paper's general semantic theorems. No proof-assistant verification, claimed escape from Tarski's theorem, or claim of completeness for the original research framework is included.

All mathematical objects are dimensionless. The library does not attach physical units; compose the converted numerical functions with a units library as appropriate to the application.

See [exponent axis, rank order and Hardy descent](exponent_axis_and_rank_order.md) for what is checked about exponents of `omega**omega`, the owner's statements recorded verbatim and marked as such, and the items that remain open or hypothetical.
