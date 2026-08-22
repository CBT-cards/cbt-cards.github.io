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
    'assets/collage-hero.webp': 180000,
    'assets/collage-library.webp': 180000,
    'assets/collage-tools.webp': 180000,
    'assets/technique-thought-evidence.webp': 65000,
    'assets/technique-thought-evidence-560w.webp': 25000,
    'assets/technique-worry-time.webp': 45000,
    'assets/technique-worry-time-560w.webp': 18000,
    'assets/technique-small-steps.webp': 60000,
    'assets/technique-small-steps-560w.webp': 22000,
    'assets/technique-grounding.webp': 65000,
    'assets/technique-grounding-560w.webp': 22000,
    'assets/metaphor-library.webp': 70000,
    'assets/metaphor-library-560w.webp': 26000,
    'assets/ai-agent-public-private.webp': 50000,
    'assets/ai-agent-public-private-560w.webp': 20000,
    'assets/collaboration.webp': 60000,
    'assets/collaboration-560w.webp': 24000,
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
if '.hero-visual picture' not in css or '.collage-media picture' not in css:
    errors.append('styles.css missing picture layout guards')

heavy = ('cbt.png','diary.png','egg-card-journey.png','egg-diary.png','egg-reflection-cards.png','collage-hero.png','collage-library.png','collage-tools.png')
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
    og = re.search(r'<meta property="og:image" content="https://cbt-cards\.github\.io(/assets/[^\"]+)"', text)
    if og:
        is_shared_preview = og.group(1) == "/assets/social-preview.jpg"
        if not (ROOT / og.group(1).lstrip('/')).exists() or (not is_shared_preview and 'property="og:image:alt"' not in text):
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
    errors.append('Open Graph image is missing locally or has no contextual alt: ' + ', '.join(bad_og))

generator = (ROOT / 'scripts/build_localized_pages.py').read_text(encoding='utf-8')
if '<img src="/assets/app-icon.webp" width="46" height="46" alt="" decoding="async" />' not in generator:
    errors.append('localized page generator still emits the PNG header icon')

home = (ROOT / 'index.html').read_text(encoding='utf-8')
hero = re.search(r'<img[^>]+src="/assets/collage-hero\.png"[^>]*>', home)
if not hero or 'fetchpriority="high"' not in hero.group(0) or 'loading="lazy"' in hero.group(0):
    errors.append('home hero must be eager with fetchpriority=high')
if 'src="/assets/collage-library.png" width="1536" height="1024"' not in home:
    errors.append('home collage-library intrinsic dimensions are not 1536x1024')
for name in ('collage-library.png', 'collage-tools.png'):
    match = re.search(rf'<img[^>]+src="/assets/{re.escape(name)}"[^>]*>', home)
    if not match or 'loading="lazy"' not in match.group(0) or 'decoding="async"' not in match.group(0):
        errors.append(f'below-fold home image {name} must be lazy/async')

if errors:
    print('Asset budget checks failed:')
    for error in errors:
        print('- ' + error)
    raise SystemExit(1)
print(f'asset budget check passed: {len(BUDGETS)} optimized runtime assets, {total} bytes total; heavy PNGs only as picture fallbacks/source assets')
