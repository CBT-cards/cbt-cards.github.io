#!/usr/bin/env python3
"""Apply ARWP Image Discovery to the reviewed CBT Cards editorial visual cohort."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from apply_editorial_visuals import VISUALS

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"


def set_meta(source: str, key: str, value: str, content: str) -> str:
    pattern = re.compile(rf'<meta\b(?=[^>]*\b{re.escape(key)}=["\']{re.escape(value)}["\'])[^>]*>', re.I)
    replacement = f'<meta {key}="{value}" content="{content}" />'
    if pattern.search(source):
        return pattern.sub(replacement, source, count=1)
    return source.replace('</head>', replacement + '\n</head>', 1)


def ensure_large_preview(source: str) -> str:
    match = re.search(r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>', source, re.I)
    if not match:
        return source.replace('</head>', '<meta name="robots" content="max-image-preview:large" />\n</head>', 1)
    tag = match.group(0)
    content_match = re.search(r'\bcontent=["\']([^"\']*)["\']', tag, re.I)
    content = content_match.group(1) if content_match else ''
    if re.search(r'(?:^|,)\s*max-image-preview\s*:', content, re.I):
        return source
    next_content = f'{content},max-image-preview:large' if content.strip() else 'max-image-preview:large'
    replacement = re.sub(r'\bcontent=["\'][^"\']*["\']', f'content="{next_content}"', tag, count=1, flags=re.I)
    if replacement == tag:
        replacement = tag[:-1] + f' content="{next_content}">'
    return source[:match.start()] + replacement + source[match.end():]


def add_image_to_node(value, image_url: str):
    if isinstance(value, list):
        return [add_image_to_node(item, image_url) for item in value]
    if not isinstance(value, dict):
        return value
    raw_type = value.get('@type')
    types = raw_type if isinstance(raw_type, list) else [raw_type] if raw_type else []
    if 'WebPage' in types:
        value['primaryImageOfPage'] = {
            '@type': 'ImageObject',
            'url': image_url,
            'contentUrl': image_url,
            'width': 1536,
            'height': 1024,
        }
    if 'Article' in types:
        value['image'] = image_url
    for key, child in list(value.items()):
        if key in {'primaryImageOfPage', 'image'}:
            continue
        value[key] = add_image_to_node(child, image_url)
    return value


def enrich_jsonld(source: str, canonical: str, image_url: str) -> str:
    found_webpage = False

    def replace(match: re.Match[str]) -> str:
        nonlocal found_webpage
        open_tag, raw, close_tag = match.groups()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)

        def inspect(value):
            nonlocal found_webpage
            if isinstance(value, list):
                for item in value:
                    inspect(item)
            elif isinstance(value, dict):
                raw_type = value.get('@type')
                types = raw_type if isinstance(raw_type, list) else [raw_type] if raw_type else []
                if 'WebPage' in types:
                    found_webpage = True
                for child in value.values():
                    inspect(child)

        inspect(parsed)
        enriched = add_image_to_node(parsed, image_url)
        return open_tag + json.dumps(enriched, separators=(',', ':')) + close_tag

    result = re.sub(
        r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',
        replace,
        source,
        flags=re.I,
    )
    if not found_webpage:
        webpage = {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            '@id': canonical + '#webpage',
            'url': canonical,
            'primaryImageOfPage': {
                '@type': 'ImageObject',
                'url': image_url,
                'contentUrl': image_url,
                'width': 1536,
                'height': 1024,
            },
        }
        marker = '<script type="application/ld+json" data-image-discovery="true">' + json.dumps(webpage, separators=(',', ':')) + '</script>'
        result = result.replace('</head>', marker + '\n</head>', 1)
    return result


def transform_page(rel: str, source: str) -> tuple[str, dict]:
    asset, alt, _caption = VISUALS[rel]
    canonical_match = re.search(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*\bhref=["\']([^"\']+)["\'][^>]*>', source, re.I)
    if not canonical_match:
        raise ValueError(f'{rel}: canonical missing')
    canonical = canonical_match.group(1)
    image_url = f'{ORIGIN}/assets/{asset}.png'
    png = ROOT / 'assets' / f'{asset}.png'
    webp = ROOT / 'assets' / f'{asset}.webp'
    small = ROOT / 'assets' / f'{asset}-560w.webp'
    for path in (png, webp, small):
        if not path.exists():
            raise ValueError(f'{rel}: image asset missing: {path.relative_to(ROOT)}')

    result = source
    result = ensure_large_preview(result)
    result = set_meta(result, 'property', 'og:image', image_url)
    result = set_meta(result, 'property', 'og:image:alt', alt)
    result = set_meta(result, 'property', 'og:image:width', '1536')
    result = set_meta(result, 'property', 'og:image:height', '1024')
    result = set_meta(result, 'name', 'twitter:card', 'summary_large_image')
    result = set_meta(result, 'name', 'twitter:image', image_url)
    result = set_meta(result, 'name', 'twitter:image:alt', alt)

    figure_pattern = re.compile(
        rf'(<figure class="article-visual">[\s\S]*?<img\b[^>]*\bsrc=")/assets/{re.escape(asset)}\.webp("[^>]*>)',
        re.I,
    )
    if not figure_pattern.search(result):
        raise ValueError(f'{rel}: editorial figure does not reference expected WebP')
    result = figure_pattern.sub(rf'\1/assets/{asset}.png\2', result, count=1)
    result = re.sub(
        rf'(<figure class="article-visual">[\s\S]*?<img\b[^>]*\bwidth=")[^"]+("[^>]*\bheight=")[^"]+("[^>]*>)',
        r'\g<1>1536\g<2>1024\g<3>',
        result,
        count=1,
        flags=re.I,
    )
    result = enrich_jsonld(result, canonical, image_url)
    return result, {'page': canonical, 'image': image_url, 'alt': alt, 'asset': asset}


def apply_sitemap(source: str, records: list[dict]) -> str:
    result = source
    if f'xmlns:image="{IMAGE_NS}"' not in result:
        result = re.sub(r'<urlset\b([^>]*)>', rf'<urlset\1 xmlns:image="{IMAGE_NS}">', result, count=1)
    by_page = {item['page']: item['image'] for item in records}

    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        loc_match = re.search(r'<loc>([^<]+)</loc>', inner)
        if not loc_match or loc_match.group(1) not in by_page:
            return match.group(0)
        cleaned = re.sub(r'<image:image>[\s\S]*?</image:image>', '', inner)
        image = by_page[loc_match.group(1)]
        return f'<url>{cleaned}<image:image><image:loc>{image}</image:loc></image:image></url>'

    return re.sub(r'<url>([\s\S]*?)</url>', replace, result)


def validate_inputs() -> list[dict]:
    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    records = []
    for rel in sorted(VISUALS):
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f'Image Discovery target missing: {rel}')
        transformed, record = transform_page(rel, path.read_text(encoding='utf-8'))
        if not transformed:
            raise SystemExit(f'Image Discovery transform produced empty output: {rel}')
        if f'<loc>{record["page"]}</loc>' not in sitemap:
            raise SystemExit(f'Image Discovery target is not in sitemap: {record["page"]}')
        records.append(record)
    print(f'Image Discovery inputs valid for {len(records)} reviewed editorial page(s).')
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--validate', action='store_true')
    mode.add_argument('--write', action='store_true')
    args = parser.parse_args()

    records = validate_inputs()
    if args.validate:
        return

    for rel in sorted(VISUALS):
        path = ROOT / rel
        transformed, _record = transform_page(rel, path.read_text(encoding='utf-8'))
        path.write_text(transformed, encoding='utf-8')

    sitemap_path = ROOT / 'sitemap.xml'
    sitemap_path.write_text(apply_sitemap(sitemap_path.read_text(encoding='utf-8'), records), encoding='utf-8')
    (ROOT / 'data' / 'image-discovery.json').write_text(
        json.dumps({'version': '0.1', 'site': ORIGIN + '/', 'records': records}, indent=2) + '\n',
        encoding='utf-8',
    )
    print(f'Image Discovery applied to {len(records)} reviewed editorial page(s).')


if __name__ == '__main__':
    main()
