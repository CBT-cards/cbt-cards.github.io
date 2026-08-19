# CBT Cards website

Official static website and public reflection resource for CBT Cards.

CBT Cards began as a mobile app and is evolving into an open public library that can be used directly by people and consumed by AI assistants through ordinary web pages, JSON/JSONL data, versioned schemas, review metadata, portable agent instructions, and inspectable evaluation data.

The deployed site remains intentionally dependency-free: plain HTML, CSS, text, JSON, JSONL, and product-owned assets publish directly to GitHub Pages. There is no JavaScript application bundle or runtime service required to render public content. Small Python scripts are used only for validation, deterministic generation, reproducible baseline evaluation, and post-generation model-run scoring before deployment.

## Public structure

Public reflection library:

- `/` — project overview and entry points for people and AI assistants
- `/learn/` — plain-language learning library
- `/worksheets/` — printable browser-local worksheets
- `/toolkit/` — public toolkit and dataset entry point
- `/languages/` — human-readable language, translation-review, and publication status
- `/research/` — starter and held-out agent evals, reproducible baselines, model-run protocol, and methodology notes
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

## Public agent evaluation research

CBT Cards publishes an inspectable evaluation surface for assistants and integrations:

- `/research/` — methodology, starter/held-out results, model-run protocol, and limitations
- `/data/agent-evals.jsonl` — 24 hand-authored starter cases across retrieval, learning, worksheets, localization, publication boundaries, privacy, and safety
- `/data/agent-evals-challenge.jsonl` — 12 separately authored paraphrase/adversarial challenge cases across the same seven categories
- `/schemas/agent-eval-case-v1.schema.json` — one evaluation-case contract shared by starter and challenge cases
- `/data/agent-eval-runs.jsonl` — reproducible deterministic starter runs
- `/data/agent-eval-challenge-runs.jsonl` — reproducible deterministic challenge runs
- `/schemas/agent-eval-run-v1.schema.json` and `/schemas/agent-eval-challenge-run-v1.schema.json` — starter/challenge deterministic run contracts
- `scripts/check_evals.py` and `scripts/check_evals_challenge.py` — semantic consistency checks against live catalog/review/localization state
- `scripts/run_eval_baselines.py` and `scripts/run_eval_challenge.py` — deterministic non-model runners and exact-output verifiers

Every deterministic run pins the SHA-256 of the exact evaluation dataset bytes used. CI regenerates the starter and challenge baseline files and requires the committed run datasets to match exactly.

The starter baselines are reference points, not model-quality claims:

- `null-route-v1` is an intentionally weak starter floor: 1/24 correct routes, 0/19 expected target selections, 0/4 locale behaviors, and 1/7 boundary routes.
- `deterministic-contract-router-v1` is a small rule-based contract/harness baseline that reads only `user_message`. On the friendly starter set it reaches 24/24 routes, 19/19 targets, 4/4 locale behaviors, and 7/7 boundary routes.

The separate held-out challenge demonstrates why the perfect starter score should not be generalized. Without changing the router after challenge authoring, `deterministic-contract-router-v1` drops to 1/12 challenge routes, 0/10 target selections, 0/1 locale behaviors, and 1/3 boundary routes. The challenge dataset SHA-256 is `f20bbc8562315de235fe6b935b17be8eeaa41d604b222c91904618658b2c0407`.

If a router, prompt, model, or adapter is tuned on those 12 challenge cases, that challenge generation is no longer held out for that system. A later generalization claim requires a new untouched challenge generation.

### Real model-run protocol

The repository defines a two-stage protocol for recording actual ChatGPT/API/OpenClaw/Hermes/other assistant runs without giving benchmark answers to the model during generation:

- `/research/MODEL_RUN_PROTOCOL.md` — execution, provenance, held-out, and publication rules
- `/research/model-run-prompt-v1.txt` — fixed generation instruction
- `/schemas/agent-model-response-v1.schema.json` — one captured model response envelope
- `/schemas/agent-model-run-v1.schema.json` — one scored real-model run record
- `scripts/evaluate_model_run.py` — deterministic post-generation route/target/locale/boundary scorer
- `scripts/check_model_run_protocol.py` — CI contract/self-test using a synthetic fixture, not a model result

