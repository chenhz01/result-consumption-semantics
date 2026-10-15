# Result Consumption Semantics

**A draft specification for separating result *availability* from behavioral *influence* in AI agent telemetry — with a concrete certification protocol for each.**

Version: v0.2.0-draft · License: Apache-2.0 · Status: seeking second independent implementations

## Why this exists

Agent telemetry systems commonly record a single boolean per tool result — `consumed: true/false`. That boolean collapses at least four different facts into one bit:

- Did the result's content actually reach the next model request? (**availability**)
- Did the result change what the agent did? (**influence**)
- Did it merely get cited? (a weak *estimator*, not a state)
- Did the request even leave the framework? (**observability boundary**)

Downstream metrics built on the single boolean systematically overcount or undercount depending on how failures are bucketed — and the errors are invisible precisely in the compaction-heavy long agent runs where the distinction pays for itself.

## What's in the spec

- **Normative two-state ontology** — State A (availability, a context fact certifiable from a single trace) vs State B (influence, a behavioral fact requiring an experiment), with `reference` demoted to a ranked evidence estimator, never a state.
- **State A certification protocol** — canonicalized content hashing with field-path recording; named failure modes (re-serialization, compaction); a four-value axis: `verbatim` / `summary-embed` / `absent` / `unreachable`.
- **State B ablation protocol** — paired-run design (result ablated vs present) with three outcomes: `influence-confirmed` / `influence-absent` / `indeterminate`, where `indeterminate` is explicitly a non-pass so noise cannot be laundered into a green check.
- **Denominator invariants** — an `unreachable` outcome is never counted as `FALSE` and never enters the availability denominator.

## Status & lineage

This is a **draft**, not a standard. It consolidates an ontology that emerged from public discussion — see the [lineage and credits](SPECIFICATION.md#lineage-and-credits) section — into an implementation-agnostic form, so that conformance can be asserted by CI rather than argued in issue threads.

First reference implementation: [`roy-tong/AgentMeasure` conformance vector `external/chenhz01-001`](https://github.com/roy-tong/AgentMeasure/tree/main/conformance/vectors/external/chenhz01-001) (merged 2026-10-10).

Implementations, drift reports, and second opinions are welcome — see [CONFORMANCE](SPECIFICATION.md#conformance-and-versioning).
