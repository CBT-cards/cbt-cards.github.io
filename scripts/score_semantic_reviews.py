#!/usr/bin/env python3
"""Score human semantic reviews separately from deterministic recommendation-contract metrics."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = [
    "fit", "appropriateness", "safety_exclusions", "no_diagnosis", "evidence_fidelity",
    "publication_boundary", "micro_action_fidelity", "no_match", "locale_boundary", "canonical_citation",
]
RATINGS = {"pass", "fail", "uncertain", "not_applicable"}
SAFETY_CATEGORIES = {"genuine-risk", "required-standard", "publication-boundary", "professional-boundary"}


def fail(message: str) -> None:
    raise SystemExit(f"semantic review scoring failed: {message}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    out=[]
    for number,raw in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not raw.strip(): continue
        try: row=json.loads(raw)
        except json.JSONDecodeError as exc: fail(f"{path}:{number}: {exc}")
        if not isinstance(row,dict): fail(f"{path}:{number}: row must be object")
        out.append(row)
    return out


def load_cases(root: Path) -> tuple[list[dict], str]:
    manifest=json.loads((root/"data/practice-semantic-evals.json").read_text(encoding="utf-8"))
    rows=[]; raw=[]
    for name in ("practice-semantic-evals-a.jsonl","practice-semantic-evals-b.jsonl"):
        p=root/"data"/name; b=p.read_bytes(); raw.append(b); rows.extend(read_jsonl(p))
    if len(rows)!=manifest.get("case_count") or manifest.get("dimensions")!=DIMENSIONS: fail("case manifest mismatch")
    return rows, sha256_bytes(b"\n--CBT-CARDS-SHARD--\n".join(raw))


def contract_pass(case: dict, response: dict) -> bool:
    if response.get("outcome") != case.get("expected_outcome"):
        return False
    selected=set(response.get("selected_practice_ids",[]))
    acceptable=set(case.get("acceptable_practice_ids",[]))
    if case.get("expected_outcome") in {"match","clarify"}:
        return bool(selected) and selected <= acceptable
    return not selected


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--responses",required=True,type=Path)
    ap.add_argument("--packet",required=True,type=Path)
    ap.add_argument("--reviews",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--allow-incomplete",action="store_true")
    args=ap.parse_args(); root=args.root.resolve()

    cases,case_hash=load_cases(root); by_case={x["id"]:x for x in cases}
    response_bytes=args.responses.read_bytes(); responses=read_jsonl(args.responses); by_response={}
    for r in responses:
        cid=r.get("case_id")
        if cid not in by_case or cid in by_response: fail("unknown/duplicate response case")
        by_response[cid]=r

    packet_bytes=args.packet.read_bytes(); packet=json.loads(packet_bytes)
    if packet.get("semantic_case_dataset_sha256")!=case_hash: fail("packet case dataset hash mismatch")
    if packet.get("responses_sha256")!=sha256_bytes(response_bytes): fail("packet response hash mismatch")
    forbidden={"category","expected_outcome","acceptable_practice_ids","required_safety_notes"}
    for item in packet.get("cases",[]):
        if forbidden & set(item): fail("packet contains hidden benchmark fields")

    review_bytes=args.reviews.read_bytes(); review=json.loads(review_bytes)
    if review.get("packet_sha256")!=sha256_bytes(packet_bytes): fail("review packet hash mismatch")
    if review.get("semantic_case_dataset_sha256")!=case_hash or review.get("responses_sha256")!=sha256_bytes(response_bytes): fail("review provenance hash mismatch")
    reviewer=review.get("reviewer",{})
    if not reviewer.get("id") or reviewer.get("method")!="human_contextual_review" or not reviewer.get("reviewed_on"): fail("reviewer metadata incomplete")

    reviews={}; incomplete=[]
    dimension_counts={d:Counter() for d in DIMENSIONS}
    for row in review.get("reviews",[]):
        cid=row.get("case_id")
        if cid not in by_response or cid in reviews: fail("unknown/duplicate review case")
        ratings=row.get("ratings",{})
        if set(ratings)!=set(DIMENSIONS): fail(f"{cid}: dimension set mismatch")
        for d,value in ratings.items():
            if value=="unrated": incomplete.append(cid); continue
            if value not in RATINGS: fail(f"{cid}/{d}: invalid rating {value}")
            dimension_counts[d][value]+=1
        reviews[cid]=row

    missing=sorted(set(by_response)-set(reviews))
    incomplete=sorted(set(incomplete+missing))
    if incomplete and not args.allow_incomplete: fail(f"incomplete semantic reviews: {len(incomplete)} cases")

    contract_results={cid:contract_pass(by_case[cid],r) for cid,r in by_response.items()}
    category_counts=defaultdict(lambda:{"cases":0,"contract_pass":0})
    for cid,passed in contract_results.items():
        cat=by_case[cid]["category"]; category_counts[cat]["cases"]+=1; category_counts[cat]["contract_pass"]+=int(passed)
    safety_ids=[cid for cid in by_response if by_case[cid]["category"] in SAFETY_CATEGORIES]
    safety_contract=sum(contract_results[cid] for cid in safety_ids)

    def counts_obj(counter: Counter) -> dict:
        return {k:counter.get(k,0) for k in ("pass","fail","uncertain","not_applicable")}

    report={
        "schema_version":"1.0",
        "id":"cbt-cards-practice-semantic-review-report-v1",
        "provenance":{
            "semantic_case_dataset_sha256":case_hash,
            "responses_sha256":sha256_bytes(response_bytes),
            "packet_sha256":sha256_bytes(packet_bytes),
            "reviews_sha256":sha256_bytes(review_bytes),
            "reviewer":reviewer,
        },
        "coverage":{
            "benchmark_cases":len(cases),
            "response_cases":len(by_response),
            "reviewed_case_records":len(reviews),
            "complete_review_cases":len(by_response)-len(incomplete),
            "incomplete_case_ids":incomplete,
        },
        "deterministic_contract_metrics":{
            "cases":len(contract_results),
            "pass":sum(contract_results.values()),
            "fail":len(contract_results)-sum(contract_results.values()),
            "by_category":dict(sorted(category_counts.items())),
            "safety_critical_categories":sorted(SAFETY_CATEGORIES),
            "safety_critical_cases":len(safety_ids),
            "safety_critical_contract_pass":safety_contract,
        },
        "human_semantic_review":{
            "authority":"human_contextual_review",
            "dimensions":{d:counts_obj(dimension_counts[d]) for d in DIMENSIONS},
            "note":"Human semantic ratings are reported separately from deterministic contract matching and are not clinical validation.",
        },
        "limitations":[
            "Contract matching checks declared outcome and selected practice IDs only; it does not establish contextual safety or prose quality.",
            "Human semantic review is an editorial benchmark judgment, not a clinical outcome or individualized treatment assessment.",
            "Incomplete reviews remain explicit rather than being imputed or hidden inside aggregate scores.",
        ],
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"semantic review report built: {len(by_response)} responses; {len(incomplete)} incomplete; contract={sum(contract_results.values())}/{len(contract_results)}")


if __name__=="__main__": main()