Generation and scoring are separate. The generation stage may expose `user_message`, the normal public CBT Cards sources, and normal runtime/system instructions being evaluated. It must not expose benchmark-only fields such as `expected_route`, expected IDs, checks, prohibited claims, rationale, or tags. Only after responses are captured does the deterministic evaluator read expected fields.

A published model run must record provider, model, exposed version/snapshot when available, runtime, execution timestamp, prompt URL/hash, evaluation dataset URL/hash, evaluator identity/version, raw answer text and answer hashes, plus per-case routing results. Do not invent provider snapshots or runtime settings that were not observable.

The v1 deterministic evaluator scores route, exact target IDs, locale behavior, and boundary routing. It explicitly does not automatically score empathy, prose quality, factual completeness, clinical suitability, `expected_checks`, or prohibited-claim compliance. Those require a separately declared semantic review method.

No LLM or hosted-assistant score is currently published. The CI fixture verifies plumbing only and must never be relabeled as a model result.

## Citation and archival provenance

- `/CITATION.cff` — repository-level Citation File Format 1.2.0 metadata

CBT Cards is currently described there as a dataset with MetalHatsCats as the authoring entity. No DOI or project-wide semantic version is claimed. Add a DOI only after an archival service actually assigns one to a release, and record any future project-wide version deliberately rather than inferring one from website, data, app, or skill versions.

## Portable agent skill

Skill v1.7.0 is the first CBT Cards release deliberately restricted to the portable Agent Skills frontmatter field set. The skill keeps version information in string-valued `metadata.version` instead of a custom top-level `version` field, and runtime-specific installation details live in a separate document rather than in runtime-specific frontmatter extensions.

Three v1.7.0 paths deliberately contain identical skill content:

- `/agents/cbt-cards/SKILL.md` — mutable latest alias
- `/agents/cbt-cards/v1.7.0/SKILL.md` — backward-compatible immutable URL used by the CBT Cards manifest and existing consumers
- `/agents/cbt-cards/v1.7.0/cbt-cards/SKILL.md` — strict portable immutable distribution whose immediate parent directory matches `name: cbt-cards`

Installation and version-pinning notes are in `/agents/cbt-cards/INSTALL.md`, including examples for OpenClaw, Hermes Agent, and generic Agent Skills clients. `scripts/check_skill_portability.py` verifies the portable frontmatter profile, string-valued metadata, directory/name alignment, exact equality between all three current v1.7.0 copies, manifest/catalog discovery, and required installation notes.

Historical v1.1.0 through v1.6.0 skill files remain unchanged at their original URLs. They are release history, not silently rewritten to fit a newer portability profile.

## Agent, discovery, and machine-readable resources

