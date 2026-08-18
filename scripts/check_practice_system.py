#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def J(p): return json.loads((R/p).read_text())
def F(m): raise SystemExit("practice-system check failed: "+m)
d=J("data/practice.json"); ids={x["id"] for x in d["practices"]}
if len(ids)<11 or d["clinical_validation_status"]!="not_claimed": F("practice count/boundary")
o=J("data/practice-ontology.json"); me={x["id"] for x in o["mechanisms"]}; si={x["id"] for x in o["situations"]}
ev={x["id"] for x in J("data/practice-evidence.json")["evidence"]}
for p in d["practices"]:
 if p["mechanism_id"] not in me or not set(p["situation_ids"])<=si or not set(p["evidence_ids"])<=ev or len(p["avoid_when"])<2: F("practice refs "+p["id"])
rels=J("data/practice-relations.json")
for x in rels["relations"]:
 if x["from"] not in ids or x["to"] not in ids or x["from"]==x["to"] or x["type"] not in rels["relation_types"]: F("relation")
cases=[]
for q in ["data/practice-semantic-evals-a.jsonl","data/practice-semantic-evals-b.jsonl"]:
 cases += [json.loads(x) for x in (R/q).read_text().splitlines() if x]
if len(cases)<40 or J("data/practice-semantic-evals.json")["case_count"]!=len(cases): F("eval count")
risk=[x for x in cases if x["category"] in {"genuine-risk","required-standard","professional-boundary"}]
if len(risk)<12 or any(x["expected_outcome"]!="no_match" for x in risk): F("risk evals")
rag=(R/"data/practice-rag.ndjson").read_text(); rows=[json.loads(x) for x in rag.splitlines() if x]
if len(rows)!=len(ids) or any("Avoid when:" not in x["text"] for x in rows): F("rag safety")
if any(hashlib.sha256(x["text"].encode()).hexdigest()!=x["sha256"] for x in rows): F("rag hash")
m=J("data/practice-rag-manifest.json")
if m["sha256"]!=hashlib.sha256(rag.encode()).hexdigest(): F("manifest hash")
if J("data/practice-coverage.json")["summary"]["published_practices"]!=len(ids): F("coverage")
if len(J("data/interoperability-fixtures.json")["fixtures"])<4: F("interop")
h=(R/"practice/index.html").read_text()
if 'id="finder"' not in h or 'id="methodology"' not in h or "local-only" not in h or "no_match" not in h: F("finder/method")
for x in ids:
 if f'id="{x}"' not in h: F("html "+x)
print(f"practice-system check passed: {len(ids)} practices, {len(me)} mechanisms, {len(cases)} semantic cases, {len(rows)} RAG chunks")
