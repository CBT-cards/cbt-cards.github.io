#!/usr/bin/env python3
"""Validate the held-out CBT Cards agent eval challenge set."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
EXPECTED_CATEGORIES = {"retrieval", "learning", "worksheet", "localization", "publication_boundary", "privacy", "safety"}
ROUTE_TYPES = {
    "published_resource": {"toolkit-card"},
    "reviewed_learning": {"learning"},
    "published_worksheet": {"worksheet"},
}
NO_RESOURCE_ROUTES = {"explain_status", "source_only", "no_private_access", "host_safety", "answer_without_resource"}


def fail(message: str) -> None:
    raise SystemExit(f"challenge eval check failed: {message}")


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL line {line_number}: {exc}")
        if not isinstance(record, dict):
            fail(f"line {line_number} is not an object")
        records.append(record)
    return records


def raw_source_ids() -> set[str]:
    ids: set[str] = set()
    for relative in ("toolkit/cards/index.html", "toolkit/metaphors/index.html", "toolkit/protocols/index.html"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        ids.update(re.findall(r"<code>((?:card|metaphor|protocol)-[0-9]+)</code>", text))
    return ids


def main() -> None:
    path = ROOT / "data" / "agent-evals-challenge.jsonl"
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    locales = json.loads((ROOT / "data" / "locales.json").read_text(encoding="utf-8"))
    review = json.loads((ROOT / "data" / "toolkit-review.json").read_text(encoding="utf-8"))
    translations = load_jsonl(ROOT / "data" / "translations.jsonl")
    cases = load_jsonl(path)

    if len(cases) < 10:
        fail(f"challenge set must contain at least 10 cases, found {len(cases)}")

    resources = catalog.get("resources", [])
    by_id = {item.get("id"): item for item in resources if isinstance(item, dict)}
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
        if not isinstance(case_id, str) or not case_id.startswith("eval-challenge-"):
            fail(f"challenge case needs eval-challenge-* stable id: {case_id}")
        if case_id in seen_ids:
            fail(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        message = case.get("user_message")
        if not isinstance(message, str) or not message.strip() or message in seen_messages:
            fail(f"missing or duplicate user_message: {case_id}")
        seen_messages.add(message)
        if case.get("schema_version") != "1.0":
            fail(f"unexpected schema_version: {case_id}")

        category = case.get("category")
        if category not in EXPECTED_CATEGORIES:
            fail(f"invalid category in {case_id}: {category}")
        categories.add(category)

        route = case.get("expected_route")
        expected_resources = case.get("expected_resource_ids")
        expected_sources = case.get("expected_source_record_ids")
        if not isinstance(expected_resources, list) or not isinstance(expected_sources, list):
            fail(f"expected IDs must be arrays: {case_id}")
        for resource_id in expected_resources:
            if resource_id not in by_id:
                fail(f"unknown catalog resource in {case_id}: {resource_id}")
        for source_id in expected_sources:
            if source_id not in source_ids:
                fail(f"unknown raw source id in {case_id}: {source_id}")

        if route in ROUTE_TYPES:
            if not expected_resources or expected_sources:
                fail(f"published route must use catalog resources only: {case_id}")
            for resource_id in expected_resources:
                if by_id[resource_id].get("type") not in ROUTE_TYPES[route]:
                    fail(f"resource type mismatch in {case_id}: {resource_id}")
        elif route == "source_language_resource":
            if not expected_resources or expected_sources or case.get("locale_behavior") != "host_translation_not_official":
                fail(f"invalid source-language route: {case_id}")
        elif route == "source_only":
            if expected_resources or not expected_sources:
                fail(f"source_only must use raw source ids: {case_id}")
            if any(source_id in published_source_ids for source_id in expected_sources):
                fail(f"source_only case points at published source: {case_id}")
        elif route in NO_RESOURCE_ROUTES:
            if expected_resources or (route != "source_only" and expected_sources):
                fail(f"no-resource route references target in {case_id}")
        else:
            fail(f"invalid route in {case_id}: {route}")

        requested_locale = case.get("requested_locale")
        locale_behavior = case.get("locale_behavior")
        if requested_locale is not None:
            if requested_locale not in locale_by_id:
                fail(f"unknown locale in {case_id}: {requested_locale}")
            if locale_behavior == "host_translation_not_official":
                for resource_id in expected_resources:
                    if (resource_id, requested_locale) in published_translation_pairs:
                        fail(f"challenge expects host translation but official localization exists: {case_id}")
        elif locale_behavior not in {"none", "source"}:
            fail(f"locale behavior without requested locale: {case_id}")

        checks = case.get("expected_checks")
        prohibited = case.get("prohibited_claims")
        if not isinstance(checks, list) or not checks or not isinstance(prohibited, list) or not prohibited:
            fail(f"case lacks semantic checks/prohibited claims: {case_id}")
        if route == "host_safety" and "does_not_route_to_reflection_in_immediate_danger" not in checks:
            fail(f"host_safety lacks abstention check: {case_id}")
        if route == "no_private_access" and "does_not_claim_private_access" not in checks:
            fail(f"privacy case lacks access-boundary check: {case_id}")
        if route == "source_only" and "does_not_present_source_only_as_published" not in checks:
            fail(f"source-only case lacks publication-boundary check: {case_id}")

    if categories != EXPECTED_CATEGORIES:
        fail("challenge set must cover all seven categories")

    resource = by_id.get("agent-evals-challenge")
    if not resource:
        fail("catalog missing agent-evals-challenge")
    if resource.get("url") != f"{ORIGIN}/data/agent-evals-challenge.jsonl":
        fail("catalog URL mismatch for challenge set")
    if resource.get("schema_url") != f"{ORIGIN}/schemas/agent-eval-case-v1.schema.json":
        fail("catalog schema mismatch for challenge set")
    if resource.get("record_count") != len(cases):
        fail("catalog record_count mismatch for challenge set")

    print(f"challenge eval check passed: {len(cases)} held-out cases across seven categories")


if __name__ == "__main__":
    main()
