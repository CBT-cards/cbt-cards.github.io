#!/usr/bin/env python3
"""Validate CBT Cards public JSON Schema discovery and safety-critical contract metadata."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
ORIGIN="https://cbt-cards.github.io"
DRAFT="https://json-schema.org/draft/2020-12/schema"
EXPECTED_IDS={
 "catalog-v1","changelog-v1","worksheets-v1","toolkit-review-v1","toolkit-source-v1",
 "content-review-v1","toolkit-audit-v1","knowledge-record-v1","locales-v1","translation-record-v1",
 "agent-eval-case-v1","agent-eval-run-v1","agent-eval-challenge-run-v1",
 "agent-model-response-v1","agent-model-run-v1","skill-manifest-v1",
}
def fail(m): raise SystemExit("schema check failed: "+m)
def local(url):
 p=urlparse(url)
 if f"{p.scheme}://{p.netloc}"!=ORIGIN: return None
 return ROOT/p.path.lstrip("/")
def run_shape(schema,label,dataset):
 req=set(schema.get("required",[]))
 for k in ("id","eval_dataset","eval_dataset_sha256","executed","runner","metrics","case_results","notes"):
  if k not in req: fail(f"{label} must require {k}")
 if schema.get("properties",{}).get("eval_dataset",{}).get("const")!=dataset: fail(f"{label} dataset")
 runner=set(schema["properties"]["runner"].get("required",[]))
 for k in ("id","type","version","implementation_url","input_fields"):
  if k not in runner: fail(f"{label} runner {k}")
def main():
 manifest=json.loads((ROOT/"schemas/index.json").read_text()); catalog=json.loads((ROOT/"data/catalog.json").read_text())
 if manifest.get("schema_version")!="1.0": fail("manifest version")
 entries=manifest.get("schemas")
 if not isinstance(entries,list): fail("manifest list")
 ids=[x.get("id") for x in entries]
 if len(ids)!=len(set(ids)) or set(ids)!=EXPECTED_IDS: fail("manifest ID set")
 resources=catalog.get("resources")
 if not isinstance(resources,list): fail("catalog resources")
 by_url={x.get("url"):x for x in resources}; by_id={x.get("id"):x for x in resources}
 if by_id.get("schema-manifest",{}).get("url")!=f"{ORIGIN}/schemas/index.json": fail("schema-manifest catalog entry")
 seen_schema=set(); seen_inst=set(); interface_only=0
 for e in entries:
  sid=e["id"]; surl=e.get("url"); inst=e.get("instance")
  if not isinstance(surl,str) or surl in seen_schema: fail("schema URL "+str(sid))
  seen_schema.add(surl); sp=local(surl)
  if sp is None or not sp.exists(): fail("missing schema "+surl)
  s=json.loads(sp.read_text())
  if s.get("$schema")!=DRAFT or s.get("$id")!=surl or s.get("type")!="object": fail("schema root "+sid)
  if not isinstance(s.get("required"),list) or not s["required"]: fail("schema required "+sid)
  if inst is None: interface_only+=1; continue
  if not isinstance(inst,str) or inst in seen_inst: fail("instance "+sid)
  seen_inst.add(inst); ip=local(inst)
  if ip is None or not ip.exists(): fail("missing instance "+inst)
  if by_url.get(inst,{}).get("schema_url")!=surl: fail("catalog schema_url "+inst)
 tr=json.loads((ROOT/"schemas/toolkit-review-v1.schema.json").read_text()); dp=tr["properties"]["default_for_unlisted_records"]["properties"]
 if dp["review_status"].get("const")!="unreviewed" or dp["publication_status"].get("const")!="source_only" or dp["clinical_validation_status"].get("const")!="not_claimed": fail("toolkit safe defaults")
 cr=json.loads((ROOT/"schemas/content-review-v1.schema.json").read_text())
 if cr["properties"]["policy"]["properties"]["clinical_validation_status"].get("const")!="not_claimed": fail("content review clinical boundary")
 ta=json.loads((ROOT/"schemas/toolkit-audit-v1.schema.json").read_text())
 if ta["properties"]["source_record_count"].get("const")!=115: fail("audit record count")
 if ta["properties"]["scope"]["properties"]["publication_authority"].get("const")!="none": fail("audit publication authority")
 knowledge=json.loads((ROOT/"schemas/knowledge-record-v1.schema.json").read_text())
 for k in ("canonical_url","summary","safety_scope","reviewed","sources"):
  if k not in set(knowledge.get("required",[])): fail("knowledge "+k)
 locales=json.loads((ROOT/"schemas/locales-v1.schema.json").read_text())
 for k in ("canonical","source_locale","updated","locales"):
  if k not in set(locales.get("required",[])): fail("locales "+k)
 trans=json.loads((ROOT/"schemas/translation-record-v1.schema.json").read_text())
 for k in ("resource_id","locale","source_locale","source_reviewed","translation_status","review_status","publication_status","canonical_url","reviewed","title","safety_scope"):
  if k not in set(trans.get("required",[])): fail("translation "+k)
 props=trans["properties"]
 if set(props["translation_status"].get("enum",[]))!={"machine_draft","human_reviewed"}: fail("translation status enum")
 if set(props["publication_status"].get("enum",[]))!={"not_published","published"}: fail("translation publication enum")
 ae=json.loads((ROOT/"schemas/agent-eval-case-v1.schema.json").read_text())
 for k in ("id","category","user_message","expected_route","expected_resource_ids","expected_source_record_ids","expected_checks","prohibited_claims","rationale"):
  if k not in set(ae.get("required",[])): fail("agent eval "+k)
 run_shape(json.loads((ROOT/"schemas/agent-eval-run-v1.schema.json").read_text()),"agent eval run",f"{ORIGIN}/data/agent-evals.jsonl")
 run_shape(json.loads((ROOT/"schemas/agent-eval-challenge-run-v1.schema.json").read_text()),"challenge run",f"{ORIGIN}/data/agent-evals-challenge.jsonl")
 mr=json.loads((ROOT/"schemas/agent-model-response-v1.schema.json").read_text())
 for k in ("case_id","answer","route","resource_ids","source_record_ids","locale_behavior"):
  if k not in set(mr.get("required",[])): fail("model response "+k)
 mrun=json.loads((ROOT/"schemas/agent-model-run-v1.schema.json").read_text())
 for k in ("id","eval_dataset","eval_dataset_sha256","executed","model","prompt","evaluator","metrics","case_results","semantic_evaluation","notes"):
  if k not in set(mrun.get("required",[])): fail("model run "+k)
 model_req=set(mrun["properties"]["model"].get("required",[]))
 for k in ("provider","model","version_or_snapshot","runtime","runtime_metadata"):
  if k not in model_req: fail("model provenance "+k)
 pp=mrun["properties"]["prompt"]["properties"]
 if pp["expected_fields_hidden"].get("const") is not True or pp["url"].get("const")!=f"{ORIGIN}/research/model-run-prompt-v1.txt": fail("model prompt contract")
 ep=mrun["properties"]["evaluator"]["properties"]
 if ep["id"].get("const")!="route-contract-evaluator-v1": fail("evaluator id")
 sem=mrun["properties"]["semantic_evaluation"]["properties"]
 for k in ("automatic_expected_checks_scored","automatic_prohibited_claims_scored"):
  if sem[k].get("type")!="boolean": fail("semantic flag "+k)
 print(f"schema check passed: {len(entries)} contracts; {interface_only} interface-only")
if __name__=="__main__": main()
