# Interoperability

Ordinatics uses SymPy's native expressions as its value interface. It does not create a second symbolic engine or pretend that arrays of floating-point values are transfinite ordinals.

## Exact conversions

```python
from fractions import Fraction
import sympy as sp
from ordinatics import OMEGA, X, Ordinal, specialize, wrap

alpha = OMEGA**2 + 2
expr = alpha.to_sympy()
assert Ordinal.from_sympy(expr) == alpha
assert sp.diff(expr, X) == 2*X
assert specialize(expr, at=Fraction(1, 3)) == sp.Rational(19, 9)
assert wrap(expr) == sp.Rational(9, 4)
```

`Ordinal.from_sympy` accepts only polynomials with nonnegative exact integer coefficients. `wrap` and `specialize` operate on the larger rational-function domain over the rationals. Exact rational inputs include `fractions.Fraction` and SymPy rationals; floating inputs are deliberately rejected at that boundary.

You can compose expressions with SymPy's `Poly`, `Matrix`, equation solvers, symbolic calculus, or code generation. A consumer that accepts SymPy expressions can consume these outputs. Compatibility with every downstream library is not claimed; inspect each consumer's conversion rules, particularly assumptions and coercions.

## Numerical work

```python
import numpy as np
import sympy as sp
from scipy.integrate import quad
from ordinatics import OMEGA, X

p = (OMEGA**2 + 1).to_sympy()
f = sp.lambdify(X, p, modules="numpy")
assert np.allclose(f(np.array([0, 1, 2])), [1, 2, 5])
value, estimated_error = quad(f, 0, 1)
assert abs(value - 4/3) < 1e-10
```

For arbitrary precision:

```python
import mpmath as mp
g = sp.lambdify(X, p, modules="mpmath")
with mp.workdps(50):
    value = g(mp.mpf(1) / 3)
```

The choice of a finite numerical argument is explicit. These computations evaluate a polynomial representation; they do not replace omega by an ordinary real number in ordinal arithmetic. Floating-point results and integration error estimates are numerical evidence, not exact algebraic identities.

The executable [scientific example](../examples/scientific_interop.py) exercises the installed interoperability path.
