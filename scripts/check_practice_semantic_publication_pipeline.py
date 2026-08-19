#!/usr/bin/env python3
"""Exercise the complete practice-semantic publication path with synthetic non-model data."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
HIDDEN = ["category", "expected_outcome", "acceptable_practice_ids", "required_safety_notes"]
DIMENSIONS = [
    "fit", "appropriateness", "safety_exclusions", "no_diagnosis", "evidence_fidelity",
    "publication_boundary", "micro_action_fidelity", "no_match", "locale_boundary", "canonical_citation",
]
SHARDS = [ROOT / "data/practice-semantic-evals-a.jsonl", ROOT / "data/practice-semantic-evals-b.jsonl"]
CONTEXT = [
    ROOT / "data/practice.json", ROOT / "data/practice-recommendations.json",
    ROOT / "data/practice-evidence.json", ROOT / "data/practice-rag.ndjson",
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def main() -> None:
    cases = []
    shard_raw = []
    for path in SHARDS:
        shard_raw.append(path.read_bytes())
        cases.extend(rows(path))
    if len(cases) != 41:
        raise SystemExit("synthetic publication pipeline fixture expects 41 cases")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        responses = tmp / "responses.jsonl"
        execution = tmp / "execution.json"
        packet = tmp / "packet.json"
        reviews = tmp / "reviews.json"
        scored = tmp / "scored.json"
        rendered = tmp / "result.md"

        with responses.open("w", encoding="utf-8") as fh:
            for case in cases:
                fh.write(json.dumps({
                    "case_id": case["id"],
                    "answer": "Synthetic publication-pipeline fixture. This is not a model result.",
                    "outcome": "no_match",
                    "selected_practice_ids": [],
                    "canonical_urls": [],
                    "runtime_metadata": {"store": False, "web_search_enabled": False},
                }, separators=(",", ":")) + "\n")

        response_bytes = responses.read_bytes()
        manifest = ROOT / "data/practice-semantic-evals.json"
        prompt = ROOT / "research/practice-semantic-model-prompt-v1.txt"
        skill = ROOT / "agents/cbt-cards/SKILL.md"
        execution_obj = {
            "schema_version": "1.0",
            "id": "cbt-cards-practice-semantic-execution-v1",
            "provider": "openai",
            "runtime": "openai-responses-api",
            "requested_model": "synthetic-ci-fixture-not-a-model",
            "reasoning_effort": "none",
            "max_output_tokens": 256,
            "store": False,
            "web_search_enabled": False,
            "input_fields": ["user_message"],
            "benchmark_fields_hidden": HIDDEN,
            "eval_manifest_url": f"{ORIGIN}/data/practice-semantic-evals.json",
            "eval_manifest_sha256": sha_bytes(manifest.read_bytes()),
            "semantic_case_dataset_sha256": sha_bytes(b"\n--CBT-CARDS-SHARD--\n".join(shard_raw)),
            "eval_shards": [
                {"url": f"{ORIGIN}/data/{p.name}", "sha256": sha_bytes(p.read_bytes()), "case_count": len(rows(p))}
                for p in SHARDS
            ],
            "prompt_url": f"{ORIGIN}/research/practice-semantic-model-prompt-v1.txt",
            "prompt_sha256": sha_bytes(prompt.read_bytes()),
            "skill_url": f"{ORIGIN}/agents/cbt-cards/SKILL.md",
            "skill_sha256": sha_bytes(skill.read_bytes()),
            "context_resources": [
                {"url": f"{ORIGIN}/data/{p.name}", "sha256": sha_bytes(p.read_bytes()), "bytes": len(p.read_bytes())}
                for p in CONTEXT
            ],
            "response_count": 41,
            "responses_sha256": sha_bytes(response_bytes),
            "started": "2026-08-19T00:00:00Z",
            "completed": "2026-08-19T00:00:01Z",
        }
        execution.write_text(json.dumps(execution_obj, indent=2) + "\n", encoding="utf-8")

        run(str(ROOT / "scripts/check_practice_semantic_execution.py"), "--execution", str(execution), "--responses", str(responses))
        run(str(ROOT / "scripts/build_semantic_review_packet.py"), "--responses", str(responses), "--packet-out", str(packet), "--review-template-out", str(reviews))

        review_obj = json.loads(reviews.read_text(encoding="utf-8"))
        review_obj["reviewer"] = {
            "id": "synthetic-ci-fixture-not-a-human-review",
            "method": "human_contextual_review",
            "reviewed_on": "2026-08-19",
        }
        for row in review_obj["reviews"]:
            row["ratings"] = {dimension: "not_applicable" for dimension in DIMENSIONS}
            row["safety_comment"] = ""
            row["notes"] = "Synthetic CI fixture only; not a model result and not a human quality judgment."
        reviews.write_text(json.dumps(review_obj, indent=2) + "\n", encoding="utf-8")

        run(str(ROOT / "scripts/score_semantic_reviews.py"), "--responses", str(responses), "--packet", str(packet), "--reviews", str(reviews), "--output", str(scored))
        run(str(ROOT / "scripts/check_practice_semantic_publication_candidate.py"), "--execution", str(execution), "--responses", str(responses), "--packet", str(packet), "--reviews", str(reviews), "--report", str(scored))
        run(str(ROOT / "scripts/build_practice_semantic_publication_report.py"), "--execution", str(execution), "--report", str(scored), "--output", str(rendered))

        text = rendered.read_text(encoding="utf-8")
        required = [
            "synthetic-ci-fixture-not-a-model",
            "Benchmark performance is not clinical validation",
            "Safety-critical contract pass",
            "Human semantic review",
            "Frozen context resources",
        ]
        for token in required:
            if token not in text:
                raise SystemExit(f"synthetic publication report missing: {token}")
        if "41" not in text:
            raise SystemExit("synthetic publication report lost complete-case count")

    print("practice semantic publication pipeline check passed: complete synthetic 41-case chain; not a model result")


if __name__ == "__main__":
    main()
