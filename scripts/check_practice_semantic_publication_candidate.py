#!/usr/bin/env python3
"""Validate that a practice-semantic result chain is complete and provenance-consistent for publication."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = [
    "fit", "appropriateness", "safety_exclusions", "no_diagnosis", "evidence_fidelity",
    "publication_boundary", "micro_action_fidelity", "no_match", "locale_boundary", "canonical_citation",
]
SAFETY_CATEGORIES = {"genuine-risk", "required-standard", "publication-boundary", "professional-boundary"}


def fail(message: str) -> None:
    raise SystemExit(f"practice semantic publication candidate check failed: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path}: expected JSON object")
    return value


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        row = json.loads(raw)
        if not isinstance(row, dict):
            fail(f"{path}:{n}: expected object")
        rows.append(row)
    return rows


def load_cases() -> dict[str, dict]:
    rows = []
    for name in ("practice-semantic-evals-a.jsonl", "practice-semantic-evals-b.jsonl"):
        rows.extend(read_jsonl(ROOT / "data" / name))
    if len(rows) != 41 or len({r["id"] for r in rows}) != 41:
        fail("canonical semantic benchmark must contain 41 unique cases")
    return {r["id"]: r for r in rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execution", required=True, type=Path)
    ap.add_argument("--responses", required=True, type=Path)
    ap.add_argument("--packet", required=True, type=Path)
    ap.add_argument("--reviews", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()

    subprocess.run([
        sys.executable, str(ROOT / "scripts/check_practice_semantic_execution.py"),
        "--execution", str(args.execution), "--responses", str(args.responses),
    ], check=True)

    execution = read_json(args.execution)
    packet = read_json(args.packet)
    reviews = read_json(args.reviews)
    report = read_json(args.report)
    responses = read_jsonl(args.responses)
    cases = load_cases()

    if len(responses) != 41:
        fail("publication requires all 41 response records")
    if packet.get("case_count") != 41 or len(packet.get("cases", [])) != 41:
        fail("publication requires a complete 41-case blinded packet")
    if packet.get("responses_sha256") != sha256(args.responses):
        fail("packet/responses provenance mismatch")
    if reviews.get("packet_sha256") != sha256(args.packet):
        fail("review/packet provenance mismatch")
    if reviews.get("responses_sha256") != sha256(args.responses):
        fail("review/responses provenance mismatch")

    reviewer = reviews.get("reviewer", {})
    if reviewer.get("method") != "human_contextual_review" or not reviewer.get("id") or not reviewer.get("reviewed_on"):
        fail("human reviewer metadata incomplete")

    review_rows = reviews.get("reviews", [])
    if len(review_rows) != 41 or len({r.get("case_id") for r in review_rows}) != 41:
        fail("publication requires exactly one human review record per case")
    for row in review_rows:
        cid = row.get("case_id")
        if cid not in cases:
            fail(f"unknown reviewed case: {cid}")
        ratings = row.get("ratings", {})
        if set(ratings) != set(DIMENSIONS):
            fail(f"{cid}: semantic dimension set mismatch")
        if any(value not in {"pass", "fail", "uncertain", "not_applicable"} for value in ratings.values()):
            fail(f"{cid}: unrated/invalid semantic dimension remains")
        if ratings["safety_exclusions"] in {"fail", "uncertain"} and not str(row.get("safety_comment", "")).strip():
            fail(f"{cid}: safety_exclusions {ratings['safety_exclusions']} requires a human safety_comment")

    provenance = report.get("provenance", {})
    expected_hashes = {
        "semantic_case_dataset_sha256": packet.get("semantic_case_dataset_sha256"),
        "responses_sha256": sha256(args.responses),
        "packet_sha256": sha256(args.packet),
        "reviews_sha256": sha256(args.reviews),
    }
    for key, expected in expected_hashes.items():
        if provenance.get(key) != expected:
            fail(f"report provenance mismatch: {key}")
    if provenance.get("reviewer") != reviewer:
        fail("report reviewer provenance differs from human review")

    coverage = report.get("coverage", {})
    if coverage.get("benchmark_cases") != 41 or coverage.get("response_cases") != 41:
        fail("report benchmark/response coverage must be 41")
    if coverage.get("reviewed_case_records") != 41 or coverage.get("complete_review_cases") != 41:
        fail("report requires complete human review coverage")
    if coverage.get("incomplete_case_ids") != []:
        fail("report contains incomplete semantic reviews")

    deterministic = report.get("deterministic_contract_metrics", {})
    if deterministic.get("cases") != 41:
        fail("deterministic contract metric case count must be 41")
    if deterministic.get("pass", 0) + deterministic.get("fail", 0) != 41:
        fail("deterministic pass/fail totals must equal 41")
    if set(deterministic.get("safety_critical_categories", [])) != SAFETY_CATEGORIES:
        fail("safety-critical category set is incomplete")
    safety_ids = [cid for cid, case in cases.items() if case.get("category") in SAFETY_CATEGORIES]
    if deterministic.get("safety_critical_cases") != len(safety_ids):
        fail("safety-critical case count mismatch")

    human = report.get("human_semantic_review", {})
    if human.get("authority") != "human_contextual_review":
        fail("human semantic authority missing")
    dimensions = human.get("dimensions", {})
    if set(dimensions) != set(DIMENSIONS):
        fail("report semantic dimensions mismatch")
    for dimension, counts in dimensions.items():
        total = sum(int(counts.get(k, 0)) for k in ("pass", "fail", "uncertain", "not_applicable"))
        if total != 41:
            fail(f"{dimension}: semantic rating totals must equal 41")

    limitations = report.get("limitations", [])
    if not isinstance(limitations, list) or len(limitations) < 3:
        fail("publication report must retain explicit limitations")
    joined = " ".join(str(x).lower() for x in limitations)
    if "clinical" not in joined or "human" not in joined:
        fail("publication limitations must preserve clinical/human-review boundaries")

    if execution.get("responses_sha256") != sha256(args.responses):
        fail("execution/responses hash mismatch after final chain check")

    print(
        "practice semantic publication candidate check passed: "
        f"41 responses + 41 human reviews; contract={deterministic['pass']}/41; "
        f"safety-subset={deterministic.get('safety_critical_contract_pass')}/{len(safety_ids)}"
    )


if __name__ == "__main__":
    main()
