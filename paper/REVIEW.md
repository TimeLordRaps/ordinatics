# Manuscript review, September 7, 2026

> **Coordinates superseded.** The digests in this review identify local
> corrections on commit `1bdeb75`, not the files beside it today. The
> findings and corrections below are live and were verified present in the
> current manuscript; only the coordinates went stale. **Section 8 of the
> current manuscript is unreviewed.** See the re-dating addendum at the end
> of this file for current digests and coverage.

This records an assisted mathematical and implementation review of **Ordinal
Arithmetic: An Ordinal-First Metalanguage Approach to Definable Arithmetic Truth**,
by Tyler Roost. It is not external peer review or a proof-assistant certificate.

## Reviewed coordinate

- Repository: `https://github.com/TimeLordRaps/ordinatics`
- Workspace coordinate: branch `main`
- Base commit: `1bdeb7593bc043c949ba9ec3912ae148608b967d`
- Revision: local manuscript corrections on that commit, labeled preprint version
  1.0, September 7, 2026. That document label does not establish publication.
- Source: `paper/ordinal_arithmetic.tex`
- Source Secure Hash Algorithm 256-bit (SHA-256) digest, over actual file bytes:
  `fbbf5ff7dacfc52391b5b5e8700ef6431f834e6b15142cf8b1a55cf74bf0ecce`
- Source SHA-256 after normalizing line endings to line feeds and encoding as UTF-8:
  `17bfda9fde35c22e0eabad08fd237008e6e8bf144228543fe03746ea70f0218f`
- PDF SHA-256:
  `95d28aa95d901b82f2240c390c002750264523dab55444fad4ca1b0a4a01eb53`

The digests identify this reviewed revision; they do not prove its theorems.

## Finding

No counterexample or unresolved contradiction was found in the reviewed
arguments after the corrections below. Three separately tasked assistant
reviewers examined ordinal semantics, algebra/branches, and correspondence with
the Python implementation. The ordinal and algebra reviewers rechecked the
affected statements after correction. These are bounded internal checks, not
independent human mathematical validation.

The supportable contribution is an explicit reconstruction and dependency
analysis. Finite ordinals interpret arithmetic, a partial rational-function
specialization supplies the value layer, and an externally defined hierarchy
organizes truth predicates for earlier languages. The satisfaction construction
assumes Zermelo-Fraenkel set theory with the Axiom of Choice. It does not derive
arithmetic truth from the ordinal-arithmetic structure alone, establish that the
wrap anchor is necessary, evade Tarski's undefinability theorem, or derive the
source notes' ground-and-term-former axioms.

## Corrections incorporated

| Location | Issue | Correction |
| --- | --- | --- |
| Section 1 | The title could suggest definability in ordinal arithmetic alone. | State that ordinal-first refers to the domain and dependency order; the ambient metalanguage is explicitly set theory. |
| Theorem 3.1 | The inverse criterion quantified over zero while writing an undefined inverse. | State the criterion in terms of being a unit of the localization. |
| Section 3.1 | An unspecified branch restriction blurred a set bijection and an analytic inverse. | Give a half-open strip for the set bijection and a slit codomain for an analytic logarithm branch. |
| Section 5 | The coding assumptions were too abbreviated for the diagonalization argument. | Require injective effective coding, canonical ordinal indices, computable parsing, numeral formation, and capture-avoiding substitution. |
| Section 5.1 | Formula membership was written as membership in a vocabulary. | State membership in the language's formulas, restricted to well-formed formulas. |
| Section 6 | The successor discussion did not explicitly exclude the terminal stage. | Restrict it to stages below the chosen bound. |
| Section 7 | Normalization and pole detection were described collectively. | Distinguish rational-function normalization from specialization and wrap evaluation. |
| Section 7 | Node construction and validation were conflated. | State that rank and evaluation validate closed quotation and stage membership. |
| Section 7 | The computational role of transfinite labels was implicit. | Explain direct evaluation of closed quoted trees, without constructing prior transfinite truth sets. |
| Section 7 | Bounded-quantifier scope needed precision. | State that the bound uses the outer assignment and the binder applies only to the body. |

Added references to the Stacks Project localization chapter and the National
Institute of Standards and Technology logarithm/branch reference. The approved
title and the framework name Ordinatics remain unchanged. The build script now
retains the manuscript's date and version in the Markdown reading copy.

## Mathematical checks and limits

- Absorption obstructs the stated unital additive map by cancellation, without
  assuming injectivity.
- Ordinals below the selected bound are closed under the stated finite ordinary
  operations. Their finite part interprets standard arithmetic.
- The localization's evaluation map, kernel, unit criterion, and obstruction to
  extending it to the whole rational-function field have the stated proofs.
- The polynomial representation preserves the natural operations, not ordinary
  ordinal addition and multiplication.
- A fixed logarithm value gives the stated multiplicative rational-power map;
  incompatible choices of roots do not. The complex exponential has the stated
  period lattice.
- Satisfaction for each set-sized structure supplies a definable recursion step
  in the assumed metatheory. Recursion through the terminal stage and uniqueness
  are justified within that metatheory.
- Reduct compatibility preserves earlier satisfaction. Finite predicate support
  justifies the union of truth sets at nonzero limit stages.
- Effective syntax supports the diagonal argument, including the terminal
  language. The countable predicate vocabulary does not supply self-truth.
- The Python evaluator handles bounded finite trees. Its ordinal labels enforce
  typing; they do not implement the full mathematical hierarchy.

These checks do not establish a novel theorem, minimal metatheoretic strength,
conservativity of an unspecified proof system, a soundness theorem for a future
certificate checker, or correctness of every execution of the Python library.

## Validation evidence

