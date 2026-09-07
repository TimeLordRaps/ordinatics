# Typed bounded satisfaction

The executable fragment uses standard natural-number arithmetic with finite, exclusive quantifier bounds. It is distinct from the paper's full unbounded first-order satisfaction relation.

## Syntax

Terms: `Nat(value)`, `Var(name)`, `Add(left, right)`, and `Mul(left, right)`.

Formulas: `Eq(left, right)`, `Lt(left, right)`, `Not(body)`, `And(left, right)`, `Exists(variable, bound, body)`, `ForAll(variable, bound, body)`, and `Truth(level, sentence)`.

Bounds are terms; for example:

```python
from ordinatics import ForAll, Lt, Nat, Var, evaluate

formula = ForAll("n", Nat(10), Lt(Var("n"), Nat(10)))
assert evaluate(formula)
```

`ForAll("n", Nat(0), body)` is true, and `Exists("n", Nat(0), body)` is false, provided the complete syntax is valid and required free assignments are supplied. Bounds are evaluated in the outer environment. A variable is bound only in the quantifier's body; occurrences in the bound remain free or refer to an outer binder. Names inside quotations cannot be bound by surrounding quantifiers or assignments.

## Language levels

`rank(formula)` returns an exact `Ordinal`. Arithmetic formulas have rank zero. Connectives and quantifiers take the maximum of their constituent ranks. `Truth(beta, sentence)` has rank `beta + 1` and requires a closed sentence whose rank is at most `beta`.

```python
from ordinatics import Eq, Nat, Truth, ZERO, ONE, LanguageMembershipError, evaluate

quote = Truth(ZERO, Eq(Nat(2), Nat(2)))
assert evaluate(quote, stage=ONE)
try:
    evaluate(quote, stage=ZERO)
except LanguageMembershipError:
    pass
else:
    raise AssertionError("a rank-one formula is not in the rank-zero language")
```

With `stage=None`, evaluation uses the formula's least valid stage. An explicit stage must be an `Ordinal`. This implementation quotes actual immutable syntax trees, not strings or numerical sentence codes. Invalid quotations raise errors before evaluation. The paper's convention that malformed numerical codes are absent from a truth set is not an instruction to reinterpret malformed Python objects as false.

## Assignments and limits

```python
from ordinatics import Add, Eq, Nat, Var, evaluate

formula = Eq(Add(Var("n"), Nat(1)), Nat(3))
assert evaluate(formula, {"n": 2})
```

Natural constants and assignments accept exact nonnegative integer inputs, including NumPy integer scalars and SymPy integers. They normalize to Python `int`, preventing fixed-width overflow. Booleans and floats are rejected.

`evaluate(formula, assignment=None, *, stage=None, max_steps=10000)` shares a work-step budget between syntax validation and evaluation. Every quantifier iteration is charged. Deep valid syntax is evaluated using explicit stacks. The budget is a work-step count, not a wall-clock, memory, or big-integer bit-complexity guarantee. Large integer operands and large ordinal coefficient arrays can still be expensive. The library is not a sandbox for hostile Python objects.

Errors are explicit:

| Exception | Meaning |
|---|---|
| `MalformedSyntaxError` | Unsupported, wrongly typed, cyclic, or malformed syntax; invalid natural-number input |
| `LanguageMembershipError` | A quotation or formula exceeds its permitted stage |
| `FreeVariableError` | A quoted sentence is open or evaluation lacks an assignment |
| `EvaluationLimitError` | The work budget was exhausted; no truth value was established |

All inherit `OrdinaticsSemanticsError`. An error is not a false sentence. The evaluator does not implement unbounded quantification, a universal self-truth predicate, a proof search engine, or construction of an infinite truth hierarchy.
