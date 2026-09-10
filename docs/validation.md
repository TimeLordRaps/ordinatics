# Validation of development version 0.2.0.dev0

These observations were recorded on September 10, 2026. They establish the
listed behavior at the reviewed source state and exact dependency coordinate.
They are not a formal soundness proof, a proof of novelty, evidence of Python
Package Index publication, or evidence that the open completeness target holds.

## Local software checks

The primary local environment used Windows, Python 3.12.8, SymPy 1.14.0,
NumPy 2.5.3, and SciPy 1.18.1.

- `python -m pytest tests -vv -s --durations=10 --timeout=60`: 237 passed in
  21.05 seconds with the updated foundation installed.
- Both examples, Ruff, and `python -m pip check` passed.
- Build and Twine checks passed for the wheel and source distribution.
- Both artifacts retained the exact committed Hypermath pin; the archive
  checker also rejected case-folding, trailing-dot, and Unicode-normalization
  path collisions in its regression tests.
- An isolated environment installed and exercised both project wheels.

## Grounding

The locked Hypermath commit is
[`4352a54d8198afc745c048a211ae4681f57d2799`](https://github.com/TimeLordRaps/hypermath/tree/4352a54d8198afc745c048a211ae4681f57d2799).
Its fresh audit and replay completed: all eight native processes and the
assumption policy passed. Proof admissibility failed because the current
self-derivation proof still depends on admissions. Self-derivation, source
adequacy, and recursive arithmetic completeness remained `UNKNOWN`.

The reviewed foundation now includes decoder factorization, finite-reuse
preservation, and the equivalence between native numeral injectivity and
preservation of all standard numeral-equality queries. Its six-form model
refutes an equality-query decoder for the current encoding. These checked
results identify requirements for the arithmetic bridge; they do not supply it.

The new `ground_syntax` process checks 23 dependency reports for the primitive
record checker, round-trip decoding, soundness relative to four source rules,
and finite rule-reinstantiation. Three additional countermodel results show
that interpreted semantic values need not retain these records. The audit
binds 53 stable inputs and retains 67 source assumptions and 16 admission sites.
This source-syntax fragment does not construct ranked acceptance derivations
or an arithmetic interpretation.

The integrity commands now reject an absent, unattempted, or non-passing
assumption-policy result even when all native processes finish. The foundation
also preserves the two new checker-source files as line-feed bytes on Windows.
Regression tests reproduce both failure modes. Matching replay alone can
reproduce a policy failure; it must not be treated as an integrity pass.

## Paper

`python scripts/build_paper.py --render` completed two LaTeX passes and rendered
15 pages. All pages were visually inspected. The PDF title is exact, all 17
bibliography entries are cited, and no clipping or overlap was observed.
Proposition 6.7 gives the primitive-record result with its proof and semantic
interpretation boundary; the conditional coverage result remains Theorem 6.6.

PDF SHA-256: `E4F7CD5B75B7C41DC55890AEBC3F1D6D2BB3B6A10D7E0115B71EB9BB017FAAC3`.

Hosted results must be read from the
[checks workflow](https://github.com/TimeLordRaps/ordinatics/actions/workflows/ci.yml)
at the exact commit. Later source or dependency changes invalidate these observations.
