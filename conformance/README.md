# Conformance Kit

Self-serve tools for declaring conformance to the Result Consumption Semantics spec (`rcs@`).

## Contents

| file | purpose |
|------|---------|
| `state-b-vector-template.md` | Package layout + `vector.json` schema + hard rules for a State B (influence) vector (§5.4 V-1..V-4) |
| `state-b-self-check.py` | Stdlib-only structural validator — judges discipline, never conclusions |
| `badge-state-a.svg` / `badge-state-b.svg` | Badges for READMEs of implementations that ship a conformant axis |

## Quick start

1. Copy `state-b-vector-template.md` into your repo and fill the package.
2. Validate: `python state-b-self-check.py your-vector.json --spec-version-file /path/to/spec/VERSION`
3. Badge your README only after the checker passes — badges are claims, and claims name their state (I-3).

## Versioning discipline (§7)

The canonical spec version lives in the spec repo's `VERSION` file. Embed your aligned version as a constant and assert equality in one line:

```python
assert SPEC_VERSION == open("VERSION").read().strip()
```

On mismatch: report a drift error. Never silently pass.

## First reference implementations

- **State A:** [`roy-tong/AgentMeasure` → `conformance/vectors/external/chenhz01-001`](https://github.com/roy-tong/AgentMeasure/tree/main/conformance/vectors/external/chenhz01-001) (merged 2026-10-10, PR #32)
- **State B:** template published in 0.2.0-draft — your vector could be the first. Negative results (`influence-absent`) with intact discipline are as publishable as positive ones.
