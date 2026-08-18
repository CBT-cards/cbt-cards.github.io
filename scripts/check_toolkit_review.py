#!/usr/bin/env python3
"""Validate CBT Cards toolkit review/publication overlay."""

from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"


def fail(message: str) -> None:
    raise SystemExit(f"toolkit review check failed: {message}")


def local_target(url: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    if parsed.path.endswith("/"):
        return ROOT / parsed.path.lstrip("/") / "index.html"
    return ROOT / parsed.path.lstrip("/")


def declared_skill_version(text: str) -> str | None:
    match = re.search(r"(?m)^version:\s*([^\s]+)\s*$", text)
    return match.group(1) if match else None


def main() -> None:
    review_path = ROOT / "data" / "toolkit-review.json"
    source_path = ROOT / "data" / "toolkit-source.json"
    catalog_path = ROOT / "data" / "catalog.json"
    knowledge_path = ROOT / "data" / "knowledge.jsonl"
    page_path = ROOT / "toolkit" / "review-status" / "index.html"
    sitemap_path = ROOT / "sitemap.xml"
    latest_skill_path = ROOT / "agents" / "cbt-cards" / "SKILL.md"
    manifest_path = ROOT / "agents" / "cbt-cards" / "manifest.json"
    v14_path = ROOT / "agents" / "cbt-cards" / "v1.4.0" / "SKILL.md"

    for path in (review_path, source_path, catalog_path, knowledge_path, page_path, sitemap_path, latest_skill_path, manifest_path, v14_path):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    review = json.loads(review_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if review.get("schema_version") != "1.0":
        fail("unexpected review schema_version")
    if review.get("canonical") != f"{ORIGIN}/data/toolkit-review.json":
        fail("unexpected review canonical URL")
    if review.get("source_dataset_id") != source.get("id"):
        fail("review overlay source_dataset_id does not match toolkit-source.json")

    defaults = review.get("default_for_unlisted_records", {})
    expected_defaults = {
        "review_status": "unreviewed",
        "publication_status": "source_only",
        "clinical_validation_status": "not_claimed",
    }
    if defaults != expected_defaults:
        fail(f"unexpected defaults for unlisted records: {defaults}")

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    resource_by_id = {item.get("id"): item for item in resources}

    for resource_id, expected_url in {
        "toolkit-review-page": f"{ORIGIN}/toolkit/review-status/",
        "toolkit-review-data": f"{ORIGIN}/data/toolkit-review.json",
        "agent-skill-v1.4.0": f"{ORIGIN}/agents/cbt-cards/v1.4.0/SKILL.md",
    }.items():
        resource = resource_by_id.get(resource_id)
        if not resource:
            fail(f"catalog missing {resource_id}")
        if resource.get("url") != expected_url:
            fail(f"catalog URL mismatch for {resource_id}")

    latest = manifest.get("latest")
    if not isinstance(latest, str) or not latest:
        fail("skill manifest missing latest version")
    latest_catalog = resource_by_id.get("agent-skill-latest")
    if not latest_catalog or latest_catalog.get("version") != latest:
        fail("catalog latest skill does not match manifest latest")
    immutable_latest = resource_by_id.get(f"agent-skill-v{latest}")
    if not immutable_latest:
        fail(f"catalog missing immutable latest skill v{latest}")

    records = review.get("records")
    if not isinstance(records, list) or not records:
        fail("review records must be a non-empty list")

    seen_source_ids: set[str] = set()
    overlay_by_source: dict[str, dict] = {}
    for record in records:
        source_id = record.get("source_record_id")
        if not isinstance(source_id, str) or not source_id:
            fail("record missing source_record_id")
        if source_id in seen_source_ids:
            fail(f"duplicate source_record_id: {source_id}")
        seen_source_ids.add(source_id)
        overlay_by_source[source_id] = record

        if record.get("review_status") != "reviewed_for_publication":
            fail(f"unexpected review_status for {source_id}")
        if record.get("publication_status") != "published":
            fail(f"unexpected publication_status for {source_id}")
        if record.get("clinical_validation_status") != "not_claimed":
            fail(f"clinical validation must not be claimed for {source_id}")
        if record.get("review_scope") != "editorial_and_safety_for_public_web_use":
            fail(f"unexpected review_scope for {source_id}")

        catalog_id = record.get("catalog_resource_id")
        catalog_resource = resource_by_id.get(catalog_id)
        if not catalog_resource:
            fail(f"missing catalog resource {catalog_id} for {source_id}")
        if catalog_resource.get("source_record_id") != source_id:
            fail(f"catalog source_record_id mismatch for {source_id}")
        if catalog_resource.get("url") != record.get("canonical_url"):
            fail(f"canonical URL mismatch for {source_id}")

        target = local_target(record.get("canonical_url", ""))
        if target is None or not target.exists():
            fail(f"published page missing for {source_id}: {record.get('canonical_url')}")

    catalog_toolkit_cards = {
        item.get("source_record_id"): item
        for item in resources
        if item.get("type") == "toolkit-card"
    }
    if set(catalog_toolkit_cards) != seen_source_ids:
        fail("published toolkit-card catalog set does not match review overlay")

    knowledge_toolkit: dict[str, dict] = {}
    for line_number, line in enumerate(knowledge_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid knowledge JSONL line {line_number}: {exc}")
        if item.get("type") == "toolkit-card":
            source_id = item.get("source_record_id")
            if source_id in knowledge_toolkit:
                fail(f"duplicate toolkit source_record_id in knowledge.jsonl: {source_id}")
            knowledge_toolkit[source_id] = item

    if set(knowledge_toolkit) != seen_source_ids:
        fail("curated toolkit-card JSONL set does not match review overlay")

    for source_id, item in knowledge_toolkit.items():
        if item.get("canonical_url") != overlay_by_source[source_id].get("canonical_url"):
            fail(f"knowledge canonical URL mismatch for {source_id}")

    sitemap_root = ET.parse(sitemap_path).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", ns)}
    if f"{ORIGIN}/toolkit/review-status/" not in sitemap_urls:
        fail("sitemap missing toolkit review-status page")

    skill = latest_skill_path.read_text(encoding="utf-8")
    if declared_skill_version(skill) != latest:
        fail("latest skill declaration does not match manifest latest")
    if f"{ORIGIN}/data/toolkit-review.json" not in skill:
        fail("latest skill does not reference toolkit review overlay")
    if "unreviewed" not in skill or "source_only" not in skill:
        fail("latest skill does not preserve default raw-record status")

    print(f"toolkit review check passed: {len(records)} published records; latest skill v{latest}; unlisted records default to source-only")


if __name__ == "__main__":
    main()
