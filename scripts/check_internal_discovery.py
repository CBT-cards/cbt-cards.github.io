#!/usr/bin/env python3
"""Verify CBT Cards Internal Discovery & Distribution after application."""
from __future__ import annotations
import importlib.util,re
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('apply_internal_discovery',ROOT/'scripts/apply_internal_discovery.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ORIGIN=mod.ORIGIN;TARGETS=mod.TARGETS

def fail(msg): raise SystemExit('internal discovery check failed: '+msg)
def local(path): return ROOT/'index.html' if path=='/' else ROOT/path.strip('/')/'index.html'
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'};root=ET.parse(ROOT/'sitemap.xml').getroot();indexed={urlparse(n.text).path for n in root.findall('s:url/s:loc',ns) if n.text}
for path,items in TARGETS.items():
    p=local(path); source=p.read_text(encoding='utf-8')
    if 'data-page-utility' not in source: fail(f'{path}: utility bar missing')
    if 'data-internal-discovery-continuation' not in source: fail(f'{path}: continuation missing')
    if '/assets/internal-discovery.js' not in source: fail(f'{path}: utility script missing')
    if re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex',source,re.I): fail(f'{path}: target became noindex')
    for _,title,href,_ in items:
        if href not in indexed: fail(f'{path}: non-indexed continuation {href}')
        if f'href="{href}"' not in source: fail(f'{path}: continuation link missing for {title}')
if not (ROOT/'assets/internal-discovery.js').exists(): fail('assets/internal-discovery.js missing')
if 'ARWP Internal Discovery & Distribution' not in (ROOT/'styles.css').read_text(encoding='utf-8'): fail('styles missing')
print(f'Internal Discovery & Distribution check passed: {len(TARGETS)} reviewed learning/practice pages expose canonical utilities and curated low-stakes continuation paths.')
