# Complex rotation by omega: what it needs

Owner's proposal (USER-STATED, 2026-10-03): rotate around a fractal transformation; for transfinite, the number of rotations is the omega constant; reals become imaginary; carry real and imaginary parts both over the transfinite rotation as the multiplier of omega. `[HYPER]`

## The core, stated exactly

* `[FORM]` A rotation by θ is `z ↦ e^{iθ} z`; a fractal (self-similar) map is a spiral similarity `z ↦ λz`, `λ = r e^{iθ}`, `r` and `θ` dimensionless. After `n` steps: `λⁿ z = rⁿ e^{inθ} z`. This is discrete scale invariance and gives complex exponents with log-periodic structure. It is also what the value map in `exponent_axis_and_rank_order.md` does with `ω^r ↦ exp(r(−log 2 + iπ))`.
* `[FORM]` Quarter-turns of the time axis are Wick rotations `t → −iτ`; ω quarter-turns is ω Wick rotations.
* `[FORM]` "Carry both parts in the multiplier of ω" is `(a + bi)·ω = aω + bω·i`. Ordinals have no subtraction or ring structure, so this needs a field with infinite elements: surcomplex numbers (surreals with `i`; algebraic closure by Conway, *recalled*) or hyperreal complexes.

## What fails, and what each failure requires

1. `[FORM]` **No value without a limit rule.** `iⁿ` cycles `1, i, −1, −i` and does not converge. Ordinal remainder: `ω = 4·ω`, identity. Cesàro mean: `0`. limsup per coordinate (infinite-time machine): all four phases at once. Hyperreal: one phase, depending on `H mod 4`, which "infinite" does not fix. The limit rule is an extra postulate and must be written down. `[OPEN]` which one.
2. `[FORM]` **Exponent law.** Ordinal addition has `1 + ω = ω`. A rotation action needs `R^{1+ω} = R¹·R^ω`, forcing `R¹ = id`. No nontrivial rotation iterates ω times consistently under ordinal addition; commutative systems (surreals, hyperreals) avoid this.
3. `[FORM]` **Parity.** A quarter-turn swaps real and imaginary only for odd counts. Every limit ordinal is even (`ω = 2·ω`), so after ω quarter-turns the reals are real again and `ω+1` makes them imaginary. Under other rules it is undetermined. Which axis is real is a choice of real section; in twistor and loop settings a reality condition fixes it, so rotating it changes the theory.

## Contractive versus inductive nesting

* `[FORM]` If `|λ| < 1`, Hutchinson's theorem gives a unique attractor, a canonical stage ω with no extra postulate. But the map applied to its attractor changes nothing: a metric, contractive nesting stops at ω and never climbs the ordinal ladder.
* Climbing needs a non-contractive inductive operator, whose closure ordinal can be large (the ε₀ route). A strange-loop attractor with a ladder needs nesting that is inductive and carries a metric: a design choice. `[OPEN]`

Physics context and the interior-geometry questions this came from: hyperphysics `docs/research/QUANTUM_GRAVITY_CANDIDATES.md`.
