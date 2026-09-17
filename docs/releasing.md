# Building and publishing Ordinatics

Distribution name: **ordinatics**. Initial version: **0.1.0**.

The source repository contains a package ready to build. Availability on the Python Package Index (PyPI) is a separate release state; a repository commit or successful local build does not establish an uploaded release. Until a release is visible on PyPI, install from a checkout with `python -m pip install .`.

## Build locally

```console
python -m pip install '.[dev,scientific]'
python -m pytest -vv -s --durations=10 --timeout=60
python -m ruff check src tests examples scripts
python -m build
python -m twine check dist/*
```

The wheel contains only the `ordinatics` Python package and its license/metadata. The source distribution also includes tests, examples, documentation, and the paper's text sources. Generated local audit files, private research directories, and credentials are excluded.

## Reproducible release builds and verification

Use `scripts/release_artifacts.py` to produce canonical source archives, deterministic wheels, normalized source distributions, and an external release manifest binding artifact digests:

```console
python -m pip install '.[test,scientific,release]'
python -m pytest -q
python scripts/check_presentation.py
python scripts/release_artifacts.py build --ref HEAD --release 0.1.0 --output-dir dist
python scripts/release_artifacts.py verify dist/ordinatics-0.1.0.manifest.json
python -m twine check dist/*.whl dist/*.tar.gz
python scripts/check_release_boundary.py dist/*.zip dist/*.whl dist/*.tar.gz
python scripts/check_installed_wheel.py --wheel-dir dist
```

To verify byte-identical reproducibility across independent builds (e.g. Linux and Windows):

```console
python scripts/release_artifacts.py compare PATH_TO_LINUX_ARTIFACTS PATH_TO_WINDOWS_ARTIFACTS
```

## Tagged releases and PyPI Trusted Publishing

The canonical publication workflow (`.github/workflows/release.yml`) triggers on signed Git tags (`v*`):
1. Verifies protected-main lineage, matching version coordinates, and green `conformance-gate`.
2. Builds exact source archive, deterministic wheel, normalized sdist, and external manifest via `release_artifacts.py`.
3. Runs twine check, release boundary scanning, and isolated-wheel smoke testing.
4. Generates cryptographic GitHub Artifact Attestations for all published assets (`zip`, `whl`, `tar.gz`, `manifest.json`).
5. Publishes a GitHub Release with attested assets.
6. Publishes the wheel and sdist to PyPI using OIDC Trusted Publishing (no long-lived credentials).

To configure PyPI Trusted Publishing for Ordinatics, the package owner sets up a pending publisher on PyPI:

| Field | Value |
|---|---|
| PyPI project name | `ordinatics` |
| GitHub owner | `TimeLordRaps` |
| Repository | `ordinatics` |
| Workflow filename | `release.yml` (and optionally `publish.yml` for manual runs) |
| Environment | `pypi` |

## After publication

Verify the actual project page and install from the public index in a clean environment:

```console
python -m pip install ordinatics==0.1.0
python -c "import ordinatics; print(ordinatics.__version__)"
```

Only after that check should documentation describe `pip install ordinatics` as a live installation route.

## Rebuild the paper

Install `pdflatex` (for example through TeX Live or MiKTeX) and Pandoc, then run:

```console
python scripts/build_paper.py
```

The script compiles the LaTeX source twice, checks for layout/reference warnings, and regenerates the Markdown reading copy. To render page images for inspection, install PyMuPDF and run `python scripts/build_paper.py --render`. Inspect the rendered pages before distributing a changed PDF. The source distribution includes the paper source and build script; the rendered PDF is available in the repository.
