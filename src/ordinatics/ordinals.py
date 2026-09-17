"""Exact, bounded ordinal arithmetic below ``omega ** omega``.

An ordinal is stored in Cantor normal form: ``coefficients[i]`` is the
nonnegative integer coefficient on the *right* of ``omega ** i``. Terms are
read from largest exponent to smallest. Ordinary ordinal ``+`` and ``*``
are noncommutative; ``natural_add`` and ``natural_mul`` instead perform the
commutative polynomial (Hessenberg) operations on this bounded domain.

SymPy conversion transports this normal form to a formal polynomial. It
preserves natural operations, not ordinary ordinal addition/multiplication.
No floating-point approximation or representation of infinity is used.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass
from functools import total_ordering
from types import NotImplementedType
from typing import Any, Iterable


def _is_boolean(value: object) -> bool:
    # NumPy's bool_ historically provided __index__; it still is not an integer
    # input to this API. Avoid importing an optional library just to reject it.
    return isinstance(value, bool) or (
        type(value).__module__ == "numpy" and type(value).__name__ in {"bool", "bool_"}
    )


def _nonnegative_index(value: object, name: str) -> int:
    if _is_boolean(value):
        raise TypeError(f"{name} must be an exact nonnegative integer, not bool")
    if isinstance(value, float):
        raise TypeError(f"{name} must be an exact nonnegative integer, not float")
    try:
        result = operator.index(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be an exact nonnegative integer") from exc
    if result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


@total_ordering
@dataclass(frozen=True, slots=True, eq=False)
class Ordinal:
    """An immutable ordinal strictly below ``omega ** omega``.

    ``Ordinal((3, 2, 1))`` means ``omega**2 + omega*2 + 3``. Coefficients
    are exact integers in ascending exponent order; trailing zeroes are
    removed. ``Ordinal()`` is zero. Use :meth:`from_int` for a finite input.
    Negative numbers, booleans and floating-point values are rejected.
    """

    coefficients: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        try:
            raw: Iterable[object] = iter(self.coefficients)
        except TypeError as exc:
            raise TypeError("coefficients must be an iterable of integers") from exc
        values = tuple(_nonnegative_index(c, "coefficient") for c in raw)
        length = len(values)
        while length and values[length - 1] == 0:
            length -= 1
        object.__setattr__(self, "coefficients", values[:length])

    @classmethod
    def from_int(cls, value: object) -> Ordinal:
        """Construct a finite ordinal from an exact nonnegative integer."""
        value = _nonnegative_index(value, "value")
        return cls((value,))

    @classmethod
    def omega_power(cls, exponent: object) -> Ordinal:
        """Construct ``omega ** n`` for a finite nonnegative integer ``n``."""
        exponent = _nonnegative_index(exponent, "exponent")
        return cls((0,) * exponent + (1,))

    @property
    def is_finite(self) -> bool:
        """Whether this ordinal is a natural number (including zero)."""
        return len(self.coefficients) <= 1

    def to_int(self) -> int:
        """Return the exact finite value; raise ValueError for infinite ordinals."""
        if not self.is_finite:
            raise ValueError("an infinite ordinal has no finite integer value")
        return self.coefficients[0] if self.coefficients else 0

    @property
    def is_limit(self) -> bool:
        """Whether this ordinal is a limit ordinal (> 0 with no immediate predecessor)."""
        return bool(self.coefficients) and self.coefficients[0] == 0

    @property
    def is_successor(self) -> bool:
        """Whether this ordinal is a successor ordinal (has an immediate predecessor)."""
        return bool(self.coefficients) and self.coefficients[0] > 0

    @property
    def predecessor(self) -> Ordinal:
        """Return the immediate predecessor of a successor ordinal."""
        if not self.is_successor:
            raise ValueError("zero and limit ordinals have no immediate predecessor")
        values = list(self.coefficients)
        values[0] -= 1
        return Ordinal(tuple(values))

    def fundamental_sequence(self, n: object) -> Ordinal:
        """Return the n-th element of the canonical fundamental sequence for a limit ordinal.

        As nonnegative integer n -> omega, fundamental_sequence(n) strictly increases to this limit ordinal.
        """
        if not self.is_limit:
            raise ValueError("fundamental sequence is only defined for limit ordinals")
        n_val = _nonnegative_index(n, "index")
        min_exp = next(i for i, c in enumerate(self.coefficients) if i > 0 and c > 0)
        values = list(self.coefficients)
        values[min_exp] -= 1
        mu = Ordinal(tuple(values))
        step = Ordinal.omega_power(min_exp - 1) * (n_val + 1)
        return mu + step

    @staticmethod
    def _operand(value: object) -> Ordinal | NotImplementedType:
        if isinstance(value, Ordinal):
            return value
        if _is_boolean(value) or isinstance(value, float):
            return NotImplemented
        try:
            result = operator.index(value)
        except TypeError:
            return NotImplemented
        return Ordinal.from_int(result)

    def __bool__(self) -> bool:
        return bool(self.coefficients)

    def __hash__(self) -> int:
        # Finite ordinals compare equal to integers and must share their hashes.
        if self.is_finite:
            return hash(self.to_int())
        return hash((Ordinal, self.coefficients))

    def __eq__(self, other: object) -> bool:
        try:
            other = self._operand(other)
        except ValueError:
            return False
        if other is NotImplemented:
            return NotImplemented
        return self.coefficients == other.coefficients

    def __lt__(self, other: object) -> bool:
        other = self._operand(other)
        if other is NotImplemented:
            return NotImplemented
        return (len(self.coefficients), self.coefficients[::-1]) < (
            len(other.coefficients), other.coefficients[::-1]
        )

    def __add__(self, other: object) -> Ordinal:
        """Ordinary ordinal addition; e.g. ``1 + OMEGA == OMEGA``."""
        other = self._operand(other)
        if other is NotImplemented:
            return NotImplemented
        if not other:
            return self
        degree = len(other.coefficients) - 1
        if degree >= len(self.coefficients):
            return other
        values = list(self.coefficients)
        values[:degree] = other.coefficients[:degree]
        values[degree] += other.coefficients[degree]
        return Ordinal(tuple(values))

    def __radd__(self, other: object) -> Ordinal:
        other = self._operand(other)
        if other is NotImplemented:
            return NotImplemented
        return other + self

    def left_sub(self, other: object) -> Ordinal:
        """Ordinal left subtraction: unique gamma such that other + gamma == self.

        Defined when other <= self. Raises ValueError if other > self.
        """
        other_ord = self._operand(other)
        if other_ord is NotImplemented:
            raise TypeError("left_sub expects an Ordinal or exact integer")
        if other_ord > self:
            raise ValueError("cannot subtract larger ordinal from smaller ordinal")
        if other_ord == self:
            return ZERO
        if not other_ord:
            return self
        max_len = max(len(self.coefficients), len(other_ord.coefficients))
        self_c = self.coefficients + (0,) * (max_len - len(self.coefficients))
        other_c = other_ord.coefficients + (0,) * (max_len - len(other_ord.coefficients))
        diff_k = 0
        for k in range(max_len - 1, -1, -1):
            if self_c[k] != other_c[k]:
                diff_k = k
                break
        res_coeffs = list(self_c[:diff_k]) + [self_c[diff_k] - other_c[diff_k]]
        return Ordinal(tuple(res_coeffs))

    def __sub__(self, other: object) -> Ordinal:
        """Ordinal subtraction (left subtraction): unique gamma such that other + gamma == self."""
        other_ord = self._operand(other)
        if other_ord is NotImplemented:
            return NotImplemented
        return self.left_sub(other_ord)

    def __rsub__(self, other: object) -> Ordinal:
        other_ord = self._operand(other)
        if other_ord is NotImplemented:
            return NotImplemented
        return other_ord.left_sub(self)

    def __mul__(self, other: object) -> Ordinal:
        """Ordinary ordinal product; e.g. ``2 * OMEGA == OMEGA``."""
        other = self._operand(other)
        if other is NotImplemented:
            return NotImplemented
        if not self or not other:
            return ZERO
        left_degree = len(self.coefficients) - 1
        values = [0] * (left_degree + len(other.coefficients))
        finite_factor = other.coefficients[0]
        if finite_factor:
            values[:left_degree] = self.coefficients[:left_degree]
            values[left_degree] = self.coefficients[left_degree] * finite_factor
        for exponent, coefficient in enumerate(other.coefficients[1:], 1):
            values[left_degree + exponent] = coefficient
        return Ordinal(tuple(values))

    def __rmul__(self, other: object) -> Ordinal:
        other = self._operand(other)
        if other is NotImplemented:
            return NotImplemented
        return other * self

    def __pow__(self, exponent: object, modulo: object = None) -> Ordinal:
        """Ordinary finite power; ``0 ** 0`` is ONE by convention.

        Transfinite exponents and modular exponentiation are outside this API.
        """
        if modulo is not None:
            raise TypeError("modular ordinal exponentiation is not supported")
        exponent = _nonnegative_index(exponent, "exponent")
        result, factor = ONE, self
        while exponent:
            if exponent & 1:
                result = result * factor
            exponent >>= 1
            if exponent:
                factor = factor * factor
        return result

    def natural_add(self, other: object) -> Ordinal:
        """Hessenberg sum: add matching coefficients without absorption."""
        other = self._operand(other)
        if other is NotImplemented:
            raise TypeError("natural_add expects an Ordinal or exact integer")
        values = [0] * max(len(self.coefficients), len(other.coefficients))
        for index, coefficient in enumerate(self.coefficients):
            values[index] += coefficient
        for index, coefficient in enumerate(other.coefficients):
            values[index] += coefficient
        return Ordinal(tuple(values))

    def natural_mul(self, other: object) -> Ordinal:
        """Hessenberg product: polynomial convolution of the coefficients."""
        other = self._operand(other)
        if other is NotImplemented:
            raise TypeError("natural_mul expects an Ordinal or exact integer")
        if not self or not other:
            return ZERO
        values = [0] * (len(self.coefficients) + len(other.coefficients) - 1)
        for left_exponent, left_coefficient in enumerate(self.coefficients):
            for right_exponent, right_coefficient in enumerate(other.coefficients):
                values[left_exponent + right_exponent] += (
                    left_coefficient * right_coefficient
                )
        return Ordinal(tuple(values))

    def to_sympy(self, symbol: object = None) -> Any:
        """Return a formal polynomial encoding of this normal form.

        Uses the ``sympy`` dependency. The default indeterminate
        is ``sympy.Symbol('X')``; custom symbols must be commutative.
        Polynomial arithmetic corresponds to the
        natural operations, and must not be read as ordinary ordinal arithmetic.
        """
        import sympy

        if symbol is None:
            symbol = sympy.Symbol("X")
        if not isinstance(symbol, sympy.Symbol) or symbol.is_commutative is not True:
            raise TypeError("symbol must be a commutative SymPy Symbol")
        return sympy.Add(
            *(sympy.Integer(c) * symbol**i for i, c in enumerate(self.coefficients))
        )

    @classmethod
    def from_sympy(cls, expression: object, symbol: object = None) -> Ordinal:
        """Read a univariate polynomial with exact nonnegative integer coefficients.

        Rejects strings, floating-point atoms, additional indeterminates,
        negative/rational coefficients and nonpolynomial expressions. This is
        a structural normal-form conversion, not an ordinal limit evaluator.
        The indeterminate must be a commutative SymPy Symbol.
        """
        import sympy

        if symbol is None:
            symbol = sympy.Symbol("X")
        if not isinstance(symbol, sympy.Symbol) or symbol.is_commutative is not True:
            raise TypeError("symbol must be a commutative SymPy Symbol")
        if not isinstance(expression, sympy.Basic):
            expression = sympy.Integer(_nonnegative_index(expression, "expression"))
        if isinstance(expression, sympy.Poly):
            expression = expression.as_expr()
        if expression.has(sympy.Float):
            raise ValueError("floating-point coefficients are not exact integers")
        if expression.free_symbols - {symbol}:
            raise ValueError("polynomial contains an unexpected symbol")
        try:
            polynomial = sympy.Poly(expression, symbol, domain=sympy.ZZ)
        except (sympy.PolynomialError, sympy.CoercionFailed, ValueError) as exc:
            raise ValueError("expected a polynomial with exact integer coefficients") from exc
        descending = polynomial.all_coeffs()
        if any(c < 0 for c in descending):
            raise ValueError("ordinal coefficients must be nonnegative")
        return cls(tuple(int(c) for c in reversed(descending)))

    def __str__(self) -> str:
        terms = []
        for exponent in range(len(self.coefficients) - 1, -1, -1):
            coefficient = self.coefficients[exponent]
            if not coefficient:
                continue
            if exponent == 0:
                terms.append(str(coefficient))
                continue
            term = "ω" if exponent == 1 else f"ω^{exponent}"
            if coefficient != 1:
                term += f"*{coefficient}"
            terms.append(term)
        return " + ".join(terms) if terms else "0"

    def __repr__(self) -> str:
        return f"Ordinal(coefficients={self.coefficients!r})"


ZERO = Ordinal()
ONE = Ordinal.from_int(1)
OMEGA = Ordinal.omega_power(1)
