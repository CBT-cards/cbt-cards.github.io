#!/usr/bin/env python3
"""Validate CBT Cards-owned practice cards and metaphor pairs."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
EXPECTED_PAIR_IDS = {
    "practice-test-your-prediction",
    "practice-problem-or-worry",
    "practice-spot-the-safety-behavior",
}


def fail(message: str) -> None:
    raise SystemExit(f"practice check failed: {message}")


def main() -> None:
    data_path = ROOT / "data" / "practice.json"
    page_path = ROOT / "practice" / "index.html"
    catalog_path = ROOT / "data" / "catalog.json"
    schema_manifest_path = ROOT / "schemas" / "index.json"
    sitemap_path = ROOT / "sitemap.xml"
    learn_path = ROOT / "learn" / "index.html"
    llms_path = ROOT / "llms.txt"
    llms_full_path = ROOT / "llms-full.txt"

    for path in (
        data_path,
        page_path,
        catalog_path,
        schema_manifest_path,
        sitemap_path,
        learn_path,
        llms_path,
        llms_full_path,
    ):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    data = json.loads(data_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        fail("unexpected schema_version")
    if data.get("id") != "cbt-cards-practice-v1":
        fail("unexpected dataset id")
    if data.get("canonical") != f"{ORIGIN}/data/practice.json":
        fail("unexpected canonical URL")
    if data.get("review_status") != "editorial_and_safety_reviewed_for_publication":
        fail("practice library must state editorial and safety publication review")
    if data.get("clinical_validation_status") != "not_claimed":
        fail("practice library must not claim clinical validation")

    ownership = data.get("ownership", "").lower()
    if "separate" not in ownership or "source corpus" not in ownership:
        fail("ownership must clearly separate CBT Cards originals from the source corpus")

    safety_scope = data.get("safety_scope", "").lower()
    for phrase in ("general wellness", "not diagnosis", "genuine safety measures"):
        if phrase not in safety_scope:
            fail(f"safety_scope missing required boundary: {phrase}")

    pairs = data.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        fail("pairs must be a non-empty list")

    ids = [pair.get("id") for pair in pairs]
    if len(ids) != len(set(ids)):
        fail("duplicate practice pair id")
    if set(ids) != EXPECTED_PAIR_IDS:
        fail(f"practice pair set differs from expected set: {sorted(set(ids))}")

    metaphor_ids: set[str] = set()
    page_text = page_path.read_text(encoding="utf-8")
    for pair in pairs:
        pair_id = pair["id"]
        if f'id="{pair_id}"' not in page_text:
            fail(f"page missing pair anchor: {pair_id}")

        for field in ("target_patterns", "best_used_when", "avoid_when", "follow_up", "evidence_basis"):
            value = pair.get(field)
            if not isinstance(value, list) or not value:
                fail(f"{pair_id}: {field} must be a non-empty list")

        card = pair.get("card")
        if not isinstance(card, dict):
            fail(f"{pair_id}: missing card object")
        steps = card.get("steps")
        if not isinstance(steps, list) or len(steps) < 2:
            fail(f"{pair_id}: card steps must contain at least two items")
        for field in ("prompt", "micro_action", "reflection_question"):
            if not isinstance(card.get(field), str) or not card[field].strip():
                fail(f"{pair_id}: card missing {field}")

        metaphor = pair.get("metaphor")
        if not isinstance(metaphor, dict):
            fail(f"{pair_id}: missing metaphor object")
        metaphor_id = metaphor.get("id")
        if not isinstance(metaphor_id, str) or not metaphor_id:
            fail(f"{pair_id}: metaphor missing id")
        if metaphor_id in metaphor_ids:
            fail(f"duplicate metaphor id: {metaphor_id}")
        metaphor_ids.add(metaphor_id)
        if f'id="{metaphor_id}"' not in page_text:
            fail(f"page missing metaphor anchor: {metaphor_id}")
        for field in ("title", "text", "use"):
            if not isinstance(metaphor.get(field), str) or not metaphor[field].strip():
                fail(f"{pair_id}: metaphor missing {field}")

        for source in pair["evidence_basis"]:
            url = source.get("url", "")
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                fail(f"{pair_id}: evidence source must be an https URL: {url}")

    safety_pair = next(pair for pair in pairs if pair["id"] == "practice-spot-the-safety-behavior")
    avoid_text = " ".join(safety_pair["avoid_when"]).lower()
    for phrase in ("genuine safety measure", "driving", "medical risk", "abuse"):
        if phrase not in avoid_text:
            fail(f"safety-behavior card missing explicit avoid_when boundary: {phrase}")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    resource_by_id = {item.get("id"): item for item in catalog.get("resources", [])}
    expected_resources = {
        "practice": f"{ORIGIN}/practice/",
        "practice-data": f"{ORIGIN}/data/practice.json",
    }
    for resource_id, url in expected_resources.items():
        item = resource_by_id.get(resource_id)
        if not item or item.get("url") != url:
            fail(f"catalog missing or mismatching {resource_id}")

    if resource_by_id["practice-data"].get("schema_url") != f"{ORIGIN}/schemas/practice-v1.schema.json":
        fail("practice-data catalog resource missing practice schema_url")

    manifest = json.loads(schema_manifest_path.read_text(encoding="utf-8"))
    practice_schema = next((item for item in manifest.get("schemas", []) if item.get("id") == "practice-v1"), None)
    if not practice_schema:
        fail("schema manifest missing practice-v1")
    if practice_schema.get("url") != f"{ORIGIN}/schemas/practice-v1.schema.json":
        fail("practice-v1 schema URL mismatch")
    if practice_schema.get("instance") != f"{ORIGIN}/data/practice.json":
        fail("practice-v1 instance URL mismatch")

    sitemap_root = ET.parse(sitemap_path).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", ns)}
    if f"{ORIGIN}/practice/" not in sitemap_urls:
        fail("sitemap missing practice page")

    if 'href="/practice/"' not in learn_path.read_text(encoding="utf-8"):
        fail("learning hub does not link to practice page")

    for index_path in (llms_path, llms_full_path):
        text = index_path.read_text(encoding="utf-8")
        if f"{ORIGIN}/practice/" not in text or f"{ORIGIN}/data/practice.json" not in text:
            fail(f"{index_path.name} missing practice discovery URLs")

    print(f"practice check passed: {len(pairs)} reviewed card/metaphor pairs with explicit safety boundaries")


if __name__ == "__main__":
    main()
