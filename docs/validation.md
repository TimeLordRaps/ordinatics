# Validation of development version 0.2.0.dev0

These observations were recorded on September 10, 2026. They establish the
listed behavior at the reviewed source state and exact dependency coordinate.
They are not a formal soundness proof, a proof of novelty, evidence of Python
Package Index publication, or evidence that the open completeness target holds.

## Local software checks

The primary local environment used Windows, Python 3.12.8, SymPy 1.14.0,
NumPy 2.5.3, and SciPy 1.18.1.

- `python -m pytest tests -vv -s --durations=10 --timeout=60`: 231 passed in
  18.42 seconds.
- Both examples, Ruff, and `python -m pip check` passed.
- Build and Twine checks passed for the wheel and source distribution.
- Both artifacts retained the exact committed Hypermath pin; the archive
  checker also rejected case-folding, trailing-dot, and Unicode-normalization
  path collisions in its regression tests.
- An isolated environment installed and exercised both project wheels.

## Grounding

The locked Hypermath commit is
[`3614e4adfb8244477dd8e5f2f0b14b515e6a509e`](https://github.com/TimeLordRaps/hypermath/tree/3614e4adfb8244477dd8e5f2f0b14b515e6a509e).
Its fresh audit and replay completed: all seven native processes and the
assumption policy passed. Proof admissibility failed because the current
self-derivation proof still depends on admissions. Self-derivation, source
adequacy, and recursive arithmetic completeness remained `UNKNOWN`.

The reviewed foundation now includes decoder factorization, finite-reuse
preservation, and the equivalence between native numeral injectivity and
preservation of all standard numeral-equality queries. Its six-form model
refutes an equality-query decoder for the current encoding. These checked
results identify requirements for the arithmetic bridge; they do not supply it.

## Paper

`python scripts/build_paper.py --render` completed two LaTeX passes and rendered
14 pages. All pages were visually inspected. The PDF title is exact, all 17
bibliography entries are cited, and no clipping or overlap was observed.

PDF SHA-256: `41FFB4B1A9D095612FD8315CCC823440C0F15978B118CC4D16B37C509A67569F`.

Hosted results must be read from the
[checks workflow](https://github.com/TimeLordRaps/ordinatics/actions/workflows/ci.yml)
at the exact commit. Later source or dependency changes invalidate these observations.
