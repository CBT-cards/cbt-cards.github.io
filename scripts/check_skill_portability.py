#!/usr/bin/env python3
"""Validate the latest CBT Cards skill against the portable Agent Skills profile."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ORIGIN="https://cbt-cards.github.io"; ALLOWED_TOP_LEVEL={"name","description","license","compatibility","metadata","allowed-tools"}; NAME_RE=re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$"); SEMVER_RE=re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
def fail(m): raise SystemExit("skill portability check failed: "+m)
def unquote(v):
 v=v.strip(); return v[1:-1] if len(v)>=2 and v[0]==v[-1] and v[0] in {'"',"'"} else v
def parse(path):
 text=path.read_text(encoding="utf-8"); lines=text.splitlines()
 if not lines or lines[0].strip()!="---": fail(f"{path.relative_to(ROOT)} missing frontmatter")
 try: closing=next(i for i in range(1,len(lines)) if lines[i].strip()=="---")
 except StopIteration: fail(f"{path.relative_to(ROOT)} missing closing frontmatter")
 top={}; meta={}; in_meta=False
 for n,raw in enumerate(lines[1:closing],2):
  if not raw.strip(): continue
  if raw.startswith("  "):
   if not in_meta or ":" not in raw: fail(f"{path.relative_to(ROOT)}:{n} malformed metadata")
   k,v=raw.strip().split(":",1); v=unquote(v)
   if not k or not v or k in meta: fail(f"{path.relative_to(ROOT)}:{n} invalid metadata")
   meta[k]=v; continue
  if raw[0].isspace() or ":" not in raw: fail(f"{path.relative_to(ROOT)}:{n} malformed field")
  in_meta=False; k,v=raw.split(":",1); k=k.strip(); v=unquote(v)
  if k not in ALLOWED_TOP_LEVEL or k in top: fail(f"{path.relative_to(ROOT)}:{n} nonportable/duplicate {k}")
  if k=="metadata":
   if v: fail("metadata must be mapping")
   top[k]=""; in_meta=True
  else:
   if not v: fail(f"empty {k}")
   top[k]=v
 return top,meta,"\n".join(lines[closing+1:])
def main():
 manifest=json.loads((ROOT/"agents/cbt-cards/manifest.json").read_text()); catalog=json.loads((ROOT/"data/catalog.json").read_text()); latest=manifest.get("latest")
 if not isinstance(latest,str) or not SEMVER_RE.fullmatch(latest): fail("manifest latest must be semver")
 alias=ROOT/"agents/cbt-cards/SKILL.md"; mirror=ROOT/f"agents/cbt-cards/v{latest}/SKILL.md"; portable=ROOT/f"agents/cbt-cards/v{latest}/cbt-cards/SKILL.md"
 for p in (alias,mirror,portable):
  if not p.exists(): fail(f"missing {p.relative_to(ROOT)}")
 text=alias.read_text(encoding="utf-8")
 if text!=mirror.read_text(encoding="utf-8") or text!=portable.read_text(encoding="utf-8"): fail("latest skill copies differ")
 for p in (alias,portable):
  top,meta,body=parse(p)
  if top.get("name")!="cbt-cards" or not NAME_RE.fullmatch(top["name"]): fail("skill name")
  if p.parent.name!="cbt-cards": fail(f"{p.relative_to(ROOT)} parent/name mismatch")
  if top.get("license")!="CC-BY-NC-SA-4.0": fail("license")
  if meta!={"author":"MetalHatsCats","version":latest,"homepage":f"{ORIGIN}/agents/"}: fail("metadata")
  if len(body.splitlines())>500 or f"version: {latest}" not in body: fail("body/version")
 for fragment in ("data/practice.json","data/toolkit-review.json","data/toolkit-audit.json","data/content-review.json","no_match","source_only","unreviewed"):
  if fragment not in text: fail("latest skill missing "+fragment)
 versions={x.get("version"):x.get("url") for x in manifest.get("versions",[]) if isinstance(x,dict)}; mirror_url=f"{ORIGIN}/agents/cbt-cards/v{latest}/SKILL.md"
 if versions.get(latest)!=mirror_url: fail("manifest immutable URL")
 by_id={x.get("id"):x for x in catalog.get("resources",[]) if isinstance(x,dict)}
 expected={"agent-skill-latest":(f"{ORIGIN}/agents/cbt-cards/SKILL.md",latest),f"agent-skill-v{latest}":(mirror_url,latest),f"agent-skill-v{latest}-portable":(f"{ORIGIN}/agents/cbt-cards/v{latest}/cbt-cards/SKILL.md",latest),"agent-skill-install":(f"{ORIGIN}/agents/cbt-cards/INSTALL.md",None)}
 for rid,(url,version) in expected.items():
  item=by_id.get(rid)
  if not item or item.get("url")!=url or (version is not None and item.get("version")!=version): fail("catalog "+rid)
 install=(ROOT/"agents/cbt-cards/INSTALL.md").read_text(encoding="utf-8")
 for fragment in ("OpenClaw","~/.openclaw/skills/cbt-cards","openclaw skills list","Hermes Agent","hermes skills install https://cbt-cards.github.io/agents/cbt-cards/SKILL.md --name cbt-cards","https://agentskills.io/specification","skills-ref validate ./cbt-cards",mirror_url):
  if fragment not in install: fail("INSTALL missing "+fragment)
 print(f"skill portability check passed: v{latest} alias and immutable portable copies aligned")
if __name__=="__main__": main()
