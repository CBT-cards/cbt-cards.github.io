#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
import json
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://cbt-cards.github.io"
SOURCE = ROOT / "data/changelog.json"
OUTPUT = ROOT / "rss.xml"
MAX_ITEMS = 30
DISCOVERY_TARGETS = [ROOT / "index.html", ROOT / "changelog/index.html"]
DISCOVERY_LINK = (
    '<link rel="alternate" type="application/rss+xml" '
    'href="https://cbt-cards.github.io/rss.xml" title="CBT Cards updates" />'
)


def rfc822(day: str) -> str:
    value = datetime.fromisoformat(day).replace(tzinfo=timezone.utc)
    return format_datetime(value, usegmt=True)


def canonical_entries() -> list[dict]:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    entries = list(data.get("entries") or [])
    entries.sort(key=lambda item: (str(item.get("date") or ""), str(item.get("id") or "")), reverse=True)
    entries = entries[:MAX_ITEMS]
    if not entries:
        raise SystemExit("data/changelog.json contains no feedable entries")
    return entries


def build() -> str:
    entries = canonical_entries()
    latest = str(entries[0]["date"])
    items = []
    for entry in entries:
        entry_id = str(entry["id"])
        date = str(entry["date"])
        title = escape(str(entry["title"]))
        summary = escape(str(entry["summary"]))
        url = f"{SITE_ORIGIN}/changelog/#{entry_id}"
        guid = f"urn:cbt-cards:changelog:{entry_id}"
        scope = escape(str(entry.get("scope") or "update"))
        items.append(
            "    <item>\n"
            f"      <title>{title}</title>\n"
            f"      <link>{url}</link>\n"
            f"      <guid isPermaLink=\"false\">{guid}</guid>\n"
            f"      <pubDate>{rfc822(date)}</pubDate>\n"
            f"      <category>{scope}</category>\n"
            f"      <description>{summary}</description>\n"
            "    </item>"
        )

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n"
        "  <channel>\n"
        "    <title>CBT Cards updates</title>\n"
        f"    <link>{SITE_ORIGIN}/changelog/</link>\n"
        "    <description>Reviewed CBT Cards website, public-data, research, localization and agent-interface updates.</description>\n"
        "    <language>en</language>\n"
        f"    <lastBuildDate>{rfc822(latest)}</lastBuildDate>\n"
        f"    <atom:link href=\"{SITE_ORIGIN}/rss.xml\" rel=\"self\" type=\"application/rss+xml\" />\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )


def inject_autodiscovery() -> int:
    changed = 0
    for path in DISCOVERY_TARGETS:
        html = path.read_text(encoding="utf-8")
        if 'type="application/rss+xml"' in html and "/rss.xml" in html:
            continue
        if "</head>" not in html:
            raise SystemExit(f"cannot add RSS autodiscovery: {path.relative_to(ROOT)} has no </head>")
        path.write_text(html.replace("</head>", f"{DISCOVERY_LINK}\n</head>", 1), encoding="utf-8")
        changed += 1
    return changed


def autodiscovery_is_present() -> bool:
    ok = True
    for path in DISCOVERY_TARGETS:
        html = path.read_text(encoding="utf-8")
        if 'rel="alternate" type="application/rss+xml"' not in html or "https://cbt-cards.github.io/rss.xml" not in html:
            print(f"{path.relative_to(ROOT)} is missing canonical RSS autodiscovery")
            ok = False
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CBT Cards RSS 2.0 feed from data/changelog.json")
    parser.add_argument("--write", action="store_true", help="write rss.xml and ensure HTML autodiscovery")
    parser.add_argument("--check", action="store_true", help="verify generated RSS and autodiscovery match the canonical contract")
    args = parser.parse_args()
    expected = build()

    if args.check:
        if not OUTPUT.exists():
            print("rss.xml is missing; run scripts/build_rss_feed.py --write")
            return 1
        actual = OUTPUT.read_text(encoding="utf-8")
        if actual != expected:
            print("rss.xml is stale relative to data/changelog.json; regenerate it")
            return 1
        if not autodiscovery_is_present():
            return 1
        print("OK: rss.xml matches canonical changelog data and HTML advertises it")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    changed = inject_autodiscovery()
    print(f"Wrote {OUTPUT.relative_to(ROOT)} from data/changelog.json; updated {changed} HTML discovery target(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
