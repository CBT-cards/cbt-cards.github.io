#!/usr/bin/env python3
"""Apply ARWP Internal Discovery & Distribution to reviewed CBT Cards learning surfaces."""
from __future__ import annotations
import argparse, html, re
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://cbt-cards.github.io'
TARGETS={
'/learn/activity-planning/':[('Practice','Activity-planning worksheet','/worksheets/activity-planning/','Move from explanation to a private browser worksheet.'),('Try','Big goals, small steps','/toolkit/cards/big-goals-small-steps/','Use a bounded practical card for the next small step.')],
'/learn/cbt-thought-record/':[('Practice','CBT thought-record worksheet','/worksheets/cbt-thought-record/','Use the free browser worksheet without signup.'),('Try','Challenge your thoughts','/toolkit/cards/challenge-your-thoughts/','Use a short evidence-checking card as a low-stakes prompt.'),('Compare','Thoughts are not facts','/toolkit/cards/thoughts-are-not-facts/','Use a related card without treating the thought as a diagnosis.')],
'/learn/worry-time/':[('Practice','Worry-time worksheet','/worksheets/worry-time/','Use the free browser worksheet for a scheduled review.'),('Try','Worry box','/toolkit/cards/worry-box/','Use the related reflection card as a bounded next step.')],
'/learn/thought-vs-fact/':[('Try','Thoughts are not facts','/toolkit/cards/thoughts-are-not-facts/','Continue with a directly related reflection card.'),('Try','Challenge your thoughts','/toolkit/cards/challenge-your-thoughts/','Use a compact question set to inspect evidence.')],
'/learn/automatic-thoughts/':[('Learn','CBT thought record','/learn/cbt-thought-record/','See one structured way to examine a specific moment.'),('Practice','Thought-record worksheet','/worksheets/cbt-thought-record/','Move into a private browser exercise.')],
'/learn/cbt-journaling/':[('Learn','CBT thought record','/learn/cbt-thought-record/','Compare journaling with a more structured reflection format.'),('Practice','Thought-record worksheet','/worksheets/cbt-thought-record/','Try the structured worksheet without creating an account.')],
'/worksheets/activity-planning/':[('Learn','Activity planning','/learn/activity-planning/','Read the educational explanation behind this worksheet.'),('Try','Big goals, small steps','/toolkit/cards/big-goals-small-steps/','Continue with a smaller-action card.')],
'/worksheets/cbt-thought-record/':[('Learn','CBT thought record','/learn/cbt-thought-record/','Read the educational explanation behind this worksheet.'),('Try','Challenge your thoughts','/toolkit/cards/challenge-your-thoughts/','Continue with a short evidence-checking card.')],
'/worksheets/worry-time/':[('Learn','Worry time','/learn/worry-time/','Read the educational explanation behind this worksheet.'),('Try','Worry box','/toolkit/cards/worry-box/','Continue with a related reflection card.')],
'/toolkit/cards/big-goals-small-steps/':[('Learn','Activity planning','/learn/activity-planning/','Open the related educational guide.'),('Practice','Activity-planning worksheet','/worksheets/activity-planning/','Use the matching browser worksheet.')],
'/toolkit/cards/challenge-your-thoughts/':[('Learn','CBT thought record','/learn/cbt-thought-record/','See the longer structured reflection method.'),('Practice','Thought-record worksheet','/worksheets/cbt-thought-record/','Use the matching private browser worksheet.')],
'/toolkit/cards/socratic-questioning/':[('Learn','CBT thought record','/learn/cbt-thought-record/','See a structured evidence-review format.'),('Try','Challenge your thoughts','/toolkit/cards/challenge-your-thoughts/','Continue with a shorter question card.')],
'/toolkit/cards/thoughts-are-not-facts/':[('Learn','Thought vs fact','/learn/thought-vs-fact/','Open the related educational explanation.'),('Try','Challenge your thoughts','/toolkit/cards/challenge-your-thoughts/','Continue with an evidence-checking card.')],
'/toolkit/cards/worry-box/':[('Learn','Worry time','/learn/worry-time/','Open the related educational explanation.'),('Practice','Worry-time worksheet','/worksheets/worry-time/','Use the matching private browser worksheet.')],
'/toolkit/cards/ground-yourself/':[('Explore','Practice library','/practice/','Choose another reviewed low-stakes practice without personalization.'),('Explore','Toolkit cards','/toolkit/cards/','Browse the reviewed card collection.')],
}
STYLE='''\n/* ARWP Internal Discovery & Distribution */\n.page-utility{display:flex;gap:.55rem;align-items:center;flex-wrap:wrap;margin:1rem 0 0;padding:.65rem .75rem;border:2px solid currentColor;border-radius:14px;background:rgba(255,255,255,.76)}.page-utility__meta{font-weight:800;margin-right:auto}.page-utility button{font:inherit;font-weight:800;border:1px solid currentColor;border-radius:999px;padding:.38rem .65rem;background:#fff;cursor:pointer}.page-utility__status{font-size:.82rem;min-height:1.2em}.internal-continuation{margin-top:2.5rem;padding-top:1.5rem;border-top:2px solid currentColor}.continuation-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.8rem}.continuation-card{display:flex;flex-direction:column;gap:.32rem;padding:1rem;border:2px solid currentColor;border-radius:16px;text-decoration:none;background:rgba(255,255,255,.72)}.continuation-card span{font-size:.75rem;font-weight:900;text-transform:uppercase;letter-spacing:.04em}.continuation-card strong{font-size:1.05rem}.continuation-card small{line-height:1.4}@media(max-width:700px){.continuation-grid{grid-template-columns:1fr}}\n'''
SCRIPT=r'''(()=>{const canonical=()=>document.querySelector('link[rel="canonical"]')?.href||location.href;const title=()=>document.querySelector('h1')?.textContent?.trim()||document.title;const status=(bar,msg)=>{const n=bar.querySelector('[data-page-utility-status]');if(n){n.textContent=msg;setTimeout(()=>n.textContent='',2200)}};document.querySelectorAll('[data-page-utility]').forEach(bar=>{bar.addEventListener('click',async e=>{const b=e.target.closest('[data-page-action]');if(!b)return;const u=canonical(),a=b.dataset.pageAction;try{if(a==='share'&&navigator.share){await navigator.share({title:title(),url:u});status(bar,'Shared');return}if(a==='save'){const k='cbt-cards:saved-pages';const s=new Set(JSON.parse(localStorage.getItem(k)||'[]'));if(s.has(u)){s.delete(u);b.setAttribute('aria-pressed','false');status(bar,'Removed from this browser')}else{s.add(u);b.setAttribute('aria-pressed','true');status(bar,'Saved in this browser')}localStorage.setItem(k,JSON.stringify([...s]));return}const text=a==='cite'?`CBT Cards. ${title()}. ${u}`:u;await navigator.clipboard.writeText(text);status(bar,a==='cite'?'Citation copied':'Link copied')}catch{status(bar,'Could not complete that action')}});try{const s=new Set(JSON.parse(localStorage.getItem('cbt-cards:saved-pages')||'[]'));bar.querySelector('[data-page-action="save"]')?.setAttribute('aria-pressed',String(s.has(canonical())))}catch{}})})();'''

