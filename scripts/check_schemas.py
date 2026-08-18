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
    "worksheets-v1",
    "toolkit-review-v1",
    "toolkit-source-v1",
    "knowledge-record-v1",
    "locales-v1",
    "translation-record-v1",
    "agent-eval-case-v1",
    "agent-eval-run-v1",
    "agent-eval-challenge-run-v1",
    "skill-manifest-v1",
}


def fail(message: str) -> None:
    raise SystemExit(f"schema check failed: {message}")


def local_path(url: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    return ROOT / parsed.path.lstrip("/")


def validate_run_shape(schema: dict, label: str, expected_dataset: str) -> None:
    required_run = set(schema.get("required", []))
    for key in ("id", "eval_dataset", "eval_dataset_sha256", "executed", "runner", "metrics", "case_results", "notes"):
        if key not in required_run:
            fail(f"{label} must require {key}")
    if schema.get("properties", {}).get("eval_dataset", {}).get("const") != expected_dataset:
        fail(f"{label} must pin eval_dataset to {expected_dataset}")
    runner_required = set(schema["properties"]["runner"].get("required", []))
    for key in ("id", "type", "version", "implementation_url", "input_fields"):
        if key not in runner_required:
            fail(f"{label} runner must require {key}")


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

    knowledge = json.loads((ROOT / "schemas" / "knowledge-record-v1.schema.json").read_text(encoding="utf-8"))
    required_knowledge = set(knowledge.get("required", []))
    for key in ("canonical_url", "summary", "safety_scope", "reviewed", "sources"):
        if key not in required_knowledge:
            fail(f"knowledge record schema must require {key}")

    locales = json.loads((ROOT / "schemas" / "locales-v1.schema.json").read_text(encoding="utf-8"))
    required_locales = set(locales.get("required", []))
    for key in ("canonical", "source_locale", "updated", "locales"):
        if key not in required_locales:
            fail(f"locale registry schema must require {key}")

    translation = json.loads((ROOT / "schemas" / "translation-record-v1.schema.json").read_text(encoding="utf-8"))
    required_translation = set(translation.get("required", []))
    for key in (
        "resource_id", "locale", "source_locale", "source_reviewed", "translation_status",
        "review_status", "publication_status", "canonical_url", "reviewed", "title", "safety_scope",
    ):
        if key not in required_translation:
            fail(f"translation record schema must require {key}")

    translation_props = translation.get("properties", {})
    if set(translation_props.get("translation_status", {}).get("enum", [])) != {"machine_draft", "human_reviewed"}:
        fail("translation schema must distinguish machine_draft and human_reviewed")
    if set(translation_props.get("publication_status", {}).get("enum", [])) != {"not_published", "published"}:
        fail("translation schema must distinguish not_published and published")

    agent_eval = json.loads((ROOT / "schemas" / "agent-eval-case-v1.schema.json").read_text(encoding="utf-8"))
    required_eval = set(agent_eval.get("required", []))
    for key in (
        "id", "category", "user_message", "expected_route", "expected_resource_ids",
        "expected_source_record_ids", "expected_checks", "prohibited_claims", "rationale",
    ):
        if key not in required_eval:
            fail(f"agent eval schema must require {key}")

    eval_run = json.loads((ROOT / "schemas" / "agent-eval-run-v1.schema.json").read_text(encoding="utf-8"))
    validate_run_shape(eval_run, "agent eval run schema", f"{ORIGIN}/data/agent-evals.jsonl")

    challenge_run = json.loads((ROOT / "schemas" / "agent-eval-challenge-run-v1.schema.json").read_text(encoding="utf-8"))
    validate_run_shape(
        challenge_run,
        "agent eval challenge run schema",
        f"{ORIGIN}/data/agent-evals-challenge.jsonl",
    )

    print(f"schema check passed: {len(entries)} versioned contracts discoverable from catalog")


if __name__ == "__main__":
    main()
