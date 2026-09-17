# Ordinatics governance

## Current phase

Ordinatics is founder-maintained alpha project work. Publication makes the mathematical
formalization, LaTeX manuscript, and reference Python implementation inspectable.

The mathematical scope is strictly bounded: concrete `Ordinal` objects represent ordinals
strictly below `omega**omega`. The semantic evaluator implements an explicit finite
step-budget algorithm over closed bounded syntax trees; it does not decide arbitrary
first-order arithmetic truth or construct infinite truth sets.

## Decision rights

Tyler Roost (@TimeLordRaps) is the author, editor, and release maintainer. Pull requests
are welcome. Normative changes require maintainer review.

The repository's Apache License 2.0 governs the code, documentation, and manuscript sources.
Its contributor patent grant is a project license term.

## Change process

1. Open an issue stating the mathematical domain or implementation coordinate being changed.
2. Declare compatibility impact, domain bounds, and falsification conditions.
3. Enforce zero required runtime dependencies on base import paths.
4. Add tests that fail before and pass after the change.
5. Ensure all CI conformance gates pass (multi-platform matrices, release integrity, stdlib smoke, presentation gate).
6. Obtain maintainer review before merging normative changes.
