# Ordinatics

**Exact ordinal arithmetic, symbolic value operations, and bounded typed satisfaction for Python.**

Companion to **[Ordinal Arithmetic: An Ordinal-First Metalanguage Approach to Definable Arithmetic Truth](https://github.com/TimeLordRaps/ordinatics/blob/main/paper/ordinal_arithmetic.pdf)** by Tyler Roost. The editable [LaTeX source](https://github.com/TimeLordRaps/ordinatics/blob/main/paper/ordinal_arithmetic.tex) and [reading copy](https://github.com/TimeLordRaps/ordinatics/blob/main/paper/ordinal_arithmetic.md) are included.

Ordinatics implements the computable parts of the paper using exact integers and SymPy expressions. Ordinary ordinal operations and commutative polynomial operations have separate methods. The semantic evaluator handles explicit bounded quantifiers; it does not decide arbitrary arithmetic truth or construct the paper's full infinite truth sets.

## Install

Python 3.10 or newer is required. For this development version, provision the
pinned Hypermath dependency from a checkout of this repository before installing
Ordinatics:

```console
python scripts/bootstrap_foundation.py
python -m pip install '.[scientific,verification]'
```

The bootstrap builds `hypermath-foundations` from the exact commit in
`verification/hypermath.json`, then installs its local wheel. It rejects a
different or modified foundation checkout. The package named `hypermath` on the
Python Package Index is an unrelated project. See [grounding](docs/grounding.md)
and [release instructions](docs/releasing.md) for the dependency and publication
requirements.

## Hypermath grounding

Ordinatics requires Hypermath's audit package and exposes `verify_grounding` to
recompute its self-derivation evidence. Verification binds the installed package
to the pinned source and can produce a Verifier Standard (VSTD) evidence record:

```console
python -u scripts/check_grounding.py --require-self-derivation --require-complete
```

The command retains its evidence before failing an unresolved mathematical gate.
The existing arithmetic functions remain usable as their documented computable
fragment. The source-to-library interpretation and recursively grounded
completeness theorem remain `UNKNOWN`; bounded evaluations do not supply those
proofs. Continuous integration (CI) tests software behavior separately and blocks
publication until the stronger grounding requirements are met.

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
python scripts/bootstrap_foundation.py
python -m pip install -e '.[dev,scientific,verification]'
python -m pytest -vv -s --durations=10 --timeout=60
python -m ruff check src tests examples scripts
python -m build
python -m twine check dist/*
```

The version 0.1 interface is experimental. See [API reference](https://github.com/TimeLordRaps/ordinatics/blob/main/docs/api.md), [mathematical scope](https://github.com/TimeLordRaps/ordinatics/blob/main/docs/mathematical_scope.md), and [change history](https://github.com/TimeLordRaps/ordinatics/blob/main/CHANGELOG.md). The repository uses the existing MIT license.
