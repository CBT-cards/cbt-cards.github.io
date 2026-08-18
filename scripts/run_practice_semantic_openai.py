#!/usr/bin/env python3
"""Generate CBT Cards practice-semantic response artifacts with frozen public context.

Generation-only. Benchmark expected outcome/IDs/category/safety annotations are never used to
construct model requests. No web search is enabled; the request receives immutable checkout
content whose SHA-256 values are recorded in the execution artifact.
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
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
API_URL = "https://api.openai.com/v1/responses"
PROMPT_PATH = ROOT / "research" / "practice-semantic-model-prompt-v1.txt"
SKILL_PATH = ROOT / "agents" / "cbt-cards" / "SKILL.md"
MANIFEST_PATH = ROOT / "data" / "practice-semantic-evals.json"
SHARD_PATHS = [
    ROOT / "data" / "practice-semantic-evals-a.jsonl",
    ROOT / "data" / "practice-semantic-evals-b.jsonl",
]
CONTEXT_PATHS = [
    ROOT / "data" / "practice.json",
    ROOT / "data" / "practice-recommendations.json",
    ROOT / "data" / "practice-evidence.json",
    ROOT / "data" / "practice-rag.ndjson",
]
OUTCOMES = ["match", "clarify", "no_match", "resource_not_practice"]
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "outcome": {"type": "string", "enum": OUTCOMES},
        "selected_practice_ids": {"type": "array", "items": {"type": "string"}},
        "canonical_urls": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "outcome", "selected_practice_ids", "canonical_urls"],
    "additionalProperties": False,
}
HIDDEN_BENCHMARK_FIELDS = [
    "category", "expected_outcome", "acceptable_practice_ids", "required_safety_notes"
]


def fail(message: str) -> None:
    raise SystemExit(f"practice semantic OpenAI generation failed: {message}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    rows=[]
    for number,raw in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not raw.strip():
            continue
        try:
            row=json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"{path.relative_to(ROOT)}:{number}: {exc}")
        if not isinstance(row,dict) or not isinstance(row.get("id"),str) or not isinstance(row.get("user_message"),str):
            fail(f"{path.relative_to(ROOT)}:{number}: expected object with id/user_message")
        rows.append(row)
    return rows


def load_cases() -> tuple[list[dict], str, list[dict]]:
    manifest=json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows=[]; raw_parts=[]; shards=[]
    for path in SHARD_PATHS:
        raw=path.read_bytes(); raw_parts.append(raw); shard_rows=read_jsonl(path); rows.extend(shard_rows)
        shards.append({"url": f"{ORIGIN}/data/{path.name}", "sha256": sha256_bytes(raw), "case_count": len(shard_rows)})
    if len(rows)!=manifest.get("case_count"):
        fail("semantic dataset count differs from manifest")
    if len({row["id"] for row in rows})!=len(rows):
        fail("duplicate semantic case ID")
    combined=sha256_bytes(b"\n--CBT-CARDS-SHARD--\n".join(raw_parts))
    return rows,combined,shards


def load_context() -> tuple[str, list[dict]]:
    chunks=[]; provenance=[]
    for path in CONTEXT_PATHS:
        raw=path.read_bytes(); text=raw.decode("utf-8")
        chunks.append(f"===== {path.name} =====\n{text}")
        provenance.append({"url": f"{ORIGIN}/data/{path.name}", "sha256": sha256_bytes(raw), "bytes": len(raw)})
    return "\n\n".join(chunks),provenance


def practice_index() -> tuple[set[str], dict[str,str]]:
    doc=json.loads((ROOT/"data/practice.json").read_text(encoding="utf-8"))
    rows=doc.get("practices",[])
    return {r["id"] for r in rows}, {r["id"]:r["canonical_url"] for r in rows}


def build_payload(*, model: str, user_message: str, prompt_text: str, skill_text: str, context_text: str) -> dict:
    return {
        "model": model,
        "store": False,
        "input": [
            {"role":"developer","content":[{"type":"input_text","text":prompt_text}]},
            {"role":"developer","content":[{"type":"input_text","text":"CBT Cards Agent Skill under evaluation:\n\n"+skill_text}]},
            {"role":"developer","content":[{"type":"input_text","text":"Frozen CBT Cards reviewed-practice context for this run:\n\n"+context_text}]},
            {"role":"user","content":[{"type":"input_text","text":user_message}]},
        ],
        "text": {"format": {"type":"json_schema","name":"cbt_cards_practice_semantic_response_v1","schema":OUTPUT_SCHEMA,"strict":True}},
    }


def api_request(payload: dict, api_key: str, timeout: int, retries: int) -> dict:
    body=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json","User-Agent":"CBT-Cards-practice-semantic-eval/1.0"}
    for attempt in range(retries+1):
        req=request.Request(API_URL,data=body,headers=headers,method="POST")
        try:
            with request.urlopen(req,timeout=timeout) as response:
                raw=response.read()
            parsed=json.loads(raw)
            if not isinstance(parsed,dict):
                fail("Responses API returned non-object JSON")
            return parsed
        except error.HTTPError as exc:
            detail=exc.read().decode("utf-8",errors="replace"); retryable=exc.code==429 or 500<=exc.code<600
            if retryable and attempt<retries:
                time.sleep(min(2**attempt,8)); continue
            fail(f"Responses API HTTP {exc.code}: {detail[:1000]}")
        except error.URLError as exc:
            if attempt<retries:
                time.sleep(min(2**attempt,8)); continue
            fail(f"Responses API network error: {exc}")
        except json.JSONDecodeError as exc:
            fail(f"Responses API returned invalid JSON: {exc}")
    fail("Responses API request exhausted retries")


def extract_output_text(response: dict) -> str:
    texts=[]; refusals=[]
    for item in response.get("output",[]):
        if not isinstance(item,dict) or item.get("type")!="message":
            continue
        for content in item.get("content",[]):
            if not isinstance(content,dict):
                continue
            if content.get("type")=="output_text" and isinstance(content.get("text"),str):
                texts.append(content["text"])
            elif content.get("type")=="refusal" and isinstance(content.get("refusal"),str):
                refusals.append(content["refusal"])
    if texts:
        return "\n".join(texts)
    if refusals:
        fail("model refusal: "+" ".join(refusals)[:500])
    fail(f"Responses API returned no output_text; status={response.get('status')!r}")


def parse_envelope(text: str, valid_practice_ids: set[str]) -> dict:
    try:
        e=json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"structured output invalid JSON: {exc}")
    required=set(OUTPUT_SCHEMA["required"])
    if not isinstance(e,dict) or set(e)!=required:
        fail("structured output fields differ from contract")
    if not isinstance(e["answer"],str) or not e["answer"].strip():
        fail("empty answer")
    if e["outcome"] not in OUTCOMES:
        fail("invalid outcome")
    selected=e["selected_practice_ids"]
    if not isinstance(selected,list) or not all(isinstance(x,str) and x for x in selected) or len(selected)!=len(set(selected)):
        fail("invalid selected_practice_ids")
    unknown=set(selected)-valid_practice_ids
    if unknown:
        fail(f"unknown selected practice IDs: {sorted(unknown)}")
    if e["outcome"]=="match" and not selected:
        fail("match must select at least one reviewed practice")
    if e["outcome"] in {"no_match","resource_not_practice"} and selected:
        fail("no_match/resource_not_practice cannot select practices")
    urls=e["canonical_urls"]
    if not isinstance(urls,list) or not all(isinstance(x,str) and x for x in urls) or len(urls)!=len(set(urls)):
        fail("invalid canonical_urls")
    for url in urls:
        p=urlparse(url)
        if f"{p.scheme}://{p.netloc}"!=ORIGIN:
            fail(f"non-CBT-Cards canonical URL: {url}")
    return e


def runtime_metadata(response: dict) -> dict:
    usage=response.get("usage") if isinstance(response.get("usage"),dict) else {}
    return {"provider_response_id":response.get("id"),"returned_model":response.get("model"),"response_status":response.get("status"),"usage":usage,"store":False,"web_search_enabled":False}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model",required=True)
    ap.add_argument("--responses",required=True)
    ap.add_argument("--execution",required=True)
    ap.add_argument("--api-key-env",default="OPENAI_API_KEY")
    ap.add_argument("--timeout",type=int,default=180)
    ap.add_argument("--retries",type=int,default=2)
    ap.add_argument("--case-id",action="append",default=[],help="Debug only; full publication candidate requires all cases")
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()
    required=[PROMPT_PATH,SKILL_PATH,MANIFEST_PATH,*SHARD_PATHS,*CONTEXT_PATHS]
    for path in required:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")
    cases,dataset_hash,shards=load_cases()
    if args.case_id:
        wanted=set(args.case_id); cases=[c for c in cases if c["id"] in wanted]; found={c["id"] for c in cases}
        if found!=wanted:
            fail("unknown --case-id values: "+",".join(sorted(wanted-found)))
    prompt_bytes=PROMPT_PATH.read_bytes(); skill_bytes=SKILL_PATH.read_bytes(); context_text,context_provenance=load_context(); valid_ids,_=practice_index()
    if args.dry_run:
        payload=build_payload(model=args.model,user_message=cases[0]["user_message"],prompt_text=prompt_bytes.decode(),skill_text=skill_bytes.decode(),context_text=context_text)
        print(json.dumps({"case_count":len(cases),"sample_case_id":cases[0]["id"],"request":payload,"semantic_case_dataset_sha256":dataset_hash,"context_resources":context_provenance,"note":"Dry-run only. No API request was made and no benchmark/model result was produced."},ensure_ascii=False,indent=2)); return
    api_key=os.environ.get(args.api_key_env)
    if not api_key:
        fail(f"missing API key environment variable: {args.api_key_env}")
    started=utc_now(); records=[]; returned_models=set(); response_ids=[]
    for index,case in enumerate(cases,1):
        payload=build_payload(model=args.model,user_message=case["user_message"],prompt_text=prompt_bytes.decode(),skill_text=skill_bytes.decode(),context_text=context_text)
        response=api_request(payload,api_key,args.timeout,args.retries); envelope=parse_envelope(extract_output_text(response),valid_ids); meta=runtime_metadata(response)
        if isinstance(meta.get("returned_model"),str) and meta["returned_model"]:
            returned_models.add(meta["returned_model"])
        if isinstance(meta.get("provider_response_id"),str) and meta["provider_response_id"]:
            response_ids.append(meta["provider_response_id"])
        records.append({"schema_version":"1.0","case_id":case["id"],**envelope,"runtime_metadata":meta}); print(f"generated {index}/{len(cases)} {case['id']}",flush=True)
    serialized="\n".join(json.dumps(r,ensure_ascii=False,separators=(",",":")) for r in records)+"\n"
    rp=Path(args.responses); rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(serialized,encoding="utf-8")
    execution={"schema_version":"1.0","id":"cbt-cards-practice-semantic-execution-v1","provider":"openai","requested_model":args.model,"returned_models":sorted(returned_models),"runtime":"openai-responses-api","api_endpoint":API_URL,"eval_manifest_url":f"{ORIGIN}/data/practice-semantic-evals.json","eval_manifest_sha256":sha256_bytes(MANIFEST_PATH.read_bytes()),"eval_shards":shards,"semantic_case_dataset_sha256":dataset_hash,"prompt_url":f"{ORIGIN}/research/practice-semantic-model-prompt-v1.txt","prompt_sha256":sha256_bytes(prompt_bytes),"skill_url":f"{ORIGIN}/agents/cbt-cards/SKILL.md","skill_sha256":sha256_bytes(skill_bytes),"context_resources":context_provenance,"input_fields":["user_message"],"benchmark_fields_hidden":HIDDEN_BENCHMARK_FIELDS,"store":False,"web_search_enabled":False,"structured_output":"cbt_cards_practice_semantic_response_v1","started":started,"completed":utc_now(),"response_count":len(records),"responses_sha256":sha256_bytes(serialized.encode()),"provider_response_ids":response_ids}
    ep=Path(args.execution); ep.parent.mkdir(parents=True,exist_ok=True); ep.write_text(json.dumps(execution,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"wrote {rp} and {ep}")

if __name__=="__main__":
    main()
