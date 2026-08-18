# CBT Cards website

Official static website and public reflection resource for CBT Cards.

CBT Cards began as a mobile app and is evolving into an open public library that can be used directly by people and consumed by AI assistants through ordinary web pages, JSON/JSONL data, versioned schemas, review metadata, and portable agent instructions.

The deployed site remains intentionally dependency-free: plain HTML, CSS, text, JSON, JSONL, and product-owned assets publish directly to GitHub Pages. There is no JavaScript application bundle or runtime service required to render public content. Small Python scripts are used only for validation and deterministic generation before deployment.

## Public structure

Public reflection library:

- `/` — project overview and entry points for people and AI assistants
- `/learn/` — plain-language learning library
- `/worksheets/` — printable browser-local worksheets
- `/toolkit/` — public toolkit and dataset entry point
- `/languages/` — human-readable language, translation-review, and publication status
- `/about/` — project origin, direction, publisher, and editorial approach
- `/changelog/` — website/public-data/agent release history, separate from mobile-app releases

Original mobile-app documentation:

- `/features/` — app cards, guided tools, journal, check-ins, privacy controls, and backup
- `/how-it-works/` — app workflow
- `/faq/` — product questions
- `/privacy/`, `/terms/`, `/support/` — policy and support pages

Learning library:

- `/learn/cbt-thought-record/`
- `/learn/automatic-thoughts/`
- `/learn/thought-vs-fact/`
- `/learn/worry-time/`
- `/learn/activity-planning/`
- `/learn/cbt-journaling/`

Printable browser worksheets:

- `/worksheets/cbt-thought-record/` — seven-step thought record
- `/worksheets/worry-time/` — six-step worry-time worksheet
- `/worksheets/activity-planning/` — seven-step activity-planning worksheet
- `/data/worksheets.json` — ordered machine-readable worksheet definitions, source links, safety scope, and privacy behavior

Worksheet pages are static HTML forms with no submit action. Text typed into them is not sent to CBT Cards. It remains in the current browser page and disappears when the page is refreshed or closed unless the user independently prints or saves it. Do not confuse public worksheet behavior with storage inside the CBT Cards mobile app.

Public toolkit:

- `/toolkit/review-status/` — CBT Cards publication-review boundary for source records
- `/data/toolkit-review.json` — machine-readable review/publication overlay keyed by stable source record ID
- `/toolkit/cards/` — source index for 77 reflection-card records
- `/toolkit/metaphors/` — source index for 23 metaphor records
- `/toolkit/protocols/` — source index for 15 protocol records with an explicit review boundary
- `/toolkit/cards/.../` — curated standalone pages for selected reviewed card records
- `/data/toolkit-source.json` — pinned source-corpus version, commit, blob SHA, record counts, license, distribution URL, review-overlay pointer, and quality notes

The related source corpus is MetalHatsCats CBT Toolkit v0.1.0. The pinned source contains 115 English records: 77 cards, 23 metaphors, and 15 protocols. The source corpus has no CBT Cards-specific per-record publication or clinical-review metadata.

Any source record not explicitly listed in `data/toolkit-review.json` defaults to `review_status: unreviewed` and `publication_status: source_only`. `reviewed_for_publication` means editorial and safety review for a standalone CBT Cards website page. It does not mean clinical validation, evidence of efficacy, diagnosis, or suitability for an individual.

## Canonical knowledge and localization model

`data/knowledge.jsonl` is the current curated source-language knowledge dataset. Each line is self-contained and uses a stable `id` that remains authoritative across pages, formats, integrations, and translations. English (`en`) is currently the source locale.

Localization is an overlay rather than a second independent content tree:

- `/languages/` — human-readable current status and publication rules
- `/data/locales.json` — locale registry and source/pilot/planned status
- `/data/translations.jsonl` — translation records keyed by `resource_id` + `locale`
- `/schemas/locales-v1.schema.json` — locale registry contract
- `/schemas/translation-record-v1.schema.json` — one translation-record contract
- `LOCALIZATION.md` — review and publication workflow
- `scripts/build_localized_pages.py` — deterministic generator for language hubs, published localized resource pages, and localized sitemap entries

Current locale state:

- `en` — source locale; machine-readable and public HTML
- `ru` — pilot locale; all 12 records in the current curated knowledge set have machine-readable drafts, but none is human-reviewed or published
- `de` — planned; no translation records exist yet

The Russian records are deliberately marked `translation_status: machine_draft`, `review_status: unreviewed`, and `publication_status: not_published`. They are development data, not official published CBT Cards translations, and they do not have canonical localized pages.

A translation becomes official published CBT Cards content only after separate human language/editorial review and an explicit published status with a canonical CBT Cards URL. `source_reviewed` records the review date of the source-language knowledge record used to make the translation. CI rejects a translation when that value no longer matches the current source record, making stale localization visible rather than silently inconsistent.

`public_html` is a locale-level capability switch, not a claim that every record in a locale is published. A locale may gradually publish reviewed records while other records remain machine drafts. Only records explicitly marked `human_reviewed`, `reviewed_for_publication`, and `published` are rendered as localized public resource pages.

