# Changelog

## 0.2.0.dev0 — unreleased

- Required `hypermath-foundations` dependency built from a reviewed Git commit.
- Fresh source-bound grounding checks and Verifier Standard evidence integration.
- Finite-trace proof evidence for witnessed composition, structural length, and
  reusable expression expansion; endpoint return still requires separate
  intermediate-step preservation evidence to establish a nonzero closed trace.
- Native finite-closure and Form-valued trace-length evidence, including
  composition and reuse preservation. The ordinal limit refutes universal
  finite ground-spanning; its admitted theorem is withdrawn, not proved.
- Finite-orbit numeral addition and multiplication respect representation
  equality without an injectivity assumption. Under explicit numeral
  injectivity, encode/decode gives a set correspondence with natural numbers
  and equal numeral Forms act identically on every starting Form. An exact action
  exists precisely when that global action compatibility holds; its construction
  uses classical choice.
- Required `finite_action` as the seventh native audit process, alongside the
  observation and full-model checks. Its six-form model satisfies all 38 current
  logical clauses with Congruent an equivalence relation, yet refutes exact and
  congruence-valued uniform finite actions. The same model satisfies the current
  self-derivation target while the tested arithmetic bridges fail. It does not
  encode the stronger unformalized native generativity intent.
- The model also refutes entailment of the former admitted ordinal zero,
  successor, and path-length computation claims. Their exact propositions remain
  named `Claim` definitions; their withdrawal is not proof completion. The
  reviewed foundation retains 16 admissions and 67 declared assumptions; its
  fresh audit binds 51 stable inputs and checks 34 proved milestone declarations.
- Separate software and mathematical CI gates, installed-wheel checks, and
  publication dependent on the complete checks workflow.
- Wheel and source-distribution qualification now require the exact committed
  Hypermath pin bytes and reject ambiguous, unsafe, linking, oversized, or
  cross-platform-colliding archive paths.
- Paper CI compiles the LaTeX source, regenerates the Markdown reading copy,
  renders every PDF page, rejects Markdown drift, and retains review artifacts.
- A passable grounding-integrity job now checks complete native execution and
  the versioned `audit-replay-2` report comparison independently of the strict
  self-derivation and completeness gate. Both evidence bundles are retained for
  90 days.
- Native generativity, `ordinalApply` correspondence, source adequacy, and
  recursively grounded arithmetic completeness remain `UNKNOWN`; the existing
  numerical and bounded semantic APIs retain their documented scope.

## 0.1.0

Initial experimental release:

- Exact ordinary and natural ordinal operations below `omega**omega`.
- Explicit conversion between ordinal coefficient representations and SymPy polynomials.
- Rational-function normalization, exact specialization, wrap, and a coherent rational-power image.
- Typed finite formula trees, ordinal language ranks, and bounded satisfaction with explicit errors and execution budgets.
- NumPy, SciPy, and SymPy examples.
- The associated mathematical paper and its editable source.
