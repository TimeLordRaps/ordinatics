# Hypermath dependency and grounding evidence

Ordinatics 0.2 depends on the `hypermath-foundations==0.1.0` distribution and
imports its `hypermath_foundations` package. This project is separate from the
unrelated package named `hypermath` on the Python Package Index (PyPI).

The intended target is recursively grounded arithmetic completeness through
Hypermath's self-derivation and fractal meta-representations. The new dependency
makes the foundation's current proof status checkable. It does not supply the
missing source-to-Ordinatics interpretation or prove the completeness target.
The existing numerical and bounded-satisfaction APIs retain their meanings.

## Provision the reviewed source first

The canonical repository, exact Git commit and distribution version are in
[`verification/hypermath.json`](../verification/hypermath.json). Review changes
to this lock together with the dependency's mathematical and package changes.
An exact package version alone does not bind the installed code to a Git commit.

From an isolated environment in the Ordinatics checkout:

```console
python scripts/bootstrap_foundation.py --timeout 120
python -m pip install -e '.[dev,scientific,verification]'
python -m pip check
```

The bootstrap uses standard-library Python and Git before the package build.
It fetches only the locked commit into `.dependencies/hypermath`. A pre-existing
checkout must have the expected repository, exact commit and clean tracked and
untracked inputs. It refuses a different or dirty checkout and never resets it.
Use a separately reviewed destination when preserving another checkout.
Git index flags that hide changes are rejected. Tracked contents are rehashed
against the commit, respecting Git's text conversion rather than relying only
on its cached status.
Every source input in the fresh audit must also belong to the pinned commit;
an ignored, uncommitted proof file cannot enter the evidence unnoticed.

The built wheel's name, version and Python bytes must match the source pin.
Installation uses that local wheel with `--no-index --no-deps`, so the installer
cannot substitute a similarly named registry package. The current foundation
base uses Python's standard library. Installing Ordinatics' extras afterward
supplies scientific libraries and the optional verification dependencies.
An unpublished dependency must be provisioned this way before an ordinary
Ordinatics install; this documentation does not assert a live PyPI release.

For continuous integration (CI), checkout without installing is also available:

```console
python scripts/bootstrap_foundation.py --checkout-only --timeout 120
```

Each external process has the stated timeout. This is not a total wall-clock
limit for the sequence. Output from builds and installations streams normally.

## Run a fresh grounding check

```python
from ordinatics import verify_grounding

result = verify_grounding(
    '.dependencies/hypermath',
    timeout=60,
    receipt_directory='artifacts/grounding',
)
print(result.foundation_status)
print(result.completeness_status)
```

`verify_grounding` checks the source before and after a fresh Hypermath audit.
It also compares the installed `hypermath_foundations` Python files with the
pinned checkout. The self-derivation gate rechecks the report's evidence;
copying a `PASS` string into a report is not a way to pass this interface.
No precomputed report or earlier receipt is accepted as an input.

The result contains:

| Field | Meaning |
| --- | --- |
| `foundation_status` | Status of the dependency's checked `Hypermath.selfDerivation` claim |
| `completeness_status` | `UNKNOWN` until the interpretation bridge and arithmetic completeness theorem are established |
| `pin` | Reviewed repository, full commit and distribution coordinate |
| `report` | Defensive copy of the fresh dependency report, including proof assumptions and incomplete obligations |
| `receipt_path` | Local Python path to the requested receipt, or `None` |
| `to_dict()` | JSON-compatible snapshot; its receipt locator is the basename within the requested receipt directory |

Requesting `receipt_directory` uses the Verifier Standard (VSTD) adapter in
Hypermath. The `verification` extra includes the pinned `verifier-standard`
dependency through Hypermath. The adapter receives the verified foundation root
for a fresh replay using the same audit implementation. The pinned
`audit-replay-2` mechanism compares the complete report, including every check,
claim, admission, runner, toolchain, execution, and source-coordinate field.
Only Lake's `Built`/`Replayed` wording, the scheduling numerator on those build
progress lines, and parallel line ordering are normalized. The total job count,
marker, target, message, line ending, and multiplicity remain bound.
Its receipt binds evidence to named claims; receipt creation does not imply that
every mathematical claim passed. The foundation
and the source-to-library bridge remain separate verification obligations.
A requested replay that fails or contradicts its bound evidence raises an error
after preserving the receipt bundle; the earlier report cannot override it.

All mathematical objects and logical statuses here are dimensionless. Timeout
values are seconds per subprocess; they do not bound big-integer complexity.

## Finite foundation evidence and the remaining bridge

Hypermath's `finite_trace` audit process checks its constructive finite-trace
proofs and concrete probes in `lean4/Hypermath/Trace.lean` and
`lean4/TraceChecks.lean`. Traces carry edge evidence and matching endpoints;
their lengths are computed from the recorded steps. The proofs cover composition
identities and associativity, length addition, and preservation under mappings
that justify every translated edge. Reusable trace expressions contain existing
witnesses, and expansion preserves their edge sequence and derived length.

