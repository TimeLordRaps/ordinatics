# Validation of the cycle-correction integration

Recorded September 10, 2026 for Ordinatics development version `0.2.0.dev0`,
with exact Hypermath pin
[`b35b795c13390e5e10430238e033955ca5053847`](https://github.com/TimeLordRaps/hypermath/tree/b35b795c13390e5e10430238e033955ca5053847).
This record supersedes the older validation snapshot for the current review;
it does not rewrite that snapshot's outcomes. A different dependency pin,
source change, or altered audit mechanism requires fresh evidence.

## Mathematical change

The full two-chain model refutes the proposed two-step simulation cycle,
nontrivial simulation pair, and original self-derivation target while
satisfying all 38 clauses. The six-form model satisfies those clauses and
the target without the required arithmetic bridges. Conditional assembly
isolates the remaining cycle obligation. The foundation preserves the exact
target as an unproved proposition, rather than exporting an admitted proof.

There are 67 declared assumptions, comprising 29 parameters and 38 clauses,
and 11 remaining admission sites. Five sites were withdrawn after
counterexamples; their removal is not proof completion. The production audit
binds 38 milestones, and the full-model group binds 30 dependency reports.
No native axiom was introduced to assume the cycle or record acceptance.

## Reproduced local checks

The environment was Windows with Python 3.12.8, SymPy 1.14.0, NumPy 2.5.3,
and SciPy 1.18.1. The bootstrap built and installed the exact pinned
`hypermath-foundations==0.1.0` wheel and checked its Python bytes.

- `python -m pytest tests -vv -s --durations=10 --timeout=60`: all 237 tests
  passed in 35.59 seconds. The retained report is
  `build/cycle-integration-tests.xml`.
- Both examples, Ruff, and `python -m pip check` passed.
- Source and wheel builds, Twine metadata validation, and packaged-pin checks
  passed. Both distributions retain the exact new foundation pin.
- An isolated environment installed and exercised both project wheels.

The tests exercise software contracts. They do not establish a native
arithmetic interpretation, source adequacy, or arithmetic completeness.

## Fresh grounding and replay

All eleven Lean processes and the exact assumption policy passed against the
clean pinned foundation, with all 60 inputs stable. The report identifies
`Hypermath.selfDerivation` as a `def`: its body is the named proposition, not
evidence of its truth. Proof admissibility is `FAIL`; self-derivation, source
adequacy, and recursive arithmetic completeness remain `UNKNOWN`.

Fresh Verifier Standard (VSTD) replay through `audit-replay-2` returned
`audit_replay_matches=PASS`. The underlying audit's Secure Hash Algorithm
256-bit (SHA-256) digest is
`6ac24119e6033eae936b54a111cbd321ca9a2f57899b3feac8bb971b82b93fc7`.
Evidence is retained in `build/verification-cycle-integration/`.

The strict command with `--require-self-derivation --require-complete`
returned 2 for the missing arithmetic bridge or completeness proof. Integrity
and replay passes are separate from that failed mathematical gate. The
research and release obligations were not replaced with a weaker target.

## Manuscript

`python scripts/build_paper.py --render` completed two LaTeX passes and
produced the 19-page paper and Markdown reading copy. Every rendered page was
inspected, including the new proposition and proof at full page size. The
approved title is unchanged and all 17 bibliography entries are cited.
No clipping, overlap, undefined references, or overfull text was found.

Proposition 6.13 presents the cycle equivalence and both model interpretations.
The abstract and source citation reflect the corrected foundation. The
earlier finite representation, execution, and conditional coverage results
retain their scopes. The paper does not claim the native completeness target
has been achieved.

PDF SHA-256:
`2edec7761c6566df8f13acdffef1288b200261b306a1741ee1b18de0358639d6`.

These are local validation observations. Hosted checks belong to their exact
review commit; neither this record nor the remaining open review establishes
a merge, Python Package Index release, or Zenodo publication.
