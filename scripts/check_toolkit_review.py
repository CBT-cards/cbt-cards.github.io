#!/usr/bin/env python3
"""Validate CBT Cards toolkit review/publication overlay across web and Agent Skill surfaces."""

from __future__ import annotations

import json
from pathlib import Path
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


def main() -> None:
    review_path = ROOT / "data" / "toolkit-review.json"
    source_path = ROOT / "data" / "toolkit-source.json"
    catalog_path = ROOT / "data" / "catalog.json"
    marketplace_path = ROOT / "data" / "skill-marketplace.json"
    knowledge_path = ROOT / "data" / "knowledge.jsonl"
    page_path = ROOT / "toolkit" / "review-status" / "index.html"
    marketplace_page = ROOT / "skills" / "index.html"
    sitemap_path = ROOT / "sitemap.xml"
    latest_skill_path = ROOT / "agents" / "cbt-cards" / "SKILL.md"
    skill_manifest_path = ROOT / "agents" / "cbt-cards" / "manifest.json"

    for path in (
        review_path,
        source_path,
        catalog_path,
        marketplace_path,
        knowledge_path,
        page_path,
        marketplace_page,
        sitemap_path,
        latest_skill_path,
        skill_manifest_path,
    ):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    review = json.loads(review_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    skill_manifest = json.loads(skill_manifest_path.read_text(encoding="utf-8"))

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

    latest_skill_version = skill_manifest.get("latest")
    if not isinstance(latest_skill_version, str) or not latest_skill_version:
        fail("skill manifest missing latest version")
    expected_latest_url = f"{ORIGIN}/agents/cbt-cards/SKILL.md"
    if skill_manifest.get("latest_url") != expected_latest_url:
        fail("skill manifest latest_url mismatch")

    immutable_skill_url = f"{ORIGIN}/agents/cbt-cards/v{latest_skill_version}/SKILL.md"
    manifest_versions = {
        item.get("version"): item.get("url")
        for item in skill_manifest.get("versions", [])
        if isinstance(item, dict)
    }
    if manifest_versions.get(latest_skill_version) != immutable_skill_url:
        fail("skill manifest latest version is not mapped to its immutable URL")

    immutable_skill_path = local_target(immutable_skill_url)
    if immutable_skill_path is None or not immutable_skill_path.exists():
        fail(f"latest immutable skill is missing: {immutable_skill_url}")

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    resource_by_id = {item.get("id"): item for item in resources}
    market_items = marketplace.get("skills", [])
    market_by_id = {item.get("id"): item for item in market_items if isinstance(item, dict)}

    latest_skill_resource_id = f"agent-skill-v{latest_skill_version}"
    for resource_id, expected_url in {
        "toolkit-review-page": f"{ORIGIN}/toolkit/review-status/",
        "toolkit-review-data": f"{ORIGIN}/data/toolkit-review.json",
        latest_skill_resource_id: immutable_skill_url,
    }.items():
        resource = resource_by_id.get(resource_id)
        if not resource:
            fail(f"catalog missing {resource_id}")
        if resource.get("url") != expected_url:
            fail(f"catalog URL mismatch for {resource_id}")

    latest_alias_resource = resource_by_id.get("agent-skill-latest")
    if not latest_alias_resource:
        fail("catalog missing agent-skill-latest")
    if latest_alias_resource.get("url") != expected_latest_url:
        fail("catalog latest skill URL mismatch")
    if latest_alias_resource.get("version") != latest_skill_version:
        fail("catalog latest skill version does not match manifest")

    records = review.get("records")
    if not isinstance(records, list) or not records:
        fail("review records must be a non-empty list")

    seen_source_ids: set[str] = set()
    overlay_by_source: dict[str, dict] = {}
    catalog_sources: set[str] = set()
    agent_skill_sources: set[str] = set()
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

        target = local_target(record.get("canonical_url", ""))
        if target is None or not target.exists():
            fail(f"published page missing for {source_id}: {record.get('canonical_url')}")

        publication_surface = record.get("publication_surface", "catalog_resource")
        publication_id = record.get("catalog_resource_id")
        if publication_surface == "catalog_resource":
            catalog_resource = resource_by_id.get(publication_id)
            if not catalog_resource:
                fail(f"missing catalog resource {publication_id} for {source_id}")
            if catalog_resource.get("source_record_id") != source_id:
                fail(f"catalog source_record_id mismatch for {source_id}")
            if catalog_resource.get("url") != record.get("canonical_url"):
                fail(f"canonical URL mismatch for {source_id}")
            catalog_sources.add(source_id)
        elif publication_surface == "agent_skill":
            if not source_id.startswith("metaphor-"):
                fail(f"agent_skill publication must be a metaphor source record: {source_id}")
            market_item = market_by_id.get(publication_id)
            if not market_item:
                fail(f"missing marketplace record {publication_id} for {source_id}")
            if market_item.get("kind") != "metaphor" or market_item.get("source_id") != source_id:
                fail(f"marketplace source/kind mismatch for {source_id}")
            if market_item.get("name") != record.get("skill_name"):
                fail(f"skill_name mismatch for {source_id}")
            if market_item.get("canonical_human_url") != record.get("canonical_url"):
                fail(f"marketplace canonical URL mismatch for {source_id}")
            skill_path = local_target(market_item.get("skill_url", ""))
            if skill_path is None or not skill_path.exists():
                fail(f"marketplace SKILL.md missing for {source_id}")
            agent_skill_sources.add(source_id)
        else:
            fail(f"unknown publication_surface for {source_id}: {publication_surface}")

    expected_agent_skill_sources = {"metaphor-4", "metaphor-5", "metaphor-18", "metaphor-19"}
    if agent_skill_sources != expected_agent_skill_sources:
        fail(f"unexpected reviewed metaphor Agent Skill set: {sorted(agent_skill_sources)}")

    catalog_toolkit_cards = {
        item.get("source_record_id"): item
        for item in resources
        if item.get("type") == "toolkit-card"
    }
    if set(catalog_toolkit_cards) != catalog_sources:
        fail("published toolkit-card catalog set does not match catalog-resource review records")

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

    if set(knowledge_toolkit) != catalog_sources:
        fail("curated toolkit-card JSONL set does not match catalog-resource review records")
    for source_id, item in knowledge_toolkit.items():
        if item.get("canonical_url") != overlay_by_source[source_id].get("canonical_url"):
            fail(f"knowledge canonical URL mismatch for {source_id}")

    sitemap_root = ET.parse(sitemap_path).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", ns)}
    for expected in (f"{ORIGIN}/toolkit/review-status/", f"{ORIGIN}/skills/"):
        if expected not in sitemap_urls:
            fail(f"sitemap missing publication surface {expected}")

    skill = latest_skill_path.read_text(encoding="utf-8")
    immutable_skill = immutable_skill_path.read_text(encoding="utf-8")
    if f"version: {latest_skill_version}" not in skill:
        fail(f"latest skill alias is not v{latest_skill_version}")
    if skill != immutable_skill:
        fail("latest skill alias does not match latest immutable skill")
    if f"{ORIGIN}/data/toolkit-review.json" not in skill:
        fail("latest skill does not reference toolkit review overlay")
    if "unreviewed" not in skill or "source_only" not in skill:
        fail("latest skill does not preserve default raw-record status")

    print(
        f"toolkit review check passed: {len(records)} published source records "
        f"({len(catalog_sources)} catalog, {len(agent_skill_sources)} metaphor Agent Skills); "
        f"latest broad skill v{latest_skill_version}; unlisted records default to source-only"
    )


if __name__ == "__main__":
    main()
