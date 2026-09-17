# Security policy

## Supported release

Only the latest tagged public release is supported. Security corrections are published
additively.

## Reporting

Do not place secrets, private vulnerability details, or exploit payloads in a public issue.
Use **Security** → **Report a vulnerability** in the canonical GitHub repository to open a
private vulnerability report with the maintainer:

`https://github.com/TimeLordRaps/ordinatics/security/advisories/new`

If GitHub does not show the private-reporting form, report only the non-sensitive fact that
the private route is unavailable.

## Scope

Ordinatics evaluates mathematical expressions, transfinite stage progressions, and bounded
logical formulas. The semantic evaluator enforces an explicit `step_budget` parameter to
prevent denial-of-service via transfinite loops or deeply nested syntax trees.

Report cases where:
- unbudgeted evaluation or unbounded iteration causes unrecoverable process hangs;
- cyclic or malformed syntax trees bypass frozen dataclass validation;
- numeric overflow occurs during normal form arithmetic or Hessenberg natural operations;
- credentials, tokens, or private environment coordinates leak into published artifacts.
