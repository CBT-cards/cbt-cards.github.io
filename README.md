# CBT Cards website

Official static website and public knowledge resource for CBT Cards.

The site is intentionally dependency-free: plain HTML, CSS, text, JSON, JSONL, and product-owned assets deploy directly to GitHub Pages. There is no JavaScript application bundle or build step required to render public content.

## Public structure

Core product documentation:

- `/` — product overview, learning/worksheet/toolkit entry points, and store links
- `/features/` — cards, guided tools, structured journal, check-ins, privacy controls, and backup
- `/how-it-works/` — product workflow
- `/faq/` — product questions with matching FAQ structured data
- `/privacy/`, `/terms/`, `/support/` — policy and support pages
- `/about/` — publisher, provenance, and editorial approach
- `/changelog/` — website/public-data release history, explicitly separate from mobile-app releases
- `/data/changelog.json` — machine-readable changelog with stable release IDs, dates, scopes, and changed resource IDs

Learning library:

- `/learn/` — learning hub
- `/learn/cbt-thought-record/`
- `/learn/automatic-thoughts/`
- `/learn/thought-vs-fact/`
- `/learn/worry-time/`
- `/learn/activity-planning/`
- `/learn/cbt-journaling/`

Printable browser worksheets:

- `/worksheets/` — worksheet hub
- `/worksheets/cbt-thought-record/` — seven-step thought record
- `/worksheets/worry-time/` — six-step worry-time worksheet
- `/worksheets/activity-planning/` — seven-step activity-planning worksheet
- `/data/worksheets.json` — ordered machine-readable worksheet definitions, source links, safety scope, and privacy behavior

Worksheet pages are static HTML forms with no submit action. Text typed into them is not sent to CBT Cards. It remains in the current browser page and disappears when the page is refreshed or closed unless the user independently prints or saves it. Do not confuse public worksheet behavior with storage inside the CBT Cards mobile app.

Public toolkit:

- `/toolkit/` — human-readable dataset landing page with `Dataset` structured data
- `/toolkit/review-status/` — CBT Cards publication-review boundary for source records
- `/data/toolkit-review.json` — machine-readable review/publication overlay keyed by stable source record ID
- `/toolkit/cards/` — source index for 77 reflection-card records
- `/toolkit/metaphors/` — source index for 23 metaphor records
- `/toolkit/protocols/` — source index for 15 protocol records with an explicit review boundary
- `/toolkit/cards/.../` — curated standalone pages for selected reviewed card records
- `/data/toolkit-source.json` — pinned source-corpus version, commit, blob SHA, record counts, license, distribution URL, review-overlay pointer, and quality notes

The related source corpus is MetalHatsCats CBT Toolkit v0.1.0. The pinned source contains 115 English records: 77 cards, 23 metaphors, and 15 protocols. The source corpus has no CBT Cards-specific per-record publication or clinical-review metadata.

Any source record not explicitly listed in `data/toolkit-review.json` defaults to `review_status: unreviewed` and `publication_status: source_only`. `reviewed_for_publication` means editorial and safety review for a standalone CBT Cards website page. It does not mean clinical validation, evidence of efficacy, diagnosis, or suitability for an individual.

Agent, discovery, and machine-readable resources:

- `/agents/` — integration guide
- `/agents/cbt-cards/SKILL.md` — latest mutable skill alias, currently v1.4.0
- `/agents/cbt-cards/manifest.json` — skill version manifest
- `/agents/cbt-cards/v1.1.0/SKILL.md` — immutable historical skill version
- `/agents/cbt-cards/v1.2.0/SKILL.md` — immutable version adding raw-corpus/curated-content rules
- `/agents/cbt-cards/v1.3.0/SKILL.md` — immutable version adding worksheet rendering/privacy rules
- `/agents/cbt-cards/v1.4.0/SKILL.md` — immutable version requiring toolkit review-overlay checks
- `/llms.txt` — compact public index
- `/llms-full.txt` — extended source-priority, release, worksheet, corpus, publication-status, and safety index
- `/data/catalog.json` — canonical public resource catalog with stable IDs
- `/data/changelog.json` — scoped website/public-data release provenance
- `/data/knowledge.jsonl` — RAG-friendly curated prose knowledge records for public learning resources and reviewed toolkit cards
- `/data/worksheets.json` — structured form definitions kept separate from prose knowledge records
- `/data/toolkit-review.json` — CBT Cards-owned source-record publication status
- `/feed.xml` — Atom discovery feed
- `/feed.json` — JSON Feed 1.1 discovery feed
- `/.well-known/security.txt` — standard public security contact

