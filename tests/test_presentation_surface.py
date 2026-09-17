"""The public first impression is a checked repository surface."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_professional_presentation_surface_has_no_drift() -> None:
    path = ROOT / "scripts/check_presentation.py"
    spec = importlib.util.spec_from_file_location("check_presentation", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.run() == []


def test_public_boundary_catches_private_coordinates_without_naming_them() -> None:
    path = ROOT / "scripts" / "check_presentation.py"
    spec = importlib.util.spec_from_file_location("check_presentation_boundaries", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    drive_path = "E:" + "\\" + "private-workspace" + "\\" + "plan.md"
    private_locator = "evaluator" + "-vault://artifact"
    local_artifact = "private-model" + ".gguf"
    deployment_field = "model" + "_path"
    assert "drive-qualified local path" in module.public_boundary_violations(drive_path)
    assert "synthetic private locator" in module.public_boundary_violations(private_locator)
    assert "local model artifact filename" in module.public_boundary_violations(local_artifact)
    assert "private deployment field" in module.public_boundary_violations(deployment_field)


def test_lineage_claim_gate_rejects_causal_upgrades_without_blocking_boundaries() -> None:
    path = ROOT / "scripts" / "check_presentation.py"
    spec = importlib.util.spec_from_file_location("check_presentation_lineage", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    causal_lineage = "causal" + " lineage"
    causal_ancestors = "causal" + " ancestors"
    causal_process = "causal" + " process"
    causal_contribution = "causally" + " contributed"
    for phrase in (
        causal_lineage,
        causal_ancestors,
        causal_process,
        causal_contribution,
    ):
        assert module.lineage_causality_violations(phrase)

    assert module.lineage_causality_violations("recorded lineage") == []
    assert module.lineage_causality_violations(
        "The recorded edge does not establish causal influence."
    ) == []


def test_pages_build_and_internal_navigation(tmp_path: Path) -> None:
    from html.parser import HTMLParser

    path = ROOT / "scripts/build_pages.py"
    spec = importlib.util.spec_from_file_location("build_pages", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    output = tmp_path / "site"
    module.build(output)

    assert (output / "index.html").is_file()
    assert (output / "README.md").is_file()
    assert (output / "CHANGELOG.md").is_file()
    assert (output / "LICENSE").is_file()
    assert (output / "CITATION.cff").is_file()
    assert (output / "paper/ordinal_arithmetic.pdf").is_file()
    assert (output / "paper/ordinal_arithmetic.md").is_file()
    assert (output / "docs/api.md").is_file()
    assert (output / "docs/validation.md").is_file()

    class LinkParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.links: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            for name, val in attrs:
                if name in ("href", "src") and val:
                    self.links.append(val)

    parser = LinkParser()
    parser.feed((output / "index.html").read_text(encoding="utf-8"))
    for link in parser.links:
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = output / link
        assert target.is_file(), f"broken link in generated index.html: {link}"
