# CBT Cards — ARWP Growth adoption record

Baseline: 2026-09-06  
Site: https://cbt-cards.github.io/  
Repository: `CBT-cards/cbt-cards.github.io`  
Verticals: editorial / documentation / research-dataset / software-product  
Goals: Search / generative Search / Discover / AI citation / referrals / agent retrieval / useful-practice discovery

ARWP rollout baseline revision: `0d60109d0986d1f15fa30cce7bbdaec36ceb108f`.

This record applies the current Agent-Ready Web Profile Growth decision loop to CBT Cards. It is implementation evidence, not a ranking, recommendation, indexing, clinical-validity, citation, or traffic claim.

## Publisher policy

- Public Search crawling: allowed for canonical public pages. Intentionally `noindex` localization previews remain outside the public Search inventory.
- Search/answer crawlers with provider-specific controls: `OAI-SearchBot` is explicitly allowed; the general public crawl rule remains allowed.
- Model-training crawlers: no separate restriction is introduced by this rollout. The current general crawl rule remains unchanged until the publisher makes a distinct training/reuse decision.
- Public reuse/license boundary: current project and resource-level rights remain authoritative. CBT Cards must not be described as a permission-free open-reuse corpus.
- Safety boundary: Growth work must not convert general-wellness material, research-watch candidates, or evidence records into diagnosis, treatment selection, individualized medical advice, or clinical-efficacy claims.

## Site classification and priority surfaces

Canonical entity home: `https://cbt-cards.github.io/`  
Primary human routes: `/practice/`, `/learn/`, `/worksheets/`, `/research/`, `/research/practice-watch/`  
Primary machine routes: `/ai/site-profile.json`, `/ai/ai-search-profile.json`, `/ai/content-profile.json`, `/data/catalog.json`, `/data/practice-evidence.json`, `/knowledge/graph.json`, `/trust/trust.json`, `/llms.txt`

The site already has a strong technical baseline: canonical URLs, a public sitemap, explicit crawler policy, `max-image-preview:large` on priority pages, representative editorial imagery on the main learning surfaces, a canonical publisher identity, evidence/provenance data, stable agent retrieval resources, and an owner-side Search measurement pipeline.

## Selected hypotheses

| Hypothesis ID | Baseline observation | Action | Verification | Outcome signal / owner-data gate |
| --- | --- | --- | --- | --- |
| `search-foundation-first` | Canonicals, sitemap and crawl policy exist; intended public pages are indexable. | Keep eligibility checks ahead of optional metadata work. | `scripts/check_site.py`, `scripts/check_crawl_graph.py`, production HTTP checks and weekly ARWP Growth audit. | Indexed priority pages; Search impressions. |
| `non-commodity-evidence` | Reviewed practices, evidence provenance, original semantic evaluations and Monthly Practice Watch add material beyond commodity summaries. | Preserve source-backed reasoning, negative findings, explicit non-claims and the review gate between research signals and reviewed practices. | Editorial review checks, practice-system checks and source inspection. | New relevant impressions/citations to evidence-rich pages; useful engagement. |
| `answer-addressability` | Important practice and research items already expose stable fragments and descriptive headings. | Preserve stable IDs; prefer question/decision/evidence headings and meaningful internal links rather than query-variant pages. | Crawl/link checks plus manual content review. | Deep-link traffic; section-level citations; precise agent retrieval. |
| `identity-and-provenance` | Homepage exposes the canonical publisher entity; learning Articles resolve author/publisher to that identity; Trust Center and corrections data exist. | Keep one publisher identity and truthful review/provenance links. Do not invent individual authors. | Structured-data checks and manual authorship review. | Consistent attribution and entity interpretation. |
| `discover-visual-preview` | Homepage and core learning pages allow large previews and use high-resolution representative imagery. Some text-first research pages intentionally do not yet claim a representative image. | Keep large-preview eligibility and only add page-specific Discover/social imagery when a genuinely representative visible asset exists. | HTML/meta/asset checks plus manual image-content fit review. | Discover and image-result impressions/CTR where available. |
| `chatgpt-search-access` | `OAI-SearchBot` is explicitly allowed; training/reuse policy is not conflated with Search access. | Preserve Search access and keep any future GPTBot/training change as a separate publisher decision. | `robots.txt` review plus weekly ARWP audit. | Observable ChatGPT referrals/citations, if measurable. |
| `freshness-without-fake-recency` | Sitemap dates stay stable for unchanged pages while updated research routes carry newer meaningful dates. | Change `lastmod`, visible review dates and structured dates only after material content changes; keep IndexNow post-deploy. | Sitemap checks, content-review checks and IndexNow receipts. | Faster recrawl after material updates; fewer stale-result observations. |
| `platform-ai-measurement` | `data/search-measurement.json`, Google Search workflow and IndexNow receipts already separate owner data from implementation claims. | Keep unavailable metrics null; add Bing/AI citation observations only from defensible owner or observable sources. | Search-distribution checks and weekly/monthly measurement review. | Generative Search impressions, AI citations, unique cited priority pages, referrals. |

`preferred-source-loop` remains **planned / not selected for this rollout**. A user-facing control should be added only if CBT Cards is actually eligible/selectable and repeat-reader value is measurable.

`agent-readable-routes` remains an **interoperability experiment, not a ranking hypothesis**. CBT Cards already has real agent-facing resources (profile, catalog, retrieval data and a versioned Agent Skill), so those surfaces are retained without presenting them as Search ranking factors.

## New ARWP content contract

`/ai/content-profile.json` records the site-specific adaptive content policy introduced in this rollout:

- content archetypes rather than one mandatory article template;
- meaningful graph relations between concepts, evidence and next questions;
- canonical publisher identity and truthful review freshness;
- semantically accurate structured data that mirrors visible content;
- large-image eligibility without forcing decorative images onto every page;
- warning-only style fingerprint linting;
- no forced word counts, keyword density, mandatory FAQ blocks, synthetic statistics, invented first-hand experience, uniform section order or query-variant page factory.

## Build / CI evidence

- Site quality gate: `.github/workflows/deploy-pages.yml` runs the repository's Python syntax checks plus deterministic practice, content review, schemas, canonical/structured-data, crawl graph, discovery, asset, privacy, search-distribution, license and project-state checks.
- ARWP validation: `.github/workflows/arwp.yml` validates `ai/site-profile.json` against current ARWP and parses the AI-search, content, trust, corrections and knowledge surfaces.
- Recurring ARWP Growth audit: `.github/workflows/arwp-growth.yml` follows current ARWP `main`, records the exact checked-out ARWP revision and uploads the Growth profile plus revision metadata as a 30-day artifact.
- Longitudinal owner-data checks remain external gates. Missing Search/AI metrics remain missing rather than being converted to zero.

## Measurement window

Before: existing CBT Cards Search measurement baseline and checkpoints in `data/search-measurement.json`.  
After: continue the existing scheduled checkpoints after this 2026-09-06 rollout.  
Metrics: Google Search/generative visibility where owner data is available; Bing AI citation data when available; observable ChatGPT/referral evidence; priority-page discovery; no synthetic attribution to ARWP changes.

## Decision

`keep`

Reason: the rollout adds governance, adaptive content semantics and repeatable measurement without weakening the site's existing safety, evidence, licensing or privacy boundaries. Visibility outcomes remain an external measurement question; neutral or negative results must be preserved and can trigger `revise`, `revert` or `retire` later.
