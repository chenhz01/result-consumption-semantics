# State B Conformance Vector Template

**Applies to:** rcs@0.2.0-draft (§5, §5.4)
**Status:** template — copy this directory, fill every REQUIRED field, run `state-b-self-check.py` before submitting a vector.

A State B vector is a *package*, not a claim. It exists so that a third party can re-run the paired experiment and reach the same outcome discipline — not so that the author can assert influence.

## 1. Package layout

```
<your-vector-id>/
├── vector.json          # REQUIRED — the machine-readable declaration (schema below)
├── present-trace.jsonl  # REQUIRED — the observed run's event stream
├── ablated-trace.jsonl  # REQUIRED — the counterfactual run's event stream
├── variance-baseline.md # REQUIRED — how run-to-run variance was measured WITHOUT ablation
└── README.md            # REQUIRED — human summary: what was ablated, why this result
```

## 2. `vector.json` schema

```json
{
  "spec_version": "0.2.0-draft",          // REQUIRED — must equal the VERSION file of the spec you claim
  "vector_id": "your-id-001",             // REQUIRED — stable identifier
  "subject": {                            // REQUIRED — what was ablated
    "step": 3,
    "result_ref": "tool_call#7",
    "ablation_mode": "remove | neutral-placeholder"
  },
  "ablation_policy": "summary-embed outcomes first; high-stakes steps",  // REQUIRED — V-3
  "delta_surface": "tool_calls_issued | downstream_state | final_answer_content",  // REQUIRED — V-1
  "threshold": {                          // REQUIRED — pre-declared, part of V-1
    "metric": "e.g. count of tool calls differing beyond noise",
    "value": 1
  },
  "variance_baseline": {                  // REQUIRED — V-2
    "runs_without_ablation": 3,
    "observed_variance": "describe the noise floor",
    "source": "variance-baseline.md"
  },
  "outcome": "influence-confirmed | influence-absent | indeterminate",  // REQUIRED — V-4
  "passed": false,                        // REQUIRED — MUST be false when outcome == "indeterminate"
  "environment": {                        // REQUIRED — replay honesty (§5.3)
    "model": "...",
    "determinism_limits": "what could not be held constant"
  }
}
```

## 3. Hard rules (validated by `state-b-self-check.py`)

1. `spec_version` MUST match the spec's `VERSION` file (drift check, §7).
2. All of V-1..V-4 present; a missing field is non-conformant regardless of conclusions.
3. `outcome: "indeterminate"` ⇒ `passed: false`. Self-check fails otherwise. There is no honest way to pass on an indeterminate.
4. `absent` experiments are not evidence of absence: if `ablated-trace.jsonl` is missing because replay was impossible, the vector MUST declare `outcome: "indeterminate"` with a reason, or simply not be submitted.

## 4. What reviewers check (and what they refuse)

Reviewers re-run the paired experiment when the environment permits and check the *discipline*, not the conclusion:

- Was the delta surface and threshold declared before outcomes were read? (V-1)
- Is the variance baseline real data, or an assertion? (V-2)
- Does the ablation policy name its selection rule? (V-3)
- Is `indeterminate` reported as a non-pass where it occurs? (V-4)

A vector whose conclusion is `influence-absent` is **as publishable** as one with `influence-confirmed`. Negative results with intact discipline are the point; positive results without discipline are noise.
