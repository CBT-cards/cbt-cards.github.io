# CBT Cards redesign QA

## Scope

- Selected visual direction: kinetic torn-paper collage, ultramarine/yolk/coral palette, bold black display type, friendly CBT Cards mascot.
- Reference: `/Users/dzmitryikharlanau/.codex/generated_images/01a02a38-39b5-7371-9e96-626c4ee469cb/exec-244c10fd-cb77-4f37-94c5-9ead1c5d19f6.png`
- Final implementation capture: `/private/tmp/cbt-final-audit/01-home-desktop-viewport.png`
- Flow and responsive captures: `/private/tmp/cbt-final-audit/02-practice-desktop.png` through `/private/tmp/cbt-final-audit/24-practice-article-image.png`.
- Responsive captures: desktop 1440 × 1024; mobile 390 × 844.

## Comparison pass

The implementation carries the selected direction through real generated paper-collage assets, the original CBT Cards logo, oversized condensed-feeling Nunito headings, a yolk/cobalt/coral/pink palette, hard black rules, offset shadows, and situation-first controls. The production version intentionally keeps live HTML text and controls instead of baking the mock's content into an image.

The initial mobile pass put the mascot below the full situation picker. That reduced the bright visual impact at the first viewport. The hero was restructured into three responsive grid areas so the collage appears after the short introduction and before the longer interactive picker on narrow screens, while preserving the desktop composition.

The initial mobile navigation required horizontal scrolling, which was especially awkward for Russian labels. It now wraps into readable rows, keeps practical tap targets, and creates no root-page overflow. A second pass also removed excess mobile hero whitespace from pages that use overlapping editorial visuals.

## Verified surfaces

- Homepage desktop and mobile: no clipping or root horizontal overflow; hero image crops cleanly; title remains exactly `CBT Cards`.
- Practice library: visual page hero, local Practice Finder, and reviewed-practice content remain usable. Selecting `sit-looping-worry` returns `Problem or Worry?`, moves focus to the result, and the result link lands on a visible thematic illustration plus fit/exclusion notes.
- Thought-record worksheet: seven fields render without overflow; focus is visible; typed content stays local to the page.
- Inner-page shell: shared header, tokens, hero imagery, typography, footer, prose, tables, details, cards, and forms apply across all 41 canonical pages plus 14 noindex localization previews.
- Contact, Partnerships, and AI get-started: coherent collaboration/AI imagery, clear trust boundaries, working internal routes, and mobile compositions verified in-browser.
- Localizations: `/ru/` exposes 12 machine-draft review previews and `/de/` a planned-language hub; both are visibly labelled and `noindex`, while their navigation wraps for longer labels.
- Future content: card grids use auto-fit columns; navigation wraps; logical CSS properties and language-specific heading adjustments support longer translations and future RTL content.
- Accessibility spot checks: one H1 on every checked page, contextual image alt, labelled controls, Finder result focus, visible focus ring, reduced-motion rule, mobile tap targets, and no root horizontal overflow. This is a focused product audit, not a claim of full accessibility conformance.

## Automated checks

- Site integrity: 55 HTML pages, 41 indexed canonical URLs, internal links, sitemap, catalog, JSON, and JSON-LD passed.
- Crawl graph: 41 indexed pages, maximum depth 3, no orphans.
- Practice artifacts, practice graph, localization, localized pages, worksheets, schemas, asset budgets, privacy wording, skill portability, content review, toolkit review/audit, eval fixtures, and deterministic baselines passed.
- Design shell regeneration check passed.
- Discovery check passed under the repository's local Python 3.9 runtime after making its annotations runtime-compatible.

## Remaining findings

- P0: none.
- P1: none.
- P2: none blocking acceptance. The production hero is deliberately calmer than the ideation mock so live practice copy, safety boundaries, and future translated strings remain readable and editable.

final result: passed
