#!/usr/bin/env python3
"""Validate the isolated OpenAI model-run adapter without making an API call."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_model_openai.py"
PROMPT_PATH = ROOT / "research" / "model-run-prompt-v1.txt"
SKILL_PATH = ROOT / "agents" / "cbt-cards" / "SKILL.md"


def fail(message: str) -> None:
    raise SystemExit(f"model runner check failed: {message}")


def load_runner():
    spec = importlib.util.spec_from_file_location("run_model_openai", RUNNER_PATH)
    if spec is None or spec.loader is None:
        fail("could not import run_model_openai.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    for path in (RUNNER_PATH, PROMPT_PATH, SKILL_PATH):
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

    tools = payload.get("tools")
    expected_tools = [{
        "type": "web_search",
        "filters": {"allowed_domains": ["cbt-cards.github.io"]},
        "search_context_size": "medium",
    }]
    if tools != expected_tools:
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
    route_enum = set(schema.get("properties", {}).get("route", {}).get("enum", []))
    if route_enum != set(runner.ROUTES):
        fail("structured output route enum differs from evaluator routes")
    locale_enum = set(schema.get("properties", {}).get("locale_behavior", {}).get("enum", []))
    if locale_enum != set(runner.LOCALE_BEHAVIORS):
        fail("structured output locale enum differs from evaluator contract")

    print(
        "model runner check passed: user_message-only case input, strict structured output, "
        "store=false, CBT Cards-only web search, no benchmark answer leakage"
    )


if __name__ == "__main__":
    main()
