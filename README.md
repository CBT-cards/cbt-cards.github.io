# CBT Cards website

Official static website and public knowledge resource for CBT Cards.

The site is intentionally dependency-free: plain HTML, CSS, text, JSON, JSONL, and product-owned assets deploy directly to GitHub Pages.

## Public structure

Core documentation:

- `/` — product overview and public-resource entry points
- `/features/`, `/how-it-works/`, `/faq/`
- `/privacy/`, `/terms/`, `/support/`
- `/about/` — publisher and provenance
- `/about/editorial-review/` — editorial review/freshness policy
- `/about/localization/` — website locale publication policy
- `/changelog/` — website/public-data release history

Knowledge and tools:

- `/learn/` — sourced learning library
- `/worksheets/` — static browser-local printable worksheets
- `/toolkit/` — curated public toolkit and source-corpus provenance
- `/toolkit/review-status/` — raw-source vs published-resource boundary

## Website localization

`data/locales.json` is the canonical source of truth for **website** locales. It currently records English (`en`) as the only published locale, served at the root URL.

The locale registry does not assert Android or iOS language support. Mobile-app language claims require separate verification from the application/build or current store metadata.

Before a second web locale ships:

- use stable locale URLs and self-canonical pages;
- add reciprocal `hreflang` and `x-default` where appropriate;
- update sitemap, catalog, agent indexes, navigation, and locale discovery together;
- preserve stable resource identity and provenance;
- implement reciprocal locale validation in CI;
- require human publication review for health-adjacent translations;
- use the correct document direction and layout review for RTL locales.

Machine translation may assist drafting, but is not sufficient review for health-adjacent public content.

## Editorial review freshness

`data/content-review.json` covers all catalog resources with type `learning`, `worksheet`, or `toolkit-card`. The project target is review at least every 365 days. This is an editorial-maintenance policy, not a clinical standard.

The deploy gate derives `next_review_due` from `last_reviewed + target_interval_days` and blocks overdue covered resources. Editorial review is not clinical validation, efficacy evidence, diagnosis, or individualized treatment review.

## Toolkit publication boundary

`data/toolkit-review.json` separates the related raw source corpus from CBT Cards-published standalone pages. Any unlisted source record defaults to `unreviewed` and `source_only`. `reviewed_for_publication` means editorial and safety review for public web use, not clinical validation.

## Agent and machine-readable interfaces

- `/agents/` — integration guide
- `/agents/cbt-cards/SKILL.md` — latest mutable skill alias, currently v1.6.0
- `/agents/cbt-cards/manifest.json` — skill version manifest
- `/agents/cbt-cards/v1.1.0/SKILL.md` through `/v1.6.0/SKILL.md` — immutable versions
- `/llms.txt`, `/llms-full.txt`
- `/data/catalog.json` — canonical resource catalog
- `/data/changelog.json` — scoped release provenance
- `/data/content-review.json` — editorial freshness registry
- `/data/locales.json` — website locale registry
- `/data/knowledge.jsonl` — curated prose records
- `/data/worksheets.json` — worksheet definitions
- `/data/toolkit-review.json`, `/data/toolkit-source.json`
- `/schemas/index.json` — JSON Schema manifest
- `/feed.xml`, `/feed.json`
- `/.well-known/security.txt`

CBT Cards-owned structured formats use versioned JSON Schema draft 2020-12 contracts. Breaking contract changes should publish a new schema-version URL rather than silently changing an existing contract.

## Local preview

```bash
python3 -m http.server 4173
```

## Quality checks

Run the same static checks used by GitHub Actions:

```bash
python3 scripts/check_site.py
python3 scripts/check_crawl_graph.py
python3 scripts/check_content_review.py
python3 scripts/check_locales.py
python3 scripts/check_worksheets.py
python3 scripts/check_discovery.py
python3 scripts/check_changelog.py
python3 scripts/check_toolkit_review.py
python3 scripts/check_schemas.py
```

The checks cover metadata/canonicals/JSON-LD/internal links, sitemap crawl reachability, review freshness, locale language signals, worksheet privacy and structure, feed parity, changelog provenance, toolkit publication status, schema discovery, and agent skill-version consistency.

## Deployment and discovery

`.github/workflows/deploy-pages.yml` publishes `main` to GitHub Pages only after quality checks pass. Successful push deployments trigger a non-blocking IndexNow notification for changed/deleted public HTML URLs.

## Content and data rules

- Keep product, privacy, support, and data-handling claims consistent with verified current sources.
- Use the privacy policy as primary for mobile-app data handling.
- Do not claim diagnosis, treatment, cure, prevention, or clinical validation that the sources do not establish.
- Do not infer app languages from website locale metadata.
- Do not infer a mobile-app release from website/data/agent changes.
- Keep health-adjacent translations under human publication review.
- Keep public worksheets static/no-submit unless privacy documentation and architecture deliberately change.
- A raw toolkit record must not become a standalone published page without explicit review-overlay approval.
- Stable resource/source IDs are authoritative; titles are not guaranteed unique.
- When changing the agent skill, publish an immutable version, update manifest/catalog/llms indexes, and preserve older semantic validators as forward-compatible checks.

## License

Original CBT Cards website content is licensed under [CC BY-NC-SA 4.0](LICENSE). CBT Cards names and logos are not licensed for reuse. The related CBT Toolkit source corpus has separate documented provenance and licensing in `data/toolkit-source.json`.
