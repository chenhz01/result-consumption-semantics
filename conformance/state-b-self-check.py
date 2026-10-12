#!/usr/bin/env python3
"""State B conformance vector structural validator (rcs@0.2.0-draft, §5.4 V-1..V-4).

Usage:
    python state-b-self-check.py <vector.json> [--spec-version-file VERSION]

Exit codes:
    0 — structurally conformant (discipline intact; conclusions not judged)
    1 — non-conformant (details on stderr)
    2 — usage / IO error

Stdlib only. Judge the discipline, never the conclusion: a vector claiming
influence-absent with intact V-1..V-4 passes; a vector claiming
influence-confirmed with a missing variance baseline fails.
"""

import argparse
import json
import sys
from pathlib import Path

REQUIRED_OUTCOMES = {"influence-confirmed", "influence-absent", "indeterminate"}
REQUIRED_KEYS = {
    "spec_version",
    "vector_id",
    "subject",
    "ablation_policy",      # V-3
    "delta_surface",        # V-1
    "threshold",            # V-1
    "variance_baseline",    # V-2
    "outcome",              # V-4
    "passed",
    "environment",
}
REQUIRED_SUBJECT_KEYS = {"step", "result_ref", "ablation_mode"}


def fail(msgs, msg):
    msgs.append(msg)


def check_vector(data, spec_version, msgs):
    # --- required keys ---
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        fail(msgs, f"missing required key(s): {', '.join(sorted(missing))}")

    # --- V-1: delta surface + threshold declared ---
    if "delta_surface" in data and not str(data["delta_surface"]).strip():
        fail(msgs, "V-1: delta_surface is empty")
    if "threshold" in data:
        thr = data["threshold"]
        if not isinstance(thr, dict) or "metric" not in thr or "value" not in thr:
            fail(msgs, "V-1: threshold must be an object with 'metric' and 'value'")

    # --- V-2: variance baseline is real structure, not an assertion string ---
    if "variance_baseline" in data:
        vb = data["variance_baseline"]
        if not isinstance(vb, dict):
            fail(msgs, "V-2: variance_baseline must be an object")
        else:
            if not vb.get("runs_without_ablation"):
                fail(msgs, "V-2: variance_baseline.runs_without_ablation missing or zero")
            if not str(vb.get("observed_variance", "")).strip():
                fail(msgs, "V-2: variance_baseline.observed_variance empty")

    # --- V-3: ablation policy names a selection rule ---
    if "ablation_policy" in data and not str(data["ablation_policy"]).strip():
        fail(msgs, "V-3: ablation_policy is empty")

    # --- V-4: outcome discipline ---
    outcome = data.get("outcome")
    if outcome not in REQUIRED_OUTCOMES:
        fail(msgs, f"V-4: outcome must be one of {sorted(REQUIRED_OUTCOMES)}, got {outcome!r}")
    elif outcome == "indeterminate" and data.get("passed") is not False:
        fail(msgs, "V-4: outcome 'indeterminate' MUST carry passed=false (non-pass discipline)")

    # --- subject structure ---
    if "subject" in data:
        subj = data["subject"]
        if not isinstance(subj, dict):
            fail(msgs, "subject must be an object")
        else:
            subj_missing = REQUIRED_SUBJECT_KEYS - subj.keys()
            if subj_missing:
                fail(msgs, f"subject missing key(s): {', '.join(sorted(subj_missing))}")

    # --- drift check: spec_version vs spec's VERSION file ---
    if "spec_version" in data and spec_version is not None and data["spec_version"] != spec_version:
        fail(
            msgs,
            f"drift: vector spec_version {data['spec_version']!r} != spec VERSION {spec_version!r} "
            "(§7: report a drift error, do not silently pass)",
        )

    # --- honesty guardrail: no boolean flattening of the outcome axis ---
    if "passed" in data and not isinstance(data["passed"], bool):
        fail(msgs, "passed must be a boolean")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("vector", help="path to vector.json")
    ap.add_argument(
        "--spec-version-file",
        default=None,
        help="path to the spec's VERSION file (enables the §7 drift check)",
    )
    args = ap.parse_args()

    vec_path = Path(args.vector)
    if not vec_path.is_file():
        print(f"IO error: {vec_path} not found", file=sys.stderr)
        return 2

    try:
        data = json.loads(vec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Parse error: {vec_path} is not valid JSON: {exc}", file=sys.stderr)
        return 2

    spec_version = None
    if args.spec_version_file:
        sv_path = Path(args.spec_version_file)
        if sv_path.is_file():
            spec_version = sv_path.read_text(encoding="utf-8").strip()

    msgs = []
    check_vector(data, spec_version, msgs)

    if msgs:
        print("NON-CONFORMANT:", file=sys.stderr)
        for m in msgs:
            print(f"  - {m}", file=sys.stderr)
        return 1

    print(f"OK: {data.get('vector_id', '<unnamed>')} — V-1..V-4 discipline intact (conclusion not judged)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
