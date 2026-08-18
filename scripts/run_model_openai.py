#!/usr/bin/env python3
"""Generate CBT Cards model-response envelopes with the OpenAI Responses API.

This script is generation-only. It deliberately never reads benchmark expected fields
as model inputs and does not score the responses it creates.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
API_URL = "https://api.openai.com/v1/responses"
PROMPT_PATH = ROOT / "research" / "model-run-prompt-v1.txt"
SKILL_PATH = ROOT / "agents" / "cbt-cards" / "SKILL.md"
DATASETS = {
    "starter": (ROOT / "data" / "agent-evals.jsonl", f"{ORIGIN}/data/agent-evals.jsonl"),
    "challenge": (ROOT / "data" / "agent-evals-challenge.jsonl", f"{ORIGIN}/data/agent-evals-challenge.jsonl"),
}
ROUTES = [
    "published_resource",
    "reviewed_learning",
    "published_worksheet",
    "source_language_resource",
    "explain_status",
    "source_only",
    "no_private_access",
    "host_safety",
    "answer_without_resource",
]
LOCALE_BEHAVIORS = [
    "none",
    "source",
    "official_localization",
    "host_translation_not_official",
    "status_only",
]
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "route": {"type": "string", "enum": ROUTES},
        "resource_ids": {"type": "array", "items": {"type": "string"}},
        "source_record_ids": {"type": "array", "items": {"type": "string"}},
        "locale_behavior": {"type": "string", "enum": LOCALE_BEHAVIORS},
    },
    "required": ["answer", "route", "resource_ids", "source_record_ids", "locale_behavior"],
    "additionalProperties": False,
}


def fail(message: str) -> None:
    raise SystemExit(f"OpenAI model generation failed: {message}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL at {path.relative_to(ROOT)}:{line_number}: {exc}")
        if not isinstance(item, dict):
            fail(f"non-object record at {path.relative_to(ROOT)}:{line_number}")
        if not isinstance(item.get("id"), str) or not isinstance(item.get("user_message"), str):
            fail(f"dataset line {line_number} lacks id/user_message")
        records.append(item)
    return records


def build_payload(*, model: str, user_message: str, prompt_text: str, skill_text: str) -> dict:
    """Build one isolated request. Only user_message is taken from the eval case."""
    return {
        "model": model,
        "store": False,
        "input": [
            {
                "role": "developer",
                "content": [{"type": "input_text", "text": prompt_text}],
            },
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": "CBT Cards public skill under evaluation:\n\n" + skill_text,
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_message}],
            },
        ],
        "tools": [
            {
                "type": "web_search",
                "filters": {"allowed_domains": ["cbt-cards.github.io"]},
                "search_context_size": "medium",
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "cbt_cards_model_response_v1",
                "schema": OUTPUT_SCHEMA,
                "strict": True,
            }
        },
    }


def api_request(payload: dict, api_key: str, timeout: int, retries: int) -> dict:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "CBT-Cards-agent-eval/1.0",
    }
    for attempt in range(retries + 1):
        req = request.Request(API_URL, data=body, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=timeout) as response:
                raw = response.read()
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                fail("Responses API returned a non-object JSON payload")
            return parsed
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if retryable and attempt < retries:
                time.sleep(min(2 ** attempt, 8))
                continue
            fail(f"Responses API HTTP {exc.code}: {detail[:1000]}")
        except error.URLError as exc:
            if attempt < retries:
                time.sleep(min(2 ** attempt, 8))
                continue
            fail(f"Responses API network error: {exc}")
        except json.JSONDecodeError as exc:
            fail(f"Responses API returned invalid JSON: {exc}")
    fail("Responses API request exhausted retries")


def extract_output_text(response: dict) -> str:
    texts: list[str] = []
    refusals: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                texts.append(content["text"])
            elif content.get("type") == "refusal" and isinstance(content.get("refusal"), str):
                refusals.append(content["refusal"])
    if texts:
        return "\n".join(texts)
    if refusals:
        fail("model returned a refusal instead of the required structured envelope: " + " ".join(refusals)[:500])
    fail(f"Responses API returned no output_text; status={response.get('status')!r}")


def parse_envelope(text: str) -> dict:
    try:
        envelope = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"structured output is not valid JSON: {exc}")
    if not isinstance(envelope, dict):
        fail("structured output is not an object")
    required = set(OUTPUT_SCHEMA["required"])
    if set(envelope) != required:
        fail(f"structured output fields differ from contract: {sorted(envelope)}")
    if not isinstance(envelope["answer"], str) or not envelope["answer"].strip():
        fail("structured output answer is empty")
    if envelope["route"] not in ROUTES:
        fail(f"invalid route from model: {envelope['route']!r}")
    if envelope["locale_behavior"] not in LOCALE_BEHAVIORS:
        fail(f"invalid locale_behavior from model: {envelope['locale_behavior']!r}")
    for field in ("resource_ids", "source_record_ids"):
        values = envelope[field]
        if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
            fail(f"{field} must be an array of non-empty strings")
        if len(values) != len(set(values)):
            fail(f"{field} contains duplicates")
    return envelope


def response_runtime_metadata(response: dict) -> dict:
    output = response.get("output", [])
    web_search_calls = sum(
        1 for item in output if isinstance(item, dict) and item.get("type") == "web_search_call"
    )
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    return {
        "provider_response_id": response.get("id"),
        "returned_model": response.get("model"),
        "response_status": response.get("status"),
        "web_search_call_count": web_search_calls,
        "usage": usage,
        "store": False,
        "web_search_allowed_domains": ["cbt-cards.github.io"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--responses", required=True, help="Output JSONL path for generated response envelopes")
    parser.add_argument("--execution", required=True, help="Output JSON path for generation provenance")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--case-id", action="append", default=[], help="Debug only: generate selected case ID(s)")
    parser.add_argument("--dry-run", action="store_true", help="Validate request construction without calling the API")
    args = parser.parse_args()

    if not PROMPT_PATH.exists() or not SKILL_PATH.exists():
        fail("missing model-run prompt or current CBT Cards skill")
    dataset_path, dataset_url = DATASETS[args.dataset]
    cases = load_jsonl(dataset_path)
    if args.case_id:
        requested = set(args.case_id)
        cases = [case for case in cases if case["id"] in requested]
        found = {case["id"] for case in cases}
        if found != requested:
            fail("unknown --case-id value(s): " + ",".join(sorted(requested - found)))

    prompt_bytes = PROMPT_PATH.read_bytes()
    skill_bytes = SKILL_PATH.read_bytes()
    prompt_text = prompt_bytes.decode("utf-8")
    skill_text = skill_bytes.decode("utf-8")

    if args.dry_run:
        sample = cases[0]
        payload = build_payload(
            model=args.model,
            user_message=sample["user_message"],
            prompt_text=prompt_text,
            skill_text=skill_text,
        )
        plan = {
            "dataset": args.dataset,
            "case_count": len(cases),
            "sample_case_id": sample["id"],
            "request": payload,
            "note": "Dry-run only. No API request was made and no benchmark result was produced.",
        }
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        fail(f"missing API key environment variable: {args.api_key_env}")

    started = utc_now()
    responses: list[dict] = []
    returned_models: set[str] = set()
    provider_response_ids: list[str] = []

    for index, case in enumerate(cases, start=1):
        payload = build_payload(
            model=args.model,
            user_message=case["user_message"],
            prompt_text=prompt_text,
            skill_text=skill_text,
        )
        response = api_request(payload, api_key=api_key, timeout=args.timeout, retries=args.retries)
        envelope = parse_envelope(extract_output_text(response))
        metadata = response_runtime_metadata(response)
        returned_model = metadata.get("returned_model")
        if isinstance(returned_model, str) and returned_model:
            returned_models.add(returned_model)
        response_id = metadata.get("provider_response_id")
        if isinstance(response_id, str) and response_id:
            provider_response_ids.append(response_id)
        record = {
            "schema_version": "1.0",
            "case_id": case["id"],
            "answer": envelope["answer"],
            "route": envelope["route"],
            "resource_ids": envelope["resource_ids"],
            "source_record_ids": envelope["source_record_ids"],
            "locale_behavior": envelope["locale_behavior"],
            "runtime_metadata": metadata,
        }
        responses.append(record)
        print(f"generated {index}/{len(cases)} {case['id']}", flush=True)

    serialized = "\n".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in responses
    ) + "\n"
    responses_path = Path(args.responses)
    responses_path.parent.mkdir(parents=True, exist_ok=True)
    responses_path.write_text(serialized, encoding="utf-8")

    completed = utc_now()
    execution = {
        "schema_version": "1.0",
        "provider": "openai",
        "requested_model": args.model,
        "returned_models": sorted(returned_models),
        "runtime": "openai-responses-api",
        "api_endpoint": API_URL,
        "dataset": args.dataset,
        "eval_dataset": dataset_url,
        "eval_dataset_sha256": sha256_bytes(dataset_path.read_bytes()),
        "prompt_url": f"{ORIGIN}/research/model-run-prompt-v1.txt",
        "prompt_sha256": sha256_bytes(prompt_bytes),
        "skill_url": f"{ORIGIN}/agents/cbt-cards/SKILL.md",
        "skill_sha256": sha256_bytes(skill_bytes),
        "input_fields": ["user_message"],
        "expected_fields_hidden": True,
        "store": False,
        "web_search_allowed_domains": ["cbt-cards.github.io"],
        "structured_output": "cbt_cards_model_response_v1",
        "started": started,
        "completed": completed,
        "response_count": len(responses),
        "responses_sha256": sha256_bytes(serialized.encode("utf-8")),
        "provider_response_ids": provider_response_ids,
    }
    execution_path = Path(args.execution)
    execution_path.parent.mkdir(parents=True, exist_ok=True)
    execution_path.write_text(
        json.dumps(execution, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {responses_path} and {execution_path}")


if __name__ == "__main__":
    main()
