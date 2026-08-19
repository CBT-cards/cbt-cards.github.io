#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BUDGETS = {
    'assets/Nunito-Regular.woff2': 50000,
    'assets/Nunito-ExtraBold.woff2': 50000,
    'assets/app-icon.webp': 12000,
    'assets/cbt.webp': 120000,
    'assets/cbt-560w.webp': 20000,
    'assets/diary.webp': 110000,
    'assets/diary-560w.webp': 45000,
    'assets/egg-card-journey.webp': 60000,
    'assets/egg-card-journey-560w.webp': 20000,
    'assets/egg-diary.webp': 40000,
    'assets/egg-diary-560w.webp': 15000,
    'assets/egg-diary-1024w.webp': 30000,
    'assets/egg-reflection-cards.webp': 60000,
    'assets/egg-reflection-cards-500w.webp': 20000,
    'assets/social-preview.jpg': 100000,
}
errors = []
total = 0
for rel, maximum in BUDGETS.items():
    path = ROOT / rel
    if not path.exists():
        errors.append(f'missing optimized asset: {rel}')
        continue
    size = path.stat().st_size
    total += size
    if size > maximum:
        errors.append(f'{rel}: {size} bytes exceeds {maximum}')

css = (ROOT / 'styles.css').read_text(encoding='utf-8')
if '.ttf' in css:
    errors.append('styles.css still references TTF')
for name in ('Nunito-Regular.woff2', 'Nunito-ExtraBold.woff2'):
    if name not in css:
        errors.append(f'styles.css missing {name}')
if '.hero-art picture' not in css or '.split > picture' not in css:
    errors.append('styles.css missing picture layout guards')

heavy = ('cbt.png','diary.png','egg-card-journey.png','egg-diary.png','egg-reflection-cards.png')
app_png_body = []
unwrapped = []
malformed = []
bad_og = []
for path in ROOT.rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    body = text.split('</head>', 1)[-1]
    if 'src="/assets/app-icon.png"' in body:
        app_png_body.append(str(path.relative_to(ROOT)))
    if re.search(r'/\s+decoding=', text):
        malformed.append(str(path.relative_to(ROOT)))
    if 'property="og:image"' in text and 'assets/social-preview.jpg' not in text:
        bad_og.append(str(path.relative_to(ROOT)))
    for name in heavy:
        for match in re.finditer(rf'<img[^>]+src="/assets/{re.escape(name)}"[^>]*>', body):
            prefix = body[max(0, match.start()-400):match.start()]
            if '<picture>' not in prefix or 'type="image/webp"' not in prefix:
                unwrapped.append(f'{path.relative_to(ROOT)}:{name}')
if app_png_body:
    errors.append('body still uses 512px PNG app icon: ' + ', '.join(app_png_body))
if malformed:
    errors.append('malformed self-closing image attributes: ' + ', '.join(malformed))
if unwrapped:
    errors.append('heavy PNG body image without WebP picture source: ' + ', '.join(unwrapped))
if bad_og:
    errors.append('Open Graph image is not the 1200x630 preview: ' + ', '.join(bad_og))

generator = (ROOT / 'scripts/build_localized_pages.py').read_text(encoding='utf-8')
if '<img src="/assets/app-icon.webp" width="42" height="42" alt="" decoding="async" />' not in generator:
    errors.append('localized page generator still emits the PNG header icon')

home = (ROOT / 'index.html').read_text(encoding='utf-8')
hero = re.search(r'<img[^>]+src="/assets/egg-reflection-cards\.png"[^>]*>', home)
if not hero or 'fetchpriority="high"' not in hero.group(0) or 'loading="lazy"' in hero.group(0):
    errors.append('home hero must be eager with fetchpriority=high')
if 'src="/assets/egg-card-journey.png" width="992" height="1586"' not in home:
    errors.append('home egg-card-journey intrinsic dimensions are not 992x1586')
for name in ('egg-card-journey.png', 'egg-diary.png'):
    match = re.search(rf'<img[^>]+src="/assets/{re.escape(name)}"[^>]*>', home)
    if not match or 'loading="lazy"' not in match.group(0) or 'decoding="async"' not in match.group(0):
        errors.append(f'below-fold home image {name} must be lazy/async')

if errors:
    print('Asset budget checks failed:')
    for error in errors:
        print('- ' + error)
    raise SystemExit(1)
print(f'asset budget check passed: {len(BUDGETS)} optimized runtime assets, {total} bytes total; heavy PNGs only as picture fallbacks/source assets')
