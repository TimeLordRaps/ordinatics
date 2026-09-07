"""Run after ``pip install '.[scientific]'``.

Keep ordinal structure exact, then explicitly choose a polynomial and a
floating-point numerical model. The integral is of that real polynomial; it
does not integrate ordinals or imply a physical interpretation.
"""

import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import brentq

from ordinatics import Ordinal
from ordinatics.algebra import X, wrap


def main() -> None:
    # Coefficients are low to high: 1 + omega**2.
    ordinal = Ordinal((1, 0, 1))
    polynomial = ordinal.to_sympy()
    exact_value = wrap(polynomial)
    assert exact_value == sp.Rational(5, 4)

    numerical = sp.lambdify(X, polynomial, modules="numpy")
    grid = np.linspace(0.0, 2.0, 5)
    integral, estimated_error = quad(numerical, 0.0, 1.0)
    root = brentq(lambda value: numerical(value) - 2.0, 0.0, 2.0)

    print(f"Ordinal: {ordinal}")
    print(f"Exact polynomial: {polynomial}")
    print(f"Exact wrap value: {exact_value}")
    print(f"Numerical samples at {grid}: {numerical(grid)}")
    print(f"Integral on [0, 1]: {integral:.12g}; estimated error {estimated_error:.3g}")
    print(f"Root of polynomial - 2 on [0, 2]: {root:.12g}")
    assert np.isclose(integral, 4.0 / 3.0)
    assert np.isclose(root, 1.0)


if __name__ == "__main__":
    main()
