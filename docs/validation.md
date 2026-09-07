# Validation of version 0.1.0

These observations describe the initial distribution's exercised behavior. Tests support specific cases; they are not a formal soundness proof, a proof of the manuscript's novelty, or evidence of PyPI publication.

## Local checks

On Windows with Python 3.12.8, SymPy 1.14.0, NumPy 2.5.3, and SciPy 1.18.1:

- `python -m pytest -vv -s --durations=10 --timeout=60`: 102 passed.
- Both example scripts and the README/interoperability Python blocks completed successfully.
- `python -m ruff check src tests examples scripts`: passed.
- `python -m build`: built a wheel and source distribution.
- `python -m twine check dist/*`: both distributions passed metadata/rendering checks.

A separate environment installed the wheel with the minimum supported SymPy version, 1.13.3. The imported package came from the environment's installed `site-packages`. Its test run passed 99 cases and skipped three NumPy-dependent cases because the optional scientific dependencies were absent.

The tests exercise ordinary ordinal absorption, operation order, finite powers, natural operations, polynomial conversions, exact specialization, poles, the chosen exponential branch, binder scope, quotation closure and rank, malformed syntax, and budget exhaustion. Bounds and samples in those tests limit the evidence they provide.

## Paper

The LaTeX source compiled twice without the script's layout/reference warnings. All nine rendered pages were visually inspected. The title, references, equations, and computational companion are included in the PDF and Markdown reading copy. The manuscript states its external set-theoretic assumptions and distinguishes the executable bounded fragment from the full satisfaction hierarchy.

## Hosted checks

The repository's [checks workflow](https://github.com/TimeLordRaps/ordinatics/actions/workflows/ci.yml) tests Linux on Python 3.10, 3.12, and 3.13, and Windows on Python 3.12. Consult a run at the exact commit being used for current hosted results. A later source, dependency, interpreter, or build change can invalidate these local observations and requires the relevant checks to be rerun.
