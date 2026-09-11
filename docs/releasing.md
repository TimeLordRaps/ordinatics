# Building and publishing Ordinatics

Distribution name: **ordinatics**. Development version: **0.2.0.dev0**.

The source repository contains a package ready to build. Availability on the Python Package Index (PyPI) is a separate release state; a repository commit or successful local build does not establish an uploaded release. This development version requires `hypermath-foundations==0.1.0`, built from the exact Hypermath commit in `verification/hypermath.json`. Provision that dependency before installing from a checkout.

Publication is currently blocked by unresolved self-derivation and arithmetic
completeness obligations. The complete checks workflow must pass at the publication
revision, including its mathematical gate. An expected failure remains a failure.
The workflow retains the evidence and never treats unresolved mathematics as a
passing release condition.

The checks workflow separates two propositions. **grounding integrity (audit and
replay)** passes when the exact pinned Hypermath audit completes and its Verifier
Standard evidence replay succeeds; it does not assert self-derivation or arithmetic
completeness. **foundation and completeness gate** requires those stronger claims and
therefore remains the fail-closed publication condition. Both jobs retain their
distinct evidence bundles for 90 days. A passing integrity job does not qualify a
release while the completeness gate fails.

## Build locally

```console
python scripts/bootstrap_foundation.py
python -m pip install -e '.[dev,scientific,verification]'
python -m pytest -vv -s --durations=10 --timeout=60
python -m ruff check src tests examples scripts
python -m build
python -m twine check dist/*
python -u scripts/check_grounding.py --require-self-derivation --require-complete
```

The wheel contains the `ordinatics` Python package, the reviewed Hypermath pin,
and license/metadata. The source distribution also includes tests, examples,
documentation, the dependency bootstrap, and the paper's text sources. Generated
local audit files, private research directories, and credentials are excluded.
The [grounding contract](grounding.md) explains source and installed-package checks.
Use a fresh `--output` directory when repeating the grounding command; existing
evidence bundles are preserved.

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

After the account owner has configured it, the mathematical requirements are
established, and the release is authorized, run **publish to PyPI** from the
repository's Actions tab on `main`. The workflow calls the same complete checks
workflow, downloads its tested distribution artifacts, and requires the mandatory
Hypermath package version to be available from the package index. It compares
the indexed wheel's payload with the qualified foundation wheel and checks an
isolated installation using that indexed dependency. Only the final
upload job has permission to request a publishing token. It does not run on
ordinary pushes and uses no long-lived token committed to the repository.

The comparison first validates every wheel file against its `RECORD` manifest.
It permits manifest row order, the `WHEEL` Generator header, and Windows versus
Unix line endings in generated `METADATA`. All other payload bytes, including
the Python checker, proof policy, metadata text, entry points and license, must
match. Python source line endings are fixed by the foundation's Git attributes.
The normal checks workflow also compares its independently built Linux and
Windows foundation wheels, so this portability contract is exercised before release.

A missing project at PyPI's JSON endpoint does not guarantee that its name is available for registration; the registry's upload response is authoritative. Existing version files cannot be overwritten. Increment the version in `pyproject.toml` and `src/ordinatics/__init__.py` for subsequent releases, and update the changelog.

## After publication

Verify the actual project page and install from the public index in a clean environment:

```console
python -m pip install ordinatics==0.2.0.dev0
python -c "import ordinatics; print(ordinatics.__version__)"
```

Only after that check should documentation describe `pip install ordinatics` as a live installation route.

## Rebuild the paper

Install `pdflatex` (for example through TeX Live or MiKTeX) and Pandoc, then run:

```console
python scripts/build_paper.py
```

The script compiles the LaTeX source twice, checks for layout/reference warnings, and regenerates the Markdown reading copy. To render page images for inspection, install PyMuPDF and run `python scripts/build_paper.py --render`. Inspect the rendered pages before distributing a changed PDF. The source distribution includes the paper source and build script; the rendered PDF is available in the repository.
