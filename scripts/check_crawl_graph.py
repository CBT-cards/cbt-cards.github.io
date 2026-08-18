#!/usr/bin/env python3
"""Validate internal crawl reachability for indexed CBT Cards pages."""

from __future__ import annotations

from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
MAX_DEPTH = 3
KEY_HOME_HUBS = {
    "/learn/",
    "/worksheets/",
    "/toolkit/",
    "/about/",
    "/changelog/",
    "/agents/",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(value)


def fail(message: str) -> None:
    raise SystemExit(f"crawl graph check failed: {message}")


def normalize_url(url: str) -> str | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    cleaned = parsed._replace(query="", fragment="")
    path = cleaned.path or "/"
    return urlunparse(("https", "cbt-cards.github.io", path, "", "", ""))


def local_html(url: str) -> Path:
    path = urlparse(url).path
    if path == "/":
        return ROOT / "index.html"
    if not path.endswith("/"):
        fail(f"indexed HTML URL must end with slash: {url}")
    return ROOT / path.lstrip("/") / "index.html"


def main() -> None:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        fail("missing sitemap.xml")

    tree = ET.parse(sitemap)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    indexed = [node.text for node in tree.findall("s:url/s:loc", ns) if node.text]
    indexed_set = set(indexed)
    if len(indexed) != len(indexed_set):
        fail("duplicate URL in sitemap")
    home = f"{ORIGIN}/"
    if home not in indexed_set:
        fail("homepage missing from sitemap")

    graph: dict[str, set[str]] = {url: set() for url in indexed}
    inbound: dict[str, set[str]] = {url: set() for url in indexed}

    for source in indexed:
        html_path = local_html(source)
        if not html_path.exists():
            fail(f"missing indexed HTML target: {html_path.relative_to(ROOT)}")
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for href in parser.hrefs:
            resolved = urljoin(source, href)
            normalized = normalize_url(resolved)
            if normalized is None or normalized not in indexed_set:
                continue
            graph[source].add(normalized)
            if normalized != source:
                inbound[normalized].add(source)

    orphans = sorted(url for url in indexed if url != home and not inbound[url])
    if orphans:
        fail("indexed pages without inbound indexed links: " + ", ".join(orphans))

    distances: dict[str, int] = {home: 0}
    queue: deque[str] = deque([home])
    while queue:
        source = queue.popleft()
        for target in graph[source]:
            if target not in distances:
                distances[target] = distances[source] + 1
                queue.append(target)

    unreachable = sorted(indexed_set - set(distances))
    if unreachable:
        fail("indexed pages unreachable from homepage: " + ", ".join(unreachable))

    too_deep = sorted((url, depth) for url, depth in distances.items() if depth > MAX_DEPTH)
    if too_deep:
        fail("crawl depth exceeds limit: " + ", ".join(f"{url} depth={depth}" for url, depth in too_deep))

    home_paths = {urlparse(url).path for url in graph[home]}
    missing_hubs = sorted(KEY_HOME_HUBS - home_paths)
    if missing_hubs:
        fail("homepage does not directly link key hubs: " + ", ".join(missing_hubs))

    max_depth = max(distances.values())
    print(f"crawl graph check passed: {len(indexed)} indexed pages, max depth {max_depth}, no orphans")


if __name__ == "__main__":
    main()
