#!/usr/bin/env python3
"""Validate the portable CBT Cards practice-system contract surface."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"contracts/practice-system-v1.schema.json"
DRAFT="https://json-schema.org/draft/2020-12/schema"
URL="https://cbt-cards.github.io/contracts/practice-system-v1.schema.json"

def fail(msg): raise SystemExit("practice contract check failed: "+msg)
def main():
 s=json.loads(PATH.read_text(encoding="utf-8"))
 if s.get("$schema")!=DRAFT or s.get("$id")!=URL or s.get("type")!="object": fail("root metadata")
 required=set(s.get("required",[]))
 for key in ("schema_version","id","canonical","updated","review_status","clinical_validation_status","safety_scope","ontology_url","evidence_url","relations_url","recommendation_contract_url","practices"):
  if key not in required: fail("root required "+key)
 props=s.get("properties",{})
 if props.get("review_status",{}).get("const")!="editorial_and_safety_reviewed_for_publication": fail("root review status")
 if props.get("clinical_validation_status",{}).get("const")!="not_claimed": fail("root clinical boundary")
 defs=s.get("$defs",{})
 expected={"practice","mechanism","situation","evidence","relation","recommendation_example","semantic_case","rag_record","interoperability_fixture"}
 if not expected<=set(defs): fail("missing reusable definitions")
 practice_req=set(defs["practice"].get("required",[]))
 for key in ("best_used_when","avoid_when","evidence_ids","review_status","clinical_validation_status"):
  if key not in practice_req: fail("practice required "+key)
 semantic=defs["semantic_case"]["properties"]
 if set(semantic["expected_outcome"].get("enum",[]))!={"match","clarify","no_match","resource_not_practice"}: fail("semantic outcome vocabulary")
 rag_req=set(defs["rag_record"].get("required",[]))
 for key in ("review_status","clinical_validation_status","safety_scope","sha256"):
  if key not in rag_req: fail("RAG required "+key)
 if defs["rag_record"]["properties"]["review_status"].get("const")!="editorial_and_safety_reviewed_for_publication": fail("RAG review status")
 if defs["rag_record"]["properties"]["clinical_validation_status"].get("const")!="not_claimed": fail("RAG clinical boundary")
 instances=s.get("x-instance-contracts",{})
 for key in ("practice","ontology","evidence","relations","recommendations","rag","coverage","interoperability"):
  if key not in instances: fail("instance contract discovery "+key)
 print("practice contract check passed: reviewed practice, semantic, RAG and interoperability definitions are explicit")
if __name__=="__main__": main()
