#!/usr/bin/env python3
"""Validate CBT Cards review coverage and freshness across public content and owned practices."""
from __future__ import annotations
import json
from datetime import date,timedelta
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]; ORIGIN="https://cbt-cards.github.io"; CATALOG_TYPES={"learning","worksheet","toolkit-card"}
def fail(m): raise SystemExit("content review check failed: "+m)
def local_target(url):
 p=urlparse(url)
 if f"{p.scheme}://{p.netloc}"!=ORIGIN: return None
 return ROOT/p.path.lstrip("/")/"index.html" if p.path.endswith("/") else ROOT/p.path.lstrip("/")
def load_jsonl(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def main():
 registry=json.loads((ROOT/"data/content-review.json").read_text()); catalog=json.loads((ROOT/"data/catalog.json").read_text()); practice=json.loads((ROOT/"data/practice.json").read_text()); toolkit_review=json.loads((ROOT/"data/toolkit-review.json").read_text()); knowledge=load_jsonl(ROOT/"data/knowledge.jsonl")
 policy_page=ROOT/"about/editorial-review/index.html"; about_page=ROOT/"about/index.html"
 for p in (policy_page,about_page):
  if not p.exists(): fail(f"missing {p.relative_to(ROOT)}")
 if registry.get("schema_version")!="1.0" or registry.get("canonical")!=f"{ORIGIN}/data/content-review.json": fail("registry identity")
 policy=registry.get("policy",{})
 if set(policy.get("covered_catalog_resource_types",[]))!=CATALOG_TYPES or policy.get("include_owned_practices") is not True or policy.get("review_kind")!="editorial_source_and_safety" or policy.get("clinical_validation_status")!="not_claimed": fail("policy")
 interval=policy.get("target_interval_days")
 if not isinstance(interval,int) or interval<=0: fail("target interval")
 resources=catalog.get("resources",[]); by_id={x.get("id"):x for x in resources}
 if len(by_id)!=len(resources): fail("duplicate catalog IDs")
 for rid,url in {"content-review-page":f"{ORIGIN}/about/editorial-review/","content-review-data":f"{ORIGIN}/data/content-review.json"}.items():
  if rid not in by_id or by_id[rid].get("url")!=url: fail("catalog "+rid)
 expected_catalog={x["id"]:x for x in resources if x.get("type") in CATALOG_TYPES}; expected_practices={x["id"]:x for x in practice.get("practices",[])}
 items=registry.get("items",[]); by_review={}; today=date.today()
 for item in items:
  rid=item.get("id")
  if not rid or rid in by_review: fail("duplicate/missing id "+str(rid))
  by_review[rid]=item
  if item.get("status")!="reviewed" or item.get("review_scope")!="editorial_source_and_safety" or item.get("clinical_validation_status")!="not_claimed": fail("review status "+rid)
  try: last=date.fromisoformat(item.get("last_reviewed","")); due=date.fromisoformat(item.get("next_review_due",""))
  except ValueError: fail("review dates "+rid)
  if last>today or due!=last+timedelta(days=interval) or today>due: fail("freshness "+rid)
  target=local_target(item.get("canonical_url",""))
  if target is None or not target.exists(): fail("canonical target "+rid)
  if item.get("kind")=="catalog_resource":
   source=expected_catalog.get(rid)
   if not source or item.get("content_type")!=source.get("type") or item.get("canonical_url")!=source.get("url") or source.get("reviewed")!=item.get("last_reviewed"): fail("catalog alignment "+rid)
  elif item.get("kind")=="owned_practice":
   source=expected_practices.get(rid)
   if not source or item.get("content_type")!="practice" or item.get("canonical_url")!=source.get("canonical_url") or source.get("review_status")!="editorial_and_safety_reviewed_for_publication" or source.get("clinical_validation_status")!="not_claimed": fail("practice alignment "+rid)
  else: fail("unknown review kind "+rid)
 expected=set(expected_catalog)|set(expected_practices)
 if set(by_review)!=expected: fail(f"coverage mismatch missing={sorted(expected-set(by_review))} extra={sorted(set(by_review)-expected)}")
 knowledge_dates={x["id"]:x.get("reviewed") for x in knowledge if x.get("id") in expected_catalog}
 for rid,x in expected_catalog.items():
  if x.get("type") in {"learning","toolkit-card"} and knowledge_dates.get(rid)!=by_review[rid]["last_reviewed"]: fail("knowledge review date "+rid)
 overlay={x["catalog_resource_id"]:x for x in toolkit_review.get("records",[])}
 for rid,x in expected_catalog.items():
  if x.get("type")=="toolkit-card" and overlay.get(rid,{}).get("reviewed_at")!=by_review[rid]["last_reviewed"]: fail("toolkit overlay review date "+rid)
 if 'href="/about/editorial-review/"' not in about_page.read_text(encoding="utf-8"): fail("about page link")
 summary=registry.get("summary",{})
 if summary.get("covered_items")!=len(items) or summary.get("catalog_resources")!=len(expected_catalog) or summary.get("owned_practices")!=len(expected_practices): fail("summary counts")
 print(f"content review check passed: {len(items)} items ({len(expected_catalog)} catalog + {len(expected_practices)} practices), next due {min(x['next_review_due'] for x in items)}")
if __name__=="__main__": main()
