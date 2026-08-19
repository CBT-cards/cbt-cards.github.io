# Legacy CBT Cards redirect audit

Verification date: **19 August 2026**

Scope: public HTTP/search behavior only. This repository cannot modify the legacy `metalhatscats.com` deployment.

## Observed live legacy surfaces

The external recheck found these URLs still resolving as independent MetalHatsCats content rather than redirecting to the standalone CBT Cards site:

- `https://metalhatscats.com/products/cbt-cards`
- `https://metalhatscats.com/products/cbt-cards/privacy` (normalizes to a trailing-slash URL on the same host)
- `https://metalhatscats.com/products/cbt-cards/terms` (normalizes to a trailing-slash URL on the same host)
- `https://metalhatscats.com/cbt`

Search results also continue to expose both the legacy CBT Cards product page and the MetalHatsCats CBT Toolkit page as independent results. The duplicate product/knowledge surface therefore remains externally visible.

The 2026-08-19 fetch for deeper routes such as `/cbt/cards`, `/cbt/metaphors`, `/cbt/protocols`, and `/news/cbt-cards-app` was inconclusive. They remain redirect requirements until a successful external HTTP check proves otherwise.

## Why this matters

The legacy product page contains product, privacy, and health-adjacent wording that can drift from `cbt-cards.github.io`. Once CBT Cards has its own canonical site, allowing both domains to act like authoritative product pages splits provenance and can expose stale claims even when the standalone site is corrected.

The standalone CBT Cards domain is the canonical source for current CBT Cards product/privacy/support/public-library material. The MetalHatsCats CBT Toolkit dataset landing page remains legitimate source provenance for the pinned source corpus; it is not the canonical CBT Cards product site.

## Required external changes

On the legacy MetalHatsCats deployment, configure permanent redirects for the mappings in `MIGRATION.md`, then verify the actual deployed HTTP behavior rather than the source configuration alone.

After deployment:

1. Fetch every legacy URL without following redirects and record status + `Location`.
2. Confirm the final target is the expected `https://cbt-cards.github.io/...` URL.
3. Confirm legacy product/privacy/terms pages no longer render independent indexable product content.
4. Request recrawl/removal in search-engine webmaster tools where available.
5. Recheck search results after recrawl and record whether the standalone CBT Cards URLs are selected.

## Repository-side invariant

Until the legacy host is fixed, CBT Cards code/data must not reintroduce those legacy product/CBT URLs as canonical or recommended CBT Cards resources. `scripts/check_legacy_boundary.py` enforces that boundary for public HTML, the public catalog, curated knowledge data, LLM indexes, and current Agent Skill files.
