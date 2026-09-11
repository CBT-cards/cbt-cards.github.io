#!/usr/bin/env python3
"""Bounded live verification for the deployed CBT Cards Image Discovery surface."""

from __future__ import annotations

import json
import re
import time
import urllib.request

ORIGIN = "https://cbt-cards.github.io"
SAMPLE = 12


def fetch(url: str) -> tuple[bytes, str]:
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CBT-Cards-Image-Discovery-Check/1.0"})
            with urllib.request.urlopen(req, timeout=20) as response:
                return response.read(), response.headers.get_content_type()
        except Exception as exc:  # pragma: no cover - live network guard
            last = exc
            time.sleep(attempt + 1)
    raise SystemExit(f"live_image_discovery: fetch failed for {url}: {last}")


sitemap_bytes, _ = fetch(ORIGIN + "/sitemap.xml")
manifest_bytes, _ = fetch(ORIGIN + "/data/image-discovery.json")
sitemap = sitemap_bytes.decode("utf-8")
manifest = json.loads(manifest_bytes.decode("utf-8"))
records = manifest.get("records") or []
if not records:
    raise SystemExit("live_image_discovery: deployed manifest has no records")
if 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' not in sitemap:
    raise SystemExit("live_image_discovery: deployed sitemap lacks image namespace")

for record in records[:SAMPLE]:
    page = record["page"]
    image = record["image"]
    if f"<image:loc>{image}</image:loc>" not in sitemap:
        raise SystemExit(f"live_image_discovery: sitemap omits {image}")
    page_bytes, _ = fetch(page)
    source = page_bytes.decode("utf-8")
    if not re.search(rf'<meta\b(?=[^>]*property=["\']og:image["\'])[^>]*content=["\']{re.escape(image)}["\']', source, re.I):
        raise SystemExit(f"live_image_discovery: og:image mismatch for {page}")
    if not re.search(rf'<meta\b(?=[^>]*name=["\']twitter:image["\'])[^>]*content=["\']{re.escape(image)}["\']', source, re.I):
        raise SystemExit(f"live_image_discovery: twitter:image mismatch for {page}")
    if "max-image-preview:large" not in source:
        raise SystemExit(f"live_image_discovery: large preview missing for {page}")
    _image_bytes, content_type = fetch(image)
    if not content_type.startswith("image/"):
        raise SystemExit(f"live_image_discovery: preferred image is not image content: {image} ({content_type})")

print(f"CBT Cards live Image Discovery passed on {min(SAMPLE, len(records))}/{len(records)} reviewed editorial page(s).")
