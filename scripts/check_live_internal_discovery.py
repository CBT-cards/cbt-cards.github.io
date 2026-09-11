#!/usr/bin/env python3
"""Bounded live verification for CBT Cards Internal Discovery & Distribution."""
from __future__ import annotations
from urllib.request import Request,urlopen
BASE='https://cbt-cards.github.io'
PATHS=['/learn/cbt-thought-record/','/learn/worry-time/','/worksheets/cbt-thought-record/','/toolkit/cards/challenge-your-thoughts/','/toolkit/cards/worry-box/']
for path in PATHS:
    req=Request(BASE+path,headers={'User-Agent':'CBTCardsInternalDiscoveryCheck/1.0'})
    with urlopen(req,timeout=20) as r:
        body=r.read().decode('utf-8','replace')
        if r.status!=200: raise SystemExit(f'{path}: unexpected HTTP {r.status}')
    for marker in ('data-page-utility','data-internal-discovery-continuation','/assets/internal-discovery.js'):
        if marker not in body: raise SystemExit(f'{path}: missing live marker {marker}')
print(f'Live Internal Discovery & Distribution passed on {len(PATHS)} reviewed CBT Cards pages.')