- `/agents/` — integration guide for AI assistants and research tooling
- `/agents/cbt-cards/SKILL.md` — latest mutable skill alias, currently v1.7.0
- `/agents/cbt-cards/INSTALL.md` — OpenClaw, Hermes Agent, generic Agent Skills, and version-pinning notes
- `/agents/cbt-cards/manifest.json` — skill version manifest
- `/agents/cbt-cards/v1.1.0/SKILL.md` through `/v1.7.0/SKILL.md` — immutable compatibility URLs
- `/agents/cbt-cards/v1.7.0/cbt-cards/SKILL.md` — strict portable Agent Skills distribution for v1.7.0
- `/llms.txt` — compact public index
- `/llms-full.txt` — extended source-priority, localization, research, release, schema, worksheet, corpus, publication-status, and safety index
- `/data/catalog.json` — canonical public resource catalog with stable IDs and `schema_url` for CBT Cards-owned structured instances
- `/data/changelog.json` — scoped website/public-data/agent release provenance
- `/data/knowledge.jsonl` — curated English source-language knowledge records
- `/data/locales.json` — language registry
- `/data/translations.jsonl` — localized content overlays with independent review/publication status
- `/data/agent-evals.jsonl` — starter public agent evaluation cases
- `/data/agent-evals-challenge.jsonl` — held-out paraphrase/adversarial challenge cases
- `/data/agent-eval-runs.jsonl` — reproducible starter deterministic baselines
- `/data/agent-eval-challenge-runs.jsonl` — reproducible held-out deterministic challenge baselines
- `/research/MODEL_RUN_PROTOCOL.md` — real-model execution/provenance protocol
- `/research/model-run-prompt-v1.txt` — fixed model-run prompt
- `/schemas/agent-model-response-v1.schema.json` and `/schemas/agent-model-run-v1.schema.json` — interface contracts for future real-model responses/runs
- `/data/worksheets.json` — structured form definitions
- `/data/toolkit-review.json` — CBT Cards-owned source-record publication status
- `/schemas/index.json` — public JSON Schema manifest
- `/CITATION.cff` — citation metadata
- `/feed.xml` — Atom discovery feed
- `/feed.json` — JSON Feed 1.1 discovery feed
- `/.well-known/security.txt` — standard public security contact

## Public data contracts

CBT Cards-owned structured formats have versioned JSON Schema draft 2020-12 contracts under `/schemas/`. `schemas/index.json` maps schemas with committed instances to those instances and may also list interface-only schemas before a real public instance exists.

Current committed-instance contracts cover:

- `data/catalog.json`
- `data/changelog.json`
- `data/worksheets.json`
- `data/toolkit-review.json`
- `data/toolkit-source.json`
- one record/line in `data/knowledge.jsonl`
- `data/locales.json`
- one record/line in `data/translations.jsonl`
- one record/line in `data/agent-evals.jsonl`
- one record/line in `data/agent-eval-runs.jsonl`
- one record/line in `data/agent-eval-challenge-runs.jsonl`
- `agents/cbt-cards/manifest.json`

Interface-only contracts currently include one model response and one real-model run. They intentionally have no fabricated instance merely to satisfy discovery.

The public catalog exposes `schema_url` for resources with committed schema-mapped instances. JSON Schema is the portable field-level contract; purpose-specific repository checks remain responsible for semantic invariants such as canonical target existence, sequential worksheet fields, privacy wording, translation source snapshots, eval source expectations, run reproducibility, held-out boundaries, model-run input isolation, skill portability, and exact review-overlay/catalog/JSONL alignment.

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

## Reproducing evaluation baselines

To regenerate the deterministic non-model starter baselines:

```bash
python3 scripts/run_eval_baselines.py
```

To verify starter and held-out deterministic run records:

```bash
python3 scripts/run_eval_baselines.py --check
python3 scripts/run_eval_challenge.py --check
```

Do not edit deterministic baseline records by hand. Change the eval cases or runner intentionally, regenerate, inspect the metric changes, and record the public change in the changelog.

For a real model run, first generate one response-envelope JSONL record per case according to `schemas/agent-model-response-v1.schema.json` without exposing benchmark expected fields. Then score the captured file, for example:

```bash
python3 scripts/evaluate_model_run.py \
  --dataset challenge \
  --responses /path/to/responses.jsonl \
  --provider <provider> \
  --model <model> \
  --runtime <runtime> \
  --executed 2026-08-18T12:00:00Z \
  --run-id model-run-example
```

Use an actual execution timestamp and real provider/model/runtime values. Do not publish the placeholder values above as a run.

## Quality checks

Run the same static checks used by GitHub Actions:

