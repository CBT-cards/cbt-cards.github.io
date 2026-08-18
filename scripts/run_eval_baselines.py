#!/usr/bin/env python3
"""Generate reproducible non-model baselines for the CBT Cards agent eval set."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
EVAL_PATH = ROOT / "data" / "agent-evals.jsonl"
RUNS_PATH = ROOT / "data" / "agent-eval-runs.jsonl"
EXECUTED = "2026-08-18"
BOUNDARY_ROUTES = {"source_only", "no_private_access", "host_safety", "answer_without_resource"}


def fail(message: str) -> None:
    raise SystemExit(f"eval baseline failed: {message}")


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


def prediction(route: str, resources: list[str] | None = None, sources: list[str] | None = None, locale_behavior: str = "none") -> dict:
    return {
        "route": route,
        "resource_ids": resources or [],
        "source_record_ids": sources or [],
        "locale_behavior": locale_behavior,
    }


def null_route(_: str) -> dict:
    return prediction("answer_without_resource")


def keyword_router(message: str) -> dict:
    text = message.casefold()

    if "immediate danger" in text:
        return prediction("host_safety")
    if "mental disorder" in text and "worksheet" in text:
        return prediction("answer_without_resource")
    if ("read my" in text and "journal" in text) or ("pull my" in text and "mood" in text and "stress" in text):
        return prediction("no_private_access")

    if "translations.jsonl" in text and ("official" in text or "published" in text):
        return prediction("explain_status", locale_behavior="status_only")

    if "protocol" in text:
        match = re.search(r"protocol-([0-9]+)", text)
        source_id = f"protocol-{match.group(1)}" if match else None
        if source_id is None and "fear of judgment" in text:
            source_id = "protocol-2"
        if source_id is None and "fear of failure" in text:
            source_id = "protocol-10"
        return prediction("source_only", sources=[source_id] if source_id else [])

    if any("а" <= char <= "я" or char == "ё" for char in text):
        if "дневник" in text and "мысл" in text:
            return prediction("source_language_resource", ["cbt-thought-record"], locale_behavior="host_translation_not_official")
        if "мысл" in text and ("факт" in text or "≠" in message):
            return prediction("source_language_resource", ["source-card-21"], locale_behavior="host_translation_not_official")

    if "deutsche" in text or "auf deutsch" in text or "gibt es" in text:
        if "worry time" in text:
            return prediction("source_language_resource", ["worry-time"], locale_behavior="host_translation_not_official")

    if "worksheet" in text or "form" in text or "fields one by one" in text or "step by step in the browser" in text:
        if "thought record" in text:
            return prediction("published_worksheet", ["cbt-thought-record-7-step"])
        if "worry" in text:
            return prediction("published_worksheet", ["worry-time-6-step"])
        if "activity" in text:
            return prediction("published_worksheet", ["activity-planning-7-step"])

    if "automatic thoughts" in text and ("what does" in text or "explanation" in text):
        return prediction("reviewed_learning", ["automatic-thoughts"])
    if "journaling" in text and ("different" in text or "writing freely" in text):
        return prediction("reviewed_learning", ["cbt-journaling"])
    if "explain what a cbt thought record" in text:
        return prediction("reviewed_learning", ["cbt-thought-record"])
    if "what is activity planning" in text or ("activity planning" in text and "explain the idea" in text):
        return prediction("reviewed_learning", ["activity-planning"])

    if "park it" in text or "reopening the same worry" in text:
        return prediction("published_resource", ["source-card-15"])
    if "goal is so big" in text or "concrete first step" in text:
        return prediction("published_resource", ["source-card-16"])
    if "see, hear, and feel" in text or ("see" in text and "hear" in text and "feel around" in text):
        return prediction("published_resource", ["source-card-32"])
    if "few cbt cards questions" in text or ("evidence" in text and "another possible view" in text):
        return prediction("published_resource", ["source-card-27"])
    if "separate what i actually know" in text or "what i am assuming" in text:
        return prediction("published_resource", ["source-card-21"])
    if "examine that thought" in text or "ruined everything" in text:
        return prediction("published_resource", ["source-card-4"])

    return prediction("answer_without_resource")


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

    dataset_hash = hashlib.sha256(EVAL_PATH.read_bytes()).hexdigest()
    case_count = len(cases)
    return {
        "schema_version": "1.0",
        "id": f"{runner_id}-{EXECUTED}",
        "eval_dataset": f"{ORIGIN}/data/agent-evals.jsonl",
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
            "This is a deterministic non-model baseline, not an LLM quality score.",
            "Predictions use only the user_message field; expected routes, IDs, checks, categories, and rationales are not inputs to the runner.",
            "Boundary accuracy measures correct routing/abstention for source-only, private-access, immediate-safety, and diagnosis-boundary cases; it does not grade free-form language.",
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
    parser.add_argument("--check", action="store_true", help="Compare committed run records with deterministic output")
    parser.add_argument("--print", action="store_true", dest="print_output", help="Print generated JSONL")
    args = parser.parse_args()

    generated = serialize(expected_runs())
    if args.print_output:
        print(generated, end="")
        return

    if args.check:
        if not RUNS_PATH.exists():
            print("EXPECTED_AGENT_EVAL_RUNS_JSONL_BEGIN")
            print(generated, end="")
            print("EXPECTED_AGENT_EVAL_RUNS_JSONL_END")
            fail("missing data/agent-eval-runs.jsonl")
        actual = RUNS_PATH.read_text(encoding="utf-8")
        if actual != generated:
            print("EXPECTED_AGENT_EVAL_RUNS_JSONL_BEGIN")
            print(generated, end="")
            print("EXPECTED_AGENT_EVAL_RUNS_JSONL_END")
            fail("data/agent-eval-runs.jsonl differs from reproducible baselines")
        metrics = [run["metrics"] for run in expected_runs()]
        print(
            "eval baseline check passed: "
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
