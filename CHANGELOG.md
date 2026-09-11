# Changelog

## 0.2.0.dev0 — unreleased

- Required `hypermath-foundations` dependency built from a reviewed Git commit.
- Advanced the exact foundation pin to `b35b795c13390e5e10430238e033955ca5053847`.
  Eleven mandatory Lean processes now include primitive records, composed
  derivations with complete rule-tree recovery, and single-term record encodings.
  One model of all 38 clauses retains the encoded records faithfully, but its
  congruence-preserving paths cannot implement a direct record-to-formula
  transition. The checker remains a host function; native ranked acceptance
  and full arithmetic coverage remain open. Paper Propositions 6.8–6.12 give
  these bounded results and their proofs, including a closed but invalid
  record and an explicit instruction machine with exact trace acceptance.
  The machine has 40 exact reports and adds no native axioms or admissions.
  Fresh builds include every reporter dependency without relying on cached
  compiled modules.
- Integrated the full-clause cycle counterexample and unchanged self-derivation
  target as an unproved proposition. Conditional assembly isolates the missing
  cycle; a closed theorem is still required by the proof gate. Proposition 6.13
  presents the equivalence and the two models. Removing five admitted proof
  sites records unsupported claims, not five proved results.
- Checked observation-factorization and finite-reuse preservation results from
  Hypermath. Preserving all standard numeral-equality queries requires injective
  native numeral representation; the existing countermodel refutes a decoder
  for those queries. These results do not discharge the arithmetic bridge.
- Fresh source-bound grounding checks and Verifier Standard evidence integration.
- Grounding integrity now rejects failed, missing, or unattempted assumption
  policy checks even when native execution completes and replay agrees. The
  foundation also preserves its primitive Lean checker bytes in fresh Windows
  checkouts. Mathematical `UNKNOWN` outcomes remain distinct from these errors.
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
  reviewed foundation retains 11 admissions and 67 declared assumptions; its
  fresh audit binds 60 stable inputs and checks 38 proved milestone declarations,
  plus separate groups of 23 primitive, 26 composed-calculus, 45 encoded-record,
  30 full-model, and 40 record-machine dependency reports. Exact dependency
  checks retain classical choice where used; none of these five groups uses
  an admission.
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
