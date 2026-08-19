#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; PAGE=ROOT/'mobile-releases/index.html'; ABOUT=ROOT/'about/index.html'; CHANGELOG=ROOT/'data/changelog.json'; SITEMAP=ROOT/'sitemap.xml'; ORIGIN='https://cbt-cards.github.io'
EXPECTED=(("3.1 CBT IN ACTION","3 Mar 2026"),("3.0 CBT","26 Jan 2026"),("2.2. MetalHatsCats Version","8 Dec 2025"),("2.1","7 Jul 2025"),("2.0 Final","28 Apr 2025"),("1.6","24 Jan 2025"),("1.5","7 Jan 2025"),("1.4","3 Jan 2025"),("1.3","28 Nov 2024"),("1.2","17 Nov 2024"),("1.1","4 Nov 2024"),("1.0","30 Oct 2024"))
def fail(m): raise SystemExit('mobile release history check failed: '+m)
def main():
 for p in (PAGE,ABOUT,CHANGELOG,SITEMAP):
  if not p.exists(): fail('missing '+str(p.relative_to(ROOT)))
 page=PAGE.read_text(); about=ABOUT.read_text()
 for f in ('href="https://cbt-cards.github.io/mobile-releases/"','19 August 2026','updated 9 March 2026','does <strong>not</strong> expose a reliable Android version name or version code','does not label the Android release “3.1”','https://apps.apple.com/us/app/id6737169041','https://play.google.com/store/apps/details?id=cbt.cbtcards.stressrelief','Some localized Apple storefronts display the 3.1 and 3.0 dates'):
  if f not in page: fail('page missing '+f)
 for v,d in EXPECTED:
  if v not in page or d not in page: fail('missing Apple history '+v+' / '+d)
 if page.count('<tr><td')!=len(EXPECTED): fail('Apple row count mismatch')
 if 'href="/mobile-releases/"' not in about or 'Public-site releases, dataset changes, or agent-skill versions do not imply a new Android or iOS release.' not in about: fail('About page lost mobile-history boundary')
 entries=json.loads(CHANGELOG.read_text()).get('entries',[])
 if any(e.get('scope')=='mobile' for e in entries): fail('website/data changelog contains mobile scope')
 root=ET.parse(SITEMAP).getroot(); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}; urls={n.text for n in root.findall('s:url/s:loc',ns)}
 if ORIGIN+'/mobile-releases/' not in urls: fail('sitemap missing mobile release history')
 print(f'mobile release history check passed: {len(EXPECTED)} Apple versions; Google Play date without invented Android version')
if __name__=='__main__': main()
