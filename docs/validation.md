# Validation of development version 0.2.0.dev0

These observations were recorded on September 10, 2026. They establish the
listed behavior at the reviewed source state and exact dependency coordinate.
They are not a formal soundness proof, a proof of novelty, evidence of Python
Package Index publication, or evidence that the open completeness target holds.

## Local software checks

The primary local environment used Windows, Python 3.12.8, SymPy 1.14.0,
NumPy 2.5.3, and SciPy 1.18.1.

- `python -m pytest tests -vv -s --durations=10 --timeout=60`: 237 passed in
  21.12 seconds with the updated foundation installed.
- Both examples, Ruff, and `python -m pip check` passed.
- Build and Twine checks passed for the wheel and source distribution.
- Both artifacts retained the exact committed Hypermath pin; the archive
  checker also rejected case-folding, trailing-dot, and Unicode-normalization
  path collisions in its regression tests.
- An isolated environment installed and exercised both project wheels.

## Grounding

The locked Hypermath commit is
[`34c9c99345bb3cdeac7be9a67713d9aa0c99d6da`](https://github.com/TimeLordRaps/hypermath/tree/34c9c99345bb3cdeac7be9a67713d9aa0c99d6da).
Its fresh audit and replay completed: all ten native processes and the
assumption policy passed. Proof admissibility failed because the current
self-derivation proof still depends on admissions. Self-derivation, source
adequacy, and recursive arithmetic completeness remained `UNKNOWN`.

The reviewed foundation now includes decoder factorization, finite-reuse
preservation, and the equivalence between native numeral injectivity and
preservation of all standard numeral-equality queries. Its six-form model
refutes an equality-query decoder for the current encoding. These checked
results identify requirements for the arithmetic bridge; they do not supply it.

The `ground_syntax` process checks 23 dependency reports for the primitive
record checker, round-trip decoding, soundness relative to four source rules,
and finite rule-reinstantiation. Three additional countermodel results show
that interpreted semantic values need not retain these records. The audit
binds 58 stable inputs and retains 67 source assumptions and 16 admission sites.
The `ground_derivation` process checks 26 reports for composed derivations,
full rule-tree reconstruction, and relative soundness. The `record_encoding`
process checks 45 reports for single-term encodings, exact recovery, checker
agreement, malformed inputs, and representation cost.

The `full_model` process now checks 20 exact reports, including a faithful
interpretation of those records in one model of all 38 clauses. Its preserving
paths cannot carry encoded records directly to encoded formulas. This is a
boundary on that specific transition, not all native computation. Model
checking remains a host operation. The native ranked acceptance construction,
source adequacy, and arithmetic interpretation remain open.

The integrity commands now reject an absent, unattempted, or non-passing
assumption-policy result even when all native processes finish. The foundation
also preserves the two new checker-source files as line-feed bytes on Windows.
Regression tests reproduce both failure modes. Matching replay alone can
reproduce a policy failure; it must not be treated as an integrity pass.

## Paper

`python scripts/build_paper.py --render` completed two LaTeX passes and rendered
16 pages. All pages were visually inspected. The PDF title is exact, all 17
bibliography entries are cited, and no clipping or overlap was observed.
Proposition 6.7 gives the primitive-record result. Propositions 6.8–6.10 add
composed reconstruction, ground-term encoding with explicit cost, and the
faithful model with its operational boundary. The conditional coverage result
remains Theorem 6.6; its hypotheses have not been discharged.

PDF SHA-256: `190F24063EE9B0654FABDDA1316EFABBE59B48FDC291348F241C77981EBD8F26`.

Hosted results must be read from the
[checks workflow](https://github.com/TimeLordRaps/ordinatics/actions/workflows/ci.yml)
at the exact commit. Later source or dependency changes invalidate these observations.
