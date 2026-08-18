#!/usr/bin/env python3
"""Validate the CBT Cards 115-record source-corpus editorial audit."""
from __future__ import annotations
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def J(p): return json.loads((R/p).read_text(encoding="utf-8"))
def F(m): raise SystemExit("toolkit audit check failed: "+m)
a=J("data/toolkit-audit.json"); s=J("data/toolkit-source.json"); rev=J("data/toolkit-review.json"); p=J("data/practice.json")
if a.get("schema_version")!="1.0" or a.get("source_dataset_id")!=s.get("id") or a.get("source_commit")!=s.get("source_commit"): F("source pin")
if a.get("source_record_count")!=s.get("record_count") or a.get("source_record_count")!=115: F("record count")
ids=set()
for rel in ("toolkit/cards/index.html","toolkit/metaphors/index.html","toolkit/protocols/index.html"):
 text=(R/rel).read_text(encoding="utf-8"); ids.update(re.findall(r"<code>((?:card|metaphor|protocol)-[0-9]+)</code>",text))
if len(ids)!=115: F(f"source index ids={len(ids)}")
parts=a.get("triage_partitions",{}); all_part=[]
for name,arr in parts.items():
 if len(arr)!=len(set(arr)): F("duplicate within partition "+name)
 all_part+=arr
if set(all_part)!=ids or len(all_part)!=115: F("triage partitions must be an exact 115-record partition")
pub=set(parts.get("published",[])); overlay={x["source_record_id"] for x in rev["records"] if x.get("publication_status")=="published"}
if pub!=overlay: F("published partition differs from toolkit review overlay")
protocols={x for x in ids if x.startswith("protocol-")}
if set(parts.get("do_not_promote_without_separate_protocol_review",[]))!=protocols: F("protocol gate")
risky={"card-20","card-22","card-24","card-30","card-46","card-51","card-52","card-53","card-60","card-64","card-65","card-71","card-72","card-74","card-75"}
if not risky<=set(parts.get("do_not_promote_without_rework",[])): F("known risky/rework cards")
flags=a.get("quality_flags",{})
if not {"card-24","card-54","card-36","card-68","protocol-1","protocol-8"}<=set(flags.get("duplicate_title",[])): F("duplicate-title flags")
for group in a.get("similarity_groups",[]):
 members=set(group.get("record_ids",[]))
 if len(members)<2 or not members<=ids: F("similarity group")
practice_ids={x["id"] for x in p["practices"]}
for pid,source_ids in a.get("owned_practice_overlaps",{}).items():
 if pid not in practice_ids or not set(source_ids)<=ids: F("owned-practice overlap")
summary=a["summary"]
if summary.get("records")!=115 or summary.get("published")!=len(pub): F("summary")
page=(R/"toolkit/audit/index.html").read_text(encoding="utf-8")
if "/data/toolkit-audit.json" not in page or "not publication approval" not in page.lower(): F("human audit boundary")
print(f"toolkit audit check passed: 115 records; {len(pub)} published; {summary['flagged_records']} flagged; {summary['similarity_groups']} similarity groups")
