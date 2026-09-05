#!/usr/bin/env python3
"""Install a consent-aware GTM loader deterministically."""
import argparse, re
from pathlib import Path
ID="GTM-W6NHM6C3"; MARK="portfolio-analytics-consent"
SNIP=f'''<!-- {MARK} --><script>(function(w,d,id){{var k='portfolio_analytics_consent';function load(){{if(d.querySelector('script[data-portfolio-gtm]'))return;w.dataLayer=w.dataLayer||[];w.dataLayer.push({{'gtm.start':Date.now(),event:'gtm.js'}});var s=d.createElement('script');s.async=true;s.dataset.portfolioGtm='';s.src='https://www.googletagmanager.com/gtm.js?id='+id;d.head.appendChild(s)}}function ask(){{var b=d.createElement('div');b.setAttribute('role','dialog');b.style.cssText='position:fixed;z-index:2147483647;left:1rem;right:1rem;bottom:1rem;max-width:42rem;margin:auto;padding:1rem;border-radius:12px;background:#111;color:#fff;font:16px/1.45 system-ui;box-shadow:0 8px 30px #0008';b.innerHTML='We use optional analytics to improve this site. <button data-yes>Allow</button> <button data-no>Decline</button>';b.onclick=function(e){{if(e.target.matches('[data-yes]')){{localStorage.setItem(k,'yes');b.remove();load()}}if(e.target.matches('[data-no]')){{localStorage.setItem(k,'no');b.remove()}}}};d.body.appendChild(b)}}var c=localStorage.getItem(k);if(c==='yes')load();else if(c!=='no')d.addEventListener('DOMContentLoaded',ask)}})(window,document,'{ID}');</script><!-- /{MARK} -->'''
OLD=re.compile(r'\s*<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->|\s*<!-- Google Tag Manager \(noscript\) -->.*?<!-- End Google Tag Manager \(noscript\) -->',re.S)
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();n=0
 for f in Path.cwd().rglob('*.html'):
  if any(x in {'.git','.tmp','agents'} for x in f.parts):continue
  old=f.read_text(); new=OLD.sub('',old)
  if MARK not in new:new=new.replace('<head>','<head>\n'+SNIP,1)
  if new!=old:
   n+=1
   if a.write:f.write_text(new)
 print(f'Consent analytics {"updated" if a.write else "missing"}: {n}')
 return 1 if n and not a.write else 0
if __name__=='__main__':raise SystemExit(main())
