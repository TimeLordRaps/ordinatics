#!/usr/bin/env python3
"""Assemble source documentation and manuscript copies into the GitHub Pages artifact."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAPER = ROOT / "paper"


class PagesBuildError(RuntimeError):
    pass


def build(output: Path) -> Path:
    output = output.resolve()
    if output == ROOT:
        raise PagesBuildError("Pages output cannot be the repository root")
    if output.exists() and any(output.iterdir()):
        raise PagesBuildError(f"refusing to merge into non-empty Pages output: {output}")
    if output.exists():
        output.rmdir()

    output.mkdir(parents=True, exist_ok=True)
    if DOCS.is_dir():
        shutil.copytree(DOCS, output / "docs")

    paper_out = output / "paper"
    paper_out.mkdir(parents=True, exist_ok=True)
    for name in ("ordinal_arithmetic.md", "ordinal_arithmetic.pdf", "ordinal_arithmetic.tex"):
        src = PAPER / name
        if src.is_file():
            shutil.copy2(src, paper_out / name)

    for name in ("README.md", "CHANGELOG.md", "LICENSE", "CITATION.cff"):
        src = ROOT / name
        if src.is_file():
            shutil.copy2(src, output / name)

    # Basic landing page
    index_html = output / "index.html"
    index_html.write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ordinatics</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #222; }
    h1 { border-bottom: 1px solid #ccc; padding-bottom: 10px; }
    a { color: #0366d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
    ul { list-style-type: square; }
    .card { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 16px; margin: 20px 0; }
  </style>
</head>
<body>
  <h1>Ordinatics</h1>
  <p><strong>Exact ordinal arithmetic, ordinal calculus, dynamics, symbolic specialization, and bounded typed satisfaction for Python.</strong></p>
  <div class="card">
    <h3>Documentation and Manuscript</h3>
    <ul>
      <li><a href="paper/ordinal_arithmetic.pdf">Manuscript (PDF)</a></li>
      <li><a href="paper/ordinal_arithmetic.md">Manuscript (Markdown reading copy)</a></li>
      <li><a href="docs/api.md">API Reference</a></li>
      <li><a href="docs/mathematical_scope.md">Mathematical Scope</a></li>
      <li><a href="docs/semantics.md">Typed Satisfaction Semantics</a></li>
      <li><a href="docs/interoperability.md">SymPy, NumPy, and SciPy Interoperability</a></li>
      <li><a href="docs/validation.md">Validation and Soundness</a></li>
      <li><a href="docs/releasing.md">Release Verification Guide</a></li>
    </ul>
  </div>
  <p>Source repository: <a href="https://github.com/TimeLordRaps/ordinatics">github.com/TimeLordRaps/ordinatics</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args(argv)
    try:
        out = build(args.output)
        print(f"[PAGES OK] assembled documentation site at {out}")
    except PagesBuildError as exc:
        print(f"[PAGES FAIL] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
