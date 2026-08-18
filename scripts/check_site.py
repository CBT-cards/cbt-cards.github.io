#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://cbt-cards.github.io"
SITE_HOST = "cbt-cards.github.io"
IGNORE_DIRS = {".git", ".github", "scripts"}
IGNORE_FILES = {"404.html"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.h1 = 0
        self.description = None
        self.canonical = None
        self.links = []
        self.jsonld = []
        self._script_type = None
        self._script_buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._script_type = "jsonld"
            self._script_buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._script_type == "jsonld":
            text = "".join(self._script_buf).strip()
            if text:
                self.jsonld.append(text)
            self._script_type = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self._script_type == "jsonld":
            self._script_buf.append(data)


def url_to_local(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in {"http", "https"} or parsed.netloc != SITE_HOST:
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


errors = []
html_files = sorted(
    p for p in ROOT.rglob("*.html")
    if not any(part in IGNORE_DIRS for part in p.parts) and p.name not in IGNORE_FILES
)
canonicals = set()

for path in html_files:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT)

    if not parser.title.strip():
        errors.append(f"{rel}: missing <title>")
    if not parser.description:
        errors.append(f"{rel}: missing meta description")
    if parser.h1 != 1:
        errors.append(f"{rel}: expected exactly one h1, found {parser.h1}")
    if not parser.canonical:
        errors.append(f"{rel}: missing canonical")
    elif not parser.canonical.startswith(SITE_ORIGIN + "/"):
        errors.append(f"{rel}: canonical is outside the site origin: {parser.canonical}")
    elif parser.canonical in canonicals:
        errors.append(f"{rel}: duplicate canonical {parser.canonical}")
    else:
        canonicals.add(parser.canonical)

    for raw in parser.jsonld:
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON-LD: {exc}")

    for href in parser.links:
        target = url_to_local(href)
        if target is not None and not target.exists():
            errors.append(f"{rel}: broken internal link {href}")

sitemap = ROOT / "sitemap.xml"
if not sitemap.exists():
    errors.append("missing sitemap.xml")
else:
    try:
        tree = ET.parse(sitemap)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = {n.text for n in tree.findall("s:url/s:loc", ns)}
        for canonical in sorted(canonicals):
            if canonical not in locs:
                errors.append(f"sitemap missing canonical {canonical}")
        for loc in sorted(locs):
            target = url_to_local(loc)
            if target is None:
                errors.append(f"sitemap contains URL outside site origin: {loc}")
            elif not target.exists():
                errors.append(f"sitemap URL has no local target: {loc}")
    except Exception as exc:
        errors.append(f"invalid sitemap.xml: {exc}")

catalog_path = ROOT / "data/catalog.json"
if not catalog_path.exists():
    errors.append("missing data/catalog.json")
else:
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        if catalog.get("canonical") != f"{SITE_ORIGIN}/data/catalog.json":
            errors.append("data/catalog.json: unexpected canonical URL")
        for resource in catalog.get("resources", []):
            url = resource.get("url")
            if not url:
                errors.append(f"data/catalog.json: resource missing url: {resource.get('id', '<unknown>')}")
                continue
            target = url_to_local(url)
            if target is not None and not target.exists():
                errors.append(f"data/catalog.json: missing local target for {resource.get('id')}: {url}")
    except json.JSONDecodeError as exc:
        errors.append(f"data/catalog.json: invalid JSON: {exc}")

if errors:
    print("Site quality checks failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(
    f"OK: {len(html_files)} HTML pages checked; {len(canonicals)} canonical URLs; "
    "internal links, sitemap, catalog, JSON and JSON-LD parsed."
)
