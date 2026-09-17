"""Deep regression tests for Ordinal Calculus and Dynamics.

Tests:
- Left subtraction and ordinal difference operators
- Limit, successor, predecessor, and fundamental sequences
- Normal ordinal functions, monotonicity, and continuity at limits
- Fixed point computation via stage ascent and minimality
- Ordinal derivatives F' as fixed point enumerators
- The Veblen hierarchy: exact evaluations, DomainError boundaries, and symbolic Veblen terms
- Discrete and ordinal dynamical systems, transfinite orbits, and attractors
"""

import pytest

from ordinatics.calculus import (
    Delta,
    DomainError,
    NormalFunction,
    OrdinalDerivative,
    VeblenHierarchy,
    VeblenTerm,
    delta,
    derivative,
    least_fixed_point,
    ordinal_supremum,
    veblen,
)
from ordinatics.dynamics import (
    OrdinalDynamicalSystem,
    OrdinalTransformation,
    find_attractor,
    find_fixed_point,
    orbit,
)
from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal

# ============================================================================
# 1. Left subtraction and difference operators
# ============================================================================

def test_ordinal_left_subtraction_exactness():
    # beta - alpha is gamma such that alpha + gamma == beta
    assert Ordinal.from_int(5) - 3 == Ordinal.from_int(2)
    assert OMEGA - 1 == OMEGA
    assert 1 + (OMEGA - 1) == OMEGA

    assert (OMEGA + 3) - OMEGA == Ordinal.from_int(3)
    assert OMEGA + ((OMEGA + 3) - OMEGA) == OMEGA + 3

    assert (OMEGA * 2 + 5) - (OMEGA + 2) == OMEGA + 5
    assert (OMEGA + 2) + ((OMEGA * 2 + 5) - (OMEGA + 2)) == OMEGA * 2 + 5

    assert (OMEGA**2 + OMEGA*3 + 1) - (OMEGA*5 + 7) == OMEGA**2 + OMEGA*3 + 1

    # Equal ordinals
    assert OMEGA - OMEGA == ZERO
    assert ZERO - ZERO == ZERO
    assert OMEGA - ZERO == OMEGA

    # Subtraction errors
    with pytest.raises(ValueError, match="cannot subtract larger ordinal"):
        _ = Ordinal.from_int(3) - 5
    with pytest.raises(ValueError, match="cannot subtract larger ordinal"):
        _ = Ordinal.from_int(3) - OMEGA
    with pytest.raises(ValueError, match="cannot subtract larger ordinal"):
        _ = OMEGA - (OMEGA + 1)


def test_difference_operator_delta():
    # Identity: Delta(alpha) = (alpha + 1) - alpha = 1
    def f_id(a):
        return a

    assert delta(f_id, 0) == ONE
    assert delta(f_id, 5) == ONE
    assert delta(f_id, OMEGA) == ONE
    assert delta(f_id, OMEGA**2 + OMEGA) == ONE

    # Linear: F(alpha) = alpha * 2 (right multiplication: F(alpha) = 2*alpha)
    def f_double(a):
        return 2 * a

    assert delta(f_double, 0) == Ordinal.from_int(2)
    assert delta(f_double, 1) == Ordinal.from_int(2)
    # At omega: 2 * (omega + 1) = omega + 2; 2 * omega = omega; delta = (omega + 2) - omega = 2
    assert delta(f_double, OMEGA) == Ordinal.from_int(2)

    # Scaling: F(alpha) = omega * alpha
    def f_omega(a):
        return OMEGA * a

    assert delta(f_omega, 0) == OMEGA
    assert delta(f_omega, 1) == OMEGA
    assert delta(f_omega, 2) == OMEGA

    # Decreasing function raises ValueError
    def f_dec(a):
        return Ordinal.from_int(max(0, 10 - a.to_int())) if a.is_finite else ZERO

    with pytest.raises(ValueError, match="weakly increasing"):
        delta(f_dec, 2)


