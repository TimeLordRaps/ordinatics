# Mutation record for the claims suites

`semantics.py` and `algebra.py` were both audited and no defect was found in
either. That leaves a problem of evidence: a suite written against correct code
passes whether or not it is testing anything, and a negative control is
unavailable, because there is no unfixed source to run against.

Mutation testing is the substitute. Inject a plausible defect, run the suite,
and require it to fail. A mutation that survives is a gap in the tests — not a
property of the code.

The harnesses are `scratchpad/mutate_semantics.py` and
`scratchpad/mutate_algebra.py`. Each mutation is a single textual substitution
whose anchor is required to match exactly once, applied to the module under
test, with the original restored in a `finally` block. Rerun them after changing
either a module or its suite.

## `semantics.py` result

**13 of 13 killing mutations are caught. 1 equivalent mutant survives, as predicted.**

| # | Mutation | Outcome |
|---|---|---|
| 1 | evaluation is not charged to the budget at all | caught |
| 2 | a quotation has the rank of its level, not level + 1 | caught |
| 3 | stratification is not enforced | caught |
| 4 | quotations need not be closed | caught |
| 5 | a quantifier also binds its variable in the bound term | caught |
| 6 | an exhausted `Exists` reports `True` instead of `False` | caught |
| 7 | `And` does not short-circuit correctly | caught |
| 8 | `Lt` is evaluated as `<=` | caught |
| 9 | `Add` is evaluated as multiplication | caught |
| 10 | cyclic syntax is not detected | caught |
| 11 | booleans pass as naturals | caught |
| 12 | the budget allows one step past exhaustion | caught |
| 13 | an explicit stage below the rank is accepted | caught |
| E1 | a quotation is evaluated in the surrounding environment | **equivalent — must survive** |

### The three that did not pass on the first run

The first run of this harness reported three survivors. Two were faults in the
harness rather than gaps in the suite, and one was a real gap. Recording which
is which is the point of this file: **a survivor list is not a finding until
each entry has been diagnosed.** The same thing happened on the algebra side,
with a different cause, and is recorded there.

### 12 — the budget allows one step past exhaustion: a real gap, now closed

`_Budget.take` guards with `if self.remaining == 0`. Mutating it to
`if self.remaining < 0` lets exactly one extra step through, and every test in
the suite passed. They all chose budgets far away from the boundary — large
enough to succeed or small enough to fail obviously — so none of them could see
a one-step shift.

Closed by `test_the_budget_boundary_is_exact`, which counts the ten steps of
`Eq(Nat(0), Nat(0))` by hand and asserts refusal at nine, and by
`test_one_step_below_the_minimum_always_refuses`, which binary-searches the
least viable budget for six formula shapes and requires `least - 1` to raise.
The second form needs no hand count, so it extends to shapes whose step count is
not worth deriving.

This is the mutation that justifies the whole exercise. It is a genuine
off-by-one that 96 passing tests did not constrain, and nothing but a boundary
test would have found it.

### 1 — quantifier iterations are not charged: the mutation was too weak

The original mutation skipped `budget.take()` only for `quantifier_next`
instructions. Each iteration of a quantifier also pushes a `quantifier_result`
and an `eval` of the body, and both were still charged, so the budget continued
to bound iterations and the suite was right not to fail.

A mutation that does not actually implement the defect it is named after tests
nothing. Replaced with the faithful version — remove the charge from the
evaluation loop entirely, which is what "the budget bounds syntax and not
iterations" would mean — and it is caught.

### E1 — a quotation is evaluated in the surrounding environment: equivalent

Changing `pending.append(("eval", node.sentence, {}))` to pass `env` instead of
`{}` survives, and no test can kill it.

`_analyze` refuses any `Truth` whose sentence has free variables. So every `Var`
inside a quotation is bound by a quantifier inside that quotation, and each such
quantifier builds a fresh child environment that rebinds the name. Nothing
inside a quotation ever reads the environment it was handed. The two versions
agree on every input the evaluator accepts.

It is listed separately and asserted to survive. A suite that killed this mutant
would be distinguishing two programs that cannot be distinguished, which would
mean the test was asserting something other than what it claimed.


## `algebra.py` result

**14 of 14 mutations are caught.** No survivors and no equivalent mutants.

| # | Mutation | Outcome |
|---|---|---|
| 1 | `specialize` substitutes before cancelling | caught |
| 2 | `rational_function` does not cancel common factors | caught |
| 3 | `wrap` specializes at +1/2 | caught |
| 4 | the chosen logarithm has the wrong sign | caught |
| 5 | the chosen logarithm drops its imaginary part | caught |
| 6 | `complex_period` is off by a factor of two | caught |
| 7 | bools are accepted as numbers | caught (see below) |
| 8 | strings are parsed after all | caught (see below) |
| 9 | floats are accepted as exact | caught |
| 10 | infinity and NaN pass the exactness gate | caught |
| 11 | matrices count as scalars | caught |
| 12 | foreign symbols are allowed through | caught |
| 13 | an irrational point is accepted by `_rational` | caught |
| 14 | a noncommutative symbol is accepted as the variable | caught |

### 7 and 8 — the guards are layered, and the first run could not see it

Both survived the first run, and neither was an equivalent mutant.

Deleting the early `isinstance(value, (str, bytes, bytearray, bool))` check does
not let a string or a bool through. `sp.sympify(value, strict=True)` refuses
every string on its own — including `"3"`, which has an obvious numeric reading
— and `sp.sympify(True, strict=True)` returns a `BooleanTrue`, which fails the
`isinstance(result, sp.Expr)` check on the next line. Two independent layers,
each sufficient.

The suite asserted only that `TypeError` was raised, which both layers do, so it
could not distinguish them. Closed by
`test_the_text_and_bool_guards_are_a_distinct_layer_from_strict_sympify`, which
pins the early guard's message, exercises `strict=True` directly so that
removing *either* layer fails a test, and records that plain `sympify` really
would parse `"X + 1"` — so `strict=True` is load-bearing rather than decorative.

Pinning an error message is brittle on purpose here. The claim being tested is
which defence exists, and the message is the only observable that separates the
two.

### A dead branch, found while writing the tests

`rational_function` raises `"expr has an identically zero denominator"`. That
line is unreachable through the public entry point: SymPy collapses `X/(X - X)`,
`1/0` and similar to `zoo` at construction time, and `_exact_expr`'s infinity
check rejects them first. The refusal is correct either way, so this is defence
in depth and not a defect — but no test asserts that message, because asserting
it would mean asserting something that never happens.
