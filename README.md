# CBT Cards public reflection resource

CBT Cards is a static, inspectable library of practical reflection resources for people and the AI assistants they choose to use. It began as a mobile app; the repository now treats the public web/data layer as a first-class product with stable IDs, provenance, safety boundaries, review metadata, retrieval-ready data, versioned schemas, and reproducible evaluation tooling.

The website intentionally remains simple: plain HTML, CSS, JSON/JSONL/NDJSON, Markdown, product-owned assets, and small Python validation/generation scripts published through GitHub Pages. There is no server-side account system and no JavaScript application bundle required to read the public library.

For the current verified snapshot and the deliberately unresolved boundaries, see [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Start here

Human-facing public resource:

- `/` — project overview
- `/practice/` — situation-first Practice Finder
- `/learn/` — reviewed learning guides
- `/worksheets/` — browser-local blank worksheets with no submit action
- `/toolkit/` — pinned 115-record source toolkit and curated publication layer
- `/toolkit/audit/` — record-complete editorial/source-corpus audit
- `/about/editorial-review/` — review freshness policy
- `/languages/` — website translation/publication status
- `/research/` — agent/model evaluation methods and tooling
- `/agents/` — AI-assistant integration guide
- `/changelog/` — website/data/agent history
- `/mobile-releases/` — separately sourced mobile-app release history

Original mobile-product documentation remains under `/features/`, `/how-it-works/`, `/faq/`, `/privacy/`, `/terms/`, and `/support/`. A website, data, translation, research, schema, or Agent Skill release is not a mobile-app release.

## Reviewed practice layer

The trusted CBT Cards-owned practice layer currently contains **11 reviewed practices**. Routing starts from a plain-language situation/mechanism, not a diagnosis.

Canonical resources:

- `data/practice.json` — reviewed practices, fit/exclusion fields and micro-actions
- `data/practice-ontology.json` — situation/mechanism ontology
- `data/practice-evidence.json` — evidence and claim provenance
- `data/practice-relations.json` — reviewed progression/relationship graph
- `data/practice-recommendations.json` — agent recommendation contract and `no_match`
- `data/practice-rag.ndjson` + `data/practice-rag-manifest.json` — stable retrieval chunks with safety kept in-chunk and SHA-256 provenance
- `agents/cbt-cards/PRACTICE_SYSTEM.md` — agent-facing practice-routing guide

Agents should prefer one reviewed practice when there is a clear fit, preserve `avoid_when`, and return `no_match` rather than inventing guidance. Genuine danger, mandatory safety/professional/accessibility requirements, and medical/legal/financial/safeguarding decisions are outside the practice-routing contract.

## Source toolkit and trust layers

The related MetalHatsCats CBT Toolkit v0.1.0 is pinned as a **115-record source corpus**: 77 cards, 23 metaphors, and 15 protocols.

Three different trust layers are deliberately separate:

1. `data/toolkit-review.json` is the publication authority for source records. Unlisted records remain `unreviewed` and `source_only`.
2. `data/toolkit-audit.json` is a record-complete editorial triage layer for duplicates, framework attribution, overclaim, treatment-like wording, and future review priority. Audit candidacy is not publication approval.
3. `data/content-review.json` records freshness for **26 trusted items**: six learning pages, three worksheets, six curated source-toolkit cards, and all eleven owned practices.

Editorial review is not clinical validation or evidence of efficacy. Metaphors are memory aids, not evidence.

## Evaluation and real-model pipeline

The repository keeps deterministic routing checks, semantic review, and real hosted-model execution separate.

Existing evaluation layers include:

- 24 starter routing/boundary cases in `data/agent-evals.jsonl`
- 12 separately authored held-out challenge cases in `data/agent-evals-challenge.jsonl`
- **41 practice-semantic cases** in `data/practice-semantic-evals*.jsonl`
- blinded reviewer-packet generation and separate human semantic-review contracts
- a frozen-context provider runner for practice-semantic generation
- execution gates that verify case coverage, input provenance and absence of benchmark-answer leakage

A deterministic baseline is a harness check, not an LLM-quality or clinical-quality score. No hosted-model result is currently published as project evidence until a real execution is captured with provenance and the required human semantic/safety review is completed.

See `research/MODEL_RUN_PROTOCOL.md` and `research/SEMANTIC_EVAL_PROTOCOL.md`.

## Agent Skill

The current portable CBT Cards Agent Skill is **v1.8.0**.

- mutable latest: `agents/cbt-cards/SKILL.md`
- immutable compatibility URL: `agents/cbt-cards/v1.8.0/SKILL.md`
- strict portable distribution: `agents/cbt-cards/v1.8.0/cbt-cards/SKILL.md`
- version manifest: `agents/cbt-cards/manifest.json`
- install/pinning notes: `agents/cbt-cards/INSTALL.md`

Historical skill files remain immutable release history. Runtime-specific installation notes stay outside portable `SKILL.md` frontmatter.

## Localization

Website localization and mobile/store language support are separate sources of truth.

- English is the canonical source locale for current curated knowledge.
- Russian contains machine-draft overlays for all 12 current curated knowledge records; zero are currently human-reviewed/published.
- German is planned.
- Mobile/store languages are tracked separately in `MOBILE_LOCALE_AUDIT.md` and must not be inferred from `data/locales.json`.

Generated localized pages use `/<locale>/resources/<resource_id>/` and are produced only for explicitly human-reviewed, reviewed-for-publication, published records. Edit locale/translation data and run `scripts/build_localized_pages.py`; do not hand-edit generated localized pages.

## Privacy and mobile-product provenance

`/privacy/` is the canonical website policy, while `MOBILE_PRIVACY_AUDIT.md` records the current reconciliation boundary between app implementation claims and public store disclosures. Journal/check-in content handling and technical analytics/identifier telemetry are treated as distinct questions.

`/mobile-releases/` contains the separately sourced mobile release history. Apple exposes a detailed public version history; Google Play currently exposes a reliable update date but not a version name/code that this repository can safely infer.

## Performance

The production site uses WOFF2 fonts and responsive WebP sources for heavy body imagery while retaining original PNGs as source/fallback assets where appropriate. `scripts/check_asset_budget.py` enforces runtime byte budgets and optimized references.

The controlled mobile Lighthouse comparison documented in `PERFORMANCE.md` measured median performance score **0.72 → 0.91**, LCP **18.98 s → 3.38 s**, and transferred bytes **4.47 MB → 478 KB**. These are controlled lab measurements, not field Core Web Vitals.

## Search and distribution

`SEARCH_DISTRIBUTION.md` and `data/search-measurement.json` define the search/distribution operating loop. The sitemap, crawler policy, IndexNow receipt, eight-week measurement ledger, and curated outreach queue are kept separate from claims about actual Search Console/Bing performance.

Missing provider metrics stay `null`, not zero. The project does not add client-side analytics merely to fill a dashboard.

Legacy MetalHatsCats URLs are tracked in `LEGACY_REDIRECT_AUDIT.md`. Redirects require changes on the legacy host and are not considered implemented merely because this repository documents the desired mapping.

## Licensing and reuse

The current public license remains **CC BY-NC-SA 4.0**. Commercial reuse is not granted by the public license without separate permission.

`data/knowledge.jsonl` exposes record-level `license_url` and `rights_basis` so consumers can distinguish six CBT Cards-original learning records from six records adapted from the pinned toolkit source. `LICENSING_DECISION.md` compares possible future licensing approaches, but it is explicitly a pending publisher/legal decision and **not a new license grant**.

CBT Cards names, logos and trademark rights are not granted for reuse by the content license.

## Public machine-readable entry points

- `llms.txt` / `llms-full.txt`
- `data/catalog.json`
- `schemas/index.json`
- `data/knowledge.jsonl`
- `data/locales.json` / `data/translations.jsonl`
- `data/practice*.json` / `data/practice-rag.ndjson`
- `data/changelog.json`
- `CITATION.cff`
- `feed.xml` / `feed.json`
- `.well-known/security.txt`

## Quality gates

The main Pages workflow runs the repository's validation chain before deployment. Important gates include localization generation, starter/held-out eval reproducibility, model-run input isolation, skill portability, HTML/canonical/link/crawl checks, worksheets, schemas, toolkit publication/audit, content freshness, semantic-review blinding, frozen-context semantic model execution, optimized asset budgets, privacy consistency, legacy-host boundaries, website/mobile locale boundaries, search-distribution observability, licensing provenance, mobile release-history separation, and project-state consistency.

Useful targeted checks:

```bash
python3 scripts/check_practice_system.py
python3 scripts/check_semantic_review_pipeline.py
python3 scripts/check_practice_semantic_model_runner.py
python3 scripts/check_content_review.py
python3 scripts/check_toolkit_audit.py
python3 scripts/check_localization.py
python3 scripts/build_localized_pages.py --check
python3 scripts/check_asset_budget.py
python3 scripts/check_privacy_consistency.py
python3 scripts/check_mobile_locale_boundary.py
python3 scripts/check_legacy_boundary.py
python3 scripts/check_search_distribution.py
python3 scripts/check_license_boundaries.py
python3 scripts/check_mobile_release_history.py
python3 scripts/check_project_state.py
python3 scripts/check_site.py
python3 scripts/check_crawl_graph.py
python3 scripts/check_schemas.py
```

## Local preview

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173/`.

## Contribution rule of thumb

Public reflection content is written for people first; machine-readable forms preserve the same meaning and publication status. Do not turn raw toolkit presence into recommendation status, do not machine-publish unreviewed translations, do not infer app releases from repository activity, and do not describe a CI fixture or deterministic router as a hosted-model result.

See `CONTRIBUTING.md` for the review workflow.
