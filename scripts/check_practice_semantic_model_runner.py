#!/usr/bin/env python3
"""Validate the frozen-context OpenAI practice-semantic runner without an API call."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/"scripts/run_practice_semantic_openai.py"
PROMPT=ROOT/"research/practice-semantic-model-prompt-v1.txt"
SKILL=ROOT/"agents/cbt-cards/SKILL.md"

def fail(m): raise SystemExit("practice semantic model runner check failed: "+m)
def load():
    spec=importlib.util.spec_from_file_location("semantic_runner",RUNNER)
    if spec is None or spec.loader is None: fail("cannot import runner")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def main():
    mod=load(); context,prov=mod.load_context()
    fake={"id":"sem-fixture-no-leak","user_message":"I keep checking a harmless message because I fear I missed something.","category":"SECRET_CATEGORY","expected_outcome":"SECRET_OUTCOME","acceptable_practice_ids":["SECRET_PRACTICE"],"required_safety_notes":["SECRET_SAFETY"]}
    payload=mod.build_payload(model="test-model",user_message=fake["user_message"],prompt_text=PROMPT.read_text(),skill_text=SKILL.read_text(),context_text=context)
    if payload.get("model")!="test-model" or payload.get("store") is not False: fail("model/store")
    if "tools" in payload: fail("semantic runner must not enable web search/tools")
    inputs=payload.get("input")
    if not isinstance(inputs,list) or len(inputs)!=4: fail("expected 3 developer messages + 1 user message")
    users=[x for x in inputs if x.get("role")=="user"]
    if users!=[{"role":"user","content":[{"type":"input_text","text":fake["user_message"]}]}]: fail("user input must be exactly user_message")
    serialized=json.dumps(payload,ensure_ascii=False)
    for secret in ("SECRET_CATEGORY","SECRET_OUTCOME","SECRET_PRACTICE","SECRET_SAFETY"):
        if secret in serialized: fail("benchmark-only value leaked: "+secret)
    fmt=payload.get("text",{}).get("format",{})
    if fmt.get("type")!="json_schema" or fmt.get("strict") is not True: fail("strict structured output")
    schema=fmt.get("schema",{})
    if set(schema.get("required",[]))!={"answer","outcome","selected_practice_ids","canonical_urls"} or schema.get("additionalProperties") is not False: fail("response schema")
    if set(schema.get("properties",{}).get("outcome",{}).get("enum",[]))!=set(mod.OUTCOMES): fail("outcome enum")
    if len(prov)!=4: fail("frozen context resource count")
    for item in prov:
        if not item.get("url","").startswith("https://cbt-cards.github.io/data/") or len(item.get("sha256",""))!=64 or not item.get("bytes"): fail("context provenance")
    cases,dataset_hash,shards=mod.load_cases()
    if len(cases)!=41 or len(dataset_hash)!=64 or len(shards)!=2: fail("semantic dataset provenance")
    dry={"category":"SECRET_CATEGORY","expected_outcome":"SECRET_OUTCOME","acceptable_practice_ids":["SECRET_PRACTICE"],"required_safety_notes":["SECRET_SAFETY"]}
    for value in dry.values():
        values=value if isinstance(value,list) else [value]
        for v in values:
            if v in context: fail("sentinel unexpectedly present in frozen public context")
    print("practice semantic model runner check passed: user_message-only benchmark input, frozen hashed context, strict output, no web search")
if __name__=="__main__": main()
