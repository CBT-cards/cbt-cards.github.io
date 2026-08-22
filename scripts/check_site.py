#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import json
import re
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
        self.robots = ""
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
        elif tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content", "")
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


def require_local_target(label, url, errors):
    target = url_to_local(url)
    if target is None:
        errors.append(f"{label}: URL is outside site origin: {url}")
        return None
    if not target.exists():
        errors.append(f"{label}: missing local target: {url}")
        return None
    return target


def skill_version(path):
    if not path.exists():
        return None
    match = re.search(r"(?m)^version:\s*([^\s]+)\s*$", path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


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
    elif "noindex" not in parser.robots.lower() and parser.canonical in canonicals:
        errors.append(f"{rel}: duplicate canonical {parser.canonical}")
    elif "noindex" not in parser.robots.lower():
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

robots_path = ROOT / "robots.txt"
if not robots_path.exists():
    errors.append("missing robots.txt")
else:
    robots = robots_path.read_text(encoding="utf-8")
    if not re.search(r"(?mi)^User-agent:\s*OAI-SearchBot\s*$", robots):
        errors.append("robots.txt: missing explicit OAI-SearchBot group")
    if "Sitemap: https://cbt-cards.github.io/sitemap.xml" not in robots:
        errors.append("robots.txt: missing canonical sitemap declaration")

indexnow_path = ROOT / "data/indexnow.json"
if not indexnow_path.exists():
    errors.append("missing data/indexnow.json")
else:
    try:
        indexnow = json.loads(indexnow_path.read_text(encoding="utf-8"))
        if indexnow.get("host") != SITE_HOST:
            errors.append("data/indexnow.json: unexpected host")
        if indexnow.get("endpoint") != "https://api.indexnow.org/indexnow":
            errors.append("data/indexnow.json: unexpected endpoint")
        key = indexnow.get("key", "")
        if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
            errors.append("data/indexnow.json: invalid key format")
        key_file = ROOT / f"{key}.txt"
        if not key_file.exists():
            errors.append(f"data/indexnow.json: missing root key file {key}.txt")
        elif key_file.read_text(encoding="utf-8").strip() != key:
            errors.append("data/indexnow.json: key file contents differ from configured key")
        expected_location = f"{SITE_ORIGIN}/{key}.txt"
        if indexnow.get("key_location") != expected_location:
            errors.append("data/indexnow.json: key_location does not match root key file")
    except json.JSONDecodeError as exc:
        errors.append(f"data/indexnow.json: invalid JSON: {exc}")

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
            require_local_target("sitemap", loc, errors)
    except Exception as exc:
        errors.append(f"invalid sitemap.xml: {exc}")

catalog_path = ROOT / "data/catalog.json"
catalog = None
catalog_by_id = {}
if not catalog_path.exists():
    errors.append("missing data/catalog.json")
else:
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        if catalog.get("canonical") != f"{SITE_ORIGIN}/data/catalog.json":
            errors.append("data/catalog.json: unexpected canonical URL")
        for resource in catalog.get("resources", []):
            resource_id = resource.get("id")
            url = resource.get("url")
            if not resource_id:
                errors.append("data/catalog.json: resource missing id")
                continue
            if resource_id in catalog_by_id:
                errors.append(f"data/catalog.json: duplicate resource id {resource_id}")
            catalog_by_id[resource_id] = resource
            if not url:
                errors.append(f"data/catalog.json: resource missing url: {resource_id}")
                continue
            require_local_target(f"data/catalog.json resource {resource_id}", url, errors)
    except json.JSONDecodeError as exc:
        errors.append(f"data/catalog.json: invalid JSON: {exc}")

knowledge_path = ROOT / "data/knowledge.jsonl"
knowledge_ids = set()
if not knowledge_path.exists():
    errors.append("missing data/knowledge.jsonl")
else:
    for line_number, raw_line in enumerate(knowledge_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"data/knowledge.jsonl:{line_number}: invalid JSON: {exc}")
            continue

        required = {
            "id", "locale", "type", "title", "canonical_url", "summary",
            "key_points", "product_relation", "safety_scope", "reviewed", "sources"
        }
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"data/knowledge.jsonl:{line_number}: missing fields: {', '.join(missing)}")

        record_id = record.get("id")
        if not record_id:
            continue
        if record_id in knowledge_ids:
            errors.append(f"data/knowledge.jsonl:{line_number}: duplicate id {record_id}")
        knowledge_ids.add(record_id)

        catalog_resource = catalog_by_id.get(record_id)
        if catalog_resource is None:
            errors.append(f"data/knowledge.jsonl:{line_number}: id {record_id} missing from catalog")
        else:
            if catalog_resource.get("type") != record.get("type"):
                errors.append(
                    f"data/knowledge.jsonl:{line_number}: type differs from catalog for {record_id} "
                    f"({record.get('type')} != {catalog_resource.get('type')})"
                )
            if catalog_resource.get("url") != record.get("canonical_url"):
                errors.append(f"data/knowledge.jsonl:{line_number}: canonical URL differs from catalog for {record_id}")
            source_record_id = record.get("source_record_id")
            if source_record_id and catalog_resource.get("source_record_id") != source_record_id:
                errors.append(f"data/knowledge.jsonl:{line_number}: source_record_id differs from catalog for {record_id}")

        canonical_url = record.get("canonical_url")
        if canonical_url:
            require_local_target(f"data/knowledge.jsonl record {record_id}", canonical_url, errors)

        key_points = record.get("key_points")
        if not isinstance(key_points, list) or not key_points:
            errors.append(f"data/knowledge.jsonl:{line_number}: key_points must be a non-empty list")
        sources = record.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"data/knowledge.jsonl:{line_number}: sources must be a non-empty list")

