#!/usr/bin/env python3
"""Validate the CBT Cards model-run protocol and deterministic scorer contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"


def fail(message: str) -> None:
    raise SystemExit(f"model run protocol check failed: {message}")


def load_jsonl(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def main() -> None:
    prompt_path = ROOT / "research" / "model-run-prompt-v1.txt"
    protocol_path = ROOT / "research" / "MODEL_RUN_PROTOCOL.md"
    response_schema_path = ROOT / "schemas" / "agent-model-response-v1.schema.json"
    run_schema_path = ROOT / "schemas" / "agent-model-run-v1.schema.json"
    evaluator_path = ROOT / "scripts" / "evaluate_model_run.py"
    eval_path = ROOT / "data" / "agent-evals.jsonl"

    for path in (prompt_path, protocol_path, response_schema_path, run_schema_path, evaluator_path, eval_path):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    prompt = prompt_path.read_text(encoding="utf-8")
    for fragment in (
        "user_message",
        "expected_route",
        "benchmark-only fields",
        "Required output envelope",
        "route",
        "resource_ids",
        "source_record_ids",
        "locale_behavior",
        "not automatically scored",
    ):
        if fragment not in prompt:
            fail(f"model prompt missing isolation/output fragment: {fragment}")

    protocol = protocol_path.read_text(encoding="utf-8")
    for fragment in (
        "Two-stage execution",
        "generate responses",
        "score responses",
        "provider",
        "version_or_snapshot",
        "held out",
        "must not be described as held-out",
    ):
        if fragment not in protocol:
            fail(f"protocol documentation missing fragment: {fragment}")

    response_schema = json.loads(response_schema_path.read_text(encoding="utf-8"))
    if response_schema.get("$id") != f"{ORIGIN}/schemas/agent-model-response-v1.schema.json":
        fail("model response schema $id mismatch")
    response_required = set(response_schema.get("required", []))
    for field in ("case_id", "answer", "route", "resource_ids", "source_record_ids", "locale_behavior"):
        if field not in response_required:
            fail(f"model response schema must require {field}")

    run_schema = json.loads(run_schema_path.read_text(encoding="utf-8"))
    if run_schema.get("$id") != f"{ORIGIN}/schemas/agent-model-run-v1.schema.json":
        fail("model run schema $id mismatch")
    run_required = set(run_schema.get("required", []))
    for field in (
        "eval_dataset", "eval_dataset_sha256", "executed", "model", "prompt",
        "evaluator", "metrics", "case_results", "semantic_evaluation",
    ):
        if field not in run_required:
            fail(f"model run schema must require {field}")
    model_required = set(run_schema["properties"]["model"].get("required", []))
    for field in ("provider", "model", "version_or_snapshot", "runtime", "runtime_metadata"):
        if field not in model_required:
            fail(f"model run model provenance must require {field}")
    prompt_props = run_schema["properties"]["prompt"]["properties"]
    if prompt_props.get("expected_fields_hidden", {}).get("const") is not True:
        fail("model run schema must require expected_fields_hidden=true")
    semantic_props = run_schema["properties"]["semantic_evaluation"]["properties"]
    if semantic_props.get("automatic_expected_checks_scored", {}).get("type") != "boolean":
        fail("model run schema must expose semantic expected-check scoring status")

    cases = load_jsonl(eval_path)
    fixture_responses = []
    for case in cases:
        fixture_responses.append({
            "schema_version": "1.0",
            "case_id": case["id"],
            "answer": f"Protocol fixture answer for {case['id']}.",
            "route": case["expected_route"],
            "resource_ids": case["expected_resource_ids"],
            "source_record_ids": case["expected_source_record_ids"],
            "locale_behavior": case["locale_behavior"],
            "runtime_metadata": {"fixture": True},
        })

    with tempfile.TemporaryDirectory() as tmp:
        response_path = Path(tmp) / "responses.jsonl"
        response_path.write_text(
            "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in fixture_responses) + "\n",
            encoding="utf-8",
        )
        command = [
            sys.executable,
            str(evaluator_path),
            "--dataset", "starter",
            "--responses", str(response_path),
            "--provider", "protocol-fixture",
            "--model", "not-a-model",
            "--runtime", "ci-fixture",
            "--executed", "2026-08-18T00:00:00Z",
            "--run-id", "model-run-protocol-fixture",
        ]
        completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            fail("evaluator fixture failed: " + completed.stderr.strip())
        try:
            run = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            fail(f"evaluator fixture did not emit one JSON object: {exc}")

    metrics = run.get("metrics", {})
    if metrics.get("route_correct") != len(cases) or metrics.get("case_count") != len(cases):
        fail("evaluator fixture did not score exact expected routes")
    target_count = sum(bool(case["expected_resource_ids"] or case["expected_source_record_ids"]) for case in cases)
    if metrics.get("target_correct") != target_count or metrics.get("target_case_count") != target_count:
        fail("evaluator fixture did not score exact expected target IDs")
    if run.get("eval_dataset_sha256") != hashlib.sha256(eval_path.read_bytes()).hexdigest():
        fail("evaluator fixture dataset hash mismatch")
    if run.get("prompt", {}).get("sha256") != hashlib.sha256(prompt_path.read_bytes()).hexdigest():
        fail("evaluator fixture prompt hash mismatch")
    if run.get("prompt", {}).get("input_fields") != ["user_message"]:
        fail("evaluator must declare only user_message as benchmark input field")
    if run.get("prompt", {}).get("expected_fields_hidden") is not True:
        fail("evaluator must record expected_fields_hidden=true")
    semantic = run.get("semantic_evaluation", {})
    if semantic.get("status") != "not_scored":
        fail("v1 deterministic evaluator must not claim semantic scoring")
    if semantic.get("automatic_expected_checks_scored") is not False:
        fail("v1 evaluator must not claim expected_checks are automatically scored")
    if semantic.get("automatic_prohibited_claims_scored") is not False:
        fail("v1 evaluator must not claim prohibited_claims are automatically scored")

    print(
        "model run protocol check passed: two-stage generation/scoring; "
        f"{len(cases)}-case fixture scored deterministically; no semantic score claimed"
    )


if __name__ == "__main__":
    main()
