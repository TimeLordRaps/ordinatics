"""Ordinal Calculus: difference operators, normal functions, derivatives, and Veblen hierarchy.

Provides:
- Difference operator Delta: Delta F(alpha) = F(alpha + 1) - F(alpha)
- Normal ordinal functions: strictly increasing and continuous at limits
- Ordinal derivatives: F' enumerating the fixed points of F (F(gamma) == gamma)
- Least fixed point computation via transfinite stage ascent
- Veblen hierarchy phi_alpha(beta) with exact Ordinal evaluation below omega**omega
  and symbolic VeblenTerm representations for transfinite epsilon/zeta levels.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass
from typing import Callable, Iterable

from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal, _is_boolean, _nonnegative_index


class DomainError(ValueError):
    """Raised when an ordinal value exceeds the bounded Ordinal representation (< omega**omega)."""


def _to_ordinal(value: object, name: str = "value") -> Ordinal:
    if isinstance(value, Ordinal):
        return value
    if _is_boolean(value) or isinstance(value, float):
        raise TypeError(f"{name} must be an exact nonnegative integer or Ordinal")
    try:
        idx = operator.index(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be an exact nonnegative integer or Ordinal") from exc
    if idx < 0:
        raise ValueError(f"{name} must be nonnegative")
    return Ordinal.from_int(idx)


def _sequence_limit(samples: list[Ordinal]) -> Ordinal:
    """Infer the ordinal limit of an increasing sequence of ordinals below omega**omega.

    If the sequence stabilizes, returns the maximum.
    If degrees strictly grow without bound, raises DomainError.
    Otherwise finds the highest degree whose coefficients grow and takes the limit.
    """
    if not samples:
        return ZERO
    # If trailing elements are identical, it has stabilized
    if len(samples) >= 2 and samples[-1] == samples[-2]:
        return samples[-1]

    degrees = [len(s.coefficients) - 1 if s.coefficients else 0 for s in samples]
    # Check if degrees are growing unboundedly
    if len(degrees) >= 3 and degrees[-1] > degrees[0] + 1 and all(d2 >= d1 for d1, d2 in zip(degrees, degrees[1:])):
        raise DomainError("Sequence degrees grow unboundedly; limit is >= omega**omega")

    # Find highest exponent where coefficients increase across the sequence
    max_deg = max(degrees)
    growing_exp = -1
    for exp in range(max_deg, -1, -1):
        coeffs = [s.coefficients[exp] if exp < len(s.coefficients) else 0 for s in samples]
        if any(c2 > c1 for c1, c2 in zip(coeffs, coeffs[1:])):
            growing_exp = exp
            break

    if growing_exp < 0:
        return max(samples)

    # The term at growing_exp ascends to omega**(growing_exp + 1)
    # Ordinal addition of omega**(growing_exp + 1) to terms above growing_exp:
    # Terms at and below growing_exp are wiped out; coefficient at growing_exp + 1 increments.
    high_terms = list(samples[-1].coefficients[growing_exp + 1:])
    if high_terms:
        high_terms[0] += 1
    else:
        high_terms = [1]
    result_coeffs = [0] * (growing_exp + 1) + high_terms
    return Ordinal(tuple(result_coeffs))


def ordinal_supremum(ordinals: Iterable[Ordinal | int]) -> Ordinal:
    """Return the supremum of an iterable of ordinals.

    For finite collections, returns max(ordinals) (or ZERO if empty).
    For lists exhibiting monotonic transfinite growth, infers the limit below omega**omega.
    """
    items = [_to_ordinal(x) for x in ordinals]
    if not items:
        return ZERO
    if len(items) == 1:
        return items[0]
    # Check if monotonic increasing
    is_increasing = all(a <= b for a, b in zip(items, items[1:]))
    if is_increasing and items[-1] > items[0] and len(items) >= 4:
        return _sequence_limit(items)
    return max(items)


def delta(func: Callable[[Ordinal], Ordinal], alpha: Ordinal | int) -> Ordinal:
    """Ordinal difference operator: Delta F(alpha) = F(alpha + 1) - F(alpha).

    Evaluates the left difference (unique gamma such that F(alpha) + gamma == F(alpha + 1)).
    Raises ValueError if F(alpha + 1) < F(alpha).
    """
    alpha_ord = _to_ordinal(alpha, "alpha")
    val_alpha = _to_ordinal(func(alpha_ord), "F(alpha)")
    val_succ = _to_ordinal(func(alpha_ord + ONE), "F(alpha + 1)")
    if val_succ < val_alpha:
        raise ValueError(
            f"Difference operator requires weakly increasing function; "
            f"F({alpha_ord + ONE}) = {val_succ} < F({alpha_ord}) = {val_alpha}"
        )
    return val_succ - val_alpha


class DifferenceOperator:
    """Difference operator on ordinal functions.

    Supports order n: Delta**n F(alpha).
    """

    def __init__(self, func: Callable[[Ordinal], Ordinal], order: int = 1) -> None:
        ord_int = _nonnegative_index(order, "order")
        if ord_int < 1:
            raise ValueError("order must be a positive integer >= 1")
        self.func = func
        self.order = ord_int
        # Pre-compose the difference operator for the given order
        current = func
        for _ in range(ord_int - 1):
            prev = current

            def _step(x: Ordinal, f: Callable[[Ordinal], Ordinal] = prev) -> Ordinal:
                return delta(f, x)

            current = _step
        self._step_func = current

    def __call__(self, alpha: Ordinal | int) -> Ordinal:
        alpha_ord = _to_ordinal(alpha, "alpha")
        return delta(self._step_func, alpha_ord)

    def __pow__(self, power: int) -> DifferenceOperator:
        """Compose difference operators: (Delta**n)**m = Delta**(n*m)."""
        pow_int = _nonnegative_index(power, "power")
        if pow_int < 1:
            raise ValueError("power must be a positive integer >= 1")
        return DifferenceOperator(self.func, order=self.order * pow_int)

    def __repr__(self) -> str:
        return f"DifferenceOperator({self.func!r}, order={self.order})"


Delta = DifferenceOperator


def least_fixed_point(
    func: Callable[[Ordinal], Ordinal],
    start: Ordinal | int = 0,
    max_iter: int = 100,
) -> Ordinal:
    """Compute the least fixed point gamma >= start of an ordinal function func.

    Iterates gamma_{k+1} = func(gamma_k). If finite steps do not stabilize,
    accelerates along ordinal limit sequences. Raises DomainError if the fixed
    point reaches or exceeds omega**omega.
    """
    gamma = _to_ordinal(start, "start")
    history: list[Ordinal] = [gamma]

    for step in range(max_iter):
        next_gamma = _to_ordinal(func(gamma), "F(gamma)")
        if next_gamma == gamma:
            return gamma
        if next_gamma < gamma:
            raise ValueError(
                f"Function is not weakly increasing: F({gamma}) = {next_gamma} < {gamma}"
            )
        # If degree is growing steadily over recent iterations, detect divergence to >= omega**omega
        if len(history) >= 4 and len(next_gamma.coefficients) > len(history[0].coefficients) + 1:
            # Check if each step adds a degree
            recent_degrees = [len(h.coefficients) for h in history[-3:]]
            if recent_degrees[-1] > recent_degrees[0]:
                raise DomainError(
                    "Fixed point sequence degrees grow unboundedly; "
                    "least fixed point exceeds bounded Ordinal domain (< omega**omega)"
                )

        history.append(next_gamma)
        gamma = next_gamma

        # After several non-stabilizing steps, attempt limit acceleration
        if len(history) >= 12:
            try:
                lim = _sequence_limit(history[-10:])
            except DomainError:
                raise
            if lim > gamma:
                gamma = lim
                history = [gamma]
                if _to_ordinal(func(gamma)) == gamma:
                    return gamma

    raise DomainError(
        f"Least fixed point search did not converge within {max_iter} iterations"
    )


class NormalFunction:
    """A normal ordinal function: strictly increasing and continuous at limit ordinals.

    Can be called directly F(alpha) -> Ordinal.
    Provides `.derivative()` returning F' which enumerates the fixed points of F.
    """

    def __init__(
        self,
        func: Callable[[Ordinal], Ordinal],
        name: str = "F",
        derivative_func: NormalFunction | None = None,
    ) -> None:
        self._func = func
        self.name = name
        self._derivative_func = derivative_func

    def __call__(self, alpha: Ordinal | int) -> Ordinal:
        alpha_ord = _to_ordinal(alpha, "alpha")
        return self._func(alpha_ord)

    def is_strictly_increasing(self, test_ordinals: Iterable[Ordinal | int]) -> bool:
        """Check if F is strictly increasing on the provided test ordinals."""
        sorted_ords = sorted({_to_ordinal(x) for x in test_ordinals})
        for a, b in zip(sorted_ords, sorted_ords[1:]):
            if not (self(a) < self(b)):
                return False
        return True

    def is_continuous_at_limit(self, limit_ordinal: Ordinal | int, sample_count: int = 8) -> bool:
        """Check if F(lambda) == sup { F(lambda[n]) } for a limit ordinal lambda."""
        lim_ord = _to_ordinal(limit_ordinal, "limit_ordinal")
        if not lim_ord.is_limit:
            raise ValueError(f"{lim_ord} is not a limit ordinal")
        samples = [self(lim_ord.fundamental_sequence(i)) for i in range(sample_count)]
        sup = ordinal_supremum(samples)
        return self(lim_ord) == sup

    def is_normal(self, test_bound: Ordinal | int = 15) -> bool:
        """Test normality (strictly increasing and continuous at limits) up to test_bound."""
        bound_ord = _to_ordinal(test_bound, "test_bound")
        # Generate finite sample ordinals
        test_samples: list[Ordinal] = [Ordinal.from_int(i) for i in range(min(10, bound_ord.to_int() + 1 if bound_ord.is_finite else 10))]
        if bound_ord >= OMEGA:
            test_samples.extend([OMEGA, OMEGA + ONE, OMEGA + 2, OMEGA * 2])
        if bound_ord >= OMEGA**2:
            test_samples.extend([OMEGA**2, OMEGA**2 + OMEGA, OMEGA**2 * 2])
        test_samples = [s for s in test_samples if s <= bound_ord]

        if not self.is_strictly_increasing(test_samples):
            return False

        # Test limit ordinals among samples
        limit_samples = [s for s in test_samples if s.is_limit]
        for lim in limit_samples:
            if not self.is_continuous_at_limit(lim):
                return False
        return True

    def derivative(self) -> NormalFunction:
        """Return the ordinal derivative F' enumerating the fixed points of F."""
        if self._derivative_func is not None:
            return self._derivative_func
        return OrdinalDerivative(self)

    @classmethod
    def add_left(cls, beta: Ordinal | int) -> NormalFunction:
        """Normal function F(alpha) = beta + alpha."""
        beta_ord = _to_ordinal(beta, "beta")
        name = f"add_left({beta_ord})"

        def _fn(alpha: Ordinal) -> Ordinal:
            return beta_ord + alpha

        # Analytical derivative:
        # If beta == 0, F(alpha) = alpha, fixed points are all ordinals: F'(alpha) = alpha.
        # If beta > 0:
        # Let omega**k be the smallest power of omega strictly greater than beta.
        # Then fixed points are omega**k + alpha!
        def _deriv_fn(alpha: Ordinal) -> Ordinal:
            if not beta_ord:
                return alpha
            k = len(beta_ord.coefficients)
            power = Ordinal.omega_power(k)
            return power + alpha

        deriv = cls(_deriv_fn, name=f"{name}'")
        return cls(_fn, name=name, derivative_func=deriv)

    @classmethod
    def multiply_left(cls, beta: Ordinal | int) -> NormalFunction:
        """Normal function F(alpha) = beta * alpha for beta >= 1."""
        beta_ord = _to_ordinal(beta, "beta")
        if not beta_ord:
            raise ValueError("beta must be >= 1 for a normal function")
        name = f"multiply_left({beta_ord})"

        def _fn(alpha: Ordinal) -> Ordinal:
            return beta_ord * alpha

        def _deriv_fn(alpha: Ordinal) -> Ordinal:
            if beta_ord == ONE:
                return alpha
            if beta_ord.is_finite:
                # Fixed points of n * alpha (n >= 2) are 0, omega, omega*2, ..., omega * alpha
                return OMEGA * alpha
            # For infinite beta, beta * alpha fixed points
            if beta_ord == OMEGA:
                if alpha == ZERO:
                    return ZERO
                raise DomainError(
                    "Derivative of multiply_left(OMEGA) for alpha > 0 exceeds omega**omega"
                )
            return least_fixed_point(_fn, alpha)

        deriv = cls(_deriv_fn, name=f"{name}'")
        return cls(_fn, name=name, derivative_func=deriv)

    @classmethod
    def omega_power(cls) -> NormalFunction:
        """Normal function F(alpha) = omega**alpha for finite alpha."""
        name = "omega_power"

        def _fn(alpha: Ordinal) -> Ordinal:
            if not alpha.is_finite:
                raise DomainError(f"omega**{alpha} >= omega**omega exceeds bounded Ordinal domain")
            return Ordinal.omega_power(alpha.to_int())

        return cls(_fn, name=name)

    def __repr__(self) -> str:
        return f"NormalFunction({self.name})"


