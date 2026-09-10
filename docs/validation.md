# Validation of development version 0.2.0.dev0

These observations were recorded on September 10, 2026. They establish the
listed behavior at the reviewed source state and exact dependency coordinate.
They are not a formal soundness proof, a proof of novelty, evidence of Python
Package Index publication, or evidence that the open completeness target holds.

## Local software checks

The primary local environment used Windows, Python 3.12.8, SymPy 1.14.0,
NumPy 2.5.3, and SciPy 1.18.1.

- `python -m pytest tests -vv -s --durations=10 --timeout=60`: 231 passed in
  272.07 seconds.
- Both examples, Ruff, and `python -m pip check` passed.
- Build and Twine checks passed for the wheel and source distribution.
- Both artifacts retained the exact committed Hypermath pin; the archive
  checker also rejected case-folding, trailing-dot, and Unicode-normalization
  path collisions in its regression tests.
- An isolated environment installed and exercised both project wheels.

## Grounding

The locked Hypermath commit is
[`6b050fc292ca2e9fc3169dce70388e3b79431bea`](https://github.com/TimeLordRaps/hypermath/tree/6b050fc292ca2e9fc3169dce70388e3b79431bea).
Its audit completed and preserved `UNKNOWN` for self-derivation, source adequacy,
and recursive arithmetic completeness. The strict gate returned nonzero and
reported that the arithmetic bridge or completeness proof is missing, as intended.

## Paper

`python scripts/build_paper.py --render` completed two LaTeX passes and rendered
13 pages. All pages were visually inspected. The PDF title is exact, all 17
bibliography entries are cited, and no clipping or overlap was observed.

PDF SHA-256: `1A1B25489CF3352E1FFD6510193CD76171B6A5BCD87E1CE7CC14E7D7C94A7D36`.

Hosted results must be read from the
[checks workflow](https://github.com/TimeLordRaps/ordinatics/actions/workflows/ci.yml)
at the exact commit. Later source or dependency changes invalidate these observations.