def local(path:str)->Path:
    return ROOT/'index.html' if path=='/' else ROOT/path.strip('/')/'index.html'
def canonical(source:str)->str:
    m=re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',source,re.I)
    return m.group(1) if m else ''
def utility()->str:
    return '<div class="page-utility" data-page-utility><span class="page-utility__meta">Educational resource</span><button type="button" data-page-action="save" aria-pressed="false">Save</button><button type="button" data-page-action="share">Share</button><button type="button" data-page-action="copy">Copy link</button><button type="button" data-page-action="cite">Cite</button><span class="page-utility__status" data-page-utility-status role="status" aria-live="polite"></span></div>'
def continuation(items)->str:
    cards=''.join(f'<a class="continuation-card" href="{html.escape(href)}"><span>{html.escape(job)}</span><strong>{html.escape(title)}</strong><small>{html.escape(note)}</small></a>' for job,title,href,note in items)
    return f'<section class="internal-continuation" data-internal-discovery-continuation><p class="kicker">Continue from here</p><h2>Choose the next useful step.</h2><div class="continuation-grid">{cards}</div></section>'
def apply(source:str,items)->str:
    if 'data-page-utility' not in source:
        source=re.sub(r'(</h1>)',r'\1'+utility(),source,count=1,flags=re.I)
    if 'data-internal-discovery-continuation' not in source:
        source=source.replace('</main>',continuation(items)+'</main>',1)
    if '/assets/internal-discovery.js' not in source:
        source=source.replace('</body>','<script src="/assets/internal-discovery.js" defer></script>\n</body>',1)
    return source

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--validate',action='store_true');args=ap.parse_args()
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'};root=ET.parse(ROOT/'sitemap.xml').getroot(); indexed={urlparse(n.text).path for n in root.findall('s:url/s:loc',ns) if n.text}
    errors=[];changed=0
    for path,items in TARGETS.items():
        if path not in indexed: errors.append(f'{path}: not in sitemap');continue
        p=local(path)
        if not p.exists(): errors.append(f'{path}: missing HTML');continue
        for _,_,href,_ in items:
            if href not in indexed: errors.append(f'{path}: continuation target not indexed: {href}')
        source=p.read_text(encoding='utf-8')
        if canonical(source)!=ORIGIN+path: errors.append(f'{path}: canonical mismatch')
        out=apply(source,items)
        if args.write and out!=source: p.write_text(out,encoding='utf-8');changed+=1
    if errors: raise SystemExit('Internal Discovery input validation failed:\n- '+'\n- '.join(errors))
    if args.write:
        css=ROOT/'styles.css';txt=css.read_text(encoding='utf-8')
        if '/* ARWP Internal Discovery & Distribution */' not in txt: css.write_text(txt+STYLE,encoding='utf-8')
        (ROOT/'assets/internal-discovery.js').write_text(SCRIPT,encoding='utf-8')
    print(f'Internal Discovery inputs valid for {len(TARGETS)} reviewed learning/practice pages; {changed} page(s) updated.')
if __name__=='__main__':main()