The foundation's `DEntry x y` supplies a finite apply-trace whose every step
preserves native congruence; `D x y` states that such a witness exists. The
self-read is an explicit zero-step witness with composition identities.
A nonzero closed trace still requires preservation evidence for every
intermediate apply-step. An endpoint-return statement, even at the stronger
simulation relation, leaves that obligation open. The zero-step self-read
alone supplies no positive-length cycle.

The reviewed foundation also defines `finiteApplyFromGround` as the least finite
closure of the existing `ground` under `f2f`. Its Form-valued trace-length
observation uses those same finite iterates and preserves the arithmetic of
composition and reusable-expression expansion. This does not assert that distinct
iteration counts denote distinct Forms, or that native `ordinalApply` agrees
with the observation.

Write `E(n) = f2f^n(ground)`. Addition and multiplication of these finite
numeral representations respect equality unconditionally: if `E(m) = E(n)`
and `E(p) = E(q)`, then `E(m+p) = E(n+q)` and
`E(m * p) = E(n * q)`.
Multiplication here is repeated host-level addition. Equal numeral
representations also act equally on every starting Form in the finite ground
orbit. These results require neither numeral injectivity nor an action on all
Forms.

The witnessed finite orbit has a surjective encoding from natural numbers and
a classically selected decoder. If the explicit `FiniteOrbitInjective`
proposition is supplied, these maps form a two-sided set correspondence and
the numeral representation is compatible with exact iteration on every Form.
The reviewed axioms do not prove that injectivity premise or arithmetic
preservation through the correspondence.

An exact action on every Form satisfying `A(E(n), x) = f2f^n(x)` exists if and
only if equal numeral Forms induce equal iterates on every starting Form:
`E(m) = E(n)` implies `f2f^m(x) = f2f^n(x)` for all `x`. The existence
construction uses classical choice in Lean and is conditional on this
representative-independence compatibility. It does not establish an executable
native action or agreement with `ordinalApply`.

The foundation's six-form countermodel satisfies all 38 current logical
clauses, with Congruent an equivalence relation, but refutes both exact and
congruence-valued uniform finite actions. Ground's first and third numeral
Forms coincide, while one and three applications to a Form on another cycle
give noncongruent results. This leaves finite-orbit addition and multiplication
intact. The model does not encode the stronger, unformalized native intent that
all Forms arise from ground.

The same model shows that the former admitted `ordinalZeroIdentity`,
`ordinalSuccApplies`, and `pathLengthArithmetic` statements do not follow from
the declared clauses. Their exact propositions remain named definitions:
`ordinalZeroIdentityClaim`, `ordinalSuccAppliesClaim`, and
`pathLengthArithmeticClaim`. Their withdrawal from the admitted theorem list
does not prove them. The reviewed foundation retains 16 admissions and
67 declared assumptions: 29 source parameters and 38 logical clauses. Its
fresh audit binds 60 stable inputs and checks 35 individually reviewed proved
milestone declarations.

The reviewed observation layer also checks decoder factorization, uniqueness on
the encoding's image, and preservation through every finite sequence of reuse
operations that respect equality of encoded inputs. The last condition must be
proved for the actual operations. A two-bit example demonstrates how an otherwise
correct base decoder can fail after reuse exposes discarded information.

For the existing native finite numerals, preserving every standard
equality-to-a-numeral query is equivalent to numeral injectivity. The six-form
model identifies `E(1)` and `E(3)` and refutes a decoder for these queries even
though the finite-orbit operation laws hold. This identifies an additional
arithmetic interpretation obligation. The generic observation reports include
22 results without axiom dependencies and two with explicit classical choice
for decoder existence; no executable native decoder follows from that choice.

Under the declared logical clauses, `ordinalLimit` lies outside that finite
closure and cannot be reached from ground through the finite `D` relation.
Universal finite ground-spanning is therefore refuted. The corresponding
admitted theorem was withdrawn; its proposition remains an explicit claim.
This withdrawal is distinct from completing its proof.

The foundation also provides a finite source-syntax record checker in
`lean4/Hypermath/GroundSyntax.lean`. Its free `ground`/`apply` terms retain
formation syntax separately from interpreted `Form` values. It encodes exactly
four primitive source-rule schemata, decodes the record without an external
proof argument, and checks its exact syntactic conclusion. The checked
round-trip and injectivity results preserve every observation of that primitive
instance. `check_sound` proves soundness in every interpretation satisfying the
four rules; `native_check_sound` uses the six existing native parameters, those
four clauses, and Lean's propositional extensionality and quotient equality
principle. It adds no native axiom or admitted proof.

The concrete reuse operation reinstantiates a primitive rule at the next
generated argument. `reuse_many_encode` proves exact record preservation after
any finite number of these steps. Its 23 dependency reports are a separate
group from the 35 production milestones. The composed construction below
extends this primitive fragment. Neither construction represents the checker
internally or derives its own acceptance claims. Lean recursion and inductive
types remain host infrastructure.

The six-form model now also identifies the interpretations of the different
records `diff ground` and `box ground`. No decoder from that semantic value
alone recovers every primitive instance under this encoding. The three new
countermodel results have no axiom dependencies. They constrain this encoding,
not every possible alternative representation.

