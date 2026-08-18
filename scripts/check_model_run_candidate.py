#!/usr/bin/env python3
"""Validate a scored CBT Cards model-run artifact before it can be published."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "research" / "model-run-prompt-v1.txt"
DATASETS = {
    "https://cbt-cards.github.io/data/agent-evals.jsonl": ROOT / "data" / "agent-evals.jsonl",
    "https://cbt-cards.github.io/data/agent-evals-challenge.jsonl": ROOT / "data" / "agent-evals-challenge.jsonl",
}


def fail(message: str) -> None:
    raise SystemExit(f"model run candidate check failed: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid {label}: {exc}")
    if not isinstance(value, dict):
        fail(f"{label} root must be an object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution", required=True)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--run", required=True)
    args = parser.parse_args()

    execution_path = Path(args.execution)
    responses_path = Path(args.responses)
    run_path = Path(args.run)
    execution = load_object(execution_path, "execution manifest")
    run = load_object(run_path, "model run")

    eval_dataset = run.get("eval_dataset")
    dataset_path = DATASETS.get(eval_dataset)
    if dataset_path is None:
        fail(f"unknown eval_dataset: {eval_dataset!r}")
    if run.get("eval_dataset_sha256") != sha256(dataset_path):
        fail("run eval_dataset_sha256 does not match repository dataset")
    if execution.get("eval_dataset") != eval_dataset:
        fail("execution and scored run reference different datasets")
    if execution.get("eval_dataset_sha256") != run.get("eval_dataset_sha256"):
        fail("execution and scored run dataset hashes differ")

    prompt = run.get("prompt")
    if not isinstance(prompt, dict):
        fail("run prompt provenance is missing")
    current_prompt_hash = sha256(PROMPT_PATH)
    if prompt.get("sha256") != current_prompt_hash or execution.get("prompt_sha256") != current_prompt_hash:
        fail("prompt hash does not match current model-run prompt")
    if prompt.get("input_fields") != ["user_message"] or prompt.get("expected_fields_hidden") is not True:
        fail("run does not preserve benchmark input isolation")
    if execution.get("input_fields") != ["user_message"] or execution.get("expected_fields_hidden") is not True:
        fail("execution manifest does not preserve benchmark input isolation")

    if execution.get("responses_sha256") != sha256(responses_path):
        fail("response JSONL hash does not match execution manifest")
    if execution.get("store") is not False:
        fail("execution must record store=false")
    if execution.get("web_search_allowed_domains") != ["cbt-cards.github.io"]:
        fail("execution web search was not restricted to the CBT Cards public domain")

    model = run.get("model")
    if not isinstance(model, dict):
        fail("run model provenance is missing")
    for field in ("provider", "model", "version_or_snapshot", "runtime"):
        value = model.get(field)
        if not isinstance(value, str) or not value:
            fail(f"run model provenance must contain {field}")
    if model.get("provider") != execution.get("provider"):
        fail("run provider differs from execution provider")
    if model.get("model") != execution.get("requested_model"):
        fail("run model differs from execution requested_model")

    evaluator = run.get("evaluator")
    if not isinstance(evaluator, dict) or evaluator.get("id") != "route-contract-evaluator-v1" or evaluator.get("version") != "1.0.0":
        fail("run evaluator provenance differs from v1 deterministic scorer")
    semantic = run.get("semantic_evaluation")
    if not isinstance(semantic, dict):
        fail("semantic_evaluation is missing")
    if semantic.get("status") != "not_scored":
        fail("v1 candidate must not claim semantic scoring")
    if semantic.get("automatic_expected_checks_scored") is not False:
        fail("v1 candidate must not claim automatic expected-check scoring")
    if semantic.get("automatic_prohibited_claims_scored") is not False:
        fail("v1 candidate must not claim automatic prohibited-claim scoring")

    case_results = run.get("case_results")
    metrics = run.get("metrics")
    if not isinstance(case_results, list) or not isinstance(metrics, dict):
        fail("run case_results or metrics missing")
    if metrics.get("case_count") != len(case_results):
        fail("metrics case_count differs from case_results length")
    if len(case_results) != execution.get("response_count"):
        fail("scored run case count differs from generated response count")

    print(
        "model run candidate check passed: hashes/provenance aligned; "
        f"route={metrics.get('route_correct')}/{metrics.get('case_count')}; semantic score not claimed"
    )


if __name__ == "__main__":
    main()
