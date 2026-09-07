"""Exact rational functions and a chosen value map for ordinal polynomials.

``rational_function`` works in Q(X), the field of rational functions in one
indeterminate with rational coefficients. Use ``ordinal.to_sympy()`` to enter
this layer explicitly. Specialization is a ring homomorphism on polynomials
and extends to fractions whose reduced denominator is nonzero at the chosen
point. It is not a homomorphism for ordinary ordinal addition or multiplication.

All quantities here are dimensionless. Floating-point approximation belongs at
the boundary, for example through SymPy's ``lambdify(..., modules="numpy")``.
"""

from __future__ import annotations

from typing import Any

import sympy as sp
from sympy.polys.polyerrors import CoercionFailed, PolynomialError

X = sp.Symbol("X")


class PoleError(ZeroDivisionError):
    """The reduced rational function has a pole at the requested value."""


def _symbol(symbol: Any) -> sp.Symbol:
    if not isinstance(symbol, sp.Symbol) or symbol.is_commutative is not True:
        raise TypeError("symbol must be a commutative SymPy Symbol")
    return symbol


def _exact_expr(value: Any, *, label: str) -> sp.Expr:
    # sympify parses strings, so reject text before invoking that adapter.
    if isinstance(value, (str, bytes, bytearray, bool)):
        raise TypeError(f"{label} must be an exact numeric or SymPy expression, not text or bool")
    try:
        result = sp.sympify(value, strict=True)
    except (TypeError, ValueError, sp.SympifyError) as exc:
        raise TypeError(f"{label} cannot be converted to an exact SymPy expression") from exc
    if not isinstance(result, sp.Expr) or isinstance(result, (sp.MatrixBase, sp.MatrixExpr)):
        raise TypeError(f"{label} must be a scalar SymPy expression")
    if result.has(sp.Float):
        raise TypeError(f"{label} must be exact; use integers, Fraction, or SymPy Rational")
    if result.has(sp.nan, sp.oo, -sp.oo, sp.zoo):
        raise ValueError(f"{label} must not contain infinity or NaN")
    return result


def _rational(value: Any, *, label: str) -> sp.Rational:
    result = _exact_expr(value, label=label)
    if not isinstance(result, sp.Rational):
        raise ValueError(f"{label} must be an exact rational number")
    return result


def rational_function(expr: Any, *, symbol: sp.Symbol = X) -> sp.Expr:
    """Validate and reduce an exact element of Q(``symbol``).

    Accept Python integers, ``fractions.Fraction``, exact NumPy integer scalars,
    and compatible SymPy scalar expressions. Strings are never parsed. Floats,
    other free symbols, nonrational coefficients, and nonrational functions are
    rejected. Return an ordinary SymPy expression with common factors cancelled.

    This is an explicit adapter: pass ``ordinal.to_sympy(symbol)`` for an ordinal
    polynomial. NumPy arrays and SymPy matrices are not scalar inputs.
    """
    variable = _symbol(symbol)
    value = _exact_expr(expr, label="expr")
    foreign = value.free_symbols - {variable}
    if foreign:
        names = ", ".join(sorted(str(item) for item in foreign))
        raise ValueError(f"expr contains symbols other than {variable}: {names}")
    numerator, denominator = value.as_numer_denom()
    try:
        numerator_poly = sp.Poly(numerator, variable, domain=sp.QQ)
        denominator_poly = sp.Poly(denominator, variable, domain=sp.QQ)
    except (PolynomialError, CoercionFailed) as exc:
        raise ValueError(f"expr must be a rational function in {variable} with rational coefficients") from exc
    if denominator_poly.is_zero:
        raise ValueError("expr has an identically zero denominator")
    return sp.cancel(numerator_poly.as_expr() / denominator_poly.as_expr(), variable)


def specialize(expr: Any, *, symbol: sp.Symbol = X, at: Any) -> sp.Rational:
    """Evaluate the reduced rational function at an exact rational value.

    Common factors are cancelled first: ``(X**2 - 1)/(X - 1)`` specializes to
    2 at 1. A denominator that remains zero after reduction raises ``PoleError``.
    The result is exact. This convention concerns rational-function values, not
    the domain of a particular unreduced expression or a limit inferred from
    floating-point samples.
    """
    variable = _symbol(symbol)
    point = _rational(at, label="at")
    reduced = rational_function(expr, symbol=variable)
    numerator, denominator = reduced.as_numer_denom()
    denominator_value = denominator.subs(variable, point)
    if denominator_value == 0:
        raise PoleError(f"reduced rational function has a pole at {variable} = {point}")
    return sp.Rational(numerator.subs(variable, point) / denominator_value)


def wrap(expr: Any, *, symbol: sp.Symbol = X) -> sp.Rational:
    """Specialize at X = -1/2, with exact arithmetic and explicit pole errors.

    ``wrap`` is the paper's chosen polynomial value map. Its extension to Q(X)
    is partial because some rational functions have poles at -1/2.
    """
    return specialize(expr, symbol=symbol, at=sp.Rational(-1, 2))


def rational_power_image(exponent: Any) -> sp.Expr:
    """Return exp(r * (-log(2) + I*pi)) for an exact rational exponent r.

    This fixes one logarithm of -1/2 for all exponents, so the exponent-addition
    law holds coherently. It is a complex-valued extension of the chosen value
    map, not ordinal exponentiation, a real root convention, or permission to
    apply unrestricted nested principal-power identities.
    """
    rational = _rational(exponent, label="exponent")
    return sp.exp(rational * (-sp.log(2) + sp.I * sp.pi))


def complex_period() -> sp.Expr:
    """Return 2*pi*I/(-log(2) + I*pi), a period of the complex exponent map.

    For the extension F(z) = exp(z * (-log(2) + I*pi)), F(z + period) = F(z).
    The returned period is complex; it is not an integer or ordinal period.
    """
    return 2 * sp.pi * sp.I / (-sp.log(2) + sp.I * sp.pi)