def test_difference_operator_class_and_orders():
    def f(a):
        return a * a if a.is_finite else a

    d1 = Delta(f, order=1)
    assert d1(0) == ONE  # 1**2 - 0**2 = 1
    assert d1(1) == Ordinal.from_int(3)  # 2**2 - 1**2 = 3
    assert d1(2) == Ordinal.from_int(5)  # 3**2 - 2**2 = 5

    # Second order difference Delta^2(a^2) = (2(a+1) + 1) - (2a + 1) = 2
    d2 = Delta(f, order=2)
    assert d2(0) == Ordinal.from_int(2)
    assert d2(1) == Ordinal.from_int(2)
    assert d2(2) == Ordinal.from_int(2)

    with pytest.raises(ValueError, match="positive integer"):
        Delta(f, order=0)


# ============================================================================
# 2. Limit, successor, predecessor, and fundamental sequences
# ============================================================================

def test_ordinal_classification_and_predecessor():
    assert not ZERO.is_limit and not ZERO.is_successor
    assert ONE.is_successor and not ONE.is_limit
    assert ONE.predecessor == ZERO

    assert OMEGA.is_limit and not OMEGA.is_successor
    with pytest.raises(ValueError, match="no immediate predecessor"):
        _ = OMEGA.predecessor
    with pytest.raises(ValueError, match="no immediate predecessor"):
        _ = ZERO.predecessor

    succ_omega = OMEGA + 1
    assert succ_omega.is_successor and not succ_omega.is_limit
    assert succ_omega.predecessor == OMEGA

    succ_omega_2 = OMEGA + 2
    assert succ_omega_2.predecessor == succ_omega


def test_fundamental_sequences():
    # Sequence for omega: 1, 2, 3, ... -> omega
    seq_omega = [OMEGA.fundamental_sequence(i) for i in range(5)]
    assert seq_omega == [Ordinal.from_int(i + 1) for i in range(5)]
    assert all(a < b for a, b in zip(seq_omega, seq_omega[1:]))
    assert all(s < OMEGA for s in seq_omega)
    assert ordinal_supremum(seq_omega) == OMEGA

    # Sequence for omega * 2: omega + 1, omega + 2, ... -> omega * 2
    om2 = OMEGA * 2
    seq_om2 = [om2.fundamental_sequence(i) for i in range(5)]
    assert seq_om2[0] == OMEGA + 1
    assert seq_om2[1] == OMEGA + 2
    assert all(s < om2 for s in seq_om2)
    assert ordinal_supremum(seq_om2) == om2

    # Sequence for omega^2: omega, omega*2, omega*3, ... -> omega^2
    om_sq = OMEGA**2
    seq_om_sq = [om_sq.fundamental_sequence(i) for i in range(5)]
    assert seq_om_sq[0] == OMEGA
    assert seq_om_sq[1] == OMEGA * 2
    assert seq_om_sq[2] == OMEGA * 3
    assert all(s < om_sq for s in seq_om_sq)
    assert ordinal_supremum(seq_om_sq) == om_sq

    # Non-limit raises ValueError
    with pytest.raises(ValueError, match="only defined for limit ordinals"):
        (OMEGA + 1).fundamental_sequence(0)


# ============================================================================
# 3. Normal functions and continuity
# ============================================================================

def test_normal_function_add_left():
    # F(alpha) = 1 + alpha
    f = NormalFunction.add_left(1)
    assert f(0) == ONE
    assert f(1) == Ordinal.from_int(2)
    assert f(OMEGA) == OMEGA  # 1 + omega = omega
    assert f(OMEGA + 1) == OMEGA + 1  # 1 + omega + 1 = omega + 1

    # Strictly increasing and continuous at limits
    assert f.is_strictly_increasing([0, 1, 2, OMEGA, OMEGA + 1])
    assert f.is_continuous_at_limit(OMEGA)
    assert f.is_normal(test_bound=OMEGA + 2)