for resource_id, resource in catalog_by_id.items():
    if resource.get("type") in {"learning", "toolkit-card"} and resource_id not in knowledge_ids:
        errors.append(f"data/catalog.json: curated resource {resource_id} missing from knowledge.jsonl")

toolkit_source_path = ROOT / "data/toolkit-source.json"
if not toolkit_source_path.exists():
    errors.append("missing data/toolkit-source.json")
else:
    try:
        toolkit_source = json.loads(toolkit_source_path.read_text(encoding="utf-8"))
        required = {
            "id", "version", "record_count", "record_counts", "source_repository",
            "source_commit", "dataset_blob_sha", "dataset_path", "distribution", "license",
            "clinical_review_metadata_present", "publication_policy", "verified"
        }
        missing = sorted(required - set(toolkit_source))
        if missing:
            errors.append(f"data/toolkit-source.json: missing fields: {', '.join(missing)}")
        counts = toolkit_source.get("record_counts")
        if not isinstance(counts, dict):
            errors.append("data/toolkit-source.json: record_counts must be an object")
        else:
            expected_types = {"card", "metaphor", "protocol"}
            if set(counts) != expected_types:
                errors.append("data/toolkit-source.json: record_counts must contain card, metaphor, protocol")
            elif sum(counts.values()) != toolkit_source.get("record_count"):
                errors.append("data/toolkit-source.json: record_count does not equal record_counts total")
        source_commit = toolkit_source.get("source_commit", "")
        if len(source_commit) != 40:
            errors.append("data/toolkit-source.json: source_commit must be a full 40-character commit SHA")
        blob_sha = toolkit_source.get("dataset_blob_sha", "")
        if len(blob_sha) != 40:
            errors.append("data/toolkit-source.json: dataset_blob_sha must be a full 40-character blob SHA")
        distribution = toolkit_source.get("distribution", "")
        if source_commit and source_commit not in distribution:
            errors.append("data/toolkit-source.json: distribution must be pinned to source_commit")
        if toolkit_source.get("clinical_review_metadata_present") is not False:
            errors.append("data/toolkit-source.json: clinical_review_metadata_present must remain explicit false until source schema changes")
    except json.JSONDecodeError as exc:
        errors.append(f"data/toolkit-source.json: invalid JSON: {exc}")

manifest_path = ROOT / "agents/cbt-cards/manifest.json"
manifest = None
if not manifest_path.exists():
    errors.append("missing agents/cbt-cards/manifest.json")
else:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        latest = manifest.get("latest")
        latest_url = manifest.get("latest_url")
        if not latest:
            errors.append("agents/cbt-cards/manifest.json: missing latest version")
        if not latest_url:
            errors.append("agents/cbt-cards/manifest.json: missing latest_url")
        else:
            require_local_target("agents/cbt-cards/manifest.json latest_url", latest_url, errors)

        versions = manifest.get("versions")
        version_names = set()
        version_urls = {}
        if not isinstance(versions, list) or not versions:
            errors.append("agents/cbt-cards/manifest.json: versions must be a non-empty list")
        else:
            for item in versions:
                version = item.get("version")
                url = item.get("url")
                if not version or not url:
                    errors.append("agents/cbt-cards/manifest.json: each version needs version and url")
                    continue
                if version in version_names:
                    errors.append(f"agents/cbt-cards/manifest.json: duplicate version {version}")
                version_names.add(version)
                version_urls[version] = url
                target = require_local_target(f"agents/cbt-cards/manifest.json version {version}", url, errors)
                if target is not None:
                    declared = skill_version(target)
                    if declared != version:
                        errors.append(
                            f"agents/cbt-cards/manifest.json: version {version} points to skill declaring {declared}"
                        )
            if latest and latest not in version_names:
                errors.append(f"agents/cbt-cards/manifest.json: latest {latest} not present in versions")

        latest_alias = ROOT / "agents/cbt-cards/SKILL.md"
        declared_latest = skill_version(latest_alias)
        if latest and declared_latest != latest:
            errors.append(
                f"agents/cbt-cards/SKILL.md: declares {declared_latest}, manifest latest is {latest}"
            )

        catalog_latest = catalog_by_id.get("agent-skill-latest")
        if catalog_latest is None:
            errors.append("data/catalog.json: missing agent-skill-latest resource")
        elif latest and catalog_latest.get("version") != latest:
            errors.append(
                f"data/catalog.json: agent-skill-latest version {catalog_latest.get('version')} != manifest latest {latest}"
            )
        if latest:
            immutable_id = f"agent-skill-v{latest}"
            immutable = catalog_by_id.get(immutable_id)
            if immutable is None:
                errors.append(f"data/catalog.json: missing immutable latest resource {immutable_id}")
            elif immutable.get("url") != version_urls.get(latest):
                errors.append(f"data/catalog.json: {immutable_id} URL differs from manifest")
    except json.JSONDecodeError as exc:
        errors.append(f"agents/cbt-cards/manifest.json: invalid JSON: {exc}")

if errors:
    print("Site quality checks failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(
    f"OK: {len(html_files)} HTML pages checked; {len(canonicals)} canonical URLs; "
    f"{len(knowledge_ids)} curated knowledge records; internal links, sitemap, catalog, toolkit source, "
    "crawler and IndexNow policies, skill versions, JSON and JSON-LD parsed."
)