Generated localized pages use the canonical pattern `/<locale>/resources/<resource_id>/`. The generator also maintains locale hubs and the generated localization block in `sitemap.xml`. `/languages/` is always generated from the locale and translation data, so human-facing counts cannot silently drift from the machine-readable state.

## Agent, discovery, and machine-readable resources

- `/agents/` — integration guide for AI assistants and research tooling
- `/agents/cbt-cards/SKILL.md` — latest mutable skill alias, currently v1.6.0
- `/agents/cbt-cards/manifest.json` — skill version manifest
- `/agents/cbt-cards/v1.1.0/SKILL.md` through `/v1.6.0/SKILL.md` — immutable skill versions
- `/llms.txt` — compact public index
- `/llms-full.txt` — extended source-priority, localization, release, schema, worksheet, corpus, publication-status, and safety index
- `/data/catalog.json` — canonical public resource catalog with stable IDs and `schema_url` for CBT Cards-owned structured formats
- `/data/changelog.json` — scoped website/public-data/agent release provenance
- `/data/knowledge.jsonl` — curated English source-language knowledge records
- `/data/locales.json` — language registry
- `/data/translations.jsonl` — localized content overlays with independent review/publication status
- `/data/worksheets.json` — structured form definitions
- `/data/toolkit-review.json` — CBT Cards-owned source-record publication status
- `/schemas/index.json` — public JSON Schema manifest
- `/feed.xml` — Atom discovery feed
- `/feed.json` — JSON Feed 1.1 discovery feed
- `/.well-known/security.txt` — standard public security contact

## Public data contracts

CBT Cards-owned structured formats have versioned JSON Schema draft 2020-12 contracts under `/schemas/`. `schemas/index.json` maps each schema to the public instance it describes.

Current contracts cover:

- `data/catalog.json`
- `data/changelog.json`
- `data/worksheets.json`
- `data/toolkit-review.json`
- `data/toolkit-source.json`
- one record/line in `data/knowledge.jsonl`
- `data/locales.json`
- one record/line in `data/translations.jsonl`
- `agents/cbt-cards/manifest.json`

The public catalog exposes `schema_url` for these resources. JSON Schema is the portable field-level contract; purpose-specific repository checks remain responsible for semantic invariants such as canonical target existence, sequential worksheet fields, privacy wording, translation source snapshots, and exact review-overlay/catalog/JSONL alignment.

## Local preview

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173/`.

## Localization generation

After changing locale status or a human-reviewed/published translation, regenerate the localized human surface:

```bash
python3 scripts/build_localized_pages.py --write
```

Do not hand-edit generated `/languages/`, `/<locale>/`, or `/<locale>/resources/.../` HTML. Edit `data/locales.json` or `data/translations.jsonl`, then regenerate.

The generator does not publish machine drafts. It renders localized resource pages only for records that are simultaneously `human_reviewed`, `reviewed_for_publication`, and `published`, and only when the locale has `public_html: true`.

See [LOCALIZATION.md](LOCALIZATION.md) for the human review checklist and state transitions.

## Quality checks

Run the same static checks used by GitHub Actions:

```bash
python3 scripts/check_localization.py
python3 scripts/build_localized_pages.py --check
python3 scripts/check_site.py
python3 scripts/check_crawl_graph.py
python3 scripts/check_worksheets.py
python3 scripts/check_discovery.py
python3 scripts/check_changelog.py
python3 scripts/check_toolkit_review.py
python3 scripts/check_schemas.py
```

The localization checker verifies the locale registry, stable knowledge IDs, translation `(resource_id, locale)` uniqueness, source-review snapshots, key-point structure, machine-draft publication boundaries, incremental locale rollout, and generated localized output.

The localized-page generator check verifies that `/languages/`, any enabled locale hubs, published localized resource pages, and the generated localization block in `sitemap.xml` exactly match source data. Stale generated localized pages fail validation.

The site checker verifies public HTML metadata, canonical uniqueness, JSON-LD parsing, internal links, crawler/IndexNow configuration, sitemap coverage/targets, resource catalog targets, curated JSONL alignment, toolkit source metadata, and agent skill/version targets.

The crawl-graph checker rejects indexed orphan pages and verifies that public pages remain reachable within the intended depth from the homepage.

The worksheet checker verifies worksheet IDs, catalog alignment, canonical and learning-resource targets, field IDs, sequential field order, source URLs, and explicit no-submit/no-send privacy behavior.

The discovery checker verifies Atom/JSON Feed parity, canonical feed targets, security metadata, and matching catalog entries.

The changelog checker verifies schema version, stable release IDs, chronological order, allowed scopes/change types, catalog resource alignment, canonical local targets, sitemap inclusion, and discovery-feed presence.

The toolkit-review checker verifies safe defaults for unlisted source records, published source-ID uniqueness, exact alignment between the review overlay, catalog toolkit cards, curated JSONL toolkit records and canonical pages, plus manifest-driven latest-skill alignment.

The schema checker verifies schema-manifest completeness, JSON Schema 2020-12 declarations, stable `$id` values, local instance/schema targets, catalog `schema_url` discovery, localization contracts, and safety-critical constants.

## Deployment and discovery

`.github/workflows/deploy-pages.yml` publishes `main` to GitHub Pages after the quality jobs pass. After successful push deployments, a non-blocking IndexNow job submits changed/deleted public HTML URLs rather than repeatedly submitting the whole sitemap.

In repository settings use **Pages → Build and deployment → Source → GitHub Actions**.

The repository must remain `CBT-cards/cbt-cards.github.io` to serve the user-site root at `https://cbt-cards.github.io/` without a base-path prefix.