- `python -u scripts/build_paper.py --render`: completed two bounded LaTeX passes,
  regenerated the Markdown copy, and rendered all nine pages. The build reported
  no overfull boxes, unresolved references, missing-character errors, or LaTeX
  warnings selected by its checks.
- Visual inspection of all nine rendered pages found no clipping, overlap, or
  broken equations in this revision.
- `ruff check scripts/build_paper.py`: passed.
- `git diff --check`: passed after the manuscript corrections.
- Seven unique bibliography keys; every manuscript citation key resolves.
- PDF title, author, page count, and preprint label were checked after reopening;
  the Markdown copy includes the same date/version label.
- The implementation reviewer reproduced the manuscript example, finite and
  transfinite stage labels, normalization versus pole rejection, open-quotation
  rejection, and budget exhaustion against version 0.1.0.
- A full library test suite was not rerun for these manuscript-only corrections.
  No library implementation was changed by this review. Earlier software checks
  are separate evidence and are not proof of the mathematical results.

Reference metadata and mechanisms were checked against the publisher records for
Tarski and Feferman, the author-hosted Halbeisen chapter and Beeson slides, the
[Stacks Project localization section](https://stacks.math.columbia.edu/tag/00CM),
and the [official logarithm/branch reference](https://dlmf.nist.gov/4.2).
The unpublished notes are cited as motivation; their broader claims are not
certified by this review.

## Publication state at review close

This corrected revision remains local. No new commit, push, release, Zenodo
deposit, or Digital Object Identifier (DOI) was created during this review. The
existing software release's attached manuscript is the earlier revision.
Formal release remains a separate next action; external peer review and a
broader novelty assessment remain outstanding.

---

## Re-dating addendum, September 20, 2026

The review above is preserved unchanged as a dated record of what was checked on
September 7, 2026. This addendum exists because its digests no longer identify
the files beside it, and a digest-bearing review that does not match the current
bytes is worse than no review: it invites a reader to believe the current bytes
were checked.

### What the September 7 digests actually referred to

They referred to **local, uncommitted corrections** sitting on base commit
`1bdeb7593bc043c949ba9ec3912ae148608b967d`. The review says so in its own
coordinate block, and its closing section records that the corrected revision
remained local. Those corrections were later committed in `af92dbb`, together
with new material the review never saw.

This was confirmed rather than assumed. Diffing `1bdeb75` against the current
manuscript shows every correction in the "Corrections incorporated" table
present in the current bytes: the injective effective coding requirement, the
unit-of-the-localization form of the inverse criterion, the quotient-by-the-lattice
statement for the complex exponential, the restriction of the successor
discussion to stages below the bound, and the rest. **The review's findings and
corrections are live.** Only its coordinates went stale.

### Current coordinates

- Source: `paper/ordinal_arithmetic.tex`
- Source SHA-256, over actual file bytes:
  `1e7af9a1266ffd928e13e0ed9e5f621811ee546dd60c05204fdab8e21af73afb`
- Source SHA-256 after normalizing line endings to line feeds:
  `a007b794e6577cfd84a68005941da7649b936f17833cfc37a4b982c6a9a8e726`
- PDF SHA-256:
  `f1ad110ff530e6c26e202d9b06859e35125db3af6332426fd38f1bb07ddb3e25`
- Manuscript label: Preprint, version 0.3.0, September 18, 2026. Twelve pages.

### The PDF digest is only now meaningful

At the time of the September 7 review the PDF build was **not reproducible**.
Two consecutive builds from byte-identical source produced different PDFs,
because pdfTeX wrote the wall clock into `/CreationDate` and `/ModDate` and a
fresh trailer `/ID` on each run. A PDF digest recorded under those conditions
identified one build artifact, not the document, and would have gone stale on
the next build even with no edit to the source.

This is fixed as of this addendum. `scripts/build_paper.py` pins
`SOURCE_DATE_EPOCH` to the manuscript's stated date and sets
`FORCE_SOURCE_DATE`; the preamble sets `\pdftrailerid{}` and
`\pdfsuppressptexinfo=-1`. Two consecutive builds now produce identical bytes,
verified. The PDF digest above is therefore a claim about the document and can
be rechecked by rebuilding.

The source digests changed for this reason too: the five-line reproducibility
block is the only edit to the manuscript source made by this addendum. No
mathematical content was touched.

### What this addendum does NOT cover

**Section 8, "Ordinal calculus and transfinite dynamical systems", is
unreviewed.** It did not exist at the reviewed commit. It was added in
`af92dbb` and `1564656` and comprises:

- 8.1 Difference operators on ordinals
- 8.2 Normal functions and the Veblen hierarchy
- 8.3 Transfinite dynamical systems on ordinals

No reviewer examined its statements, its proofs, or its correspondence with the
implementation. Nothing in the September 7 review bears on it. It should be
read as unreviewed manuscript material until a review of it exists.

Two further items added after the review are also uncovered: the
"Superintelligence, oracle classes, and transfinite stratification" paragraph in
Section 1, and the Section 7 revisions describing direct evaluation of closed
quoted trees and the dynamical-transition work-step budget.

The library was version 0.1.0 when reviewed and is 0.3.0 now. The
implementation reviewer's reproduction was against 0.1.0.

### On the version label

The September 7 review recorded the manuscript label as "version 1.0". The
manuscript now reads "version 0.3.0". The label moved **backwards**, and that
was deliberate and correct: 1.0 asserted a completeness that external peer
review had not supplied and still has not. 0.3.0 tracks the library version and
claims less. The reversal is recorded here so that a reader encountering both
labels does not have to guess which way the document moved.

### Standing position

External peer review and a broader novelty assessment remain outstanding, as the
September 7 review stated. Nothing in this addendum is a new mathematical check.
It re-establishes coordinates and states coverage; it reviews nothing.
