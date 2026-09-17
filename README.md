# Ordinatics

**Exact ordinal arithmetic, symbolic value operations, and bounded typed satisfaction for Python.**

Companion to **[Ordinal Arithmetic: An Ordinal-First Metalanguage Approach to Definable Arithmetic Truth](https://github.com/TimeLordRaps/ordinatics/blob/main/paper/ordinal_arithmetic.pdf)** by Tyler Roost. The editable [LaTeX source](https://github.com/TimeLordRaps/ordinatics/blob/main/paper/ordinal_arithmetic.tex) and [reading copy](https://github.com/TimeLordRaps/ordinatics/blob/main/paper/ordinal_arithmetic.md) are included.

Ordinatics implements the computable parts of the paper using exact integers and SymPy expressions. Ordinary ordinal operations and commutative polynomial operations have separate methods. The semantic evaluator handles explicit bounded quantifiers; it does not decide arbitrary arithmetic truth or construct the paper's full infinite truth sets.

## Install

Python 3.10 or newer is required. Install directly from GitHub:

```console
python -m pip install "ordinatics[scientific] @ git+https://github.com/TimeLordRaps/ordinatics.git"
```

Or from a checkout of this repository:

```console
python -m pip install .
python -m pip install '.[scientific]'
```

The distribution name is `ordinatics`. See [release instructions](https://github.com/TimeLordRaps/ordinatics/blob/main/docs/releasing.md) for package-index publication status and reproducible build commands.

## Ordinary and natural ordinal arithmetic

```python
from ordinatics import OMEGA, Ordinal

assert 1 + OMEGA == OMEGA
assert OMEGA + 1 > OMEGA
assert 2 * OMEGA == OMEGA
assert OMEGA * 2 == OMEGA + OMEGA

# Natural operations are commutative polynomial operations.
assert OMEGA.natural_add(1) == OMEGA + 1
assert OMEGA.natural_mul(2) == OMEGA * 2

# Coefficients are exact, ordered from the constant term upwards.
alpha = Ordinal((3, 2, 1))  # omega**2 + omega*2 + 3
assert alpha == OMEGA**2 + OMEGA*2 + 3
```

The supported domain is all ordinals strictly below `omega**omega`, represented by finite polynomial coefficient tuples. No floating-point representation of infinity is used. Raising an ordinal to a finite nonnegative integer power stays inside this domain.

## SymPy, exact wrap, and numerical libraries

```python
import sympy as sp
from ordinatics import OMEGA, X, Ordinal, PoleError, wrap

p = (OMEGA**2 + OMEGA*2 + 3).to_sympy()
assert p == X**2 + 2*X + 3
assert Ordinal.from_sympy(p) == OMEGA**2 + OMEGA*2 + 3
assert wrap(p) == sp.Rational(9, 4)
assert wrap(1 / X) == -2

# A cancelled removable singularity is allowed; an actual pole is not.
assert wrap((X**2 - sp.Rational(1, 4)) / (X + sp.Rational(1, 2))) == -1
try:
    wrap(1 / (2*X + 1))
except PoleError:
    pass
else:
    raise AssertionError("an actual pole must be rejected")
```

Wrap specializes a rational function at `X = -1/2` after exact cancellation. It returns an exact rational or raises `PoleError`. This is a polynomial/value operation, not a homomorphism of ordinary ordinal addition. Strings, floats, and expressions outside the declared rational-function domain are rejected.

The result of `to_sympy()` is an ordinary SymPy expression. Use SymPy differentiation, integration, matrices, solvers, and `lambdify` directly. For NumPy arrays and SciPy algorithms, choose an explicit numerical evaluation point:

```python
import numpy as np
from scipy.integrate import quad

f = sp.lambdify(X, p, modules="numpy")
values = f(np.array([0.0, 1.0, 2.0]))
integral, error_estimate = quad(f, 0.0, 1.0)
assert np.allclose(values, [3.0, 6.0, 11.0])
assert abs(integral - 13/3) < 1e-10
```

These are numerical computations on a polynomial image, not numerical ordinal arithmetic. SymPy also supports `lambdify(..., modules="mpmath")` for arbitrary-precision numerical work. See [interoperability](https://github.com/TimeLordRaps/ordinatics/blob/main/docs/interoperability.md).

## Ordinal calculus and dynamics

Ordinal difference operators, normal functions, fixed-point derivative enumerators, the Veblen hierarchy, and ordinal dynamical systems provide computable calculus on ordinals below `omega**omega`:

```python
from ordinatics import (
    OMEGA, ONE, ZERO, Ordinal,
    Delta, delta, NormalFunction, derivative, least_fixed_point,
    veblen, VeblenHierarchy, VeblenTerm,
    OrdinalDynamicalSystem, orbit, find_attractor, find_fixed_point,
)

# Ordinal left subtraction: beta - alpha is unique gamma such that alpha + gamma == beta
assert OMEGA - 1 == OMEGA
assert (OMEGA + 3) - OMEGA == 3

# Difference operator: Delta F(alpha) = F(alpha + 1) - F(alpha)
f_double = lambda a: 2 * a
assert delta(f_double, 0) == 2
assert delta(f_double, OMEGA) == 2

# Normal ordinal functions and derivatives (fixed point enumerators)
f = NormalFunction.add_left(1)  # F(alpha) = 1 + alpha
assert f.is_normal()
df = f.derivative()             # F'(alpha) enumerates fixed points of F
assert df(0) == OMEGA           # Least fixed point is omega
assert df(1) == OMEGA + 1
assert f(df(0)) == df(0)

# Least fixed point search via transfinite stage ascent
assert least_fixed_point(lambda a: OMEGA + a, start=0) == OMEGA**2

# Veblen hierarchy: phi_0(beta) = omega**beta
assert veblen(0, 2) == OMEGA**2

# Transfinite levels (epsilon_0, zeta_0) via symbolic Veblen terms
e0 = veblen(1, 0, symbolic=True)
z0 = veblen(2, 0, symbolic=True)
assert str(e0) == "ε_0"
assert e0 < z0 and e0 > OMEGA**100

# Ordinal dynamical systems: orbits and attractors
sys = OrdinalDynamicalSystem(lambda x: 1 + x)
orb = sys.orbit(initial_state=0, max_stage=OMEGA + 2)
assert orb.stages[OMEGA] == OMEGA
attractor = sys.find_attractor(0)
assert attractor.is_fixed_point and attractor.states == (OMEGA,)
```

## Typed, bounded satisfaction

```python
from ordinatics import Add, Eq, Nat, Truth, ZERO, ONE, evaluate, rank

sentence = Eq(Add(Nat(1), Nat(1)), Nat(2))
assert evaluate(sentence)
quoted = Truth(ZERO, sentence)
assert rank(quoted) == ONE
assert evaluate(quoted, stage=ONE)
```

Truth-level labels are exact ordinals. A quotation at level `beta` must contain a closed formula of rank at most `beta`; its use requires a language stage of at least `beta + 1`. Invalid syntax, open quotations, insufficient stages, and exhausted evaluation budgets raise distinct exceptions. Unsupported or unevaluated claims are never silently returned as `False`.

See [semantics](https://github.com/TimeLordRaps/ordinatics/blob/main/docs/semantics.md) for the exclusive bounds on quantifiers, the step budget, and the distinction between this executable fragment and the paper's mathematical construction.

## Development

```console
python -m pip install '.[dev,scientific]'
python -m pytest -vv -s --durations=10 --timeout=60
python -m ruff check src tests examples scripts
python -m build
python -m twine check dist/*
```

The version 0.1 interface is experimental. See [API reference](https://github.com/TimeLordRaps/ordinatics/blob/main/docs/api.md), [mathematical scope](https://github.com/TimeLordRaps/ordinatics/blob/main/docs/mathematical_scope.md), and [change history](https://github.com/TimeLordRaps/ordinatics/blob/main/CHANGELOG.md). The repository uses the Apache 2.0 license.