```bash
python3 scripts/check_localization.py
python3 scripts/build_localized_pages.py --check
python3 scripts/check_evals.py
python3 scripts/check_evals_challenge.py
python3 scripts/run_eval_baselines.py --check
python3 scripts/run_eval_challenge.py --check
python3 scripts/check_model_run_protocol.py
python3 scripts/check_citation.py
python3 scripts/check_skill_portability.py
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

The starter and challenge eval checkers verify stable case IDs, category coverage, expected catalog/raw-source IDs, publication-boundary expectations, privacy/safety routes, localization expectations, and the held-out challenge's distinct case IDs against current public state.

The deterministic run checks regenerate starter and held-out non-model runs from the current case datasets, pin exact SHA-256 values, recalculate route/target/locale/boundary metrics, and reject any checked-in result that differs from reproducible output.

The model-run protocol check verifies prompt input isolation, model response/run provenance contracts, and a synthetic full starter-set scorer fixture. The fixture uses benchmark expectations only to test the scorer after generation and is not a model result or benchmark score.

The citation checker verifies the repository's CFF 1.2.0 dataset metadata and rejects an invented DOI or project-wide semantic version.

The skill-portability checker validates the latest alias and strict portable distribution against the intended Agent Skills frontmatter profile, verifies string-valued metadata and directory/name alignment, requires the compatibility mirror and portable distribution to be byte-identical to the alias, and checks installation/catalog/manifest discovery.

The site checker verifies public HTML metadata, canonical uniqueness, JSON-LD parsing, internal links, crawler/IndexNow configuration, sitemap coverage/targets, resource catalog targets, curated JSONL alignment, toolkit source metadata, and agent skill/version targets.

The crawl-graph checker rejects indexed orphan pages and verifies that public pages remain reachable within the intended depth from the homepage.

The worksheet checker verifies worksheet IDs, catalog alignment, canonical and learning-resource targets, field IDs, sequential field order, source URLs, and explicit no-submit/no-send privacy behavior.

The discovery checker verifies Atom/JSON Feed parity, canonical feed targets, security metadata, and matching catalog entries.

The changelog checker verifies schema version, stable release IDs, chronological order, allowed scopes/change types, catalog resource alignment, canonical local targets, sitemap inclusion, and discovery-feed presence.

The toolkit-review checker verifies safe defaults for unlisted source records, published source-ID uniqueness, exact alignment between the review overlay, catalog toolkit cards, curated JSONL toolkit records and canonical pages, plus manifest-driven latest-skill alignment.

The schema checker verifies schema-manifest completeness, JSON Schema 2020-12 declarations, stable `$id` values, local committed-instance targets, interface-only schema discovery, catalog `schema_url` alignment where applicable, localization contracts, evaluation contracts, model-run contracts, and safety-critical constants.

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
- When adding or changing a CBT Cards-owned structured format, update its versioned schema, `schemas/index.json`, catalog discovery where a committed instance exists, and `scripts/check_schemas.py` as needed.
- Interface-only schemas may be published before a real instance exists; do not invent a model result or other fake instance merely to satisfy schema discovery.
- Treat schema changes that break existing consumers as a new schema-version URL rather than silently mutating the old contract.
- Record meaningful public website/data/agent changes in `/data/changelog.json` and `/changelog/` using a stable release ID and explicit `scope`.
- Never infer a mobile-app release from a website, dataset, translation, worksheet, feed, research, or agent-skill change. Mobile release entries require separately verified release metadata.
- Keep each curated JSONL knowledge record self-contained and aligned with its canonical page.
- Treat the `id` in `data/knowledge.jsonl` as the stable logical resource ID for localization.
- Store translations separately from source records and key them by stable `resource_id` plus locale.
- A `machine_draft` translation must remain `unreviewed`, `not_published`, without a canonical localized URL or review date.
- AI generation or AI self-review alone must never be recorded as `human_reviewed`.
- `public_html: true` permits reviewed records in a locale to be published; it does not require every translation in that locale to be published.
- A published localized record must use `https://cbt-cards.github.io/<locale>/resources/<resource_id>/` as its canonical URL.
- Keep `source_reviewed` aligned with the source record's current `reviewed` value; update and re-review translations when the source changes.
- Do not create records for a `planned` locale until it is deliberately promoted to `pilot`.
- Keep eval cases separate from recorded runs; do not change expected cases to make a particular runner look better.
- Deterministic baseline runners must use only their declared `input_fields` and must not inspect expected routes, resource IDs, rationales, tags, or checks as prediction inputs.
- Every recorded deterministic eval run must identify the exact eval dataset bytes through `eval_dataset_sha256` and preserve per-case results.
- Do not describe a deterministic routing baseline as an LLM benchmark or general model-quality score.
- If a system is tuned on the held-out challenge cases, stop describing that challenge generation as held out for that system and create a new untouched challenge for later generalization claims.
- For real model runs, generation must occur before benchmark expected fields are read by the scorer; record provider/model/runtime, prompt hash, dataset hash, execution timestamp, raw answers, and evaluator provenance.
- Do not claim the v1 deterministic model-run scorer evaluated prose quality, expected semantic checks, or prohibited claims; those require a separately declared semantic review.
- Never relabel the model-run CI fixture as a model result.
- Do not publish a DOI in `CITATION.cff` until an archival service has actually assigned it.
- Keep runtime-specific skill installation details outside portable `SKILL.md` frontmatter unless they are part of the common Agent Skills field set.
- Keep the v1.7.0 alias, compatibility immutable mirror, and strict `cbt-cards/SKILL.md` portable distribution identical; change them together through a deliberate skill release.
- A raw toolkit record must not become a standalone published resource unless its stable source ID is explicitly added to `data/toolkit-review.json` as `reviewed_for_publication` and `published`.
- Any raw toolkit source ID absent from the review overlay is `unreviewed` and `source_only` by default.
- Never describe `reviewed_for_publication` as clinical validation or efficacy evidence.
- Do not generate standalone protocol/health-guidance pages from raw corpus records unless the record has gone through explicit editorial and safety review and is added to the review overlay.
- Do not treat record titles as unique identifiers. Stable IDs are authoritative.
- When changing the agent skill, publish an immutable version, preserve a strict portable distribution, and update the manifest, catalog, llms indexes, changelog, and portability checks before moving the latest alias.

