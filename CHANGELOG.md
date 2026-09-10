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
- Required observation and full-model audit processes. The model covers the
  declared logical clauses, without establishing stronger prose descriptions
  or source-language adequacy.
- Separate software and mathematical CI gates, installed-wheel checks, and
  publication dependent on the complete checks workflow.
- The arithmetic interpretation and recursively grounded completeness proof
  remain unestablished; the existing numerical and bounded semantic APIs retain
  their documented scope.

## 0.1.0

Initial experimental release:

- Exact ordinary and natural ordinal operations below `omega**omega`.
- Explicit conversion between ordinal coefficient representations and SymPy polynomials.
- Rational-function normalization, exact specialization, wrap, and a coherent rational-power image.
- Typed finite formula trees, ordinal language ranks, and bounded satisfaction with explicit errors and execution budgets.
- NumPy, SciPy, and SymPy examples.
- The associated mathematical paper and its editable source.
