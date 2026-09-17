# AGENTS.md

Working rules for automated contributors to Ordinatics. Read this before editing anything.

## 0. Before you touch anything

High-risk couplings are enforced by CI. Check this table first.

| If you are changing... | You must also... |
|---|---|
| the version, anywhere | bump all five: `pyproject.toml`, `src/ordinatics/__init__.py`, `CITATION.cff`, `.zenodo.json`, and a dated `## X.Y.Z - YYYY-MM-DD` heading in `CHANGELOG.md` |
| dependencies | put it in an optional extra. `dependencies = []` on base import paths is enforced by CI (`stdlib-smoke`) |
| `src/ordinatics/__init__.py` | preserve lazy exports via `_LAZY_EXPORTS` so base imports stay zero-dependency |
| mathematical contracts | preserve non-commutative ordinary operations vs commutative Hessenberg natural operations |
| boundary phrasing in `README.md` | keep exact domain bounds (`< omega**omega`), Apache 2.0 license, and alpha status disclosures |

Then, before you propose a change:

```bash
python -m pytest -q
python scripts/check_presentation.py
```

## 1. What this repository is

Ordinatics provides exact ordinal arithmetic, ordinal calculus, ordinal dynamics, symbolic
specialization, and bounded typed satisfaction for Python. It is the computational
companion to the foundational manuscript *Ordinal Arithmetic: An Ordinal-First Metalanguage
Approach to Definable Arithmetic Truth* by Tyler Roost.

The package distribution is `ordinatics`, the import package is `ordinatics`.

### 1.1 Ecosystem coordinates

Ordinatics is part of the TimeLord formal ecosystem:
- **Reference Standard of Excellence**: [`TimeLordRaps/verifier`](https://github.com/TimeLordRaps/verifier) establishes the standard for reproducible CI/CD, presentation gates, release verification, and claim discipline.
- **Adjacent Repositories**:
  - [`TimeLordRaps/hypermath`](https://github.com/TimeLordRaps/hypermath) — primitive foundational algebraic kernel, quadrilateral filtration, Lean 4 bridge.
  - [`TimeLordRaps/grounded-hyperset-theory`](https://github.com/TimeLordRaps/grounded-hyperset-theory) — Aczel's Anti-Foundation Axiom (AFA), Accessible Pointed Graphs (APGs), non-well-founded sets, and quotient abstraction.
  - [`TimeLordRaps/grounded-hypercalculi`](https://github.com/TimeLordRaps/grounded-hypercalculi) — Oracle, Language, Meta, Hyper, Ordinal, and Real Calculi.

### 1.2 Mathematical boundaries

1. **Exact ordinal domain**: Finite polynomials in `omega` with exact nonnegative integer coefficients represent ordinals strictly below `omega**omega`. No floating-point approximations or representations of infinity are permitted.
2. **Operational dualism**:
   - Ordinary operations (`+`, `*`) are noncommutative and follow transfinite ordinal arithmetic (`1 + omega == omega`, `omega + 1 > omega`).
   - Natural operations (`natural_add`, `natural_mul`) are commutative Hessenberg polynomial operations.
3. **Symbolic wrap**: Specialization of rational functions at `X = -1/2` operates strictly in `Q(X)`. Cancelled removable singularities are evaluated; actual poles raise `PoleError`. Wrap is an algebraic value map, not a homomorphism of ordinary ordinal arithmetic.
4. **Typed satisfaction**: The truth hierarchy quotes closed syntax trees at stage `beta`, yielding rank `beta + 1`. Quantifiers are bounded by explicit limits and step budgets. Evaluation failure, ill-typed formulas, and budget exhaustion raise specific exceptions; they are never converted to `False`.

## 2. Prime directive

> Zero required runtime dependencies on base import paths. Changes that strengthen a claim without stronger evidence are non-conforming.

Specifically, never:
- add a required runtime dependency to `dependencies = []` in `pyproject.toml`;
- convert `UNKNOWN` or unevaluated semantic formulas into `False`;
- silently coerce non-integers or booleans to integers;
- conflate noncommutative ordinal addition with commutative Hessenberg natural addition;
- bypass step budgets or quantifier bounds;
- weaken tests to make a suite pass.

## 3. Environment and commands

```bash
python -m pip install ".[test,scientific]"
python -m pytest -q
python scripts/check_presentation.py
python scripts/check_installed_wheel.py
```

Pure standard-library smoke check (enforcing zero runtime dependencies on base import):

```bash
PYTHONPATH=src python -S -c "import ordinatics; from ordinatics.ordinals import OMEGA, Ordinal; print(ordinatics.__version__, OMEGA)"
```

Release artifact generation and multi-platform reproducibility check:

```bash
python scripts/release_artifacts.py build --ref HEAD --release 0.1.0 --output-dir dist/release-integrity
python scripts/release_artifacts.py verify dist/release-integrity/ordinatics-0.1.0.manifest.json
python -m twine check dist/release-integrity/*.whl dist/release-integrity/*.tar.gz
python scripts/check_release_boundary.py dist/release-integrity/*.zip dist/release-integrity/*.whl dist/release-integrity/*.tar.gz
```

Cross-platform reproducibility:

```bash
python scripts/release_artifacts.py compare PATH_TO_LINUX_ARTIFACTS PATH_TO_WINDOWS_ARTIFACTS
```

## 4. Layout

- `paper/` — LaTeX manuscript (`ordinal_arithmetic.tex`), Markdown reading copy (`ordinal_arithmetic.md`), and compiled PDF (`ordinal_arithmetic.pdf`).
- `src/ordinatics/` — core implementations:
  - `ordinals.py` — Cantor normal form ordinal arithmetic below `omega**omega`.
  - `algebra.py` — SymPy rational functions and `wrap` specialization at `X = -1/2`.
  - `semantics.py` — ramified truth hierarchy, bounded quantifiers, syntax, and step-budget evaluator.
  - `calculus.py` — ordinal difference operators, normal functions, derivatives, and Veblen hierarchy.
  - `dynamics.py` — ordinal transformations, stage-indexed dynamical systems, orbits, and attractors.
- `scripts/` — `release_artifacts.py`, `check_presentation.py`, `check_release_boundary.py`, `check_installed_wheel.py`, `build_paper.py`, `build_pages.py`.
- `tests/` — pytest test suite covering all modules and presentation surfaces.

## 5. Invariants that must not be refactored away

1. **Zero required runtime dependencies**: `dependencies = []` in `pyproject.toml`. Third-party libraries (`sympy`, `numpy`, `scipy`) are optional extras (`[project.optional-dependencies]`).
2. **Lazy exports**: `_LAZY_EXPORTS` and `__getattr__` in `src/ordinatics/__init__.py` ensure `import ordinatics` never eagerly loads optional modules.
3. **LF line endings**: `.gitattributes` enforces `eol=lf` across all text files.
4. **Apache-2.0 license**: all code and specifications remain under Apache License 2.0.

## 6. Commits and change process

Work lands via pull request into `main`. Commits in this repository are GPG-signed (`git commit -S`). Never disable commit signing (`--no-gpg-sign`).
Release creation and package-index publication are maintainer acts executed exclusively through GitHub Actions with OIDC Trusted Publishing.
