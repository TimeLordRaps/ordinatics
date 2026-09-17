# Contributing to Ordinatics

Contributions are welcome when they make mathematical contracts more exact, increase
computational reliability, or improve formal alignment without strengthening unsupported
claims.

## Required for a normative change

- Identify the affected mathematical domain (`ordinals`, `algebra`, `semantics`, `calculus`, `dynamics`);
- Preserve the distinction between noncommutative ordinal operations and commutative Hessenberg natural operations;
- Maintain the strict bound of ordinals below `omega**omega` for concrete normal forms;
- Enforce zero required runtime dependencies on base import paths (`dependencies = []`);
- Include a falsification condition;
- Add tests that fail before the change and pass after it;
- Run the full test suite (`python -m pytest -q`), presentation check (`python scripts/check_presentation.py`), and pure stdlib smoke probe (`PYTHONPATH=src python -S -c "import ordinatics; print(ordinatics.__version__)"`).

Do not replace `UNKNOWN` or unevaluated semantic formulas with `False`, bypass step
budgets, or silently coerce types.

Unless explicitly stated otherwise, any contribution intentionally submitted for
inclusion in this repository is provided under the Apache License 2.0, including its
Section 3 patent terms and Section 5 contribution terms.

## Commits

Commits in this repository are GPG-signed (`git commit -S`). Pull requests are expected to
carry signed commits, and automated contributors must never bypass signing. A commit
signature binds bytes to a signing key; it does not establish the signer's legal identity,
correctness, or authorization.

## Feedback and vulnerabilities

Use the structured GitHub issue forms for mathematical ambiguities, counterexamples, and
interoperability reports. Send vulnerability details only through the private route in
`SECURITY.md`.
