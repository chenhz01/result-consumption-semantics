# Result Consumption Semantics — Draft Specification

**Version:** 0.2.0-draft
**Spec identifier:** `rcs@0.2.0-draft` (machine-readable canonical version lives in [`VERSION`](VERSION); runners SHOULD assert their aligned version in one line against it — see §7)
**License:** Apache-2.0
**Status:** Draft — seeking second independent implementations before any stability claim.

## Lineage and credits

This specification consolidates an ontology that emerged from public discussion in [roy-tong/AgentMeasure issue #11](https://github.com/roy-tong/AgentMeasure/issues/11). Credit is specific and deliberately so:

- **Two-state + ranked-evidence ontology** — formalized in AgentMeasure `design-rationale/DR-005-evidence-calibrated-consumption-claims.md` (commit `1e99a94`, revised to two-state form in `9545ff5`), authored by Roy Tong (@roy-tong), from a discussion initiated in issue #11.
- **Canonical phrasing** of the state distinction — "availability is a context fact; influence is a behavioral fact requiring ablation or rerun" — due to Gunjan Jaswal (@gunjanjaswal), acknowledged as the phrasing reference by the ontology's author.
- **Certification mechanics** — the trace-side availability protocol (Oct 2 sketch), the four-value axis with `unreachable` as its own outcome, and the first conformance vector — due to @chenhz01, author of this specification.
- **First reference implementation** — AgentMeasure conformance vector [`external/chenhz01-001`](https://github.com/roy-tong/AgentMeasure/tree/main/conformance/vectors/external/chenhz01-001), PR [#32](https://github.com/roy-tong/AgentMeasure/pull/32), merged 2026-10-10 (fixture inspected against AgentMeasure commit `67c276b`).

The purpose of this document is to make that ontology implementable **without forking any single repository's governance**. Nothing here overrides AgentMeasure's DR-005; the two documents are intended to agree, and drift between them should be filed in either project.

---

## 1. Problem statement

A consumption event carrying a single `consumed` boolean cannot represent the distinction this specification exists to draw. Four tool results can share the same boolean value while differing in kind:

| fact | question | layer |
|---|---|---|
| availability (State A) | did the result's canonical content reach the next model request? | trace (single run) |
| influence (State B) | did the result change the agent's behavior? | experiment (paired runs) |
| reference | did anything in the request mention the result? | trace (weak estimator only) |
| observability | did a request leave the framework at all? | trace (boundary condition) |

Collapsing these into one boolean makes availability metrics wrong in a specific, directional way: `unreachable` outcomes inflate apparent non-consumption, and `summary-embed` outcomes are indistinguishable from true availability.

## 2. Normative states

### 2.1 State A — Availability

**Definition.** A result is *available* at step *n+1* if and only if the canonicalized content of the result (or a projection recorded as such) is present in the model request payload issued at step *n+1*.

Availability is a **context fact**: it is certifiable from a single trace, without any knowledge of behavior.

### 2.2 State B — Influence

**Definition.** A result is *influential* at step *n+1* if and only if the agent's behavior at step *n+1* (or later) differs in a specified, measurable way between the actual run and a counterfactual run in which the result is ablated.

Influence is a **behavioral fact**: it is certifiable only by an experiment (§5). No trace-only observation can certify State B.

### 2.3 UNOBSERVABLE

If no request left the framework at step *n+1* (crash, network failure, abort before dispatch), the consumption axis is **UNOBSERVABLE** for that result. UNOBSERVABLE is a distinct outcome, not a `false`, and not a member of any evidence ranking.

## 3. Evidence axis (ranked, non-normative as states)

`reference` — the presence of result-derived text in the request — is a **weak estimator** with two named failure modes:

1. **cite-without-use** — the text is quoted (in a prompt template, a log echo, a system reminder) without affecting behavior.
2. **use-without-cite** — the content influenced behavior only through a lossy summary, leaving no verbatim trace.

The evidence axis ranks observability of influence; it never substitutes for a state:

```
reference (weakest) < summary-embed (lossy projection) < ablation-confirmed (experiment)
```

A `summary-embed` outcome is **lossy-projection evidence**: it certifies *no* State A availability, while constituting weak influence evidence. These are different rows in a conformance table and must not be merged.

## 4. State A certification protocol

1. Compute the **canonicalized content hash** of each tool result at emission time. Canonicalization MUST be applied to content, not raw bytes, so that re-serialization of JSON does not produce a false negative.
2. At each subsequent request, test whether the canonicalized content (or a declared projection of it) appears in the payload, and **record the field path** where it was found.
3. Assign exactly one outcome:
   - `verbatim` — canonical content found verbatim → **State A certified**.
   - `summary-embed` — only a declared lossy projection found (field path recorded) → State A **not** certified; weak influence evidence recorded.
   - `absent` — a request left; content found nowhere → State A certified false.
   - `unreachable` — no request left → **UNOBSERVABLE** (§2.3).

### 4.1 Invariants

- **I-1 (denominator).** `unreachable` outcomes MUST NOT be counted as `false` and MUST NOT enter the availability denominator. Availability rate = `verbatim / (verbatim + summary-embed + absent)`.
- **I-2 (no boolean flattening).** Implementations MUST NOT expose a single boolean that maps both `summary-embed` and `verbatim` to the same value.
- **I-3 (claims name their state).** Any conformance claim MUST name the state it certifies. A claim of availability supported only by reference evidence is invalid.

## 5. State B certification protocol (ablation)

State B cannot be read from a trace; it must be produced by an experiment.

### 5.1 Paired-run design

For a result *r* at step *n*:

1. **Present run** — the observed run, as recorded.
2. **Ablated run** — a replay of the same task with *r* removed from the context supplied at step *n+1* (or replaced by a declared neutral placeholder), holding the environment, model, and sampling parameters as constant as the runtime permits.

### 5.2 Delta measurement and outcomes

Compare the runs on a pre-declared behavioral delta surface: tool calls issued, downstream state changes, or the final answer's content. Assign exactly one outcome:

- `influence-confirmed` — behavioral delta beyond the pre-declared threshold.
- `influence-absent` — no delta beyond the threshold.
- `indeterminate` — run-to-run variance (without ablation) exceeds the delta. `indeterminate` is a **non-pass**: implementations MUST NOT report it as either confirmation or absence.

### 5.3 Cost and honesty boundaries

- Ablation is an experiment-layer act: it costs at least one additional run per result examined. Implementations SHOULD declare which results were selected for ablation and by what policy (e.g., `summary-embed` outcomes, high-stakes steps).
- Where paired replay is impossible (non-deterministic environments, side-effecting tools), State B MUST remain unclaimed for those steps. Absence of an experiment is absence of a State B claim — not evidence of absence.

### 5.4 State B conformance vector requirements

A State B conformance vector (introduced in 0.2.0-draft; template in [`conformance/state-b-vector-template.md`](conformance/state-b-vector-template.md), structural validator in [`conformance/state-b-self-check.py`](conformance/state-b-self-check.py)) MUST declare:

- **V-1 (delta surface).** The pre-declared behavioral delta surface (§5.2) and its threshold, stated *before* outcomes.
- **V-2 (variance baseline).** Run-to-run variance measured without ablation, so that `indeterminate` is grounded in data rather than intuition.
- **V-3 (ablation policy).** Which results were selected for ablation and by what policy (§5.3).
- **V-4 (outcome discipline).** Exactly one of `influence-confirmed` / `influence-absent` / `indeterminate`; `indeterminate` MUST be reported as a non-pass and MUST NOT be flattened into either confirmation or absence (this is the State B analogue of I-2).

A vector missing any of V-1..V-4 is non-conformant regardless of its conclusions.

## 6. Orthogonality

State A and State B are independent axes. All four combinations are meaningful; the reference implementation's fixture demonstrates three of them explicitly (verbatim-without-influence is real, and so is influence-without-availability via compaction).

Conformance reporting SHOULD present availability and influence as separate columns, joined only by declared evidence, never by inference.

## 7. Conformance and versioning

- Versioning: SemVer. While `0.x`, any field may change; stability claims are forbidden until 1.0.0.
- **Machine-readable version check.** The canonical version string lives in [`VERSION`](VERSION). Runners SHOULD embed their aligned spec version as a constant and assert equality in a single line (e.g. `assert runner.SPEC_VERSION == open("VERSION").read().strip()`); on mismatch, the runner MUST report a drift error rather than silently passing.
- A conformant implementation MUST: (a) emit the four-value availability axis per result (§4), (b) respect I-1..I-3, (c) expose ablation outcomes as a separate surface (§5) or explicitly declare State B unsupported; State B vectors additionally MUST satisfy V-1..V-4 (§5.4).
- Drift between this specification and AgentMeasure's DR-005 / M-series invariants should be filed as an issue in **either** repository; both projects benefit from the mismatch being public.

## 8. Reference implementation

[`roy-tong/AgentMeasure` → `conformance/vectors/external/chenhz01-001`](https://github.com/roy-tong/AgentMeasure/tree/main/conformance/vectors/external/chenhz01-001)

One synthetic trace; four tool results; each meets a different certification outcome (`verbatim`, `summary-embed`, `absent`, `unreachable`); expected outcomes, event stream, and trace context included. Merged 2026-10-10 via PR #32.

## License

This specification is licensed [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0). Attribution should reference this repository and the lineage section above.
