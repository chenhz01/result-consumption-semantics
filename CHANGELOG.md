# Changelog

All notable changes to the Result Consumption Semantics specification. SemVer; while `0.x`, any field may change and stability claims are forbidden (§7).

## 0.2.0-draft — 2026-10-13

- **SPEC_VERSION machine-readable check (§7).** Canonical version string now lives in [`VERSION`](VERSION); runners SHOULD assert their aligned version in one line and report a drift error on mismatch. Offered following the runner↔spec sync discussion in [AgentMeasure#11](https://github.com/roy-tong/AgentMeasure/issues/11).
- **State B conformance vector requirements (§5.4, V-1..V-4).** Delta surface + threshold (V-1), measured variance baseline (V-2), named ablation policy (V-3), and the non-pass discipline for `indeterminate` (V-4). A vector missing any of these is non-conformant regardless of its conclusions.
- **Conformance kit** ([`conformance/`](conformance/README.md)): State B vector template, stdlib-only structural validator (`state-b-self-check.py`, 3/3 checks verified: conformant pass / indeterminate-must-not-pass / version drift), and State A / State B badges.

## 0.1.0-draft — 2026-10-10

- Initial draft: two normative states (A availability — context fact; B influence — behavioral fact), `UNOBSERVABLE` boundary outcome, ranked evidence axis with two named failure modes (`cite-without-use`, `use-without-cite`), State A four-value certification protocol with invariants I-1..I-3, State B paired-run ablation protocol with `indeterminate` as explicit non-pass, lineage and credits pinned to AgentMeasure DR-005 / issue #11 / conformance vector `chenhz01-001`.