## Content and data rules

- Write public reflection content for people first; machine-readable representations should preserve the same meaning rather than create a separate editorial universe.
- Keep product feature, privacy, support, and data-handling claims consistent with the current application source and store metadata.
- Use the privacy policy as the canonical public source for mobile-app data-handling behavior.
- Learning pages must distinguish general CBT concepts from the way CBT Cards implements a reflection tool.
- Health-adjacent learning content should link to authoritative sources and record a review date.
- Worksheet prompts are educational form fields, not clinical assessments or validated rating scales.
- Public worksheet pages must remain static/no-submit unless the privacy documentation and product architecture are deliberately changed first.
- Do not claim that CBT Cards diagnoses, treats, cures, or prevents a condition. It is a general wellness and self-reflection resource.
- Keep internal links root-relative so GitHub Pages serves them correctly.
- When adding or removing an indexed non-generated page, update `sitemap.xml`, `llms.txt`, `llms-full.txt`, `data/catalog.json`, and the relevant machine-readable dataset.
- Generated localized pages and their sitemap entries must be changed through locale/translation data and `scripts/build_localized_pages.py`, not by hand.
- When adding or changing a CBT Cards-owned structured format, update its versioned schema, `schemas/index.json`, the catalog `schema_url`, and `scripts/check_schemas.py` as needed.
- Treat schema changes that break existing consumers as a new schema-version URL rather than silently mutating the old contract.
- Record meaningful public website/data/agent changes in `/data/changelog.json` and `/changelog/` using a stable release ID and explicit `scope`.
- Never infer a mobile-app release from a website, dataset, translation, worksheet, feed, or agent-skill change. Mobile release entries require separately verified release metadata.
- Keep each curated JSONL knowledge record self-contained and aligned with its canonical page.
- Treat the `id` in `data/knowledge.jsonl` as the stable logical resource ID for localization.
- Store translations separately from source records and key them by stable `resource_id` plus locale.
- A `machine_draft` translation must remain `unreviewed`, `not_published`, without a canonical localized URL or review date.
- AI generation or AI self-review alone must never be recorded as `human_reviewed`.
- `public_html: true` permits reviewed records in a locale to be published; it does not require every translation in that locale to be published.
- A published localized record must use `https://cbt-cards.github.io/<locale>/resources/<resource_id>/` as its canonical URL.
- Keep `source_reviewed` aligned with the source record's current `reviewed` value; update and re-review translations when the source changes.
- Do not create records for a `planned` locale until it is deliberately promoted to `pilot`.
- A raw toolkit record must not become a standalone published resource unless its stable source ID is explicitly added to `data/toolkit-review.json` as `reviewed_for_publication` and `published`.
- Any raw toolkit source ID absent from the review overlay is `unreviewed` and `source_only` by default.
- Never describe `reviewed_for_publication` as clinical validation or efficacy evidence.
- Do not generate standalone protocol/health-guidance pages from raw corpus records unless the record has gone through explicit editorial and safety review and is added to the review overlay.
- Do not treat record titles as unique identifiers. Stable IDs are authoritative.
- When changing the agent skill, publish an immutable version and update the manifest, catalog, llms indexes, and changelog before moving the latest alias.

## Crawlers

`robots.txt` keeps public content crawlable and explicitly allows `OAI-SearchBot` for ChatGPT search discovery. The wildcard policy remains open for other compliant crawlers. Decisions about training-specific crawler access should be treated as a separate publisher policy rather than being silently coupled to search discoverability.

## Assets

Product-owned images and fonts are stored in `/assets/`. Prefer optimized web formats for new imagery and include explicit dimensions and meaningful alt text where an image conveys content.

Large legacy PNG/TTF payload optimization is tracked separately because binary asset conversion should preserve product artwork and licensing rather than be done through text-only repository mutations.

## Migration

See [MIGRATION.md](MIGRATION.md) for legacy URL mappings. Changes to legacy hosts are external dependencies and are outside this repository's modification scope.

## License

The original CBT Cards website content is licensed under [CC BY-NC-SA 4.0](LICENSE): attribution and the same license are required for sharing or adaptations, and commercial use is not permitted without prior written permission from MetalHatsCats. CBT Cards names and logos are not licensed for reuse.

The source CBT Toolkit v0.1.0 is also documented as CC BY-NC-SA 4.0. Any future change to the reuse license for machine-readable agent/RAG or translation data must be explicit and publisher-approved rather than inferred from technical accessibility.
