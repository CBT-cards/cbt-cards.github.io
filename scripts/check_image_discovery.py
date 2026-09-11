#!/usr/bin/env python3
"""Validate the exact post-mutation CBT Cards Image Discovery artifact."""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"


def fail(message: str) -> None:
    raise SystemExit(f"image_discovery: {message}")


def meta(source: str, key: str, value: str) -> str:
    match = re.search(rf'<meta\b(?=[^>]*\b{re.escape(key)}=["\']{re.escape(value)}["\'])[^>]*>', source, re.I)
    if not match:
        return ""
    content = re.search(r'\bcontent=["\']([^"\']*)["\']', match.group(0), re.I)
    return content.group(1) if content else ""


def walk(value):
    if isinstance(value, list):
        for item in value:
            yield from walk(item)
    elif isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)


def primary_images(source: str) -> set[str]:
    found: set[str] = set()
    for match in re.finditer(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', source, re.I):
        try:
            parsed = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        for node in walk(parsed):
            raw_type = node.get('@type')
            types = raw_type if isinstance(raw_type, list) else [raw_type] if raw_type else []
            if 'WebPage' not in types:
                continue
            image = node.get('primaryImageOfPage')
            if isinstance(image, str):
                found.add(image)
            elif isinstance(image, dict):
                url = image.get('contentUrl') or image.get('url')
                if url:
                    found.add(url)
    return found


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b'\x89PNG\r\n\x1a\n':
        fail(f"preferred asset is not a PNG: {path.relative_to(ROOT)}")
    return struct.unpack('>II', data[16:24])


manifest_path = ROOT / 'data' / 'image-discovery.json'
if not manifest_path.exists():
    fail('data/image-discovery.json missing from final artifact')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
if manifest.get('version') != '0.1' or manifest.get('site') != ORIGIN + '/':
    fail('manifest identity/version mismatch')
records = manifest.get('records') or []
if not records:
    fail('manifest has no records')

sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
if f'xmlns:image="{IMAGE_NS}"' not in sitemap:
    fail('sitemap missing Google image namespace')
if re.search(r'<image:(caption|geo_location|title|license)>', sitemap, re.I):
    fail('deprecated Google image sitemap field found')

large_ready = 0
for record in records:
    page = record['page']
    image = record['image']
    alt = record['alt']
    if not page.startswith(ORIGIN + '/') or not image.startswith(ORIGIN + '/assets/'):
        fail(f'wrong origin in record: {page}')
    if not alt.strip():
        fail(f'empty reviewed alt: {page}')
    if f'<loc>{page}</loc>' not in sitemap or f'<image:loc>{image}</image:loc>' not in sitemap:
        fail(f'sitemap image entry missing: {page}')

    rel = page.removeprefix(ORIGIN + '/').rstrip('/')
    html_path = ROOT / (rel if rel else '.') / 'index.html'
    if not html_path.exists():
        fail(f'HTML target missing: {page}')
    source = html_path.read_text(encoding='utf-8')
    if meta(source, 'property', 'og:image') != image:
        fail(f'og:image mismatch: {page}')
    if meta(source, 'name', 'twitter:image') != image:
        fail(f'twitter:image mismatch: {page}')
    if meta(source, 'name', 'twitter:card') != 'summary_large_image':
        fail(f'twitter card mismatch: {page}')
    if meta(source, 'property', 'og:image:alt') != alt or meta(source, 'name', 'twitter:image:alt') != alt:
        fail(f'image alt metadata mismatch: {page}')
    robots = meta(source, 'name', 'robots').lower()
    if 'max-image-preview:large' not in robots:
        fail(f'large image preview missing: {page}')
    if 'noimageindex' in robots:
        fail(f'noimageindex conflicts with rollout: {page}')
    if image not in primary_images(source):
        fail(f'primaryImageOfPage mismatch: {page}')

    asset = ROOT / image.removeprefix(ORIGIN + '/').split('?', 1)[0]
    width, height = png_dimensions(asset)
    if width >= 1200 and width * height >= 300000:
        large_ready += 1
    expected_src = '/' + asset.relative_to(ROOT).as_posix()
    if not re.search(rf'<figure class="article-visual">[\s\S]*?<img\b[^>]*\bsrc="{re.escape(expected_src)}"', source, re.I):
        fail(f'high-resolution preferred image is not the ordinary img fallback: {page}')

print(
    f'CBT Cards Image Discovery gate passed: {len(records)} reviewed editorial page(s), '
    f'{large_ready}/{len(records)} preferred PNGs meet the Discover-oriented large-image size check; '
    'responsive WebP sources remain available for browser delivery.'
)