def test_normal_function_multiply_left():
    # F(alpha) = 2 * alpha
    f = NormalFunction.multiply_left(2)
    assert f(0) == ZERO
    assert f(1) == Ordinal.from_int(2)
    assert f(2) == Ordinal.from_int(4)
    assert f(OMEGA) == OMEGA  # 2 * omega = omega
    assert f(OMEGA + 1) == OMEGA + 2  # 2 * (omega + 1) = omega + 2

    assert f.is_strictly_increasing([0, 1, 2, OMEGA, OMEGA + 1])
    assert f.is_continuous_at_limit(OMEGA)
    assert f.is_normal(test_bound=OMEGA + 2)

    with pytest.raises(ValueError, match="beta must be >= 1"):
        NormalFunction.multiply_left(0)


def test_normal_function_omega_power():
    f = NormalFunction.omega_power()
    assert f(0) == ONE
    assert f(1) == OMEGA
    assert f(2) == OMEGA**2
    assert f(3) == OMEGA**3

    assert f.is_strictly_increasing([0, 1, 2, 3])
    # omega^omega exceeds bounded domain
    with pytest.raises(DomainError, match="exceeds bounded Ordinal domain"):
        f(OMEGA)


# ============================================================================
# 4. Fixed point computation
# ============================================================================

def test_least_fixed_point_analytic_and_ascent():
    # F(alpha) = 1 + alpha: fixed points are all ordinals >= omega
    def f1(a):
        return 1 + a

    assert least_fixed_point(f1, start=0) == OMEGA
    assert least_fixed_point(f1, start=5) == OMEGA
    assert least_fixed_point(f1, start=OMEGA) == OMEGA
    assert least_fixed_point(f1, start=OMEGA + 1) == OMEGA + 1

    # F(alpha) = omega + alpha: fixed points are all ordinals >= omega^2
    def f_om(a):
        return OMEGA + a

    assert least_fixed_point(f_om, start=0) == OMEGA**2
    assert least_fixed_point(f_om, start=OMEGA) == OMEGA**2
    assert least_fixed_point(f_om, start=OMEGA**2) == OMEGA**2
    assert least_fixed_point(f_om, start=OMEGA**2 + 1) == OMEGA**2 + 1

    # F(alpha) = 2 * alpha:
    def f2(a):
        return 2 * a

    assert least_fixed_point(f2, start=0) == ZERO  # 0 is fixed
    assert least_fixed_point(f2, start=1) == OMEGA  # least fixed point > 0 is omega
    assert least_fixed_point(f2, start=OMEGA + 1) == OMEGA * 2  # next fixed point is omega * 2


def test_least_fixed_point_divergence_detection():
    # F(alpha) = omega * alpha: fixed points are 0 and epsilon-like powers
    # start = 1 -> alpha_0 = 1, alpha_1 = omega, alpha_2 = omega^2, ... -> omega^omega (out of bounds)
    def f_mult_om(a):
        return OMEGA * a

    with pytest.raises(DomainError, match="exceeds bounded Ordinal domain"):
        least_fixed_point(f_mult_om, start=1)


# ============================================================================
# 5. Ordinal derivatives F'
# ============================================================================

def test_ordinal_derivative_fixed_point_enumeration():
    # F(alpha) = 1 + alpha
    # F'(alpha) = omega + alpha enumerates fixed points
    f = NormalFunction.add_left(1)
    df = f.derivative()

    assert df(0) == OMEGA
    assert df(1) == OMEGA + 1
    assert df(2) == OMEGA + 2
    assert df(OMEGA) == OMEGA * 2

    # Verify each value is genuinely a fixed point of F
    for i in range(5):
        fp = df(i)
        assert f(fp) == fp

    # Monotonicity of derivative
    assert df.is_strictly_increasing([0, 1, 2, 3, OMEGA])


def test_ordinal_derivative_of_multiplication():
    # F(alpha) = 2 * alpha
    # Fixed points are 0, omega, omega*2, omega*3, ...
    f = NormalFunction.multiply_left(2)
    df = f.derivative()

    assert df(0) == ZERO
    assert df(1) == OMEGA
    assert df(2) == OMEGA * 2
    assert df(3) == OMEGA * 3

    for i in range(4):
        fp = df(i)
        assert f(fp) == fp


