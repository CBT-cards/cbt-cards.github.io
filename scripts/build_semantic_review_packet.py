#!/usr/bin/env python3
"""Build a blinded human-review packet from captured practice recommendation responses."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = [
    "fit",
    "appropriateness",
    "safety_exclusions",
    "no_diagnosis",
    "evidence_fidelity",
    "publication_boundary",
    "micro_action_fidelity",
    "no_match",
    "locale_boundary",
    "canonical_citation",
]
HIDDEN_BENCHMARK_FIELDS = [
    "category",
    "expected_outcome",
    "acceptable_practice_ids",
    "required_safety_notes",
]


def fail(message: str) -> None:
    raise SystemExit(f"semantic review packet build failed: {message}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"{path}:{number}: invalid JSON: {exc}")
        if not isinstance(row, dict):
            fail(f"{path}:{number}: row must be object")
        rows.append(row)
    return rows


def load_cases(root: Path) -> tuple[list[dict], str]:
    manifest = json.loads((root / "data/practice-semantic-evals.json").read_text(encoding="utf-8"))
    rows = []
    raw_parts = []
    for name in ("practice-semantic-evals-a.jsonl", "practice-semantic-evals-b.jsonl"):
        path = root / "data" / name
        raw = path.read_bytes()
        raw_parts.append(raw)
        rows.extend(read_jsonl(path))
    if len(rows) != manifest.get("case_count"):
        fail("semantic case count differs from manifest")
    if manifest.get("dimensions") != DIMENSIONS:
        fail("dimension order differs from protocol")
    joined = b"\n--CBT-CARDS-SHARD--\n".join(raw_parts)
    return rows, sha256_bytes(joined)


def validate_response(row: dict, practice_ids: set[str]) -> None:
    required = {"case_id", "answer", "outcome", "selected_practice_ids", "canonical_urls"}
    missing = sorted(required - set(row))
    if missing:
        fail(f"response {row.get('case_id')}: missing {', '.join(missing)}")
    if row["outcome"] not in {"match", "clarify", "no_match", "resource_not_practice"}:
        fail(f"response {row['case_id']}: invalid outcome")
    if not isinstance(row["answer"], str) or not row["answer"].strip():
        fail(f"response {row['case_id']}: empty answer")
    selected = row["selected_practice_ids"]
    if not isinstance(selected, list) or len(selected) != len(set(selected)):
        fail(f"response {row['case_id']}: selected_practice_ids must be unique array")
    unknown = set(selected) - practice_ids
    if unknown:
        fail(f"response {row['case_id']}: unknown practice IDs: {sorted(unknown)}")
    if not isinstance(row["canonical_urls"], list):
        fail(f"response {row['case_id']}: canonical_urls must be array")
    if row["outcome"] in {"no_match", "resource_not_practice"} and selected:
        fail(f"response {row['case_id']}: no-match/resource outcome cannot select practices")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--packet-out", required=True, type=Path)
    parser.add_argument("--review-template-out", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()

    cases, case_dataset_sha256 = load_cases(root)
    case_by_id = {row["id"]: row for row in cases}
    if len(case_by_id) != len(cases):
        fail("duplicate semantic case ID")
    practices = json.loads((root / "data/practice.json").read_text(encoding="utf-8"))
    practice_ids = {row["id"] for row in practices.get("practices", [])}

    response_bytes = args.responses.read_bytes()
    responses = read_jsonl(args.responses)
    response_by_case = {}
    for row in responses:
        validate_response(row, practice_ids)
        case_id = row["case_id"]
        if case_id not in case_by_id:
            fail(f"unknown response case_id {case_id}")
        if case_id in response_by_case:
            fail(f"duplicate response case_id {case_id}")
        response_by_case[case_id] = row

    ordered_case_ids = [row["id"] for row in cases if row["id"] in response_by_case]
    packet_cases = []
    for case_id in ordered_case_ids:
        case = case_by_id[case_id]
        response = response_by_case[case_id]
        packet_cases.append({
            "case_id": case_id,
            "user_message": case["user_message"],
            "answer": response["answer"],
            "outcome": response["outcome"],
            "selected_practice_ids": response["selected_practice_ids"],
            "canonical_urls": response["canonical_urls"],
            "answer_sha256": sha256_bytes(response["answer"].encode("utf-8")),
        })

    packet = {
        "schema_version": "1.0",
        "id": "cbt-cards-semantic-review-packet-v1",
        "case_count": len(packet_cases),
        "semantic_case_dataset_sha256": case_dataset_sha256,
        "responses_sha256": sha256_bytes(response_bytes),
        "blinded_fields_excluded": HIDDEN_BENCHMARK_FIELDS,
        "dimensions": DIMENSIONS,
        "cases": packet_cases,
    }
    args.packet_out.parent.mkdir(parents=True, exist_ok=True)
    packet_bytes = (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.packet_out.write_bytes(packet_bytes)

    review_template = {
        "schema_version": "1.0",
        "packet_sha256": sha256_bytes(packet_bytes),
        "semantic_case_dataset_sha256": case_dataset_sha256,
        "responses_sha256": sha256_bytes(response_bytes),
        "reviewer": {"id": "", "method": "human_contextual_review", "reviewed_on": ""},
        "reviews": [
            {
                "case_id": case_id,
                "ratings": {dimension: "unrated" for dimension in DIMENSIONS},
                "safety_comment": "",
                "notes": "",
            }
            for case_id in ordered_case_ids
        ],
    }
    args.review_template_out.parent.mkdir(parents=True, exist_ok=True)
    args.review_template_out.write_text(json.dumps(review_template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"semantic review packet built: {len(packet_cases)} responses; "
        f"benchmark fields excluded={','.join(HIDDEN_BENCHMARK_FIELDS)}"
    )


if __name__ == "__main__":
    main()
