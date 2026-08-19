# CBT Cards migration inventory

Last external redirect verification: **19 August 2026**

This inventory describes the redirects that are required on the legacy `metalhatscats.com` host. It does **not** claim that a redirect exists merely because a target was planned in an earlier migration configuration.

| Old MetalHatsCats URL | Required CBT Cards target | Owner | External status on 2026-08-19 |
| --- | --- | --- | --- |
| `https://metalhatscats.com/products/cbt-cards` | `https://cbt-cards.github.io/` | legacy MetalHatsCats host | **redirect not observed**; legacy product page still resolves |
| `https://metalhatscats.com/products/cbt-cards/privacy` | `https://cbt-cards.github.io/privacy/` | legacy MetalHatsCats host | **redirect not observed**; URL remains on legacy host |
| `https://metalhatscats.com/products/cbt-cards/terms` | `https://cbt-cards.github.io/terms/` | legacy MetalHatsCats host | **redirect not observed**; URL remains on legacy host |
| `https://metalhatscats.com/cbt` | `https://cbt-cards.github.io/how-it-works/` | legacy MetalHatsCats host | **redirect not observed**; legacy CBT Toolkit page still resolves |
| `https://metalhatscats.com/cbt/cards` | `https://cbt-cards.github.io/features/` | legacy MetalHatsCats host | redirect **not verified** in the 2026-08-19 fetch; legacy `/cbt` surface remains live |
| `https://metalhatscats.com/cbt/metaphors` | `https://cbt-cards.github.io/features/` | legacy MetalHatsCats host | redirect **not verified** in the 2026-08-19 fetch; legacy `/cbt` surface remains live |
| `https://metalhatscats.com/cbt/protocols` and protocol pages | `https://cbt-cards.github.io/how-it-works/` | legacy MetalHatsCats host | redirect **not verified** in the 2026-08-19 fetch; legacy `/cbt` surface remains live |
| `https://metalhatscats.com/news/cbt-cards-app` | `https://cbt-cards.github.io/` | legacy MetalHatsCats host | redirect **not verified** in the 2026-08-19 fetch |

## Why the status changed

An earlier version of this file marked the mappings as `implemented`. That described the intended legacy-host configuration, not an externally verified HTTP outcome. The 19 August 2026 recheck found that the main legacy CBT Cards product page, its privacy/terms pages, and the `/cbt` toolkit page still resolve on `metalhatscats.com`. The inventory now records observable status instead of treating configuration intent as deployment proof.

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
