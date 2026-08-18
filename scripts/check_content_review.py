#!/usr/bin/env python3
"""Validate CBT Cards editorial review coverage and freshness."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
EXPECTED_TYPES = {"learning", "worksheet", "toolkit-card"}


def fail(message: str) -> None:
    raise SystemExit(f"content review check failed: {message}")


def local_target(url: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    if parsed.path.endswith("/"):
        return ROOT / parsed.path.lstrip("/") / "index.html"
    return ROOT / parsed.path.lstrip("/")


def main() -> None:
    registry_path = ROOT / "data" / "content-review.json"
    catalog_path = ROOT / "data" / "catalog.json"
    knowledge_path = ROOT / "data" / "knowledge.jsonl"
    policy_page = ROOT / "about" / "editorial-review" / "index.html"
    sitemap_path = ROOT / "sitemap.xml"
    about_path = ROOT / "about" / "index.html"
    latest_skill_path = ROOT / "agents" / "cbt-cards" / "SKILL.md"
    manifest_path = ROOT / "agents" / "cbt-cards" / "manifest.json"

    for path in (registry_path, catalog_path, knowledge_path, policy_page, sitemap_path, about_path, latest_skill_path, manifest_path):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if registry.get("schema_version") != "1.0":
        fail("unexpected schema_version")
    if registry.get("canonical") != f"{ORIGIN}/data/content-review.json":
        fail("unexpected registry canonical URL")

    policy = registry.get("policy", {})
    covered_types = set(policy.get("covered_resource_types", []))
    if covered_types != EXPECTED_TYPES:
        fail(f"covered resource types must be exactly {sorted(EXPECTED_TYPES)}")
    if policy.get("review_kind") != "editorial_source_and_safety":
        fail("unexpected review_kind")
    if policy.get("clinical_validation_status") != "not_claimed":
        fail("registry must not claim clinical validation")
    interval = policy.get("target_interval_days")
    if not isinstance(interval, int) or interval <= 0:
        fail("target_interval_days must be a positive integer")

    catalog_resources = catalog.get("resources")
    if not isinstance(catalog_resources, list):
        fail("catalog resources must be a list")
    catalog_by_id = {item.get("id"): item for item in catalog_resources}
    if len(catalog_by_id) != len(catalog_resources):
        fail("catalog resource IDs must be unique")

    for required_id, expected_url in {
        "content-review-page": f"{ORIGIN}/about/editorial-review/",
        "content-review-data": f"{ORIGIN}/data/content-review.json",
        "agent-skill-v1.5.0": f"{ORIGIN}/agents/cbt-cards/v1.5.0/SKILL.md",
    }.items():
        item = catalog_by_id.get(required_id)
        if not item:
            fail(f"catalog missing {required_id}")
        if item.get("url") != expected_url:
            fail(f"catalog URL mismatch for {required_id}")

    latest_catalog = catalog_by_id.get("agent-skill-latest")
    if not latest_catalog or latest_catalog.get("version") != "1.5.0":
        fail("catalog latest skill is not v1.5.0")
    if manifest.get("latest") != "1.5.0":
        fail("skill manifest latest is not v1.5.0")

    covered_catalog = {
        item["id"]: item
        for item in catalog_resources
        if item.get("type") in EXPECTED_TYPES
    }

    records = registry.get("resources")
    if not isinstance(records, list) or not records:
        fail("registry resources must be a non-empty list")
    review_by_id: dict[str, dict] = {}
    today = date.today()

    for record in records:
        resource_id = record.get("resource_id")
        if not isinstance(resource_id, str) or not resource_id:
            fail("review entry missing resource_id")
        if resource_id in review_by_id:
            fail(f"duplicate review entry: {resource_id}")
        review_by_id[resource_id] = record

        catalog_item = covered_catalog.get(resource_id)
        if not catalog_item:
            fail(f"review entry is not a covered catalog resource: {resource_id}")
        if record.get("content_type") != catalog_item.get("type"):
            fail(f"content_type mismatch for {resource_id}")
        if record.get("status") != "reviewed":
            fail(f"resource must be reviewed: {resource_id}")
        if record.get("review_scope") != "editorial_source_and_safety":
            fail(f"unexpected review_scope for {resource_id}")
        if record.get("clinical_validation_status") != "not_claimed":
            fail(f"clinical validation must not be claimed for {resource_id}")

        try:
            last_reviewed = date.fromisoformat(record.get("last_reviewed", ""))
            next_due = date.fromisoformat(record.get("next_review_due", ""))
        except ValueError as exc:
            fail(f"invalid review date for {resource_id}: {exc}")
        if last_reviewed > today:
            fail(f"last_reviewed is in the future for {resource_id}")
        expected_due = last_reviewed + timedelta(days=interval)
        if next_due != expected_due:
            fail(f"next_review_due mismatch for {resource_id}: expected {expected_due}, got {next_due}")
        if today > next_due:
            fail(f"review overdue for {resource_id}: due {next_due}")
        if catalog_item.get("reviewed") != last_reviewed.isoformat():
            fail(f"catalog reviewed date mismatch for {resource_id}")

        target = local_target(catalog_item.get("url", ""))
        if target is None or not target.exists():
            fail(f"missing canonical page for {resource_id}: {catalog_item.get('url')}")

    if set(review_by_id) != set(covered_catalog):
        missing = sorted(set(covered_catalog) - set(review_by_id))
        extra = sorted(set(review_by_id) - set(covered_catalog))
        fail(f"registry/catalog coverage mismatch; missing={missing}, extra={extra}")

    knowledge_reviewed: dict[str, str] = {}
    for line_number, line in enumerate(knowledge_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid knowledge JSONL line {line_number}: {exc}")
        resource_id = item.get("id")
        if resource_id in review_by_id:
            knowledge_reviewed[resource_id] = item.get("reviewed")

    expected_knowledge_ids = {
        resource_id for resource_id, item in covered_catalog.items()
        if item.get("type") in {"learning", "toolkit-card"}
    }
    if set(knowledge_reviewed) != expected_knowledge_ids:
        fail("learning/toolkit review registry set does not match curated knowledge dataset")
    for resource_id in expected_knowledge_ids:
        if knowledge_reviewed[resource_id] != review_by_id[resource_id]["last_reviewed"]:
            fail(f"knowledge reviewed date mismatch for {resource_id}")

    sitemap_root = ET.parse(sitemap_path).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", ns)}
    if f"{ORIGIN}/about/editorial-review/" not in sitemap_urls:
        fail("sitemap missing editorial review page")

    about_text = about_path.read_text(encoding="utf-8")
    if 'href="/about/editorial-review/"' not in about_text:
        fail("about page does not link editorial review policy")

    skill_text = latest_skill_path.read_text(encoding="utf-8")
    if "version: 1.5.0" not in skill_text:
        fail("latest skill file is not v1.5.0")
    if f"{ORIGIN}/data/content-review.json" not in skill_text:
        fail("latest skill does not reference content review registry")
    if "next_review_due" not in skill_text:
        fail("latest skill does not describe review freshness behavior")

    print(f"content review check passed: {len(records)} covered resources, next due {min(date.fromisoformat(r['next_review_due']) for r in records)}")


if __name__ == "__main__":
    main()
