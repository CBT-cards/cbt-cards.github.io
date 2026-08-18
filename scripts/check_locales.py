#!/usr/bin/env python3
"""Validate CBT Cards website locale publication state and localization readiness."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"


class HtmlLocaleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang: str | None = None
        self.html_dir: str | None = None
        self.hreflangs: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if tag == "html":
            self.html_lang = attrs_map.get("lang")
            self.html_dir = attrs_map.get("dir")
        if tag == "link":
            rel = (attrs_map.get("rel") or "").lower().split()
            hreflang = attrs_map.get("hreflang")
            if "alternate" in rel and hreflang:
                self.hreflangs.append((hreflang, attrs_map.get("href")))


def fail(message: str) -> None:
    raise SystemExit(f"locale check failed: {message}")


def local_html(url: str) -> Path:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        fail(f"sitemap URL outside canonical origin: {url}")
    path = parsed.path
    if path == "/":
        return ROOT / "index.html"
    if not path.endswith("/"):
        fail(f"indexed HTML URL must end with slash: {url}")
    return ROOT / path.lstrip("/") / "index.html"


def main() -> None:
    registry_path = ROOT / "data" / "locales.json"
    catalog_path = ROOT / "data" / "catalog.json"
    sitemap_path = ROOT / "sitemap.xml"
    about_path = ROOT / "about" / "index.html"
    policy_page = ROOT / "about" / "localization" / "index.html"

    for path in (registry_path, catalog_path, sitemap_path, about_path, policy_page):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    if registry.get("schema_version") != "1.0":
        fail("unexpected locale registry schema_version")
    if registry.get("canonical") != f"{ORIGIN}/data/locales.json":
        fail("unexpected locale registry canonical URL")

    default_locale = registry.get("default_locale")
    locales = registry.get("published_web_locales")
    if not isinstance(locales, list) or not locales:
        fail("published_web_locales must be a non-empty list")

    by_code: dict[str, dict] = {}
    prefixes: set[str] = set()
    for locale in locales:
        code = locale.get("code")
        if not isinstance(code, str) or not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)?", code):
            fail(f"invalid locale code: {code}")
        if code in by_code:
            fail(f"duplicate locale code: {code}")
        by_code[code] = locale
        prefix = locale.get("path_prefix")
        if not isinstance(prefix, str) or not prefix.startswith("/"):
            fail(f"invalid path_prefix for {code}")
        if prefix in prefixes:
            fail(f"duplicate path_prefix: {prefix}")
        prefixes.add(prefix)
        if locale.get("status") != "published":
            fail(f"non-published locale listed as published: {code}")
        if locale.get("direction") not in {"ltr", "rtl"}:
            fail(f"invalid direction for {code}")
        if locale.get("base_url") != (ORIGIN + prefix if prefix != "/" else ORIGIN + "/"):
            fail(f"base_url/path_prefix mismatch for {code}")

    if default_locale not in by_code:
        fail("default_locale is not present in published_web_locales")
    default = by_code[default_locale]
    if default.get("path_prefix") != "/":
        fail("default website locale must use the root path")

    hreflang = registry.get("hreflang", {})
    if len(locales) == 1:
        if hreflang.get("enabled") is not False:
            fail("hreflang must remain disabled while only one web locale is published")
    else:
        fail("multiple web locales require reciprocal hreflang validation to be implemented before publication")

    mobile = registry.get("mobile_app_languages", {})
    if mobile.get("status") != "not_asserted_by_this_repository":
        fail("website locale registry must not assert mobile-app language support")

    translation = registry.get("translation_policy", {})
    if translation.get("health_adjacent_content") != "human_review_required_before_publication":
        fail("health-adjacent translations must require human review")

    sitemap_root = ET.parse(sitemap_path).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [node.text for node in sitemap_root.findall("s:url/s:loc", ns) if node.text]
    if f"{ORIGIN}/about/localization/" not in sitemap_urls:
        fail("sitemap missing localization policy page")

    expected_lang = default.get("html_lang")
    expected_dir = default.get("direction")
    for url in sitemap_urls:
        html_path = local_html(url)
        if not html_path.exists():
            fail(f"missing indexed HTML page: {html_path.relative_to(ROOT)}")
        parser = HtmlLocaleParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        if parser.html_lang != expected_lang:
            fail(f"unexpected html lang on {url}: expected {expected_lang}, got {parser.html_lang}")
        if expected_dir == "rtl" and parser.html_dir != "rtl":
            fail(f"RTL locale page must declare dir=rtl: {url}")
        if parser.hreflangs:
            fail(f"hreflang found while only one web locale is published: {url} -> {parser.hreflangs}")

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    by_id = {item.get("id"): item for item in resources}
    for resource_id, expected_url in {
        "localization-page": f"{ORIGIN}/about/localization/",
        "locale-registry": f"{ORIGIN}/data/locales.json",
    }.items():
        item = by_id.get(resource_id)
        if not item:
            fail(f"catalog missing {resource_id}")
        if item.get("url") != expected_url:
            fail(f"catalog URL mismatch for {resource_id}")

    about_text = about_path.read_text(encoding="utf-8")
    if 'href="/about/localization/"' not in about_text:
        fail("About page does not link localization policy")

    print(f"locale check passed: {len(locales)} published web locale ({default_locale}); hreflang disabled until a second locale is explicitly implemented")


if __name__ == "__main__":
    main()
