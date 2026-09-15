#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://cbt-cards.github.io"
RSS = ROOT / "rss.xml"
CHANGELOG = ROOT / "data/changelog.json"
ROBOTS = ROOT / "robots.txt"
DISCOVERY_TARGETS = [ROOT / "index.html", ROOT / "changelog/index.html"]
ATOM_NS = "http://www.w3.org/2005/Atom"

errors: list[str] = []

if not RSS.exists():
    errors.append("missing rss.xml; run scripts/build_rss_feed.py --write")
else:
    try:
        root = ET.parse(RSS).getroot()
        if root.tag != "rss" or root.get("version") != "2.0":
            errors.append("rss.xml must be RSS 2.0")
        channel = root.find("channel")
        if channel is None:
            errors.append("rss.xml is missing channel")
        else:
            if channel.findtext("link") != f"{SITE_ORIGIN}/changelog/":
                errors.append("rss.xml channel link is not canonical changelog URL")
            if channel.findtext("language") != "en":
                errors.append("rss.xml language must be en")
            self_link = channel.find(f"{{{ATOM_NS}}}link")
            if self_link is None or self_link.get("href") != f"{SITE_ORIGIN}/rss.xml" or self_link.get("type") != "application/rss+xml":
                errors.append("rss.xml canonical self link is missing")

            source = json.loads(CHANGELOG.read_text(encoding="utf-8"))
            entries = sorted(
                list(source.get("entries") or []),
                key=lambda item: (str(item.get("date") or ""), str(item.get("id") or "")),
                reverse=True,
            )[:30]
            items = channel.findall("item")
            if len(items) != len(entries):
                errors.append(f"rss.xml item count {len(items)} does not match canonical changelog slice {len(entries)}")
            for item, entry in zip(items, entries):
                entry_id = str(entry.get("id") or "")
                expected_link = f"{SITE_ORIGIN}/changelog/#{entry_id}"
                expected_guid = f"urn:cbt-cards:changelog:{entry_id}"
                if item.findtext("link") != expected_link:
                    errors.append(f"rss.xml wrong link for {entry_id}")
                guid = item.find("guid")
                if guid is None or (guid.text or "") != expected_guid or guid.get("isPermaLink") != "false":
                    errors.append(f"rss.xml unstable GUID for {entry_id}")
                try:
                    pub_date = item.findtext("pubDate") or ""
                    parsed = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S GMT")
                    if parsed.date().isoformat() != str(entry.get("date")):
                        errors.append(f"rss.xml pubDate differs from source date for {entry_id}")
                except ValueError:
                    errors.append(f"rss.xml invalid pubDate for {entry_id}")
    except (ET.ParseError, json.JSONDecodeError) as exc:
        errors.append(f"rss.xml validation failed: {exc}")

for path in DISCOVERY_TARGETS:
    html = path.read_text(encoding="utf-8")
    if 'rel="alternate" type="application/rss+xml"' not in html or f'{SITE_ORIGIN}/rss.xml' not in html:
        errors.append(f"{path.relative_to(ROOT)} does not advertise canonical RSS")

for line in ROBOTS.read_text(encoding="utf-8").splitlines():
    if line.strip().lower().startswith("sitemap:") and any(token in line.lower() for token in ("rss.xml", "feed.xml", "atom.xml", "feed.json")):
        errors.append(f"robots.txt incorrectly declares a feed as sitemap: {line.strip()}")

if errors:
    print("RSS feed checks failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("OK: RSS 2.0 feed matches canonical changelog data, autodiscovery is present, and robots sitemap separation is valid.")
