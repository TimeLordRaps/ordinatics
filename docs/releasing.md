# Building and publishing Ordinatics

Distribution name: **ordinatics**. Initial version: **0.1.0**.

The source repository contains a package ready to build. Availability on the Python Package Index (PyPI) is a separate release state; a repository commit or successful local build does not establish an uploaded release. Until a release is visible on PyPI, install from a checkout with `python -m pip install .`.

## Build locally

```console
python -m pip install -e '.[dev,scientific]'
python -m pytest -vv -s --durations=10 --timeout=60
python -m ruff check src tests examples scripts
python -m build
python -m twine check dist/*
```

The wheel contains only the `ordinatics` Python package and its license/metadata. The source distribution also includes tests, examples, documentation, and the paper's text sources. Generated local audit files, private research directories, and credentials are excluded.

## PyPI Trusted Publisher

The repository includes a manually dispatched publishing workflow. To authorize its first upload, the package owner must configure a pending publisher on PyPI with these exact values:

| Field | Value |
|---|---|
| PyPI project name | `ordinatics` |
| GitHub owner | `TimeLordRaps` |
| Repository | `ordinatics` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

Configure it at [PyPI publishing settings](https://pypi.org/manage/account/publishing/). The publisher is limited by the named repository, workflow, and environment. See the [official PyPI Trusted Publisher documentation](https://docs.pypi.org/trusted-publishers/using-a-publisher/) and [pending publisher guidance](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).

After the account owner has configured it and authorized the release, run **publish to PyPI** from the repository's Actions tab on `main`. The workflow reruns tests and distribution checks before requesting the short-lived publishing token. It does not run on ordinary pushes and does not require a long-lived token committed to the repository.

A missing project at PyPI's JSON endpoint does not guarantee that its name is available for registration; the registry's upload response is authoritative. Existing version files cannot be overwritten. Increment the version in `pyproject.toml` and `src/ordinatics/__init__.py` for subsequent releases, and update the changelog.

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
