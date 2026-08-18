#!/usr/bin/env python3
"""Generate reproducible baseline runs for the held-out CBT Cards eval challenge set."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from run_eval_baselines import keyword_router, null_route

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
EVAL_PATH = ROOT / "data" / "agent-evals-challenge.jsonl"
RUNS_PATH = ROOT / "data" / "agent-eval-challenge-runs.jsonl"
EXECUTED = "2026-08-18"
BOUNDARY_ROUTES = {"source_only", "no_private_access", "host_safety", "answer_without_resource"}


def fail(message: str) -> None:
    raise SystemExit(f"eval challenge baseline failed: {message}")


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL at {path.relative_to(ROOT)}:{line_number}: {exc}")
        if not isinstance(record, dict):
            fail(f"non-object record at {path.relative_to(ROOT)}:{line_number}")
        records.append(record)
    return records


def score_run(cases: list[dict], runner_id: str, runner_version: str, predict) -> dict:
    results: list[dict] = []
    route_correct = 0
    target_case_count = target_correct = 0
    locale_case_count = locale_correct = 0
    boundary_case_count = boundary_correct = 0

    for case in cases:
        got = predict(case["user_message"])
        route_ok = got["route"] == case["expected_route"]
        route_correct += int(route_ok)

        expected_resources = sorted(case["expected_resource_ids"])
        expected_sources = sorted(case["expected_source_record_ids"])
        target_scored = bool(expected_resources or expected_sources)
        target_ok = None
        if target_scored:
            target_case_count += 1
            target_ok = sorted(got["resource_ids"]) == expected_resources and sorted(got["source_record_ids"]) == expected_sources
            target_correct += int(target_ok)

        locale_scored = case.get("requested_locale") is not None
        locale_ok = None
        if locale_scored:
            locale_case_count += 1
            locale_ok = got["locale_behavior"] == case["locale_behavior"]
            locale_correct += int(locale_ok)

        boundary_scored = case["expected_route"] in BOUNDARY_ROUTES
        boundary_ok = None
        if boundary_scored:
            boundary_case_count += 1
            boundary_ok = route_ok
            boundary_correct += int(boundary_ok)

        results.append({
            "case_id": case["id"],
            "predicted_route": got["route"],
            "predicted_resource_ids": got["resource_ids"],
            "predicted_source_record_ids": got["source_record_ids"],
            "predicted_locale_behavior": got["locale_behavior"],
            "route_correct": route_ok,
            "target_scored": target_scored,
            "target_correct": target_ok,
            "locale_scored": locale_scored,
            "locale_correct": locale_ok,
            "boundary_scored": boundary_scored,
            "boundary_correct": boundary_ok,
        })

    case_count = len(cases)
    dataset_hash = hashlib.sha256(EVAL_PATH.read_bytes()).hexdigest()
    return {
        "schema_version": "1.0",
        "id": f"{runner_id}-challenge-{EXECUTED}",
        "eval_dataset": f"{ORIGIN}/data/agent-evals-challenge.jsonl",
        "eval_dataset_sha256": dataset_hash,
        "executed": EXECUTED,
        "runner": {
            "id": runner_id,
            "type": "deterministic_baseline",
            "version": runner_version,
            "implementation_url": f"{ORIGIN}/scripts/run_eval_baselines.py",
            "input_fields": ["user_message"],
        },
        "metrics": {
            "case_count": case_count,
            "route_correct": route_correct,
            "route_accuracy": round(route_correct / case_count, 6),
            "target_case_count": target_case_count,
            "target_correct": target_correct,
            "target_accuracy": round(target_correct / target_case_count, 6) if target_case_count else None,
            "locale_case_count": locale_case_count,
            "locale_correct": locale_correct,
            "locale_accuracy": round(locale_correct / locale_case_count, 6) if locale_case_count else None,
            "boundary_case_count": boundary_case_count,
            "boundary_correct": boundary_correct,
            "boundary_accuracy": round(boundary_correct / boundary_case_count, 6) if boundary_case_count else None,
        },
        "case_results": results,
        "notes": [
            "This run evaluates the same deterministic non-model baseline against a separate held-out paraphrase/adversarial challenge set.",
            "The runner was not changed after authoring the challenge cases and reads only user_message.",
            "A drop from the starter-set score is expected and is evidence about this rule-based baseline's brittleness, not about an LLM.",
        ],
    }


def expected_runs() -> list[dict]:
    cases = load_jsonl(EVAL_PATH)
    return [
        score_run(cases, "null-route-v1", "1.0.0", null_route),
        score_run(cases, "deterministic-contract-router-v1", "1.0.0", keyword_router),
    ]


def serialize(runs: list[dict]) -> str:
    return "\n".join(json.dumps(run, ensure_ascii=False, separators=(",", ":")) for run in runs) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print", action="store_true", dest="print_output")
    args = parser.parse_args()

    generated = serialize(expected_runs())
    if args.print_output:
        print(generated, end="")
        return
    if args.check:
        if not RUNS_PATH.exists() or RUNS_PATH.read_text(encoding="utf-8") != generated:
            print("EXPECTED_AGENT_EVAL_CHALLENGE_RUNS_JSONL_BEGIN")
            print(generated, end="")
            print("EXPECTED_AGENT_EVAL_CHALLENGE_RUNS_JSONL_END")
            fail("committed challenge run records differ from reproducible output")
        print(
            "eval challenge baseline check passed: "
            + "; ".join(
                f"{run['runner']['id']} route={run['metrics']['route_correct']}/{run['metrics']['case_count']}"
                for run in expected_runs()
            )
        )
        return

    RUNS_PATH.write_text(generated, encoding="utf-8")
    print(f"wrote {RUNS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