def test_higher_order_derivative():
    # F(alpha) = 1 + alpha -> F'(alpha) = omega + alpha
    # F''(alpha) = (omega + alpha)' = omega^2 + alpha
    f = NormalFunction.add_left(1)
    df = f.derivative()
    ddf = df.derivative()

    assert ddf(0) == OMEGA**2
    assert ddf(1) == OMEGA**2 + 1
    assert ddf(2) == OMEGA**2 + 2

    # Verify ddf(alpha) is a fixed point of df, and therefore of f
    for i in range(3):
        pt = ddf(i)
        assert df(pt) == pt
        assert f(pt) == pt


# ============================================================================
# 6. Veblen hierarchy
# ============================================================================

def test_veblen_exact_evaluations():
    # phi_0(beta) = omega**beta
    assert veblen(0, 0) == ONE
    assert veblen(0, 1) == OMEGA
    assert veblen(0, 2) == OMEGA**2
    assert veblen(0, 3) == OMEGA**3

    # phi_0(omega) exceeds bounded domain
    with pytest.raises(DomainError, match="exceeds bounded Ordinal domain"):
        veblen(0, OMEGA)

    # phi_1(0) = epsilon_0 exceeds bounded domain
    with pytest.raises(DomainError, match="exceeds bounded Ordinal domain"):
        veblen(1, 0)


def test_veblen_symbolic_terms_and_ordering():
    # Construct symbolic Veblen terms
    e0 = veblen(1, 0, symbolic=True)
    e1 = veblen(1, 1, symbolic=True)
    e2 = veblen(1, 2, symbolic=True)
    z0 = veblen(2, 0, symbolic=True)
    z1 = veblen(2, 1, symbolic=True)

    assert isinstance(e0, VeblenTerm)
    assert e0.is_epsilon
    assert not e0.is_zeta
    assert z0.is_zeta

    assert str(e0) == "ε_0"
    assert str(e1) == "ε_1"
    assert str(z0) == "ζ_0"

    # Ordering within epsilon sequence
    assert e0 < e1 < e2
    assert not (e1 < e0)
    assert e0 == veblen(1, 0, symbolic=True)

    # Ordering across Veblen levels: epsilon_n < zeta_0
    assert e0 < z0
    assert e1 < z0
    assert e2 < z0
    assert z0 < z1

    # Transfinite terms exceed any bounded Ordinal
    huge_ord = OMEGA**10 + OMEGA**5 * 99 + 1000
    assert e0 > huge_ord
    assert huge_ord < e0
    assert z0 > huge_ord

    # phi_0(n) evaluated via VeblenTerm
    v_om2 = VeblenTerm(0, 2)
    assert v_om2.eval() == OMEGA**2
    assert v_om2 == OMEGA**2
    assert v_om2 < e0


def test_veblen_hierarchy_levels():
    level0 = VeblenHierarchy.level(0)
    assert level0(0) == ONE
    assert level0(1) == OMEGA
    assert level0(2) == OMEGA**2

    # phi_1 is the derivative of phi_0
    level1 = VeblenHierarchy.level(1)
    assert isinstance(level1, NormalFunction)


# ============================================================================
# 7. Discrete and Ordinal Dynamical Systems
# ============================================================================

def test_ordinal_transformation_composition_and_powers():
    t_succ = OrdinalTransformation(lambda x: x + 1, name="Succ")
    t_double = OrdinalTransformation(lambda x: 2 * x, name="Double")

    # Composition: (Double * Succ)(x) = Double(Succ(x)) = 2 * (x + 1)
    composed = t_double * t_succ
    assert composed(0) == Ordinal.from_int(2)
    assert composed(1) == Ordinal.from_int(4)
    assert composed(OMEGA) == OMEGA + 2

    # Powers
    t_add3 = t_succ**3
    assert t_add3(0) == Ordinal.from_int(3)
    assert t_add3(5) == Ordinal.from_int(8)
    assert t_add3(OMEGA) == OMEGA + 3