class OrdinalDerivative(NormalFunction):
    """Ordinal derivative F' enumerating the fixed points of a normal function F.

    F'(0) is the least fixed point of F.
    F'(alpha + 1) is the least fixed point strictly greater than F'(alpha).
    F'(lambda) is the supremum of F'(xi) for xi < lambda.
    """

    def __init__(self, base_func: Callable[[Ordinal], Ordinal] | NormalFunction) -> None:
        if isinstance(base_func, NormalFunction):
            self.base_func = base_func
            name = f"{base_func.name}'"
        else:
            func_name = getattr(base_func, "name", getattr(base_func, "__name__", "F"))
            self.base_func = NormalFunction(base_func, name=func_name)
            name = f"{func_name}'"
        self._cache: dict[Ordinal, Ordinal] = {}
        super().__init__(self._compute, name=name)

    def _compute(self, alpha: Ordinal) -> Ordinal:
        if alpha in self._cache:
            return self._cache[alpha]

        if not alpha:
            result = least_fixed_point(self.base_func, ZERO)
            self._cache[alpha] = result
            return result

        if alpha.is_limit:
            samples = [self(alpha.fundamental_sequence(i)) for i in range(8)]
            lim_cand = _sequence_limit(samples)
            try:
                result = least_fixed_point(self.base_func, lim_cand)
            except DomainError:
                result = lim_cand
            self._cache[alpha] = result
            return result

        # alpha is successor: unwind chain iteratively to avoid Python RecursionError
        chain: list[Ordinal] = []
        curr = alpha
        while curr.is_successor and curr not in self._cache:
            chain.append(curr)
            curr = curr.predecessor

        if curr in self._cache:
            prev = self._cache[curr]
        else:
            prev = self(curr)

        for succ in reversed(chain):
            prev = least_fixed_point(self.base_func, prev + ONE)
            self._cache[succ] = prev

        return prev