## Local preview

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173/`.

## Quality checks

Run the same static checks used by GitHub Actions:

```bash
python3 scripts/check_site.py
python3 scripts/check_worksheets.py
python3 scripts/check_discovery.py
python3 scripts/check_changelog.py
python3 scripts/check_toolkit_review.py
```

The site checker verifies public HTML metadata, one H1 per indexed page, canonical uniqueness, JSON-LD parsing, internal links, crawler/IndexNow configuration, sitemap coverage/targets, resource catalog targets, curated JSONL alignment, toolkit source metadata, and agent skill/version targets.

The worksheet checker verifies worksheet IDs, catalog alignment, canonical and learning-resource targets, field IDs, sequential field order, source URLs, and explicit no-submit/no-send privacy behavior.

The discovery checker verifies Atom/JSON Feed parity, canonical feed targets, security metadata, and matching catalog entries.

The changelog checker verifies schema version, stable release IDs, chronological order, allowed scopes/change types, catalog resource alignment, canonical local targets, sitemap inclusion, and discovery-feed presence.

The toolkit-review checker verifies safe defaults for unlisted source records, published source-ID uniqueness, exact alignment between the review overlay, catalog toolkit cards, curated JSONL toolkit records and canonical pages, plus latest-skill awareness of the overlay.

## Deployment and discovery

`.github/workflows/deploy-pages.yml` publishes `main` to GitHub Pages after the quality jobs pass. After successful push deployments, a non-blocking IndexNow job submits changed/deleted public HTML URLs rather than repeatedly submitting the whole sitemap.

In repository settings use **Pages → Build and deployment → Source → GitHub Actions**.

The repository must remain `CBT-cards/cbt-cards.github.io` to serve the user-site root at `https://cbt-cards.github.io/` without a base-path prefix.

## Content rules

- Keep product feature, privacy, support, and data-handling claims consistent with the current application source and store metadata.
- Use the privacy policy as the canonical public source for mobile-app data-handling behavior.
- Learning pages must distinguish general CBT concepts from CBT Cards-specific implementation.
- Health-adjacent learning content should link to authoritative sources and record a review date.
- Worksheet prompts are educational form fields, not clinical assessments or validated rating scales.
- Public worksheet pages must remain static/no-submit unless the privacy documentation and product architecture are deliberately changed first.
- Do not claim that CBT Cards diagnoses, treats, cures, or prevents a condition. It is a general wellness and self-reflection product.
- Keep internal links root-relative so GitHub Pages serves them correctly.
- When adding or removing an indexed page, update `sitemap.xml`, `llms.txt`, `llms-full.txt`, `data/catalog.json`, and the relevant machine-readable dataset.
- Record meaningful public website/data changes in `/data/changelog.json` and `/changelog/` using a stable release ID and explicit `scope`.
- Never infer a mobile-app release from a website, dataset, worksheet, feed, or agent-skill change. Mobile release entries require separately verified release metadata.
- Keep each curated JSONL knowledge record self-contained and aligned with its canonical page. Reuse the same stable resource ID in the catalog and curated dataset.
- Keep worksheet UI schemas in `data/worksheets.json`; do not duplicate form definitions into `knowledge.jsonl` unless the schema strategy changes intentionally.
- A raw toolkit record must not become a standalone published resource unless its stable source ID is explicitly added to `data/toolkit-review.json` as `reviewed_for_publication` and `published`.
- Any raw toolkit source ID absent from the review overlay is `unreviewed` and `source_only` by default.
- Never describe `reviewed_for_publication` as clinical validation or efficacy evidence.
- Keep raw toolkit source IDs separate from curated resource IDs. A curated card record also carries its original `source_record_id`.
- Do not generate standalone protocol/health-guidance pages from raw corpus records unless the record has gone through explicit editorial and safety review and is added to the review overlay.
- Do not treat record titles as unique identifiers. The source corpus already contains repeated titles; stable IDs are authoritative.
- When changing the agent skill, publish an immutable version and update `agents/cbt-cards/manifest.json`, `data/catalog.json`, and llms indexes before moving the latest alias.

## Crawlers

`robots.txt` keeps public content crawlable and explicitly allows `OAI-SearchBot` for ChatGPT search discovery. The wildcard policy remains open for other compliant crawlers. Decisions about training-specific crawler access should be treated as a separate publisher policy rather than being silently coupled to search discoverability.

## Assets

Product-owned images and fonts are stored in `/assets/`. Prefer optimized web formats for new imagery and include explicit dimensions and meaningful alt text where an image conveys content.

Large legacy PNG/TTF payload optimization is tracked separately because binary asset conversion should preserve product artwork and licensing rather than be done through text-only repository mutations.

## Migration

See [MIGRATION.md](MIGRATION.md) for legacy URL mappings. Changes to legacy hosts are external dependencies and are outside this repository's modification scope.

## License

The original CBT Cards website content is licensed under [CC BY-NC-SA 4.0](LICENSE): attribution and the same license are required for sharing or adaptations, and commercial use is not permitted without prior written permission from MetalHatsCats. CBT Cards names and logos are not licensed for reuse.

The source CBT Toolkit v0.1.0 is also documented as CC BY-NC-SA 4.0. Any future change to the reuse license for machine-readable agent/RAG data must be explicit and publisher-approved rather than inferred from technical accessibility.