def test_dynamical_system_finite_fixed_point_attractor():
    # Collatz-like decreaser on finite ordinals: x -> x - 1 until 0
    def t(x):
        return x.predecessor if x.is_successor else ZERO

    sys = OrdinalDynamicalSystem(t)
    orb = sys.orbit(initial_state=3, max_stage=10)

    assert orb.is_converged
    assert orb.attractor is not None
    assert orb.attractor.is_fixed_point
    assert orb.attractor.states == (ZERO,)
    assert orb.attractor.stage == Ordinal.from_int(3)
    assert sys.find_fixed_point(3) == ZERO


def test_dynamical_system_periodic_cycle_attractor():
    # Modulo 3 rotation: 0 -> 1 -> 2 -> 0
    def t(x):
        return Ordinal.from_int((x.to_int() + 1) % 3)

    sys = OrdinalDynamicalSystem(t)
    orb = sys.orbit(initial_state=0, max_stage=10)

    assert orb.is_converged
    assert orb.attractor is not None
    assert orb.attractor.is_periodic
    assert orb.attractor.period == 3
    assert orb.attractor.states == (ZERO, ONE, Ordinal.from_int(2))


def test_dynamical_system_transfinite_limit_stage_attractor():
    # Ascent: x -> 1 + x starting at 0
    # Steps: 0, 1, 2, ..., n, ... reaches fixed point omega at stage omega
    def t(x):
        return 1 + x

    sys = OrdinalDynamicalSystem(t)
    orb = sys.orbit(initial_state=0, max_stage=OMEGA + 2)

    assert orb.stages[ZERO] == ZERO
    assert orb.stages[ONE] == ONE
    assert orb.stages[OMEGA] == OMEGA
    assert orb.stages[OMEGA + ONE] == OMEGA  # 1 + omega = omega
    assert orb.stages[OMEGA + 2] == OMEGA

    attractor = sys.find_attractor(0)
    assert attractor.is_fixed_point
    assert attractor.states == (OMEGA,)
    assert attractor.stage == OMEGA
    assert sys.find_fixed_point(0) == OMEGA


def test_convenience_functions():
    def f_succ(x):
        return 1 + x

    def f_mod2(x):
        return Ordinal.from_int((x.to_int() + 1) % 2)

    orb = orbit(f_succ, 0, max_stage=5)
    assert len(orb) == 6
    assert orb[0] == ZERO
    assert orb[5] == Ordinal.from_int(5)

    fp = find_fixed_point(f_succ, 0)
    assert fp == OMEGA

    attr = find_attractor(f_mod2, 0)
    assert attr.is_periodic
    assert attr.period == 2


def test_veblen_hash_and_dictionary_interoperability():
    # VeblenTerm equal to Ordinal must have identical hash and work in sets/dicts
    v_om2 = VeblenTerm(0, 2)
    om2 = OMEGA**2
    assert v_om2 == om2
    assert hash(v_om2) == hash(om2)

    lookup = {om2: "omega_squared"}
    assert lookup[v_om2] == "omega_squared"

    v_one = VeblenTerm(0, 0)
    assert v_one == ONE
    assert v_one == 1
    assert hash(v_one) == hash(ONE) == hash(1)
    assert {1: "unit"}[v_one] == "unit"

    # Set membership
    s = {v_om2, v_one}
    assert om2 in s
    assert ONE in s
    assert 1 in s

    # Transfinite terms have stable hashes and distinguish levels
    e0 = veblen(1, 0, symbolic=True)
    e1 = veblen(1, 1, symbolic=True)
    z0 = veblen(2, 0, symbolic=True)
    trans_set = {e0, e1, z0}
    assert len(trans_set) == 3
    assert veblen(1, 0, symbolic=True) in trans_set


def test_ordinal_derivative_with_plain_callable_and_non_recursive():
    # Plain lambda without .name attribute
    d_lambda = OrdinalDerivative(lambda x: 1 + x)
    assert d_lambda(0) == OMEGA
    assert d_lambda(1) == OMEGA + 1
    assert derivative(lambda x: 1 + x)(0) == OMEGA

    # Deep successor evaluation must not hit Python recursion limits
    deep_ord = Ordinal.from_int(1200)
    res = d_lambda(deep_ord)
    assert res == OMEGA + deep_ord
    assert d_lambda(Ordinal.from_int(100)) == OMEGA + 100