## Crawlers

`robots.txt` keeps public content crawlable and explicitly allows `OAI-SearchBot` for ChatGPT search discovery. The wildcard policy remains open for other compliant crawlers. Decisions about training-specific crawler access should be treated as a separate publisher policy rather than being silently coupled to search discoverability.

## Assets

Product-owned images and fonts are stored in `/assets/`. Prefer optimized web formats for new imagery and include explicit dimensions and meaningful alt text where an image conveys content.

Large legacy PNG/TTF payload optimization is tracked separately because binary asset conversion should preserve product artwork and licensing rather than be done through text-only repository mutations.

## Migration

See [MIGRATION.md](MIGRATION.md) for legacy URL mappings. Changes to legacy hosts are external dependencies and are outside this repository's modification scope.

## License

The original CBT Cards website content is licensed under [CC BY-NC-SA 4.0](LICENSE): attribution and the same license are required for sharing or adaptations, and commercial use is not permitted without prior written permission from MetalHatsCats. CBT Cards names and logos are not licensed for reuse.

The source CBT Toolkit v0.1.0 is also documented as CC BY-NC-SA 4.0. Any future change to the reuse license for machine-readable agent/RAG, eval, or translation data must be explicit and publisher-approved rather than inferred from technical accessibility.


## Asset performance policy

- Keep original PNG/TTF files only as source/fallback assets when needed; production body images should prefer WebP through `<picture>` and site fonts should use WOFF2.
- The main hero must not be lazy-loaded. Give it explicit dimensions and `fetchpriority="high"`; below-fold illustrations should use `loading="lazy"` and `decoding="async"`.
- Add responsive WebP widths close to the rendered mobile/desktop size instead of shipping a multi-megabyte source image to a small viewport.
- Use `assets/social-preview.jpg` (1200×630) for Open Graph previews rather than portrait product artwork.
- `scripts/check_asset_budget.py` is the regression gate for production asset references and byte budgets.
