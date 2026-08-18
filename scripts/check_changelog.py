#!/usr/bin/env python3
"""Validate CBT Cards public changelog and release provenance."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
ALLOWED_SCOPES = {"website", "app", "data", "agent"}
ALLOWED_CHANGE_TYPES = {"added", "changed", "removed", "deprecated"}


def local_path(url: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    path = parsed.path
    if path.endswith("/"):
        return ROOT / path.lstrip("/") / "index.html"
    return ROOT / path.lstrip("/")


def fail(message: str) -> None:
    raise SystemExit(f"changelog check failed: {message}")


def main() -> None:
    changelog_path = ROOT / "data" / "changelog.json"
    catalog_path = ROOT / "data" / "catalog.json"
    page_path = ROOT / "changelog" / "index.html"
    sitemap_path = ROOT / "sitemap.xml"
    atom_path = ROOT / "feed.xml"
    json_feed_path = ROOT / "feed.json"

    for required in (changelog_path, catalog_path, page_path, sitemap_path, atom_path, json_feed_path):
        if not required.exists():
            fail(f"missing required file: {required.relative_to(ROOT)}")

    changelog = json.loads(changelog_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    if changelog.get("schema_version") != "1.0":
        fail("unexpected schema_version")
    if changelog.get("canonical") != f"{ORIGIN}/data/changelog.json":
        fail("unexpected canonical URL")

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    resource_by_id = {resource.get("id"): resource for resource in resources}
    if None in resource_by_id:
        fail("catalog resource without id")
    if len(resource_by_id) != len(resources):
        fail("duplicate resource IDs in catalog")

    for required_id, expected_url in {
        "changelog": f"{ORIGIN}/changelog/",
        "changelog-data": f"{ORIGIN}/data/changelog.json",
    }.items():
        resource = resource_by_id.get(required_id)
        if not resource:
            fail(f"catalog missing {required_id}")
        if resource.get("url") != expected_url:
            fail(f"catalog URL mismatch for {required_id}")

    entries = changelog.get("entries")
    if not isinstance(entries, list) or not entries:
        fail("entries must be a non-empty list")

    seen_ids: set[str] = set()
    seen_dates: list[date] = []
    page_text = page_path.read_text(encoding="utf-8")
    today = date.today()

    for entry in entries:
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            fail("entry missing stable id")
        if entry_id in seen_ids:
            fail(f"duplicate entry id: {entry_id}")
        seen_ids.add(entry_id)
        if f'id="{entry_id}"' not in page_text:
            fail(f"changelog page missing anchor for {entry_id}")

        try:
            entry_date = date.fromisoformat(entry.get("date", ""))
        except ValueError as exc:
            fail(f"invalid date for {entry_id}: {exc}")
        if entry_date > today:
            fail(f"future-dated entry: {entry_id}")
        seen_dates.append(entry_date)

        scope = entry.get("scope")
        if scope not in ALLOWED_SCOPES:
            fail(f"invalid scope for {entry_id}: {scope}")

        title = entry.get("title")
        summary = entry.get("summary")
        if not isinstance(title, str) or not title.strip():
            fail(f"missing title for {entry_id}")
        if not isinstance(summary, str) or not summary.strip():
            fail(f"missing summary for {entry_id}")

        changes = entry.get("changes")
        if not isinstance(changes, list) or not changes:
            fail(f"entry has no changes: {entry_id}")

        for change in changes:
            change_type = change.get("type")
            resource_id = change.get("resource_id")
            url = change.get("url")
            if change_type not in ALLOWED_CHANGE_TYPES:
                fail(f"invalid change type in {entry_id}: {change_type}")
            resource = resource_by_id.get(resource_id)
            if resource is None:
                fail(f"unknown resource_id in {entry_id}: {resource_id}")
            if resource.get("url") != url:
                fail(f"resource URL mismatch in {entry_id}: {resource_id}")
            if not isinstance(url, str) or not url.startswith(f"{ORIGIN}/"):
                fail(f"non-canonical CBT Cards URL in {entry_id}: {url}")
            if change_type != "removed":
                target = local_path(url)
                if target is None or not target.exists():
                    fail(f"missing target for {entry_id}/{resource_id}: {url}")

    if seen_dates != sorted(seen_dates, reverse=True):
        fail("entries must be ordered newest first")

    sitemap_root = ET.parse(sitemap_path).getroot()
    sitemap_ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", sitemap_ns)}
    if f"{ORIGIN}/changelog/" not in sitemap_urls:
        fail("sitemap missing changelog page")

    atom_root = ET.parse(atom_path).getroot()
    atom_ns = {"a": "http://www.w3.org/2005/Atom"}
    atom_ids = {node.text for node in atom_root.findall("a:entry/a:id", atom_ns)}
    if f"{ORIGIN}/changelog/" not in atom_ids:
        fail("Atom feed missing changelog entry")

    json_feed = json.loads(json_feed_path.read_text(encoding="utf-8"))
    json_feed_ids = {item.get("id") for item in json_feed.get("items", [])}
    if f"{ORIGIN}/changelog/" not in json_feed_ids:
        fail("JSON Feed missing changelog entry")

    print(f"changelog check passed: {len(entries)} entries, {len(seen_ids)} stable IDs")


if __name__ == "__main__":
    main()