`GroundDerivation.lean` adds typed finite derivations, predicate closes,
conjunction, and projections. Its raw records retain every premise and
annotation. Acceptance reconstructs the entire typed rule tree, whose quotation
recovers the original record. Soundness is relative to four primitive and
three predicate-close premises; adequacy for native propositions remains open.
This composed group has 26 exact dependency reports.

`GroundCode.lean` and `RecordEncoding.lean` encode those records and formulas
as single free ground terms, with exact recovery and agreement with the composed
checker. The 45-report encoding group checks tagged sorts, malformed records,
premise failures, observations, and reuse. The executable interface uses packed
numbers: a unary ground term can be exponentially larger than its prefix code.
There is no compression theorem or native internal acceptance result here.

The two-chain model in `FullAxiomModel.lean` now interprets those terms
faithfully while satisfying all 38 clauses. Decoding and checking operate on
its model values. The same model has no congruence-preserving path between any
encoded record and encoded formula: their tags differ, and every such path is
empty. This refutes that direct transition in this model, not all possible
native computation mechanisms. Together with the collapsing six-form model,
it distinguishes possible faithful interpretation from faithfulness entailed
by the clauses. It also proves that the source's executive closure and ground
anchoring hold for a record with an invalid projection, even though its
conclusion has a separate valid derivation. A conclusion-only check cannot
certify the exact inference tree. The expanded full-model group has 26 exact
dependency reports, including classical choice where used. No admission
appears in this group.

`RecordMachine.lean` compiles every composed record into explicit instructions
for the seven inference kinds. Execution checks premise formulas and
annotations, visits both conjunction branches, and preserves failure. Its
result agrees with the recursive checker on every record, including invalid
records and every surrounding stack. Trace acceptance requires every recorded
state to match that execution and the final state to establish the supplied
claim. State sequences need not uniquely identify a record; the exact record
and its instructions remain inputs to the check.

The machine group requires 40 exact dependency reports and executable rejection
probes. No report uses an admission, classical choice, or a native Hypermath
axiom. One instruction per record node is a structural count, excluding
decoding, comparisons, construction, and stored-state costs. This is an
explicit host computation; a native simulation and ranked acceptance
derivation are still missing.

The fresh audit requires eleven Lean processes: `lean_build`,
`dependency_output`, `countermodel`, `finite_trace`, `observation`, `full_model`,
`finite_action`, `ground_syntax`, `ground_derivation`, `record_encoding`, and
`record_machine`. The last four require the primitive, composed, encoded-record,
and explicit-machine reports;
`finite_action` checks the six-form countermodel and
its failure witnesses. Observation probes exercise preservation and cases where an endpoint
alone cannot determine the recorded length. Both full-clause models cover the
38 declared logical clauses; their coverage does not extend to stronger prose
descriptions, admitted theorems, or adequacy of the native source language.
The default Lean library imports every module needed by these reporters, and
the current foundation was audited from a checkout with no preexisting build
cache. A regression checks those dependencies. In job names, "native" refers
to running Lean rather than accepting a saved report; it does not assert that
Hypermath's represented rules execute the checker internally.

These checks can pass while self-derivation remains unresolved. The full-clause
countermodel also satisfies the exact proposition currently exported as
`Hypermath.selfDerivation` while refuting the uniform finite action and all
three proposed ordinal computation laws. Thus that target alone cannot supply
the required arithmetic bridge. Native generativity, correspondence with
`ordinalApply`, source adequacy, and recursive arithmetic completeness remain
unestablished (`UNKNOWN`). Native `Form` reification, transfinite paths, and the
interpretation into Ordinatics arithmetic remain separate proof obligations.
These results therefore do not promote the self-derivation, interpretation-bridge,
or completeness claims to `PASS` by themselves.

## Explicit requirements and rejection boundaries

```python
from ordinatics import GroundingNotEstablishedError, verify_grounding

try:
    verify_grounding('.dependencies/hypermath', require_grounding=True)
except GroundingNotEstablishedError as error:
    print(error.result.foundation_status)
```

`require_grounding=True` requires the fresh self-derivation gate to pass.
`require_complete=True` raises while the checked interpretation bridge and
recursive arithmetic completeness proof are absent, including if the foundation
gate eventually passes. Neither option changes `evaluate` or ordinal operations.

`GroundingEvidenceError` rejects missing or malformed reports, source identity
or commit mismatch, dirty inputs, changed inputs during checking, and a runner
whose installed source bytes differ from the pin. Invalid requirements raise
`GroundingError`. Ordinary unresolved proof obligations are reported as their
bounded status and become an exception when the corresponding requirement is
requested. They are not a false arithmetic sentence.

The committed lock and the local Git/Python/Lean executables are trusted inputs.
These checks detect mismatched source and evidence; they are not a sandbox for
a hostile interpreter, monkey-patched functions, or compromised toolchain.
Changing the pin, sources, runner, checker or interpretation invalidates earlier
evidence and requires another audit. Software test passes establish only the
tested implementation boundaries, not source-native arithmetic completeness.
