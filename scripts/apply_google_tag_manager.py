#!/usr/bin/env python3
"""Install the consent-aware GA4 loader deterministically."""
import argparse, re
from pathlib import Path
MARK='<script src="/assets/analytics-consent.js" defer></script>'
REMOVE=re.compile(r'\s*<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->|\s*<!-- Google Tag Manager \(noscript\) -->.*?<!-- End Google Tag Manager \(noscript\) -->|\s*<!-- portfolio-analytics-consent -->.*?<!-- /portfolio-analytics-consent -->',re.S)
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--write",action="store_true"); args=parser.parse_args(); changed=0
    for target in Path.cwd().rglob("*.html"):
        if any(part in {".git",".tmp","agents"} for part in target.parts): continue
        old=target.read_text(); new=REMOVE.sub("",old)
        if MARK not in new: new=new.replace("</head>","  <!-- Consent-aware aggregate website analytics -->\n  "+MARK+"\n</head>",1)
        if new!=old:
            changed+=1
            if args.write: target.write_text(new)
    print(f'Consent analytics {"updated" if args.write else "missing"}: {changed}')
    return 1 if changed and not args.write else 0
if __name__=="__main__": raise SystemExit(main())
