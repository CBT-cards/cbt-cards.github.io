#!/usr/bin/env python3
"""Validate CBT Cards locale registry and translation overlays."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"


def fail(message: str) -> None:
    raise SystemExit(f"localization check failed: {message}")


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


def main() -> None:
    locales_path = ROOT / "data" / "locales.json"
    knowledge_path = ROOT / "data" / "knowledge.jsonl"
    translations_path = ROOT / "data" / "translations.jsonl"
    catalog_path = ROOT / "data" / "catalog.json"

    for path in (locales_path, knowledge_path, translations_path, catalog_path):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    locale_registry = json.loads(locales_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    knowledge_records = load_jsonl(knowledge_path, "knowledge")
    translation_records = load_jsonl(translations_path, "translation")

    if locale_registry.get("schema_version") != "1.0":
        fail("unexpected locale-registry schema_version")
    if locale_registry.get("canonical") != f"{ORIGIN}/data/locales.json":
        fail("unexpected locale-registry canonical URL")

    source_locale = locale_registry.get("source_locale")
    if not isinstance(source_locale, str) or not source_locale:
        fail("locale registry has no source_locale")

    locales = locale_registry.get("locales")
    if not isinstance(locales, list) or not locales:
        fail("locale registry must contain locales")

    locale_by_id: dict[str, dict] = {}
    for item in locales:
        locale = item.get("locale")
        if not isinstance(locale, str) or not locale:
            fail("locale entry missing locale")
        if locale in locale_by_id:
            fail(f"duplicate locale entry: {locale}")
        locale_by_id[locale] = item

    source_entry = locale_by_id.get(source_locale)
    if not source_entry:
        fail("source_locale is absent from locale registry")
    if source_entry.get("status") != "source":
        fail("source locale must have status=source")
    if source_entry.get("machine_readable") is not True or source_entry.get("public_html") is not True:
        fail("source locale must be machine-readable and public HTML")

    source_status_count = sum(1 for item in locales if item.get("status") == "source")
    if source_status_count != 1:
        fail(f"expected exactly one source locale, found {source_status_count}")

    knowledge_by_id: dict[str, dict] = {}
    for record in knowledge_records:
        resource_id = record.get("id")
        if not isinstance(resource_id, str) or not resource_id:
            fail("knowledge record missing stable id")
        if resource_id in knowledge_by_id:
            fail(f"duplicate knowledge id: {resource_id}")
        if record.get("locale") != source_locale:
            fail(f"knowledge record {resource_id} is not in source locale {source_locale}")
        knowledge_by_id[resource_id] = record

    seen_pairs: set[tuple[str, str]] = set()
    translation_count_by_locale: dict[str, int] = {locale: 0 for locale in locale_by_id}

    for record in translation_records:
        resource_id = record.get("resource_id")
        locale = record.get("locale")
        if not isinstance(resource_id, str) or resource_id not in knowledge_by_id:
            fail(f"translation references unknown resource_id: {resource_id}")
        if not isinstance(locale, str) or locale not in locale_by_id:
            fail(f"translation for {resource_id} references unknown locale: {locale}")
        if locale == source_locale:
            fail(f"translation overlay must not duplicate source locale for {resource_id}")

        pair = (resource_id, locale)
        if pair in seen_pairs:
            fail(f"duplicate translation overlay: {resource_id}/{locale}")
        seen_pairs.add(pair)
        translation_count_by_locale[locale] += 1

        if record.get("schema_version") != "1.0":
            fail(f"unexpected translation schema_version for {resource_id}/{locale}")
        if record.get("source_locale") != source_locale:
            fail(f"source_locale mismatch for {resource_id}/{locale}")

        source_record = knowledge_by_id[resource_id]
        if record.get("source_reviewed") != source_record.get("reviewed"):
            fail(f"translation source snapshot is stale for {resource_id}/{locale}")

        source_points = source_record.get("key_points")
        translated_points = record.get("key_points")
        if not isinstance(source_points, list) or not isinstance(translated_points, list):
            fail(f"key_points must be arrays for {resource_id}/{locale}")
        if len(source_points) != len(translated_points):
            fail(f"key-point count differs from source for {resource_id}/{locale}")

        locale_entry = locale_by_id[locale]
        translation_status = record.get("translation_status")
        review_status = record.get("review_status")
        publication_status = record.get("publication_status")

        if translation_status == "machine_draft":
            if locale_entry.get("status") != "pilot":
                fail(f"machine draft exists outside a pilot locale: {resource_id}/{locale}")
            if locale_entry.get("machine_readable") is not True:
                fail(f"pilot machine draft locale must be machine-readable: {locale}")
            if locale_entry.get("public_html") is not False:
                fail(f"machine draft locale must not publish HTML: {locale}")
            if review_status != "unreviewed":
                fail(f"machine draft must remain unreviewed: {resource_id}/{locale}")
            if publication_status != "not_published":
                fail(f"machine draft must remain not_published: {resource_id}/{locale}")
            if record.get("canonical_url") is not None:
                fail(f"machine draft must not have a canonical public URL: {resource_id}/{locale}")
            if record.get("reviewed") is not None:
                fail(f"machine draft must not have a review date: {resource_id}/{locale}")
        elif translation_status == "human_reviewed":
            if review_status != "reviewed_for_publication":
                fail(f"human-reviewed translation lacks publication review: {resource_id}/{locale}")
            if record.get("reviewed") is None:
                fail(f"human-reviewed translation lacks review date: {resource_id}/{locale}")
            if publication_status == "published":
                if locale_entry.get("public_html") is not True:
                    fail(f"published translation locale is not enabled for public HTML: {locale}")
                canonical_url = record.get("canonical_url")
                if not isinstance(canonical_url, str) or not canonical_url.startswith(f"{ORIGIN}/"):
                    fail(f"published translation lacks canonical CBT Cards URL: {resource_id}/{locale}")
            elif publication_status == "not_published":
                if record.get("canonical_url") is not None:
                    fail(f"unpublished reviewed translation must not have canonical URL: {resource_id}/{locale}")
            else:
                fail(f"invalid publication_status for {resource_id}/{locale}: {publication_status}")
        else:
            fail(f"invalid translation_status for {resource_id}/{locale}: {translation_status}")

    for locale, entry in locale_by_id.items():
        if entry.get("status") == "pilot" and translation_count_by_locale.get(locale, 0) == 0:
            fail(f"pilot locale has no translation records: {locale}")
        if entry.get("status") == "planned" and translation_count_by_locale.get(locale, 0) != 0:
            fail(f"planned locale already has translation records; promote it to pilot first: {locale}")

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    resource_by_id = {item.get("id"): item for item in resources}
    expected_catalog = {
        "locale-registry": (
            f"{ORIGIN}/data/locales.json",
            f"{ORIGIN}/schemas/locales-v1.schema.json",
        ),
        "translation-dataset": (
            f"{ORIGIN}/data/translations.jsonl",
            f"{ORIGIN}/schemas/translation-record-v1.schema.json",
        ),
    }
    for resource_id, (url, schema_url) in expected_catalog.items():
        resource = resource_by_id.get(resource_id)
        if not resource:
            fail(f"catalog missing {resource_id}")
        if resource.get("url") != url:
            fail(f"catalog URL mismatch for {resource_id}")
        if resource.get("schema_url") != schema_url:
            fail(f"catalog schema_url mismatch for {resource_id}")

    print(
        "localization check passed: "
        f"{len(knowledge_by_id)} source resources; "
        f"{len(translation_records)} translation overlays across "
        f"{sum(1 for count in translation_count_by_locale.values() if count)} non-source locales"
    )


if __name__ == "__main__":
    main()
