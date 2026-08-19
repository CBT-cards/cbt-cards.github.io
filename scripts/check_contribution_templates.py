#!/usr/bin/env python3
"""Validate CBT Cards contribution forms against current editorial contracts."""
from __future__ import annotations
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATES=ROOT/".github/ISSUE_TEMPLATE"

def fail(msg): raise SystemExit("contribution template check failed: "+msg)

def blocks(path: Path):
 text=path.read_text(encoding="utf-8")
 found=[]
 for m in re.finditer(r"(?ms)^  - type: ([^\n]+)\n(.*?)(?=^  - type: |\Z)",text):
  kind=m.group(1).strip(); body=m.group(2); im=re.search(r"(?m)^    id: ([a-z0-9_]+)\s*$",body)
  found.append((kind,im.group(1) if im else None,body))
 return text,found

def validate_form(name,required_ids,required_text=()):
 path=TEMPLATES/name
 if not path.is_file(): fail("missing form "+name)
 text,items=blocks(path)
 ids=[i for _,i,_ in items if i]
 if len(ids)!=len(set(ids)): fail("duplicate field id in "+name)
 missing=set(required_ids)-set(ids)
 if missing: fail(f"{name} missing required fields {sorted(missing)}")
 by_id={i:(kind,body) for kind,i,body in items if i}
 for field in required_ids:
  body=by_id[field][1]
  if "required: true" not in body: fail(f"{name} field {field} is not required")
 for fragment in required_text:
  if fragment not in text: fail(f"{name} missing boundary text: {fragment}")
 return text,by_id

def main():
 for existing in ("data-bug.yml","safety-correction.yml","translation-review.yml"):
  if not (TEMPLATES/existing).is_file(): fail("missing existing workflow form "+existing)

 practice_text,practice=validate_form(
  "new-practice.yml",
  {"title","mechanism","situations","best_used_when","avoid_when","prompt","micro_action","reflection_question","evidence","claim_limits","wording_origin","rights_provenance","boundaries"},
  ("not publication, clinical validation, or evidence of efficacy","Evidence for a mechanism is not automatically evidence for this exact short-card format","copyrighted","Quoted wording with explicit reuse permission")
 )
 if practice["wording_origin"][0]!="dropdown": fail("new-practice wording_origin must be a dropdown")
 if practice["boundaries"][0]!="checkboxes": fail("new-practice boundaries must be checkboxes")
 if practice["boundaries"][1].count("required: true")<2: fail("new-practice needs two required boundary attestations")

 metaphor_text,metaphor=validate_form(
  "new-metaphor.yml",
  {"title","concept","metaphor_text","memory_job","misuse_risks","wording_origin","provenance","boundaries"},
  ("memory aid, not as evidence","They are not evidence","copyrighted","Quoted wording with explicit reuse permission")
 )
 if metaphor["wording_origin"][0]!="dropdown": fail("new-metaphor wording_origin must be a dropdown")
 if metaphor["boundaries"][1].count("required: true")<2: fail("new-metaphor needs two required boundary attestations")

 evidence_text,evidence=validate_form(
  "evidence-update.yml",
  {"target","source_url","evidence_class","supports","claim_scope","does_not_establish","source_status","boundaries"},
  ("what does the source support, and what does it not establish","mechanism does not automatically validate a CBT Cards short practice as treatment","guideline_supported","practical_editorial")
 )
 if evidence["evidence_class"][0]!="dropdown": fail("evidence_class must be a dropdown")
 if evidence["boundaries"][1].count("required: true")<2: fail("evidence form needs two required boundary attestations")

 guide=(ROOT/"CONTRIBUTING.md").read_text(encoding="utf-8")
 for fragment in (
  "proposed -> evidence_review -> safety_review -> editorial_review -> published",
  "memory aid, not evidence",
  "original, adapted, or quoted",
  "what the source does **not** establish",
  "python3 scripts/build_practice_artifacts.py --write",
  "Do not hand-edit a generated practice artifact",
  "LICENSING_DECISION.md",
 ):
  if fragment not in guide: fail("CONTRIBUTING.md missing current rule: "+fragment)
 print("contribution template check passed: practice, metaphor, evidence and editorial workflow forms match current contracts")
if __name__=="__main__": main()
