# Mathematical scope

| Surface | Implemented meaning | Boundary |
|---|---|---|
| `Ordinal` | Finite nonnegative integer polynomial coefficients representing ordinals below omega to the omega | No arbitrary ordinal exponentiation, epsilon-zero notation system, or proper class of ordinals |
| `+`, `*`, finite `**` | Ordinary ordinal operations | Addition and multiplication generally do not commute |
| `natural_add`, `natural_mul` | Commutative coefficient/polynomial operations | A separate algebra from ordinary ordinal operations |
| `to_sympy` / `from_sympy` | Exact representation map to/from integer polynomials in one symbol | This does not identify ordinary ordinal operations with field operations |
| `wrap` | Partial specialization of rational functions at minus one-half | Pole rejection; no evaluation on all nonzero field inverses |
| `rational_power_image` | A fixed logarithm branch for rational exponents | Not all algebraic numbers, an ordinal homomorphism, or a canonical consequence of the source ground axioms |
| `rank` | Static language rank of a finite formula tree | Does not compute infinite truth sets |
| `evaluate` | Natural-number arithmetic with explicit finite quantifier bounds and typed quotations | Not a decision procedure for arbitrary first-order arithmetic truth |

The paper's hierarchy uses unbounded natural-number quantification in an explicit set-theoretic metatheory. The Python evaluator uses a syntactically bounded fragment with finite work budgets. Passing a software test does not prove the paper's general semantic theorems. No proof-assistant verification, claimed escape from Tarski's theorem, or claim of completeness for the original research framework is included.

All mathematical objects are dimensionless. The library does not attach physical units; compose the converted numerical functions with a units library as appropriate to the application.
