# Public Python interface

All names below can be imported directly from `ordinatics`. Source docstrings specify exact parameter and error behavior.

## Ordinals

- `Ordinal(coefficients=())`: canonical immutable coefficients in ascending exponent order, with nonnegative exact integer entries.
- `Ordinal.from_int(n)`: finite ordinal.
- `Ordinal.omega_power(n)`: omega raised to a finite nonnegative integer.
- `ZERO`, `ONE`, `OMEGA`: canonical constants.
- `a + b`, `a * b`, `a ** n`: ordinary ordinal arithmetic. Exact finite integers can be operands.
- `a.natural_add(b)`, `a.natural_mul(b)`: commutative polynomial operations.
- `a.is_finite`, `a.to_int()`: inspect or extract finite ordinals; infinite extraction raises `ValueError`.
- `a.to_sympy(symbol=None)`, `Ordinal.from_sympy(expr, symbol=None)`: exact polynomial representation. The symbol must be a commutative SymPy symbol; the default is `X`.
- Ordinals support comparison, hashing, and readable string output. Finite ordinals compare equal to corresponding exact integers and share their hashes.

## Value algebra

- `X`: a commutative SymPy symbol.
- `rational_function(expr, *, symbol=X)`: validate and cancel an exact rational function over the rationals.
- `specialize(expr, *, symbol=X, at=...)`: evaluate at an exact rational point.
- `wrap(expr, *, symbol=X)`: specialize at minus one-half.
- `PoleError`: a reduced denominator vanishes at the evaluation point.
- `rational_power_image(r)`: the exact expression `exp(r*(-log(2) + I*pi))` for rational `r`.
- `complex_period()`: exact `2*pi*I/(-log(2) + I*pi)`.

Pass an ordinal through `.to_sympy()` explicitly to enter this algebra. Foreign symbols, floating-point coefficients, strings, matrices, and expressions outside the declared domain are rejected.

## Bounded semantics

- `Term`, `Formula`: base types for the supported syntax nodes.
- `Nat`, `Var`, `Add`, `Mul`: natural-number terms.
- `Eq`, `Lt`, `Not`, `And`, `Exists`, `ForAll`, `Truth`: formula constructors.
- `rank(formula, *, max_steps=10000)`: validate a formula and obtain its language rank.
- `free_variables(formula, *, max_steps=10000)`: validate and obtain its free variable names.
- `evaluate(formula, assignment=None, *, stage=None, max_steps=10000)`: bounded satisfaction, returning a Boolean only on successful evaluation.
- `OrdinaticsSemanticsError`, `MalformedSyntaxError`, `LanguageMembershipError`, `FreeVariableError`, `EvaluationLimitError`: explicit failure categories.

See [semantics](semantics.md) for binding, quotation, and budget rules.
