#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://cbt-cards.github.io"
SITE_HOST = "cbt-cards.github.io"


def local_target(url: str) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != "https" or parsed.netloc != SITE_HOST:
            return None
        path = parsed.path
    else:
        path = parsed.path
    if not path.startswith("/"):
        return None
    if path == "/":
        return ROOT / "index.html"
    candidate = ROOT / path.lstrip("/")
    if path.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def require_local(url: str, label: str, errors: list[str]) -> None:
    target = local_target(url)
    if target is None:
        errors.append(f"{label}: URL is outside the CBT Cards origin: {url}")
    elif not target.exists():
        errors.append(f"{label}: missing local target for {url}")


errors: list[str] = []

atom_path = ROOT / "feed.xml"
json_feed_path = ROOT / "feed.json"
security_path = ROOT / ".well-known/security.txt"
catalog_path = ROOT / "data/catalog.json"

atom_ids: set[str] = set()
if not atom_path.exists():
    errors.append("missing feed.xml")
else:
    try:
        tree = ET.parse(atom_path)
        root = tree.getroot()
        ns = {"a": "http://www.w3.org/2005/Atom"}
        if root.tag != "{http://www.w3.org/2005/Atom}feed":
            errors.append("feed.xml: root must be Atom feed")
        self_links = [
            node.get("href")
            for node in root.findall("a:link", ns)
            if node.get("rel") == "self"
        ]
        if self_links != [f"{SITE_ORIGIN}/feed.xml"]:
            errors.append("feed.xml: expected one canonical self link")
        for entry in root.findall("a:entry", ns):
            entry_id = (entry.findtext("a:id", default="", namespaces=ns) or "").strip()
            link = entry.find("a:link", ns)
            href = (link.get("href") if link is not None else "") or ""
            if not entry_id:
                errors.append("feed.xml: entry missing id")
                continue
            if entry_id in atom_ids:
                errors.append(f"feed.xml: duplicate entry id {entry_id}")
            atom_ids.add(entry_id)
            if href != entry_id:
                errors.append(f"feed.xml: entry link differs from id for {entry_id}")
            require_local(entry_id, "feed.xml entry", errors)
    except ET.ParseError as exc:
        errors.append(f"feed.xml: invalid XML: {exc}")

json_ids: set[str] = set()
if not json_feed_path.exists():
    errors.append("missing feed.json")
else:
    try:
        feed = json.loads(json_feed_path.read_text(encoding="utf-8"))
        if feed.get("version") != "https://jsonfeed.org/version/1.1":
            errors.append("feed.json: expected JSON Feed version 1.1")
        if feed.get("home_page_url") != f"{SITE_ORIGIN}/":
            errors.append("feed.json: unexpected home_page_url")
        if feed.get("feed_url") != f"{SITE_ORIGIN}/feed.json":
            errors.append("feed.json: unexpected feed_url")
        items = feed.get("items")
        if not isinstance(items, list) or not items:
            errors.append("feed.json: items must be a non-empty list")
        else:
            for item in items:
                item_id = item.get("id")
                url = item.get("url")
                if not item_id:
                    errors.append("feed.json: item missing id")
                    continue
                if item_id in json_ids:
                    errors.append(f"feed.json: duplicate item id {item_id}")
                json_ids.add(item_id)
                if url != item_id:
                    errors.append(f"feed.json: item url differs from id for {item_id}")
                require_local(item_id, "feed.json item", errors)
    except json.JSONDecodeError as exc:
        errors.append(f"feed.json: invalid JSON: {exc}")

if atom_ids and json_ids and atom_ids != json_ids:
    only_atom = sorted(atom_ids - json_ids)
    only_json = sorted(json_ids - atom_ids)
    if only_atom:
        errors.append(f"feeds differ: only in Atom: {', '.join(only_atom)}")
    if only_json:
        errors.append(f"feeds differ: only in JSON Feed: {', '.join(only_json)}")

if not security_path.exists():
    errors.append("missing .well-known/security.txt")
else:
    fields: dict[str, list[str]] = {}
    for raw in security_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"security.txt: malformed line: {line}")
            continue
        key, value = line.split(":", 1)
        fields.setdefault(key.strip(), []).append(value.strip())

    required = {"Contact", "Expires", "Preferred-Languages", "Canonical"}
    missing = sorted(required - fields.keys())
    if missing:
        errors.append(f"security.txt: missing fields: {', '.join(missing)}")
    if fields.get("Canonical") != [f"{SITE_ORIGIN}/.well-known/security.txt"]:
        errors.append("security.txt: unexpected Canonical value")
    for contact in fields.get("Contact", []):
        require_local(contact, "security.txt Contact", errors)
    expires_values = fields.get("Expires", [])
    if len(expires_values) == 1:
        try:
            expires = datetime.fromisoformat(expires_values[0].replace("Z", "+00:00"))
            if expires.tzinfo is None:
                errors.append("security.txt: Expires must include a timezone")
            elif expires <= datetime.now(timezone.utc):
                errors.append("security.txt: Expires is in the past")
        except ValueError:
            errors.append("security.txt: Expires is not valid RFC3339-style date-time")

if catalog_path.exists():
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        resources = {item.get("id"): item for item in catalog.get("resources", [])}
        expected = {
            "atom-feed": f"{SITE_ORIGIN}/feed.xml",
            "json-feed": f"{SITE_ORIGIN}/feed.json",
            "security-contact": f"{SITE_ORIGIN}/.well-known/security.txt",
        }
        for resource_id, url in expected.items():
            resource = resources.get(resource_id)
            if resource is None:
                errors.append(f"data/catalog.json: missing discovery resource {resource_id}")
            elif resource.get("url") != url:
                errors.append(f"data/catalog.json: wrong URL for {resource_id}")
    except json.JSONDecodeError as exc:
        errors.append(f"data/catalog.json: invalid JSON while checking discovery resources: {exc}")
else:
    errors.append("missing data/catalog.json")

if errors:
    print("Discovery checks failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print(
    f"OK: {len(atom_ids)} feed entries match across Atom and JSON Feed; "
    "security.txt and discovery catalog resources validated."
)
