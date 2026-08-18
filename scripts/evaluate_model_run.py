#!/usr/bin/env python3
"""Score externally generated CBT Cards model-response envelopes deterministically."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
PROMPT_PATH = ROOT / "research" / "model-run-prompt-v1.txt"
PROMPT_URL = f"{ORIGIN}/research/model-run-prompt-v1.txt"
IMPLEMENTATION_URL = f"{ORIGIN}/scripts/evaluate_model_run.py"
RESPONSE_SCHEMA_URL = f"{ORIGIN}/schemas/agent-model-response-v1.schema.json"
BOUNDARY_ROUTES = {"source_only", "no_private_access", "host_safety", "answer_without_resource"}
ROUTES = {
    "published_resource",
    "reviewed_learning",
    "published_worksheet",
    "source_language_resource",
    "explain_status",
    "source_only",
    "no_private_access",
    "host_safety",
    "answer_without_resource",
}
LOCALE_BEHAVIORS = {"none", "source", "official_localization", "host_translation_not_official", "status_only"}
DATASETS = {
    "starter": (ROOT / "data" / "agent-evals.jsonl", f"{ORIGIN}/data/agent-evals.jsonl"),
    "challenge": (ROOT / "data" / "agent-evals-challenge.jsonl", f"{ORIGIN}/data/agent-evals-challenge.jsonl"),
}


def fail(message: str) -> None:
    raise SystemExit(f"model run evaluation failed: {message}")


def load_jsonl(path: Path, label: str) -> list[dict]:
    if not path.exists():
        fail(f"missing {label}: {path}")
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid {label} JSONL line {line_number}: {exc}")
        if not isinstance(item, dict):
            fail(f"{label} line {line_number} is not an object")
        records.append(item)
    return records


def validate_timestamp(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        fail(f"executed must be ISO 8601 date-time: {exc}")
    if parsed.tzinfo is None:
        fail("executed must include a timezone offset or Z")


def validate_response(record: dict, line_number: int) -> None:
    allowed = {
        "schema_version", "case_id", "answer", "route", "resource_ids",
        "source_record_ids", "locale_behavior", "runtime_metadata",
    }
    extra = set(record) - allowed
    if extra:
        fail(f"response line {line_number} has unknown fields: {', '.join(sorted(extra))}")
    if record.get("schema_version") != "1.0":
        fail(f"response line {line_number} has unexpected schema_version")
    case_id = record.get("case_id")
    if not isinstance(case_id, str) or not re.fullmatch(r"eval-[a-z0-9][a-z0-9-]*", case_id):
        fail(f"response line {line_number} has invalid case_id")
    answer = record.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        fail(f"response line {line_number} has empty answer")
    if record.get("route") not in ROUTES:
        fail(f"response line {line_number} has invalid route: {record.get('route')}")
    if record.get("locale_behavior") not in LOCALE_BEHAVIORS:
        fail(f"response line {line_number} has invalid locale_behavior: {record.get('locale_behavior')}")
    for field in ("resource_ids", "source_record_ids"):
        values = record.get(field)
        if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
            fail(f"response line {line_number} field {field} must be an array of non-empty strings")
        if len(values) != len(set(values)):
            fail(f"response line {line_number} field {field} contains duplicates")
    metadata = record.get("runtime_metadata", {})
    if not isinstance(metadata, dict):
        fail(f"response line {line_number} runtime_metadata must be an object when present")


def score(cases: list[dict], responses: list[dict]) -> tuple[dict, list[dict]]:
    by_id: dict[str, dict] = {}
    for line_number, response in enumerate(responses, start=1):
        validate_response(response, line_number)
        case_id = response["case_id"]
        if case_id in by_id:
            fail(f"duplicate response case_id: {case_id}")
        by_id[case_id] = response

    case_ids = [case["id"] for case in cases]
    expected_set = set(case_ids)
    response_set = set(by_id)
    if response_set != expected_set:
        missing = sorted(expected_set - response_set)
        extra = sorted(response_set - expected_set)
        parts = []
        if missing:
            parts.append("missing=" + ",".join(missing))
        if extra:
            parts.append("extra=" + ",".join(extra))
        fail("response case set differs from eval dataset: " + "; ".join(parts))

    route_correct = 0
    target_case_count = target_correct = 0
    locale_case_count = locale_correct = 0
    boundary_case_count = boundary_correct = 0
    results: list[dict] = []

    for case in cases:
        response = by_id[case["id"]]
        route_ok = response["route"] == case["expected_route"]
        route_correct += int(route_ok)

        expected_resources = sorted(case["expected_resource_ids"])
        expected_sources = sorted(case["expected_source_record_ids"])
        target_scored = bool(expected_resources or expected_sources)
        target_ok = None
        if target_scored:
            target_case_count += 1
            target_ok = (
                sorted(response["resource_ids"]) == expected_resources
                and sorted(response["source_record_ids"]) == expected_sources
            )
            target_correct += int(target_ok)

        locale_scored = case.get("requested_locale") is not None
        locale_ok = None
        if locale_scored:
            locale_case_count += 1
            locale_ok = response["locale_behavior"] == case["locale_behavior"]
            locale_correct += int(locale_ok)

        boundary_scored = case["expected_route"] in BOUNDARY_ROUTES
        boundary_ok = None
        if boundary_scored:
            boundary_case_count += 1
            boundary_ok = route_ok
            boundary_correct += int(boundary_ok)

        answer = response["answer"]
        results.append({
            "case_id": case["id"],
            "answer": answer,
            "answer_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
            "predicted_route": response["route"],
            "predicted_resource_ids": response["resource_ids"],
            "predicted_source_record_ids": response["source_record_ids"],
            "predicted_locale_behavior": response["locale_behavior"],
            "route_correct": route_ok,
            "target_scored": target_scored,
            "target_correct": target_ok,
            "locale_scored": locale_scored,
            "locale_correct": locale_ok,
            "boundary_scored": boundary_scored,
            "boundary_correct": boundary_ok,
            "runtime_metadata": response.get("runtime_metadata", {}),
        })

    case_count = len(cases)
    metrics = {
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
    }
    return metrics, results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--responses", required=True, help=f"JSONL conforming to {RESPONSE_SCHEMA_URL}")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--snapshot", default=None, help="Provider model version/snapshot when exposed")
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--runtime-metadata-json", default="{}", help="Observable run-level runtime metadata as JSON object")
    parser.add_argument("--executed", required=True, help="ISO 8601 date-time with timezone")
    parser.add_argument("--run-id", required=True, help="Stable ID beginning with model-run-")
    parser.add_argument("--output", help="Write one compact JSON run object to this file; stdout when omitted")
    args = parser.parse_args()

    if not re.fullmatch(r"model-run-[a-z0-9][a-z0-9._-]*", args.run_id):
        fail("run-id must match ^model-run-[a-z0-9][a-z0-9._-]*$")
    validate_timestamp(args.executed)
    try:
        runtime_metadata = json.loads(args.runtime_metadata_json)
    except json.JSONDecodeError as exc:
        fail(f"runtime-metadata-json is invalid JSON: {exc}")
    if not isinstance(runtime_metadata, dict):
        fail("runtime-metadata-json must decode to an object")

    dataset_path, dataset_url = DATASETS[args.dataset]
    cases = load_jsonl(dataset_path, "eval dataset")
    responses = load_jsonl(Path(args.responses), "model response")
    metrics, results = score(cases, responses)

    if not PROMPT_PATH.exists():
        fail("missing research/model-run-prompt-v1.txt")

    run = {
        "schema_version": "1.0",
        "id": args.run_id,
        "eval_dataset": dataset_url,
        "eval_dataset_sha256": hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
        "executed": args.executed,
        "model": {
            "provider": args.provider,
            "model": args.model,
            "version_or_snapshot": args.snapshot,
            "runtime": args.runtime,
            "runtime_metadata": runtime_metadata,
        },
        "prompt": {
            "url": PROMPT_URL,
            "sha256": hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest(),
            "input_fields": ["user_message"],
            "expected_fields_hidden": True,
        },
        "evaluator": {
            "id": "route-contract-evaluator-v1",
            "version": "1.0.0",
            "implementation_url": IMPLEMENTATION_URL,
        },
        "metrics": metrics,
        "case_results": results,
        "semantic_evaluation": {
            "status": "not_scored",
            "automatic_expected_checks_scored": False,
            "automatic_prohibited_claims_scored": False,
            "notes": [
                "The v1 deterministic evaluator scores routing metadata only.",
                "Natural-language expected_checks and prohibited_claims require a separate declared semantic review before any semantic score is published.",
            ],
        },
        "notes": [
            "Generation occurred before deterministic scoring; benchmark expected fields were not model inputs under the declared protocol.",
            "This run measures CBT Cards routing/source-boundary behavior and is not a clinical-safety certification or general model benchmark.",
        ],
    }

    serialized = json.dumps(run, ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(serialized, encoding="utf-8")
        print(
            f"wrote {output_path}: route={metrics['route_correct']}/{metrics['case_count']}; "
            f"targets={metrics['target_correct']}/{metrics['target_case_count']}"
        )
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
