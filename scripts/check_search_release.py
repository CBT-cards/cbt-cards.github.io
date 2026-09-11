#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import json
import struct
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = json.loads((ROOT / "data/site-identity.json").read_text(encoding="utf-8"))
SITE_URL = IDENTITY["siteUrl"]
SITE_ORIGIN = SITE_URL.rstrip("/")


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.description = ""
        self.robots = ""
        self.canonical = ""
        self.og_site_name = ""
        self.og_url = ""
        self.icons = []
        self.jsonld = []
        self._jsonld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        elif tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content", "")
        elif tag == "meta" and attrs.get("property") == "og:site_name":
            self.og_site_name = attrs.get("content", "")
        elif tag == "meta" and attrs.get("property") == "og:url":
            self.og_url = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        elif tag == "link" and "icon" in (attrs.get("rel") or ""):
            self.icons.append(attrs.get("href", ""))
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._jsonld = True
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._jsonld:
            raw = "".join(self._buf).strip()
            if raw:
                self.jsonld.append(json.loads(raw))
            self._jsonld = False
            self._buf = []

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self._jsonld:
            self._buf.append(data)


def parse(path):
    parser = Parser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.title = " ".join(parser.title.split())
    return parser


def collect_type(value, wanted, found):
    if isinstance(value, list):
        for item in value:
            collect_type(item, wanted, found)
        return
    if not isinstance(value, dict):
        return
    raw_type = value.get("@type")
    types = raw_type if isinstance(raw_type, list) else [raw_type]
    if wanted in types:
        found.append(value)
    for child in value.values():
        collect_type(child, wanted, found)


def local_path(url):
    parsed = urllib.parse.urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != SITE_ORIGIN:
        return None
    if parsed.path == "/":
        return ROOT / "index.html"
    candidate = ROOT / parsed.path.lstrip("/")
    if parsed.path.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def png_dimensions(path):
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("configured favicon is not a PNG")
    return struct.unpack(">II", data[16:24])


errors = []
home = parse(ROOT / "index.html")
if home.title != IDENTITY["homepageTitle"]:
    errors.append(f"homepage title drift: {home.title!r}")
if home.description != IDENTITY["homepageDescription"]:
    errors.append("homepage description drift")
if home.canonical != SITE_URL:
    errors.append(f"homepage canonical drift: {home.canonical!r}")
if home.og_site_name != IDENTITY["siteName"]:
    errors.append(f"homepage og:site_name drift: {home.og_site_name!r}")
if home.og_url != SITE_URL:
    errors.append(f"homepage og:url drift: {home.og_url!r}")
if "noindex" in home.robots.lower() or "none" in home.robots.lower():
    errors.append("homepage is accidentally noindex")
if IDENTITY["faviconPath"] not in home.icons:
    errors.append("homepage does not declare the stable PNG favicon")

website_nodes = []
for value in home.jsonld:
    collect_type(value, "WebSite", website_nodes)
full_websites = [node for node in website_nodes if node.get("name") and node.get("url")]
if len(full_websites) != 1:
    errors.append(f"homepage expected one full WebSite identity, found {len(full_websites)}")
elif full_websites[0].get("name") != IDENTITY["siteName"] or full_websites[0].get("url") != SITE_URL:
    errors.append("homepage WebSite identity disagrees with site-identity.json")

favicon = ROOT / IDENTITY["faviconPath"].lstrip("/")
if not favicon.exists():
    errors.append(f"favicon missing: {favicon.relative_to(ROOT)}")
else:
    try:
        width, height = png_dimensions(favicon)
        if width != height:
            errors.append(f"favicon is not square: {width}x{height}")
        if width < 48:
            errors.append(f"favicon source is smaller than 48px: {width}x{height}")
    except ValueError as exc:
        errors.append(str(exc))

not_found = parse(ROOT / "404.html")
if "noindex" not in not_found.robots.lower():
    errors.append("404.html must be noindex")
if not_found.canonical:
    errors.append(f"404.html must not advertise canonical content: {not_found.canonical}")
if IDENTITY["siteName"] not in not_found.title:
    errors.append("404.html title does not identify CBT Cards")

sitemap_path = ROOT / "sitemap.xml"
try:
    tree = ET.parse(sitemap_path)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [node.text.strip() for node in tree.findall("s:url/s:loc", ns) if node.text]
except Exception as exc:
    errors.append(f"invalid sitemap.xml: {exc}")
    locs = []

if len(locs) != len(set(locs)):
    errors.append("sitemap contains duplicate URLs")
if SITE_URL not in locs:
    errors.append("sitemap omits canonical homepage")
if any("/404" in urllib.parse.urlparse(loc).path for loc in locs):
    errors.append("sitemap contains the 404 route")

for loc in locs:
    path = local_path(loc)
    if path is None:
        errors.append(f"sitemap leaks another host: {loc}")
        continue
    if not path.exists() or path.suffix.lower() != ".html":
        continue
    page = parse(path)
    if "noindex" in page.robots.lower() or "none" in page.robots.lower():
        errors.append(f"sitemap contains noindex URL: {loc}")
    if page.canonical and page.canonical != loc:
        errors.append(f"sitemap contains alias {loc} -> {page.canonical}")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if f"Sitemap: {SITE_ORIGIN}/sitemap.xml" not in robots:
    errors.append("robots.txt does not advertise the canonical sitemap")

for machine_path in [ROOT / "llms.txt", ROOT / "data/catalog.json"]:
    if not machine_path.exists():
        errors.append(f"missing machine-readable surface: {machine_path.relative_to(ROOT)}")
        continue
    text = machine_path.read_text(encoding="utf-8")
    if IDENTITY["siteName"] not in text or SITE_ORIGIN not in text:
        errors.append(f"{machine_path.relative_to(ROOT)} disagrees with canonical identity")

if errors:
    print(f"Search Release gate failed for {len(errors)} issue(s):")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(2)

print(f"Search Release gate passed: {len(locs)} sitemap URLs, exact CBT Cards identity, one WebSite node, favicon, robots, noindex 404 and canonical machine surfaces.")
