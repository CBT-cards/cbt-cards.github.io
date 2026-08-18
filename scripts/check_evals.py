#!/usr/bin/env python3
"""Validate CBT Cards public agent evaluation cases and source boundaries."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
EXPECTED_CATEGORIES = {
    "retrieval",
    "learning",
    "worksheet",
    "localization",
    "publication_boundary",
    "privacy",
    "safety",
}
ROUTE_TYPES = {
    "published_resource": {"toolkit-card"},
    "reviewed_learning": {"learning"},
    "published_worksheet": {"worksheet"},
}
NO_RESOURCE_ROUTES = {
    "explain_status",
    "source_only",
    "no_private_access",
    "host_safety",
    "answer_without_resource",
}


def fail(message: str) -> None:
    raise SystemExit(f"eval check failed: {message}")


def load_jsonl(path: Path, label: str) -> list[dict]:
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid {label} JSONL line {line_number}: {exc}")
        if not isinstance(record, dict):
            fail(f"{label} line {line_number} is not an object")
        records.append(record)
    return records


def raw_source_ids() -> set[str]:
    ids: set[str] = set()
    for relative in (
        "toolkit/cards/index.html",
        "toolkit/metaphors/index.html",
        "toolkit/protocols/index.html",
    ):
        path = ROOT / relative
        if not path.exists():
            fail(f"missing source index: {relative}")
        ids.update(re.findall(r"<code>((?:card|metaphor|protocol)-[0-9]+)</code>", path.read_text(encoding="utf-8")))
    return ids


def main() -> None:
    eval_path = ROOT / "data" / "agent-evals.jsonl"
    catalog_path = ROOT / "data" / "catalog.json"
    locales_path = ROOT / "data" / "locales.json"
    translations_path = ROOT / "data" / "translations.jsonl"
    review_path = ROOT / "data" / "toolkit-review.json"

    for path in (eval_path, catalog_path, locales_path, translations_path, review_path):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    cases = load_jsonl(eval_path, "eval")
    translations = load_jsonl(translations_path, "translation")
    if len(cases) < 20:
        fail(f"starter eval set must contain at least 20 cases, found {len(cases)}")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    locales = json.loads(locales_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    resource_by_id = {resource.get("id"): resource for resource in resources}
    locale_by_id = {item.get("locale"): item for item in locales.get("locales", [])}
    source_ids = raw_source_ids()
    published_source_ids = {
        record.get("source_record_id")
        for record in review.get("records", [])
        if record.get("publication_status") == "published"
    }
    published_translation_pairs = {
        (record.get("resource_id"), record.get("locale"))
        for record in translations
        if record.get("translation_status") == "human_reviewed"
        and record.get("review_status") == "reviewed_for_publication"
        and record.get("publication_status") == "published"
    }

    seen_ids: set[str] = set()
    seen_messages: set[str] = set()
    categories: set[str] = set()

    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            fail("case missing stable id")
        if case_id in seen_ids:
            fail(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)

        if case.get("schema_version") != "1.0":
            fail(f"unexpected schema_version for {case_id}")

        message = case.get("user_message")
        if not isinstance(message, str) or not message.strip():
            fail(f"case missing user_message: {case_id}")
        if message in seen_messages:
            fail(f"duplicate user_message: {case_id}")
        seen_messages.add(message)

        category = case.get("category")
        if category not in EXPECTED_CATEGORIES:
            fail(f"invalid category for {case_id}: {category}")
        categories.add(category)

        route = case.get("expected_route")
        expected_resources = case.get("expected_resource_ids")
        expected_sources = case.get("expected_source_record_ids")
        if not isinstance(expected_resources, list) or not isinstance(expected_sources, list):
            fail(f"expected IDs must be arrays: {case_id}")

        for resource_id in expected_resources:
            resource = resource_by_id.get(resource_id)
            if resource is None:
                fail(f"unknown expected resource ID in {case_id}: {resource_id}")

        for source_id in expected_sources:
            if source_id not in source_ids:
                fail(f"unknown raw source record ID in {case_id}: {source_id}")

        if route in ROUTE_TYPES:
            if not expected_resources or expected_sources:
                fail(f"published route must use catalog resource IDs only: {case_id}")
            allowed_types = ROUTE_TYPES[route]
            for resource_id in expected_resources:
                if resource_by_id[resource_id].get("type") not in allowed_types:
                    fail(f"resource type does not match {route} in {case_id}: {resource_id}")
        elif route == "source_language_resource":
            if not expected_resources or expected_sources:
                fail(f"source_language_resource must use catalog resource IDs only: {case_id}")
            if case.get("locale_behavior") != "host_translation_not_official":
                fail(f"source_language_resource must identify host translation behavior: {case_id}")
        elif route == "source_only":
            if expected_resources or not expected_sources:
                fail(f"source_only route must reference raw source records only: {case_id}")
            for source_id in expected_sources:
                if source_id in published_source_ids:
                    fail(f"source_only eval references a published source record: {case_id}/{source_id}")
        elif route in NO_RESOURCE_ROUTES:
            if expected_resources or (route != "source_only" and expected_sources):
                fail(f"no-resource route unexpectedly references a resource: {case_id}")
        else:
            fail(f"invalid expected_route for {case_id}: {route}")

        requested_locale = case.get("requested_locale")
        locale_behavior = case.get("locale_behavior")
        if requested_locale is not None:
            if requested_locale not in locale_by_id:
                fail(f"unknown requested locale in {case_id}: {requested_locale}")
            if locale_behavior == "host_translation_not_official":
                for resource_id in expected_resources:
                    if (resource_id, requested_locale) in published_translation_pairs:
                        fail(f"eval claims no official localization but one is published: {case_id}/{resource_id}/{requested_locale}")
        elif locale_behavior not in {"none", "source"}:
            fail(f"locale behavior requires requested_locale in {case_id}: {locale_behavior}")

        checks = case.get("expected_checks")
        prohibited = case.get("prohibited_claims")
        if not isinstance(checks, list) or not checks:
            fail(f"case has no expected checks: {case_id}")
        if not isinstance(prohibited, list) or not prohibited:
            fail(f"case has no prohibited claims: {case_id}")

        if route == "host_safety" and "does_not_route_to_reflection_in_immediate_danger" not in checks:
            fail(f"host_safety case lacks abstention check: {case_id}")
        if route == "no_private_access" and "does_not_claim_private_access" not in checks:
            fail(f"privacy route lacks access-boundary check: {case_id}")
        if route == "source_only" and "does_not_present_source_only_as_published" not in checks:
            fail(f"source_only route lacks publication-boundary check: {case_id}")

    missing_categories = EXPECTED_CATEGORIES - categories
    if missing_categories:
        fail("eval set missing categories: " + ", ".join(sorted(missing_categories)))

    eval_resource = resource_by_id.get("agent-evals")
    if not eval_resource:
        fail("catalog missing agent-evals")
    if eval_resource.get("url") != f"{ORIGIN}/data/agent-evals.jsonl":
        fail("catalog URL mismatch for agent-evals")
    if eval_resource.get("schema_url") != f"{ORIGIN}/schemas/agent-eval-case-v1.schema.json":
        fail("catalog schema_url mismatch for agent-evals")
    if eval_resource.get("record_count") != len(cases):
        fail("catalog record_count mismatch for agent-evals")

    print(f"agent eval check passed: {len(cases)} cases across {len(categories)} categories")


if __name__ == "__main__":
    main()
