#!/usr/bin/env python3
"""Gate a full practice-semantic provider execution before human review/publication."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="https://cbt-cards.github.io"
PROMPT=ROOT/"research/practice-semantic-model-prompt-v1.txt"
SKILL=ROOT/"agents/cbt-cards/SKILL.md"
MANIFEST=ROOT/"data/practice-semantic-evals.json"
SHARDS=[ROOT/"data/practice-semantic-evals-a.jsonl",ROOT/"data/practice-semantic-evals-b.jsonl"]
CONTEXT=[ROOT/"data/practice.json",ROOT/"data/practice-recommendations.json",ROOT/"data/practice-evidence.json",ROOT/"data/practice-rag.ndjson"]
HIDDEN=["category","expected_outcome","acceptable_practice_ids","required_safety_notes"]
REASONING={"none","low","medium","high","xhigh","max"}

def fail(m): raise SystemExit("practice semantic execution candidate check failed: "+m)
def sha(b): return hashlib.sha256(b).hexdigest()
def rows(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--execution",required=True,type=Path); ap.add_argument("--responses",required=True,type=Path); args=ap.parse_args()
    execution=json.loads(args.execution.read_text(encoding="utf-8")); response_bytes=args.responses.read_bytes(); responses=rows(args.responses)
    cases=[]; raw=[]
    for p in SHARDS: raw.append(p.read_bytes()); cases.extend(rows(p))
    expected_ids=[c["id"] for c in cases]
    if len(expected_ids)!=41 or len(set(expected_ids))!=41: fail("canonical semantic dataset must contain 41 unique cases")
    if execution.get("schema_version")!="1.0" or execution.get("id")!="cbt-cards-practice-semantic-execution-v1": fail("execution identity")
    if execution.get("provider")!="openai" or execution.get("runtime")!="openai-responses-api": fail("provider/runtime")
    if execution.get("store") is not False or execution.get("web_search_enabled") is not False: fail("store/web-search boundary")
    if execution.get("reasoning_effort") not in REASONING: fail("missing/invalid reasoning_effort provenance")
    max_tokens=execution.get("max_output_tokens")
    if not isinstance(max_tokens,int) or not 256<=max_tokens<=8192: fail("missing/invalid max_output_tokens provenance")
    if execution.get("input_fields")!=["user_message"] or execution.get("benchmark_fields_hidden")!=HIDDEN: fail("input isolation declaration")
    if execution.get("eval_manifest_url")!=f"{ORIGIN}/data/practice-semantic-evals.json" or execution.get("eval_manifest_sha256")!=sha(MANIFEST.read_bytes()): fail("eval manifest provenance")
    combined=sha(b"\n--CBT-CARDS-SHARD--\n".join(raw))
    if execution.get("semantic_case_dataset_sha256")!=combined: fail("semantic dataset hash")
    shard_meta=execution.get("eval_shards")
    if not isinstance(shard_meta,list) or len(shard_meta)!=2: fail("shard metadata")
    for meta,p in zip(shard_meta,SHARDS):
        if meta.get("url")!=f"{ORIGIN}/data/{p.name}" or meta.get("sha256")!=sha(p.read_bytes()) or meta.get("case_count")!=len(rows(p)): fail("shard provenance "+p.name)
    if execution.get("prompt_url")!=f"{ORIGIN}/research/practice-semantic-model-prompt-v1.txt" or execution.get("prompt_sha256")!=sha(PROMPT.read_bytes()): fail("prompt provenance")
    if execution.get("skill_url")!=f"{ORIGIN}/agents/cbt-cards/SKILL.md" or execution.get("skill_sha256")!=sha(SKILL.read_bytes()): fail("skill provenance")
    meta_by_url={m.get("url"):m for m in execution.get("context_resources",[]) if isinstance(m,dict)}
    if len(meta_by_url)!=len(CONTEXT): fail("context resource count")
    for p in CONTEXT:
        url=f"{ORIGIN}/data/{p.name}"; meta=meta_by_url.get(url); rawp=p.read_bytes()
        if not meta or meta.get("sha256")!=sha(rawp) or meta.get("bytes")!=len(rawp): fail("context provenance "+p.name)
    if execution.get("response_count")!=41 or len(responses)!=41: fail("full publication candidate requires 41 responses")
    if execution.get("responses_sha256")!=sha(response_bytes): fail("response hash")
    ids=[r.get("case_id") for r in responses]
    if ids!=expected_ids: fail("response IDs/order differ from frozen semantic dataset")
    if len(set(ids))!=41: fail("duplicate response IDs")
    valid_outcomes={"match","clarify","no_match","resource_not_practice"}
    for r in responses:
        for key in ("answer","outcome","selected_practice_ids","canonical_urls","runtime_metadata"):
            if key not in r: fail(f"{r.get('case_id')}: missing {key}")
        if r["outcome"] not in valid_outcomes: fail(f"{r['case_id']}: outcome")
        if not isinstance(r["answer"],str) or not r["answer"].strip(): fail(f"{r['case_id']}: answer")
        selected=r["selected_practice_ids"]
        if not isinstance(selected,list) or len(selected)!=len(set(selected)): fail(f"{r['case_id']}: selected practice IDs")
        if r["outcome"]=="match" and not selected: fail(f"{r['case_id']}: match without practice")
        if r["outcome"]=="clarify" and not 2<=len(selected)<=3: fail(f"{r['case_id']}: clarify requires 2-3 candidates")
        if r["outcome"] in {"no_match","resource_not_practice"} and selected: fail(f"{r['case_id']}: selected practice on no-match/resource outcome")
        md=r["runtime_metadata"]
        if md.get("store") is not False or md.get("web_search_enabled") is not False: fail(f"{r['case_id']}: runtime boundary")
    if not execution.get("requested_model") or not execution.get("started") or not execution.get("completed"): fail("missing execution provenance")
    print(f"practice semantic execution candidate check passed: 41 frozen-context responses, reasoning={execution['reasoning_effort']}, max_output_tokens={max_tokens}")
if __name__=="__main__": main()
