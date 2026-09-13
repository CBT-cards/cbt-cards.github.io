from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
home = root / "index.html"
if not home.exists():
    raise SystemExit(f"Missing public homepage: {home}")
html = home.read_text(encoding="utf-8")
if 'data-goose-arwp-proof-mark="0.1"' in html:
    raise SystemExit(0)
product = "https://dkharlanau.github.io/agent-ready-web-profile/product/"
contract = "https://github.com/dkharlanau/agent-ready-web-profile/blob/main/docs/PROOF-MARK.md"
mark = f'''<span data-goose-arwp-proof-mark="0.1" data-arwp-coverage="partial" role="group" aria-label="Goose ARWP Proof Mark: partial audit scope" title="ARWP evidence is present; whole-site audit scope remains incomplete." style="display:inline-flex;max-width:100%;min-height:38px;border:1px solid #080c0b;border-radius:4px;overflow:hidden;background:#fafaf7;color:#080c0b;font:10px/1.15 Arial,sans-serif;vertical-align:middle"><a href="{product}" aria-label="Open Goose ARWP" style="padding:8px 9px;background:#080c0b;color:#fafaf7;text-decoration:none;border-right:4px solid #173bea;font-weight:700;letter-spacing:.06em">GOOSE ARWP</a><a href="{contract}" aria-label="Read Proof Mark contract: partial scope" style="padding:8px 9px;color:#080c0b;text-decoration:none"><strong>PARTIAL</strong> · <span style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace">scope incomplete</span></a></span>'''
block = f'<span data-goose-arwp-proof-mark-slot="footer" style="display:block;margin-top:12px">{mark}</span>'
if "</footer>" in html.lower():
    pos = html.lower().rfind("</footer>")
    html = html[:pos] + block + html[pos:]
elif "</body>" in html.lower():
    pos = html.lower().rfind("</body>")
    html = html[:pos] + f'<footer aria-label="Site quality evidence" style="padding:20px">{block}</footer>' + html[pos:]
else:
    raise SystemExit("Public homepage has no footer or closing body for Goose ARWP Proof Mark")
home.write_text(html, encoding="utf-8")
print("Goose ARWP Proof Mark staged: PARTIAL (scope incomplete)")
