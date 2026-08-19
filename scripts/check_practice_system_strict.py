#!/usr/bin/env python3
"""Strict cross-file validation for the reviewed CBT Cards practice system."""
from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="https://cbt-cards.github.io"
REVIEW="editorial_and_safety_reviewed_for_publication"
CLINICAL="not_claimed"
SEMANTIC_OUTCOMES={"match","clarify","no_match","resource_not_practice"}
REQUIRED_CATEGORIES={"fit","ambiguity","genuine-risk","required-standard","publication-boundary","professional-boundary","no-match","progression"}
STRICT_NO_MATCH_CATEGORIES={"genuine-risk","required-standard","publication-boundary","professional-boundary"}
EXPECTED_CLIENTS={
 "OpenAI/ChatGPT-compatible":"repository_runner_available",
 "OpenClaw-style Agent Skills consumer":"contract_fixture_documented",
 "Hermes Agent-style skill consumer":"contract_fixture_documented",
 "generic HTTP/RAG client":"ci_contract_exercised",
}
SYMMETRIC_RELATIONS={"pairs_with","not_same_as"}

def fail(msg): raise SystemExit("strict practice-system check failed: "+msg)
def J(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def JL(path): return [json.loads(x) for x in (ROOT/path).read_text(encoding="utf-8").splitlines() if x.strip()]
def unique(rows,key,label):
 vals=[x.get(key) for x in rows]
 if any(not isinstance(v,str) or not v for v in vals): fail(f"{label} invalid {key}")
 if len(vals)!=len(set(vals)): fail(f"duplicate {label} {key}")
 return {x[key]:x for x in rows}
def local(url):
 p=urlparse(url)
 if f"{p.scheme}://{p.netloc}"!=ORIGIN: return None
 return ROOT/p.path.lstrip("/")
def check_date(value,label):
 try: date.fromisoformat(value)
 except (TypeError,ValueError): fail(f"invalid date {label}: {value!r}")

def source_graph():
 root=J("data/practice.json"); practices=root.get("practices",[]); bp=unique(practices,"id","practice")
 if len(bp)!=11: fail(f"expected 11 practices, found {len(bp)}")
 if root.get("review_status")!=REVIEW or root.get("clinical_validation_status")!=CLINICAL: fail("root review/clinical boundary")
 if len(root.get("safety_scope",""))<80: fail("root safety scope too weak")

 ont=J("data/practice-ontology.json"); bm=unique(ont.get("mechanisms",[]),"id","mechanism"); bs=unique(ont.get("situations",[]),"id","situation")
 if len(bm)!=11 or len(bs)!=11: fail("ontology must have 11 unique mechanisms and situations")
 for m in bm.values():
  if len(m.get("label",""))<3 or len(m.get("description",""))<20: fail("weak mechanism metadata: "+m["id"])
 for s in bs.values():
  refs=s.get("mechanism_ids")
  if not isinstance(refs,list) or not refs or len(refs)!=len(set(refs)) or not set(refs)<=set(bm): fail("invalid situation mechanisms: "+s["id"])
  if len(s.get("label",""))<20: fail("weak situation label: "+s["id"])

 ev=J("data/practice-evidence.json"); be=unique(ev.get("evidence",[]),"id","evidence")
 allowed_classes={"guideline_supported","authoritative_self_help","clinical_resource","practical_editorial"}
 for e in be.values():
  if e.get("evidence_class") not in allowed_classes: fail("evidence class: "+e["id"])
  if not str(e.get("url","")).startswith("https://"): fail("evidence HTTPS URL: "+e["id"])
  supports=e.get("supports")
  if not isinstance(supports,list) or not supports or len(supports)!=len(set(supports)) or not set(supports)<=set(bm): fail("evidence supports: "+e["id"])
  if len(e.get("claim_scope",""))<30 or len(e.get("does_not_establish",""))<30: fail("evidence claim/limitation scope: "+e["id"])
  check_date(e.get("reviewed_on"),"evidence "+e["id"])

 mechanism_use={x:[] for x in bm}; situation_use={x:[] for x in bs}; evidence_use=set()
 for p in practices:
  pid=p["id"]; mid=p.get("mechanism_id")
  if p.get("review_status")!=REVIEW or p.get("clinical_validation_status")!=CLINICAL: fail("practice review boundary: "+pid)
  if mid not in bm: fail("unknown practice mechanism: "+pid)
  mechanism_use[mid].append(pid)
  sids=p.get("situation_ids")
  if not isinstance(sids,list) or not sids or len(sids)!=len(set(sids)) or not set(sids)<=set(bs): fail("practice situation refs: "+pid)
  for sid in sids:
   situation_use[sid].append(pid)
   if mid not in bs[sid]["mechanism_ids"]: fail(f"practice {pid} mechanism incompatible with {sid}")
  eids=p.get("evidence_ids")
  if not isinstance(eids,list) or not eids or len(eids)!=len(set(eids)) or not set(eids)<=set(be): fail("practice evidence refs: "+pid)
  evidence_use.update(eids)
  if not any(mid in be[eid]["supports"] for eid in eids): fail(f"practice {pid} has no cited evidence supporting mechanism {mid}")
  for field in ("best_used_when","avoid_when"):
   values=p.get(field)
   if not isinstance(values,list) or not values or len(values)!=len(set(values)): fail(f"practice {pid} {field}")
  if len(p["avoid_when"])<3: fail("practice exclusions too weak: "+pid)
  if p.get("canonical_url")!=f"{ORIGIN}/practice/#{pid}": fail("practice canonical: "+pid)
  for field in ("title","micro_action","prompt","reflection_question"):
   if len(str(p.get(field,"")))<8: fail(f"practice {pid} weak {field}")
 if any(not v for v in mechanism_use.values()): fail("orphan mechanism(s): "+repr([k for k,v in mechanism_use.items() if not v]))
 if any(not v for v in situation_use.values()): fail("orphan situation(s): "+repr([k for k,v in situation_use.items() if not v]))
 if set(be)!=evidence_use: fail("orphan evidence: "+repr(sorted(set(be)-evidence_use)))
 return root,bp,bm,bs

def recommendations(bp,bs):
 data=J("data/practice-recommendations.json"); rules=data.get("behavior_rules")
 if not isinstance(rules,list) or len(rules)<6 or len(rules)!=len(set(rules)): fail("recommendation behavior rules")
 joined=" ".join(rules).lower()
 for phrase in ("no_match","at most three","avoid_when","source-only","not evidence","do not diagnose"):
  if phrase not in joined: fail("recommendation rule missing "+phrase)
 examples=data.get("examples",[]); unique(examples,"id","recommendation example")
 for x in examples:
  result=x.get("result"); pids=x.get("practice_ids")
  if result not in {"match","ambiguous","no_match"}: fail("recommendation result: "+x["id"])
  if not isinstance(pids,list) or len(pids)!=len(set(pids)) or not set(pids)<=set(bp): fail("recommendation refs: "+x["id"])
  if result=="match" and len(pids)!=1: fail("recommendation match cardinality: "+x["id"])
  if result=="ambiguous" and not 2<=len(pids)<=3: fail("recommendation ambiguity cardinality: "+x["id"])
  if result=="no_match" and pids: fail("recommendation no_match selected practice: "+x["id"])
  sid=x.get("situation_id")
  if sid is not None:
   if sid not in bs: fail("recommendation situation ref: "+x["id"])
   if result=="match" and sid not in bp[pids[0]]["situation_ids"]: fail("recommendation situation/practice mismatch: "+x["id"])
  if result!="match" and len(str(x.get("why","")))<8: fail("recommendation missing why: "+x["id"])

def relations(bp):
 data=J("data/practice-relations.json"); types=data.get("relation_types")
 if not isinstance(types,list) or len(types)!=len(set(types)) or not SYMMETRIC_RELATIONS<=set(types): fail("relation vocabulary")
 seen=set(); sym=set()
 for r in data.get("relations",[]):
  a,b,t=r.get("from"),r.get("to"),r.get("type")
  if a not in bp or b not in bp or a==b or t not in types: fail("relation endpoint/type")
  key=(a,b,t)
  if key in seen: fail("duplicate relation "+repr(key))
  seen.add(key)
  if t in SYMMETRIC_RELATIONS:
   skey=(tuple(sorted((a,b))),t)
   if skey in sym: fail("duplicate symmetric relation "+repr(skey))
   sym.add(skey)
  if len(r.get("note",""))<20: fail("weak relation note "+repr(key))

def semantic(bp):
 manifest=J("data/practice-semantic-evals.json"); cases=JL("data/practice-semantic-evals-a.jsonl")+JL("data/practice-semantic-evals-b.jsonl")
 unique(cases,"id","semantic case")
 msgs=[x.get("user_message") for x in cases]
 if len(msgs)!=len(set(msgs)): fail("duplicate semantic user message")
 if len(cases)!=41 or manifest.get("case_count")!=41: fail("semantic case count")
 cats={x.get("category") for x in cases}
 if not REQUIRED_CATEGORIES<=cats: fail("semantic category coverage "+repr(sorted(REQUIRED_CATEGORIES-cats)))
 for x in cases:
  outcome=x.get("expected_outcome"); pids=x.get("acceptable_practice_ids")
  if outcome not in SEMANTIC_OUTCOMES: fail("semantic outcome: "+x["id"])
  if not isinstance(pids,list) or len(pids)!=len(set(pids)) or not set(pids)<=set(bp): fail("semantic refs: "+x["id"])
  if outcome=="match" and not pids: fail("semantic match missing practice: "+x["id"])
  if outcome=="clarify" and not 2<=len(pids)<=3: fail("semantic clarify cardinality: "+x["id"])
  if outcome in {"no_match","resource_not_practice"} and pids: fail("semantic non-practice outcome selected practice: "+x["id"])
  if x["category"] in STRICT_NO_MATCH_CATEGORIES and outcome!="no_match": fail("safety/publication boundary must no_match: "+x["id"])
  if x["category"]=="no-match" and outcome not in {"no_match","resource_not_practice"}: fail("no-match category outcome: "+x["id"])
  notes=x.get("required_safety_notes")
  if not isinstance(notes,list) or len(notes)!=len(set(notes)) or any(not isinstance(n,str) for n in notes): fail("semantic safety notes: "+x["id"])
 risk=[x for x in cases if x["category"] in {"genuine-risk","required-standard","professional-boundary"}]
 if len(risk)<12: fail("insufficient safety-critical semantic coverage")
 return cases

def rag(root,bp):
 raw=(ROOT/"data/practice-rag.ndjson").read_text(encoding="utf-8"); rows=[json.loads(x) for x in raw.splitlines() if x]
 unique(rows,"chunk_id","RAG chunk"); br=unique(rows,"resource_id","RAG resource")
 if set(br)!=set(bp): fail("RAG practice set drift")
 for pid,row in br.items():
  src=bp[pid]
  expected={"chunk_id":f"{pid}:en:v1","canonical_url":src["canonical_url"],"locale":"en","mechanism_id":src["mechanism_id"],"review_status":REVIEW,"clinical_validation_status":CLINICAL,"safety_scope":root["safety_scope"]}
  for k,v in expected.items():
   if row.get(k)!=v: fail(f"RAG {pid} {k} drift")
  if "Avoid when:" not in row.get("text","") or "not clinically validated" not in row.get("text",""): fail("RAG safety text: "+pid)
  for exclusion in src["avoid_when"]:
   if exclusion not in row["text"]: fail(f"RAG {pid} missing exclusion {exclusion}")
  if hashlib.sha256(row["text"].encode()).hexdigest()!=row.get("sha256"): fail("RAG row hash: "+pid)
 man=J("data/practice-rag-manifest.json")
 if man.get("record_count")!=len(rows) or man.get("distribution")!=f"{ORIGIN}/data/practice-rag.ndjson": fail("RAG manifest count/distribution")
 if man.get("sha256")!=hashlib.sha256(raw.encode()).hexdigest(): fail("RAG manifest hash")
 if man.get("chunk_id_format")!="{resource_id}:en:v1" or man.get("review_status")!=REVIEW or man.get("clinical_validation_status")!=CLINICAL: fail("RAG manifest review/version metadata")
 sources=man.get("generated_from")
 if not isinstance(sources,list) or len(sources)<2: fail("RAG manifest generated_from")
 for src in sources:
  p=local(src.get("url",""))
  if p is None or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=src.get("sha256"): fail("RAG generated_from drift: "+str(src.get("url")))

def coverage(bp,bm,cases):
 data=J("data/practice-coverage.json"); rows=unique(data.get("mechanisms",[]),"mechanism_id","coverage mechanism")
 if set(rows)!=set(bm): fail("coverage mechanism set")
 for mid,row in rows.items():
  pids=[pid for pid,p in bp.items() if p["mechanism_id"]==mid]
  if row.get("practice_ids")!=pids: fail("coverage practices: "+mid)
  count=sum(bool(set(c.get("acceptable_practice_ids",[]))&set(pids)) for c in cases)
  if row.get("eval_case_count")!=count: fail("coverage eval count: "+mid)
 summary=data.get("summary",{})
 if summary.get("mechanisms")!=len(bm) or summary.get("published_practices")!=len(bp) or summary.get("semantic_eval_cases")!=len(cases): fail("coverage summary")
 q=data.get("editorial_queue",{}); defs=q.get("status_definitions",{})
 expected={"covered_single_practice","covered_multiple_practices","needs_practice","needs_evidence","needs_eval_coverage"}
 if set(defs)!=expected: fail("coverage queue taxonomy")
 if {x.get("mechanism_id") for x in q.get("items",[])}!=set(bm): fail("coverage queue mechanisms")
 pressure=q.get("source_audit_pressure",{})
 for k in ("similarity_groups","flagged_source_records","owned_practice_overlap_practices","priority_source_review_items","note"):
  if k not in pressure: fail("coverage duplicate-pressure signal: "+k)

def interoperability():
 data=J("data/interoperability-fixtures.json"); bf=unique(data.get("fixtures",[]),"client_class","interoperability fixture")
 if set(bf)!=set(EXPECTED_CLIENTS): fail("interoperability client set")
 for client,status in EXPECTED_CLIENTS.items():
  f=bf[client]
  if f.get("status")!=status: fail("interoperability status: "+client)
  ep=local(f.get("entrypoint",""))
  if ep is None or not ep.is_file(): fail("interoperability entrypoint: "+client)
  resources=f.get("expected_resources")
  if not isinstance(resources,list) or not resources or len(resources)!=len(set(resources)): fail("interoperability resources: "+client)
  for url in resources:
   p=local(url)
   if p is None or not p.is_file(): fail(f"interoperability missing resource {client}: {url}")
  if len(f.get("claim",""))<30: fail("interoperability weak claim: "+client)
 for client in ("OpenClaw-style Agent Skills consumer","Hermes Agent-style skill consumer"):
  if "not claimed as continuously CI-executed" not in bf[client]["claim"]: fail("interop overclaim: "+client)
 install=(ROOT/"agents/cbt-cards/INSTALL.md").read_text(encoding="utf-8")
 if "OpenClaw" not in install or "Hermes" not in install: fail("portable install notes")

def page(bp):
 text=(ROOT/"practice/index.html").read_text(encoding="utf-8")
 for fragment in ('id="finder"','id="methodology"',"local-only","no_match","Evidence and limitations","Best used when","Avoid when"):
  if fragment not in text: fail("practice page missing "+fragment)
 if text.count("<details><summary>Evidence and limitations</summary>")!=len(bp): fail("practice page evidence count")
 for pid in bp:
  if f'id="{pid}"' not in text: fail("practice page article: "+pid)

def main():
 root,bp,bm,bs=source_graph(); recommendations(bp,bs); relations(bp); cases=semantic(bp)
 subprocess.run([sys.executable,str(ROOT/"scripts/build_practice_artifacts.py"),"--check"],check=True)
 rag(root,bp); coverage(bp,bm,cases); interoperability(); page(bp)
 print(f"strict practice-system check passed: {len(bp)} practices, {len(bm)} mechanisms, {len(bs)} situations, {len(cases)} semantic cases; generated artifacts in sync")
if __name__=="__main__": main()
