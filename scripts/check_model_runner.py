#!/usr/bin/env python3
"""Validate the isolated OpenAI model-run adapter without making an API call."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_model_openai.py"
SCORER_PATH = ROOT / "scripts" / "score_model_execution.py"
CANDIDATE_CHECK_PATH = ROOT / "scripts" / "check_model_run_candidate.py"
PROMPT_PATH = ROOT / "research" / "model-run-prompt-v1.txt"
SKILL_PATH = ROOT / "agents" / "cbt-cards" / "SKILL.md"
STARTER_PATH = ROOT / "data" / "agent-evals.jsonl"
ORIGIN = "https://cbt-cards.github.io"


def fail(message: str) -> None:
    raise SystemExit(f"model runner check failed: {message}")


def load_runner():
    spec = importlib.util.spec_from_file_location("run_model_openai", RUNNER_PATH)
    if spec is None or spec.loader is None:
        fail("could not import run_model_openai.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checked(command: list[str], label: str) -> str:
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        fail(f"{label} failed: {(completed.stderr or completed.stdout).strip()}")
    return completed.stdout.strip()


def main() -> None:
    for path in (RUNNER_PATH, SCORER_PATH, CANDIDATE_CHECK_PATH, PROMPT_PATH, SKILL_PATH, STARTER_PATH):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    runner = load_runner()

    hidden_values = {
        "expected_route": "SECRET_EXPECTED_ROUTE",
        "expected_resource_ids": ["SECRET_RESOURCE_ID"],
        "expected_source_record_ids": ["SECRET_SOURCE_ID"],
        "requested_locale": "SECRET_LOCALE",
        "locale_behavior": "SECRET_LOCALE_BEHAVIOR",
        "expected_checks": ["SECRET_EXPECTED_CHECK"],
        "prohibited_claims": ["SECRET_PROHIBITED_CLAIM"],
        "rationale": "SECRET_RATIONALE",
        "tags": ["SECRET_TAG"],
    }
    fake_case = {
        "id": "eval-fixture-no-leak",
        "user_message": "Please give me a CBT Cards reflection prompt.",
        **hidden_values,
    }
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    skill = SKILL_PATH.read_text(encoding="utf-8")
    payload = runner.build_payload(
        model="test-model",
        user_message=fake_case["user_message"],
        prompt_text=prompt,
        skill_text=skill,
    )

    if payload.get("model") != "test-model":
        fail("model identifier not forwarded")
    if payload.get("store") is not False:
        fail("runner must set store=false")
    inputs = payload.get("input")
    if not isinstance(inputs, list) or len(inputs) != 3:
        fail("runner must provide two developer messages and one user message")
    user_inputs = [item for item in inputs if item.get("role") == "user"]
    if len(user_inputs) != 1:
        fail("runner must provide exactly one user message")
    user_content = user_inputs[0].get("content")
    if user_content != [{"type": "input_text", "text": fake_case["user_message"]}]:
        fail("benchmark user input must be exactly user_message")

    serialized = json.dumps(payload, ensure_ascii=False)
    for value in (
        "SECRET_EXPECTED_ROUTE",
        "SECRET_RESOURCE_ID",
        "SECRET_SOURCE_ID",
        "SECRET_LOCALE",
        "SECRET_LOCALE_BEHAVIOR",
        "SECRET_EXPECTED_CHECK",
        "SECRET_PROHIBITED_CLAIM",
        "SECRET_RATIONALE",
        "SECRET_TAG",
    ):
        if value in serialized:
            fail(f"benchmark-only value leaked into model request: {value}")

    expected_tools = [{
        "type": "web_search",
        "filters": {"allowed_domains": ["cbt-cards.github.io"]},
        "search_context_size": "medium",
    }]
    if payload.get("tools") != expected_tools:
        fail("web search must be restricted to cbt-cards.github.io")

    text_format = payload.get("text", {}).get("format", {})
    if text_format.get("type") != "json_schema" or text_format.get("strict") is not True:
        fail("runner must use strict JSON Schema structured output")
    schema = text_format.get("schema")
    if not isinstance(schema, dict) or schema.get("additionalProperties") is not False:
        fail("structured output schema must reject additional properties")
    required = set(schema.get("required", []))
    if required != {"answer", "route", "resource_ids", "source_record_ids", "locale_behavior"}:
        fail("structured output required fields differ from model-run envelope")
    if set(schema.get("properties", {}).get("route", {}).get("enum", [])) != set(runner.ROUTES):
        fail("structured output route enum differs from evaluator routes")
    if set(schema.get("properties", {}).get("locale_behavior", {}).get("enum", [])) != set(runner.LOCALE_BEHAVIORS):
        fail("structured output locale enum differs from evaluator contract")

    # Exercise the post-generation pipeline with a synthetic artifact. This fixture is
    # intentionally created after the leak test and is not a model benchmark result.
    cases = load_jsonl(STARTER_PATH)
    fixture_records = [
        {
            "schema_version": "1.0",
            "case_id": case["id"],
            "answer": f"Synthetic adapter fixture for {case['id']}.",
            "route": case["expected_route"],
            "resource_ids": case["expected_resource_ids"],
            "source_record_ids": case["expected_source_record_ids"],
            "locale_behavior": case["locale_behavior"],
            "runtime_metadata": {
                "provider_response_id": f"fixture-{case['id']}",
                "returned_model": "fixture-model-2026-08-18",
                "response_status": "completed",
                "web_search_call_count": 0,
                "usage": {},
                "store": False,
                "web_search_allowed_domains": ["cbt-cards.github.io"],
            },
        }
        for case in cases
    ]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        responses_path = tmp_path / "model-responses.jsonl"
        execution_path = tmp_path / "model-execution.json"
        run_path = tmp_path / "model-run.json"
        responses_path.write_text(
            "\n".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in fixture_records) + "\n",
            encoding="utf-8",
        )
        execution = {
            "schema_version": "1.0",
            "provider": "openai",
            "requested_model": "fixture-model",
            "returned_models": ["fixture-model-2026-08-18"],
            "runtime": "openai-responses-api",
            "api_endpoint": runner.API_URL,
            "dataset": "starter",
            "eval_dataset": f"{ORIGIN}/data/agent-evals.jsonl",
            "eval_dataset_sha256": sha256(STARTER_PATH),
            "prompt_url": f"{ORIGIN}/research/model-run-prompt-v1.txt",
            "prompt_sha256": sha256(PROMPT_PATH),
            "skill_url": f"{ORIGIN}/agents/cbt-cards/SKILL.md",
            "skill_sha256": sha256(SKILL_PATH),
            "input_fields": ["user_message"],
            "expected_fields_hidden": True,
            "store": False,
            "web_search_allowed_domains": ["cbt-cards.github.io"],
            "structured_output": "cbt_cards_model_response_v1",
            "started": "2026-08-18T00:00:00Z",
            "completed": "2026-08-18T00:01:00Z",
            "response_count": len(fixture_records),
            "responses_sha256": sha256(responses_path),
            "provider_response_ids": [record["runtime_metadata"]["provider_response_id"] for record in fixture_records],
        }
        execution_path.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        run_checked(
            [
                sys.executable,
                str(SCORER_PATH),
                "--execution", str(execution_path),
                "--responses", str(responses_path),
                "--run-id", "model-run-openai-fixture-ci",
                "--output", str(run_path),
            ],
            "scorer wrapper fixture",
        )
        candidate_output = run_checked(
            [
                sys.executable,
                str(CANDIDATE_CHECK_PATH),
                "--execution", str(execution_path),
                "--responses", str(responses_path),
                "--run", str(run_path),
            ],
            "candidate gate fixture",
        )
        run = json.loads(run_path.read_text(encoding="utf-8"))
        if run.get("metrics", {}).get("route_correct") != len(cases):
            fail("synthetic post-generation pipeline did not preserve exact fixture routes")
        if run.get("semantic_evaluation", {}).get("status") != "not_scored":
            fail("synthetic post-generation pipeline incorrectly claimed semantic scoring")
        if "candidate check passed" not in candidate_output:
            fail("candidate gate did not report success")

    print(
        "model runner check passed: user_message-only case input, strict structured output, "
        "store=false, CBT Cards-only web search, no benchmark answer leakage, artifact/scoring gate exercised"
    )


if __name__ == "__main__":
    main()
