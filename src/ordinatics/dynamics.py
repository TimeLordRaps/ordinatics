"""Discrete and ordinal dynamical systems over ordinals.

Provides:
- OrdinalTransformation: state evolution operators T: On -> On with composition and powers.
- OrdinalDynamicalSystem: dynamical systems evolving over ordinal stages (successor and limit).
- OrdinalOrbit: trajectory of states indexed by ordinal stages.
- OrdinalAttractor: fixed points and periodic cycle attractors reached at ordinal stages.
- find_attractor and find_fixed_point utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from ordinatics.calculus import _sequence_limit, _to_ordinal
from ordinatics.ordinals import OMEGA, ZERO, Ordinal, _nonnegative_index


@dataclass(frozen=True, slots=True)
class OrdinalAttractor:
    """An attractor of an ordinal dynamical system."""

    kind: str  # "fixed_point", "periodic_cycle", "limit_stage"
    states: tuple[Ordinal, ...]
    period: int
    stage: Ordinal

    @property
    def is_fixed_point(self) -> bool:
        return self.kind == "fixed_point"

    @property
    def is_periodic(self) -> bool:
        return self.kind == "periodic_cycle"

    @property
    def is_limit_stage(self) -> bool:
        return self.kind == "limit_stage"

    def __repr__(self) -> str:
        return (
            f"OrdinalAttractor(kind={self.kind!r}, states={self.states!r}, "
            f"period={self.period}, stage={self.stage!r})"
        )


class OrdinalTransformation:
    """An ordinal state transformation T: On -> On."""

    def __init__(self, func: Callable[[Ordinal], Ordinal], name: str = "T") -> None:
        self._func = func
        self.name = name

    def __call__(self, state: Ordinal | int) -> Ordinal:
        return self.step(state)

    def step(self, state: Ordinal | int) -> Ordinal:
        state_ord = _to_ordinal(state, "state")
        return _to_ordinal(self._func(state_ord), "transformed_state")

    def __mul__(self, other: OrdinalTransformation) -> OrdinalTransformation:
        """Composition of transformations: (T1 * T2)(x) = T1(T2(x))."""
        if not isinstance(other, OrdinalTransformation):
            return NotImplemented
        name = f"({self.name} * {other.name})"
        return OrdinalTransformation(lambda x: self.step(other.step(x)), name=name)

    def __pow__(self, power: int) -> OrdinalTransformation:
        """Repeated application T**n of the transformation."""
        idx = _nonnegative_index(power, "power")
        if idx == 0:
            return OrdinalTransformation(lambda x: _to_ordinal(x), name="Id")
        if idx == 1:
            return self
        composed = self
        for _ in range(idx - 1):
            composed = composed * self
        return OrdinalTransformation(composed._func, name=f"{self.name}**{idx}")

    def is_monotone(self, test_states: Iterable[Ordinal | int]) -> bool:
        """Check if T is weakly monotonic on the test states."""
        sorted_states = sorted({_to_ordinal(s) for s in test_states})
        for s1, s2 in zip(sorted_states, sorted_states[1:]):
            if self.step(s1) > self.step(s2):
                return False
        return True

    def __repr__(self) -> str:
        return f"OrdinalTransformation({self.name})"


class OrdinalOrbit:
    """An orbit of an ordinal dynamical system indexed by ordinal stages."""

    def __init__(
        self,
        initial_state: Ordinal,
        stages: dict[Ordinal, Ordinal],
        trajectory: list[Ordinal],
        attractor: OrdinalAttractor | None = None,
        max_stage: Ordinal | None = None,
    ) -> None:
        self.initial_state = initial_state
        self.stages = stages
        self.trajectory = trajectory
        self.attractor = attractor
        self.max_stage = max_stage

    @property
    def is_converged(self) -> bool:
        return self.attractor is not None

    def __getitem__(self, stage: Ordinal | int) -> Ordinal:
        stage_ord = _to_ordinal(stage, "stage")
        if stage_ord in self.stages:
            return self.stages[stage_ord]
        if self.attractor is not None:
            # Fixed point reached: holds for all subsequent evaluated stages
            if self.attractor.is_fixed_point and stage_ord >= self.attractor.stage:
                if self.max_stage is None or stage_ord <= self.max_stage:
                    return self.attractor.states[0]
            # Periodic cycle: for finite stages past attractor stage
            if (
                self.attractor.is_periodic
                and stage_ord.is_finite
                and self.attractor.stage.is_finite
                and stage_ord >= self.attractor.stage
            ):
                if self.max_stage is None or stage_ord <= self.max_stage:
                    p = self.attractor.period
                    start_idx = self.attractor.stage.to_int() - p
                    k = stage_ord.to_int() - start_idx
                    if k >= 0:
                        return self.attractor.states[k % p]
        if stage_ord.is_finite and stage_ord.to_int() < len(self.trajectory):
            return self.trajectory[stage_ord.to_int()]
        raise KeyError(f"Stage {stage_ord} was not evaluated in this orbit")

    def __contains__(self, stage: object) -> bool:
        try:
            _ = self[stage]  # type: ignore[index]
            return True
        except (KeyError, TypeError, ValueError):
            return False

    def __len__(self) -> int:
        return len(self.trajectory)

    def __iter__(self):
        return iter(self.trajectory)

    def __repr__(self) -> str:
        return (
            f"OrdinalOrbit(initial_state={self.initial_state!r}, "
            f"stages={len(self.stages)}, converged={self.is_converged})"
        )


class OrdinalDynamicalSystem:
    """A dynamical system evolving over ordinal stages."""

    def __init__(
        self,
        transformation: Callable[[Ordinal], Ordinal] | OrdinalTransformation,
        limit_rule: Callable[[list[Ordinal]], Ordinal] | None = None,
        name: str = "OrdinalDynamicalSystem",
    ) -> None:
        if isinstance(transformation, OrdinalTransformation):
            self.transformation = transformation
        else:
            self.transformation = OrdinalTransformation(transformation, name="T")
        self.limit_rule = limit_rule or _sequence_limit
        self.name = name

    def step(self, state: Ordinal | int) -> Ordinal:
        return self.transformation.step(state)

    def orbit(
        self,
        initial_state: Ordinal | int,
        max_stage: Ordinal | int = 20,
    ) -> OrdinalOrbit:
        """Compute the orbit starting at initial_state up to max_stage."""
        init_ord = _to_ordinal(initial_state, "initial_state")
        max_ord = _to_ordinal(max_stage, "max_stage")

        stages: dict[Ordinal, Ordinal] = {}
        trajectory: list[Ordinal] = []
        attractor: OrdinalAttractor | None = None

        current = init_ord
        stages[ZERO] = current
        trajectory.append(current)

        if self.step(current) == current:
            attractor = OrdinalAttractor(
                kind="fixed_point",
                states=(current,),
                period=1,
                stage=ZERO,
            )
            return OrdinalOrbit(
                initial_state=init_ord,
                stages=stages,
                trajectory=trajectory,
                attractor=attractor,
            )

        # Detect finite steps up to min(max_ord, 100) or until attractor
        finite_limit = max_ord.to_int() if max_ord.is_finite else 50
        seen_states: dict[Ordinal, int] = {current: 0}

        for n in range(1, finite_limit + 1):
            next_state = self.step(current)
            n_ord = Ordinal.from_int(n)
            stages[n_ord] = next_state
            trajectory.append(next_state)

            if next_state == current or self.step(next_state) == next_state:
                attractor = OrdinalAttractor(
                    kind="fixed_point",
                    states=(next_state,),
                    period=1,
                    stage=n_ord,
                )
                break
            elif next_state in seen_states:
                first_seen = seen_states[next_state]
                cycle_len = n - first_seen
                cycle_states = tuple(trajectory[first_seen:n])
                attractor = OrdinalAttractor(
                    kind="periodic_cycle",
                    states=cycle_states,
                    period=cycle_len,
                    stage=n_ord,
                )
                break

            seen_states[next_state] = n
            current = next_state

        # Transfinite stage evolution if max_stage >= omega
        if max_ord >= OMEGA:
            if attractor is not None and attractor.is_fixed_point:
                # System already converged to fixed point; holds for all transfinite stages
                pass
            elif attractor is None:
                # Sequence limit at omega
                try:
                    state_omega = self.limit_rule(trajectory[-15:])
                except Exception:
                    state_omega = current
                stages[OMEGA] = state_omega
                if state_omega == current:
                    attractor = OrdinalAttractor(
                        kind="limit_stage",
                        states=(state_omega,),
                        period=1,
                        stage=OMEGA,
                    )
                elif self.step(state_omega) == state_omega:
                    attractor = OrdinalAttractor(
                        kind="fixed_point",
                        states=(state_omega,),
                        period=1,
                        stage=OMEGA,
                    )

                # Advance beyond omega if requested
                if max_ord > OMEGA:
                    curr_trans = state_omega
                    trans_traj = [curr_trans]
                    trans_steps = max_ord.coefficients[0] if max_ord.coefficients else 0
                    trans_steps = min(trans_steps, 50)
                    for k in range(1, trans_steps + 1):
                        curr_trans = self.step(curr_trans)
                        stages[OMEGA + k] = curr_trans
                        trans_traj.append(curr_trans)
                        if self.step(curr_trans) == curr_trans and attractor is None:
                            attractor = OrdinalAttractor(
                                kind="fixed_point",
                                states=(curr_trans,),
                                period=1,
                                stage=OMEGA + k,
                            )

                    if max_ord >= OMEGA * 2 and (attractor is None or not attractor.is_fixed_point):
                        try:
                            state_om2 = self.limit_rule(trans_traj)
                        except Exception:
                            state_om2 = curr_trans
                        stages[OMEGA * 2] = state_om2
                        if self.step(state_om2) == state_om2 and attractor is None:
                            attractor = OrdinalAttractor(
                                kind="fixed_point",
                                states=(state_om2,),
                                period=1,
                                stage=OMEGA * 2,
                            )

        return OrdinalOrbit(
            initial_state=init_ord,
            stages=stages,
            trajectory=trajectory,
            attractor=attractor,
            max_stage=max_ord,
        )

    def find_attractor(
        self,
        initial_state: Ordinal | int,
        max_steps: int = 100,
    ) -> OrdinalAttractor:
        """Find the attractor (fixed point or cycle) reachable from initial_state."""
        orbit = self.orbit(initial_state, max_stage=max_steps)
        if orbit.attractor is not None:
            return orbit.attractor
        # Attempt limit analysis
        state_omega = self.limit_rule(orbit.trajectory[-15:])
        if self.step(state_omega) == state_omega:
            return OrdinalAttractor(
                kind="fixed_point",
                states=(state_omega,),
                period=1,
                stage=OMEGA,
            )
        raise ValueError(
            f"No attractor detected within {max_steps} steps from {initial_state}"
        )

    def find_fixed_point(
        self,
        initial_state: Ordinal | int,
        max_steps: int = 100,
    ) -> Ordinal:
        """Find a fixed point reachable by iterating the transformation."""
        attractor = self.find_attractor(initial_state, max_steps=max_steps)
        if attractor.is_fixed_point:
            return attractor.states[0]
        if attractor.kind == "limit_stage" and self.step(attractor.states[0]) == attractor.states[0]:
            return attractor.states[0]
        raise ValueError(f"System reached attractor {attractor}, which is not a fixed point")


def orbit(
    transformation: Callable[[Ordinal], Ordinal] | OrdinalTransformation,
    initial_state: Ordinal | int,
    max_stage: Ordinal | int = 20,
) -> OrdinalOrbit:
    """Compute the orbit under transformation starting at initial_state."""
    sys = OrdinalDynamicalSystem(transformation)
    return sys.orbit(initial_state, max_stage=max_stage)


def find_attractor(
    transformation: Callable[[Ordinal], Ordinal] | OrdinalTransformation,
    initial_state: Ordinal | int,
    max_steps: int = 100,
) -> OrdinalAttractor:
    """Find the attractor reached under transformation from initial_state."""
    sys = OrdinalDynamicalSystem(transformation)
    return sys.find_attractor(initial_state, max_steps=max_steps)


def find_fixed_point(
    transformation: Callable[[Ordinal], Ordinal] | OrdinalTransformation,
    initial_state: Ordinal | int,
    max_steps: int = 100,
) -> Ordinal:
    """Find the fixed point reached under transformation from initial_state."""
    sys = OrdinalDynamicalSystem(transformation)
    return sys.find_fixed_point(initial_state, max_steps=max_steps)