def test_difference_operator_composition_and_type_preservation():
    # Delta on function returning int must still return Ordinal
    def f_int(a):
        return 2 * a.to_int()

    res = delta(f_int, 1)
    assert isinstance(res, Ordinal)
    assert res == Ordinal.from_int(2)

    # DifferenceOperator powers
    d = Delta(lambda a: a * a if a.is_finite else a)
    d2 = d**2
    assert d2.order == 2
    assert d2(0) == Ordinal.from_int(2)
    assert d2(1) == Ordinal.from_int(2)

    # Boolean and invalid power rejection
    with pytest.raises(TypeError):
        _ = d**True
    with pytest.raises(ValueError):
        _ = d**0


def test_ordinal_transformation_boolean_rejection_and_identity():
    t = OrdinalTransformation(lambda x: x + 1, name="Succ")
    with pytest.raises(TypeError):
        _ = t**True
    with pytest.raises(TypeError):
        _ = t**False

    t_id = t**0
    assert t_id(0) == ZERO
    assert t_id(OMEGA) == OMEGA
    assert isinstance(t.step(0), Ordinal)


def test_dynamical_system_transfinite_evolution_no_infinite_loop():
    # System with max_stage = omega * 2 must not enter an infinite loop
    t = OrdinalTransformation(lambda x: 1 + x)
    sys = OrdinalDynamicalSystem(t)
    orb = sys.orbit(0, max_stage=OMEGA * 2)

    assert orb.stages[ZERO] == ZERO
    assert orb.stages[OMEGA] == OMEGA
    # Orbit reached fixed point at omega, so orb[omega * 2] evaluates to omega
    assert orb[OMEGA * 2] == OMEGA
    assert OMEGA * 2 in orb


def test_converged_orbit_stage_indexing_and_containment():
    # Fixed point converged at stage 0 or 1
    sys = OrdinalDynamicalSystem(lambda x: 0)
    orb = sys.orbit(5, max_stage=OMEGA + 5)

    assert orb.is_converged
    assert orb.attractor.is_fixed_point
    # Stages past convergence up to max_stage must be accessible
    assert orb[0] == Ordinal.from_int(5)
    assert orb[1] == ZERO
    assert orb[5] == ZERO
    assert orb[OMEGA] == ZERO
    assert orb[OMEGA + 3] == ZERO
    assert (OMEGA + 3) in orb

    with pytest.raises(KeyError):
        _ = orb[OMEGA + 10]  # Exceeds max_stage


def test_periodic_orbit_stage_indexing():
    # Period 2 cycle: 0 -> 1 -> 0
    sys = OrdinalDynamicalSystem(lambda x: Ordinal.from_int((x.to_int() + 1) % 2))
    orb = sys.orbit(0, max_stage=20)

    assert orb.is_converged
    assert orb.attractor.is_periodic
    assert orb[0] == ZERO
    assert orb[1] == ONE
    assert orb[2] == ZERO
    assert orb[7] == ONE
    assert orb[10] == ZERO
    assert 10 in orb

    # Limit stages for oscillating systems are not evaluated
    assert OMEGA not in orb
    with pytest.raises(KeyError):
        _ = orb[OMEGA]


def test_find_fixed_point_strictness():
    # Strictly increasing function has no fixed point
    sys_strict = OrdinalDynamicalSystem(lambda x: x + 1)
    with pytest.raises(ValueError, match="No attractor detected"):
        sys_strict.find_fixed_point(0, max_steps=20)


def test_normal_function_is_continuous_at_limit_coercion():
    f = NormalFunction.add_left(1)
    # Accepts limit ordinal and coerced arguments
    assert f.is_continuous_at_limit(OMEGA)
    with pytest.raises(ValueError, match="not a limit ordinal"):
        f.is_continuous_at_limit(0)
    with pytest.raises(ValueError, match="not a limit ordinal"):
        f.is_continuous_at_limit(5)

