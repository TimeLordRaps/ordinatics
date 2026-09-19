"""Build the paper with bounded, visible LaTeX runs and an optional page render.

Requires pdflatex and pandoc on PATH. Rendering additionally needs PyMuPDF.
Run from any directory: python scripts/build_paper.py --render
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    for executable in ("pdflatex", "pandoc"):
        if not shutil.which(executable):
            raise SystemExit(f"Install {executable} and make it available on PATH")
    for run in range(2):
        print(f"LaTeX pass {run + 1}/2; timeout 90 seconds", flush=True)
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
             "ordinal_arithmetic.tex"],
            cwd=PAPER, check=True, timeout=90,
        )
    log = (PAPER / "ordinal_arithmetic.log").read_text(encoding="utf-8", errors="replace")
    issues = [line for line in log.splitlines() if any(term in line for term in
              ("Overfull", "undefined", "Missing character", "LaTeX Warning"))]
    if issues:
        raise SystemExit("Manuscript needs inspection:\n" + "\n".join(issues))
    print("Converting a Markdown reading copy; timeout 30 seconds per conversion", flush=True)
    source = (PAPER / "ordinal_arithmetic.tex").read_text(encoding="utf-8")
    keys = re.findall(r"\\bibitem\{([^}]+)\}", source)
    source = re.sub(r"\\cite\{([^}]+)\}",
                    lambda m: "[" + str(keys.index(m[1]) + 1) + "]", source)
    source = source.replace(r"\eqref{eq:structure}", "(1)").replace(r"\eqref{eq:truth}", "(2)")
    source = re.sub(r"\\begin\{thebibliography\}\{[^}]+\}", r"\\section*{References}", source)
    source = source.replace(r"\end{thebibliography}", "")
    source = re.sub(r"\\bibitem\{([^}]+)\}",
                    lambda m: r"\paragraph{[" + str(keys.index(m[1]) + 1) + "]}", source)
    section = counter = 0
    lines = []
    for line in source.splitlines():
        if line.startswith(r"\section{"):
            section += 1
            counter = 0
        match = re.match(r"\\begin\{(theorem|proposition|lemma|definition)\}\[([^]]+)\]", line)
        if match:
            counter += 1
            line = r"\paragraph{" + f"{match[1].title()} {section}.{counter} ({match[2]})." + "}"
        line = re.sub(r"\\end\{(?:theorem|proposition|lemma|definition)\}", "", line)
        line = line.replace(r"\begin{proof}", r"\paragraph{Proof.}").replace(r"\end{proof}", "")
        lines.append(line)
    result = subprocess.run(["pandoc", "-f", "latex", "-t", "json"],
                            input="\n".join(lines), text=True, capture_output=True,
                            check=True, timeout=30)
    ast = json.loads(result.stdout)
    meta = ast["meta"]
    prefix = [
        {"t": "Header", "c": [1, ["", [], []], meta["title"]["c"]]},
        {"t": "Para", "c": [{"t": "Str", "c": "Tyler Roost"}]},
        {"t": "Para", "c": meta["date"]["c"]},
        {"t": "Header", "c": [2, ["", [], []], [{"t": "Str", "c": "Abstract"}]]},
    ]
    ast["blocks"] = prefix + meta["abstract"]["c"] + ast["blocks"]
    ast["meta"] = {}
    subprocess.run(["pandoc", "-f", "json", "-t", "markdown+tex_math_dollars", "--wrap=none",
                    "-o", str(PAPER / "ordinal_arithmetic.md")],
                   input=json.dumps(ast), text=True, check=True, timeout=30)
    if args.render:
        import fitz

        directory = PAPER / "render"
        directory.mkdir(exist_ok=True)
        doc = fitz.open(PAPER / "ordinal_arithmetic.pdf")
        for i, page in enumerate(doc):
            print(f"Render page {i + 1}/{len(doc)}", flush=True)
            page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(
                directory / f"page-{i + 1:02}.png"
            )
        print(f"Rendered {len(doc)} pages. Inspect before distributing.", flush=True)
    print("Built paper/ordinal_arithmetic.pdf and .md", flush=True)


if __name__ == "__main__":
    main()