def derivative(func: NormalFunction | Callable[[Ordinal], Ordinal]) -> NormalFunction:
    """Return the ordinal derivative of a normal function."""
    if isinstance(func, NormalFunction):
        return func.derivative()
    return NormalFunction(func).derivative()


@dataclass(frozen=True, slots=True, eq=False)
class VeblenTerm:
    """Symbolic representation of the Veblen hierarchy value phi_alpha(beta).

    phi_0(beta) = omega**beta
    phi_1(beta) = epsilon_beta (fixed points of phi_0)
    phi_2(beta) = zeta_beta (fixed points of phi_1)
    phi_{alpha + 1}(beta) enumerates fixed points of phi_alpha.
    """

    alpha: Ordinal
    beta: Ordinal

    def __init__(self, alpha: object, beta: object) -> None:
        object.__setattr__(self, "alpha", _to_ordinal(alpha, "alpha"))
        object.__setattr__(self, "beta", _to_ordinal(beta, "beta"))

    @property
    def is_epsilon(self) -> bool:
        """Whether this term is in the epsilon sequence (alpha == 1)."""
        return self.alpha == ONE

    @property
    def is_zeta(self) -> bool:
        """Whether this term is in the zeta sequence (alpha == 2)."""
        return self.alpha == Ordinal.from_int(2)

    def eval(self) -> Ordinal:
        """Evaluate to an exact Ordinal if within bounded domain (< omega**omega)."""
        if not self.alpha and self.beta.is_finite:
            return Ordinal.omega_power(self.beta.to_int())
        raise DomainError(
            f"{self} >= omega**omega exceeds bounded Ordinal representation. "
            f"Retain as symbolic VeblenTerm."
        )

    def __hash__(self) -> int:
        try:
            return hash(self.eval())
        except DomainError:
            return hash((VeblenTerm, self.alpha, self.beta))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VeblenTerm):
            return self.alpha == other.alpha and self.beta == other.beta
        if isinstance(other, (Ordinal, int)):
            try:
                return self.eval() == other
            except DomainError:
                return False
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, (Ordinal, int)):
            try:
                return self.eval() < other
            except DomainError:
                # Any VeblenTerm >= omega**omega is strictly greater than any Ordinal < omega**omega
                return False
        if isinstance(other, VeblenTerm):
            # Veblen normal form comparison
            if self.alpha == other.alpha:
                return self.beta < other.beta
            if self.alpha < other.alpha:
                return self.beta < other
            # self.alpha > other.alpha
            return self <= other.beta
        return NotImplemented

    def __le__(self, other: object) -> bool:
        return self == other or self < other

    def __gt__(self, other: object) -> bool:
        if isinstance(other, (Ordinal, int)):
            try:
                return self.eval() > other
            except DomainError:
                return True
        if isinstance(other, VeblenTerm):
            return other < self
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        return self == other or self > other

    def __str__(self) -> str:
        if not self.alpha:
            if not self.beta:
                return "1"
            if self.beta == ONE:
                return "ω"
            if self.beta.is_finite:
                return f"ω^{self.beta.to_int()}"
            return f"φ(0, {self.beta})"
        if self.alpha == ONE:
            return f"ε_{self.beta}"
        if self.alpha == Ordinal.from_int(2):
            return f"ζ_{self.beta}"
        return f"φ({self.alpha}, {self.beta})"

    def __repr__(self) -> str:
        return f"VeblenTerm(alpha={self.alpha!r}, beta={self.beta!r})"


