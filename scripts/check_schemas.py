#!/usr/bin/env python3
"""Validate CBT Cards public JSON Schema discovery and contract metadata."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
DRAFT = "https://json-schema.org/draft/2020-12/schema"
EXPECTED_IDS = {
    "catalog-v1",
    "changelog-v1",
    "content-review-v1",
    "worksheets-v1",
    "toolkit-review-v1",
    "toolkit-source-v1",
    "knowledge-record-v1",
    "skill-manifest-v1",
}


def fail(message: str) -> None:
    raise SystemExit(f"schema check failed: {message}")


def local_path(url: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    return ROOT / parsed.path.lstrip("/")


def main() -> None:
    manifest_path = ROOT / "schemas" / "index.json"
    catalog_path = ROOT / "data" / "catalog.json"
    if not manifest_path.exists():
        fail("missing schemas/index.json")
    if not catalog_path.exists():
        fail("missing data/catalog.json")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "1.0":
        fail("unexpected schema manifest version")

    entries = manifest.get("schemas")
    if not isinstance(entries, list):
        fail("schema manifest entries must be a list")

    ids = [entry.get("id") for entry in entries]
    if len(ids) != len(set(ids)):
        fail("duplicate schema IDs")
    if set(ids) != EXPECTED_IDS:
        fail(f"schema manifest IDs differ from expected set: {sorted(set(ids))}")

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    resource_by_url = {resource.get("url"): resource for resource in resources}
    resource_by_id = {resource.get("id"): resource for resource in resources}

    schema_manifest_resource = resource_by_id.get("schema-manifest")
    if not schema_manifest_resource or schema_manifest_resource.get("url") != f"{ORIGIN}/schemas/index.json":
        fail("catalog does not expose schema manifest")

    seen_schema_urls: set[str] = set()
    seen_instances: set[str] = set()

    for entry in entries:
        schema_id = entry["id"]
        schema_url = entry.get("url")
        instance_url = entry.get("instance")
        if not isinstance(schema_url, str) or not isinstance(instance_url, str):
            fail(f"missing URL for {schema_id}")
        if schema_url in seen_schema_urls:
            fail(f"duplicate schema URL: {schema_url}")
        seen_schema_urls.add(schema_url)
        if instance_url in seen_instances:
            fail(f"duplicate instance mapping: {instance_url}")
        seen_instances.add(instance_url)

        schema_path = local_path(schema_url)
        instance_path = local_path(instance_url)
        if schema_path is None or not schema_path.exists():
            fail(f"missing local schema for {schema_id}: {schema_url}")
        if instance_path is None or not instance_path.exists():
            fail(f"missing local instance for {schema_id}: {instance_url}")

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if schema.get("$schema") != DRAFT:
            fail(f"{schema_id} does not declare JSON Schema 2020-12")
        if schema.get("$id") != schema_url:
            fail(f"$id mismatch for {schema_id}")
        if schema.get("type") != "object":
            fail(f"root schema type must be object for {schema_id}")
        required = schema.get("required")
        if not isinstance(required, list) or not required:
            fail(f"schema has no required properties: {schema_id}")

        resource = resource_by_url.get(instance_url)
        if resource is None:
            fail(f"catalog missing schema-mapped instance: {instance_url}")
        if resource.get("schema_url") != schema_url:
            fail(f"catalog schema_url mismatch for {instance_url}")

    toolkit_review = json.loads((ROOT / "schemas" / "toolkit-review-v1.schema.json").read_text(encoding="utf-8"))
    default_props = toolkit_review["properties"]["default_for_unlisted_records"]["properties"]
    if default_props["review_status"].get("const") != "unreviewed":
        fail("toolkit-review schema must preserve unreviewed default")
    if default_props["publication_status"].get("const") != "source_only":
        fail("toolkit-review schema must preserve source_only default")
    if default_props["clinical_validation_status"].get("const") != "not_claimed":
        fail("toolkit-review schema must preserve not_claimed default")

    content_review = json.loads((ROOT / "schemas" / "content-review-v1.schema.json").read_text(encoding="utf-8"))
    policy_props = content_review["properties"]["policy"]["properties"]
    if policy_props["review_kind"].get("const") != "editorial_source_and_safety":
        fail("content-review schema must preserve editorial_source_and_safety review kind")
    if policy_props["clinical_validation_status"].get("const") != "not_claimed":
        fail("content-review schema must preserve not_claimed clinical status")

    knowledge = json.loads((ROOT / "schemas" / "knowledge-record-v1.schema.json").read_text(encoding="utf-8"))
    required_knowledge = set(knowledge.get("required", []))
    for key in ("canonical_url", "summary", "safety_scope", "reviewed", "sources"):
        if key not in required_knowledge:
            fail(f"knowledge record schema must require {key}")

    print(f"schema check passed: {len(entries)} versioned contracts discoverable from catalog")


if __name__ == "__main__":
    main()
