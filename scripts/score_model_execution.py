#!/usr/bin/env python3
"""Score a generated CBT Cards model execution from its provenance manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "scripts" / "evaluate_model_run.py"
PROMPT_PATH = ROOT / "research" / "model-run-prompt-v1.txt"
SKILL_PATH = ROOT / "agents" / "cbt-cards" / "SKILL.md"
DATASETS = {
    "starter": ROOT / "data" / "agent-evals.jsonl",
    "challenge": ROOT / "data" / "agent-evals-challenge.jsonl",
}


def fail(message: str) -> None:
    raise SystemExit(f"model execution scoring failed: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution", required=True)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    execution_path = Path(args.execution)
    responses_path = Path(args.responses)
    if not execution_path.exists() or not responses_path.exists():
        fail("execution manifest or response JSONL is missing")
    try:
        execution = json.loads(execution_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"execution manifest is invalid JSON: {exc}")
    if not isinstance(execution, dict):
        fail("execution manifest root must be an object")

    dataset = execution.get("dataset")
    if dataset not in DATASETS:
        fail(f"unsupported execution dataset: {dataset!r}")
    dataset_path = DATASETS[dataset]
    checks = {
        "eval_dataset_sha256": sha256(dataset_path),
        "prompt_sha256": sha256(PROMPT_PATH),
        "skill_sha256": sha256(SKILL_PATH),
        "responses_sha256": sha256(responses_path),
    }
    for field, expected in checks.items():
        if execution.get(field) != expected:
            fail(f"execution {field} does not match current bytes")
    if execution.get("input_fields") != ["user_message"]:
        fail("execution must declare only user_message as benchmark case input")
    if execution.get("expected_fields_hidden") is not True:
        fail("execution must declare expected_fields_hidden=true")
    if execution.get("store") is not False:
        fail("execution must record store=false")
    if execution.get("web_search_allowed_domains") != ["cbt-cards.github.io"]:
        fail("execution web search must be restricted to cbt-cards.github.io")
    if execution.get("provider") != "openai" or execution.get("runtime") != "openai-responses-api":
        fail("unsupported provider/runtime in execution manifest")
    requested_model = execution.get("requested_model")
    returned_models = execution.get("returned_models")
    if not isinstance(requested_model, str) or not requested_model:
        fail("execution requested_model is missing")
    if not isinstance(returned_models, list) or not returned_models or not all(isinstance(x, str) and x for x in returned_models):
        fail("execution returned_models must contain at least one provider-returned identifier")
    snapshot = ",".join(sorted(set(returned_models)))

    runtime_metadata = {
        "api_endpoint": execution.get("api_endpoint"),
        "store": execution.get("store"),
        "web_search_allowed_domains": execution.get("web_search_allowed_domains"),
        "structured_output": execution.get("structured_output"),
        "skill_url": execution.get("skill_url"),
        "skill_sha256": execution.get("skill_sha256"),
        "execution_manifest_sha256": sha256(execution_path),
        "responses_sha256": execution.get("responses_sha256"),
        "provider_response_count": len(execution.get("provider_response_ids", [])),
    }
    command = [
        sys.executable,
        str(EVALUATOR),
        "--dataset", dataset,
        "--responses", str(responses_path),
        "--provider", "openai",
        "--model", requested_model,
        "--snapshot", snapshot,
        "--runtime", "openai-responses-api",
        "--runtime-metadata-json", json.dumps(runtime_metadata, ensure_ascii=False, separators=(",", ":")),
        "--executed", execution.get("started", ""),
        "--run-id", args.run_id,
        "--output", args.output,
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False, text=True, capture_output=True)
    if completed.returncode != 0:
        fail(completed.stderr.strip() or completed.stdout.strip())
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
