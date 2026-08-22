# CBT Cards migration inventory

Last external redirect verification: **20 August 2026**. Deployment remains **not verified** on the legacy host.

This inventory describes the redirects that are required on the legacy `metalhatscats.com` host. It does **not** claim that a redirect exists merely because a target was planned in an earlier migration configuration.

| Old MetalHatsCats URL | Required CBT Cards target | Owner | External status on 2026-08-20 |
| --- | --- | --- | --- |
| `https://metalhatscats.com/products/cbt-cards` | `https://cbt-cards.github.io/` | legacy MetalHatsCats host | **redirect not observed**; legacy product page still renders independently |
| `https://metalhatscats.com/products/cbt-cards/privacy` | `https://cbt-cards.github.io/privacy/` | legacy MetalHatsCats host | **redirect not observed**; URL normalizes only to a trailing-slash page on the legacy host |
| `https://metalhatscats.com/products/cbt-cards/terms` | `https://cbt-cards.github.io/terms/` | legacy MetalHatsCats host | **redirect not observed**; URL normalizes only to a trailing-slash page on the legacy host |
| `https://metalhatscats.com/cbt` | `https://cbt-cards.github.io/how-it-works/` | legacy MetalHatsCats host | **redirect not observed**; legacy CBT Toolkit page still renders independently |
| `https://metalhatscats.com/cbt/cards` | `https://cbt-cards.github.io/features/` | legacy MetalHatsCats host | direct fetch remained inconclusive; the live `/cbt` page still links to this route, so the redirect requirement remains open |
| `https://metalhatscats.com/cbt/metaphors` | `https://cbt-cards.github.io/features/` | legacy MetalHatsCats host | direct fetch remained inconclusive; the live `/cbt` page still links to this route, so the redirect requirement remains open |
| `https://metalhatscats.com/cbt/protocols` and protocol pages | `https://cbt-cards.github.io/how-it-works/` | legacy MetalHatsCats host | direct fetch remained inconclusive; the live `/cbt` page still links to this route, so the redirect requirement remains open |
| `https://metalhatscats.com/news/cbt-cards-app` | `https://cbt-cards.github.io/` | legacy MetalHatsCats host | direct fetch remained inconclusive; keep as a redirect requirement until deployed HTTP behavior is verified |

## Verification history

An earlier version of this file marked the mappings as `implemented`. That described intended legacy-host configuration, not externally verified HTTP behavior.

The 19 August 2026 recheck established that the main legacy product, privacy/terms, and `/cbt` surfaces were still live. The 20 August 2026 recheck confirmed the same observable state: the product page and CBT Toolkit remain independent MetalHatsCats pages, while privacy and terms normalize only within the legacy host. Deeper CBT routes remain linked from the live toolkit page but could not be fetched reliably enough to claim either a redirect or an independent page.

See [`LEGACY_REDIRECT_AUDIT.md`](LEGACY_REDIRECT_AUDIT.md) for the verification record and remaining external work.

## Canonical boundary inside this repository

`CBT-cards/cbt-cards.github.io` cannot implement redirects on `metalhatscats.com`. Inside this repository:

- CBT Cards-published HTML remains self-canonical under `https://cbt-cards.github.io/`;
- the public catalog, curated knowledge data, LLM indexes, and latest Agent Skill must not use legacy product/CBT URLs as CBT Cards canonical resources;
- `metalhatscats.com/datasets/cbt-toolkit` remains valid **source provenance** for the independently pinned source corpus and is not a CBT Cards product canonical;
- the migration/audit documents may name legacy URLs because their job is to record the external dependency.

## Assets

`assets/` contains product-owned artwork from the CBT Cards Flutter app and prior product listing. Original high-resolution source/fallback files are retained where useful; production web delivery prefers the optimized variants documented in `PERFORMANCE.md`.

## Publishing

The repository is an organization Pages repository: `CBT-cards/cbt-cards.github.io`. The workflow in `.github/workflows/deploy-pages.yml` deploys `main` to `https://cbt-cards.github.io/` after quality checks pass.

No CNAME is included because the primary domain is the default GitHub Pages domain.