class VeblenHierarchy:
    """The Veblen hierarchy of normal ordinal functions phi_alpha(beta)."""

    @staticmethod
    def phi(
        alpha: Ordinal | int,
        beta: Ordinal | int,
        symbolic: bool = False,
    ) -> Ordinal | VeblenTerm:
        """Evaluate phi_alpha(beta) in the Veblen hierarchy."""
        return veblen(alpha, beta, symbolic=symbolic)

    @staticmethod
    def level(alpha: Ordinal | int) -> NormalFunction:
        """Return the alpha-th level normal function phi_alpha."""
        alpha_ord = _to_ordinal(alpha, "alpha")
        if not alpha_ord:
            return NormalFunction.omega_power()
        if alpha_ord.is_successor:
            pred = VeblenHierarchy.level(alpha_ord.predecessor)
            return pred.derivative()
        raise DomainError(f"Veblen level {alpha_ord} requires transfinite limit construction")


def veblen(
    alpha: Ordinal | int,
    beta: Ordinal | int,
    symbolic: bool = False,
) -> Ordinal | VeblenTerm:
    """Evaluate or construct phi_alpha(beta) in the Veblen hierarchy.

    If symbolic is False and alpha == 0 and beta < omega: returns exact Ordinal.
    Otherwise raises DomainError (or returns VeblenTerm if symbolic=True).
    """
    alpha_ord = _to_ordinal(alpha, "alpha")
    beta_ord = _to_ordinal(beta, "beta")
    if not symbolic:
        if not alpha_ord and beta_ord.is_finite:
            return Ordinal.omega_power(beta_ord.to_int())
        raise DomainError(
            f"phi({alpha_ord}, {beta_ord}) >= omega**omega exceeds bounded Ordinal domain. "
            f"Pass symbolic=True to obtain a VeblenTerm."
        )
    return VeblenTerm(alpha_ord, beta_ord)
