#!/usr/bin/env python3
"""Exercise the semantic-review packet/scoring pipeline with synthetic non-model data."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = [
    "fit", "appropriateness", "safety_exclusions", "no_diagnosis", "evidence_fidelity",
    "publication_boundary", "micro_action_fidelity", "no_match", "locale_boundary", "canonical_citation",
]
FORBIDDEN = {"category", "expected_outcome", "acceptable_practice_ids", "required_safety_notes"}


def fail(message: str) -> None:
    raise SystemExit(f"semantic review pipeline check failed: {message}")


def load_cases() -> list[dict]:
    rows=[]
    for name in ("practice-semantic-evals-a.jsonl","practice-semantic-evals-b.jsonl"):
        for raw in (ROOT/"data"/name).read_text(encoding="utf-8").splitlines():
            if raw.strip(): rows.append(json.loads(raw))
    return rows


def main() -> None:
    cases=load_cases()
    if len(cases)<40: fail("expected at least 40 canonical semantic cases")
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        responses=tmp/"responses.jsonl"; packet=tmp/"packet.json"; reviews=tmp/"reviews.json"; report=tmp/"report.json"
        # Synthetic CI data intentionally does not use expected outcome/target fields.
        with responses.open("w",encoding="utf-8") as fh:
            for case in cases:
                fh.write(json.dumps({
                    "case_id":case["id"],
                    "answer":"Synthetic pipeline fixture. This is not a model result.",
                    "outcome":"no_match",
                    "selected_practice_ids":[],
                    "canonical_urls":[],
                },separators=(",",":"))+"\n")
        subprocess.run([
            sys.executable,str(ROOT/"scripts/build_semantic_review_packet.py"),
            "--responses",str(responses),"--packet-out",str(packet),"--review-template-out",str(reviews)
        ],check=True)
        packet_obj=json.loads(packet.read_text(encoding="utf-8"))
        if packet_obj.get("case_count")!=len(cases): fail("packet case count")
        if packet_obj.get("blinded_fields_excluded")!=["category","expected_outcome","acceptable_practice_ids","required_safety_notes"]: fail("blinded field declaration")
        for item in packet_obj.get("cases",[]):
            if FORBIDDEN & set(item): fail("benchmark-only field leaked into reviewer packet")
        review_obj=json.loads(reviews.read_text(encoding="utf-8"))
        review_obj["reviewer"]={"id":"synthetic-ci-fixture","method":"human_contextual_review","reviewed_on":"2026-08-18"}
        for row in review_obj["reviews"]:
            row["ratings"]={d:"not_applicable" for d in DIMENSIONS}
            row["notes"]="Synthetic CI fixture; not a model result and not a human quality judgment."
        reviews.write_text(json.dumps(review_obj,indent=2)+"\n",encoding="utf-8")
        subprocess.run([
            sys.executable,str(ROOT/"scripts/score_semantic_reviews.py"),
            "--responses",str(responses),"--packet",str(packet),"--reviews",str(reviews),"--output",str(report)
        ],check=True)
        report_obj=json.loads(report.read_text(encoding="utf-8"))
        if report_obj.get("coverage",{}).get("response_cases")!=len(cases): fail("report response count")
        if report_obj.get("coverage",{}).get("complete_review_cases")!=len(cases): fail("report review completeness")
        if report_obj.get("human_semantic_review",{}).get("authority")!="human_contextual_review": fail("human review authority")
        if "deterministic_contract_metrics" not in report_obj or "human_semantic_review" not in report_obj: fail("separate metric blocks")
        if not any("not a model result" in row.get("notes","").lower() for row in review_obj["reviews"]): fail("synthetic fixture labeling")
    print(f"semantic review pipeline check passed: blinded packet + separate scoring across {len(cases)} synthetic cases")


if __name__=="__main__": main()
