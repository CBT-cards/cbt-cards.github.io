# CBT Cards website

Official static website and public knowledge resource for CBT Cards.

The site is intentionally dependency-free: plain HTML, CSS, text, JSON, JSONL, and product-owned assets deploy directly to GitHub Pages. There is no JavaScript application bundle or build step required to render public content.

## Public structure

Core product documentation:

- `/` — product overview, public toolkit entry points, and store links
- `/features/` — cards, guided tools, structured journal, check-ins, privacy controls, and backup
- `/how-it-works/` — product workflow
- `/faq/` — product questions with matching FAQ structured data
- `/privacy/`, `/terms/`, `/support/` — policy and support pages
- `/about/` — publisher, provenance, and editorial approach

Learning library:

- `/learn/` — learning hub
- `/learn/cbt-thought-record/`
- `/learn/automatic-thoughts/`
- `/learn/thought-vs-fact/`
- `/learn/worry-time/`
- `/learn/activity-planning/`
- `/learn/cbt-journaling/`

Public toolkit:

- `/toolkit/` — human-readable dataset landing page with `Dataset` structured data
- `/toolkit/cards/` — source index for 77 reflection-card records
- `/toolkit/metaphors/` — source index for 23 metaphor records
- `/toolkit/protocols/` — source index for 15 protocol records with an explicit review boundary
- `/toolkit/cards/.../` — curated standalone pages for selected reviewed card records
- `/data/toolkit-source.json` — pinned source-corpus version, commit, blob SHA, record counts, license, distribution URL, and quality notes

The related source corpus is MetalHatsCats CBT Toolkit v0.1.0 from `metalhatscats/metalhatscats-datasets`. The current pinned source contains 115 English records: 77 cards, 23 metaphors, and 15 protocols. The source corpus has no per-record clinical-review metadata, so source presence alone is not publication approval.

Agent and machine-readable resources:

- `/agents/` — integration guide
- `/agents/cbt-cards/SKILL.md` — latest mutable skill alias
- `/agents/cbt-cards/manifest.json` — skill version manifest
- `/agents/cbt-cards/v1.1.0/SKILL.md` — immutable historical skill version
- `/agents/cbt-cards/v1.2.0/SKILL.md` — current immutable skill version with raw-corpus/curated-content rules
- `/llms.txt` — compact public index
- `/llms-full.txt` — extended source-priority, corpus, and safety index
- `/data/catalog.json` — canonical public resource catalog with stable IDs
- `/data/knowledge.jsonl` — RAG-friendly curated knowledge records for public learning resources and reviewed toolkit cards

## Local preview

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173/`.

## Quality checks

Run the same static checks used by GitHub Actions:

```bash
python3 scripts/check_site.py
```

The checker verifies public HTML metadata, one H1 per indexed page, canonical uniqueness, JSON-LD parsing, internal links, sitemap coverage/targets, resource catalog targets, curated JSONL alignment, toolkit source metadata, and agent skill/version targets.

## Deployment

`.github/workflows/deploy-pages.yml` publishes `main` to GitHub Pages. The deploy job depends on the static quality job.

In repository settings use **Pages → Build and deployment → Source → GitHub Actions**.

The repository must remain `CBT-cards/cbt-cards.github.io` to serve the user-site root at `https://cbt-cards.github.io/` without a base-path prefix.

## Content rules

- Keep product feature, privacy, support, and data-handling claims consistent with the current application source and store metadata.
- Use the privacy policy as the canonical public source for data-handling behavior.
- Learning pages must distinguish general CBT concepts from CBT Cards-specific implementation.
- Health-adjacent learning content should link to authoritative sources and record a review date.
- Do not claim that CBT Cards diagnoses, treats, cures, or prevents a condition. It is a general wellness and self-reflection product.
- Keep internal links root-relative so GitHub Pages serves them correctly.
- When adding or removing an indexed page, update `sitemap.xml`, `llms.txt`, `llms-full.txt`, `data/catalog.json`, and `data/knowledge.jsonl` where relevant.
- Keep each curated JSONL knowledge record self-contained and aligned with its canonical page. Reuse the same stable resource ID in the catalog and curated dataset.
- Keep raw toolkit source IDs separate from curated resource IDs. A curated card record also carries its original `source_record_id`.
- Do not generate standalone protocol/health-guidance pages from raw corpus records unless the record has gone through explicit editorial and safety review.
- Do not treat record titles as unique identifiers. The source corpus already contains repeated titles; stable IDs are authoritative.
- When changing the agent skill, publish an immutable version and update `agents/cbt-cards/manifest.json`, `data/catalog.json`, and llms indexes before moving the latest alias.

## Crawlers

`robots.txt` keeps public content crawlable and explicitly allows `OAI-SearchBot` for ChatGPT search discovery. The wildcard policy remains open for other compliant crawlers. Decisions about training-specific crawler access should be treated as a separate publisher policy rather than being silently coupled to search discoverability.

## Assets

Product-owned images and fonts are stored in `/assets/`. Prefer optimized web formats for new imagery and include explicit dimensions and meaningful alt text where an image conveys content.

Large legacy PNG/TTF payload optimization is tracked separately because binary asset conversion should preserve product artwork and licensing rather than be done through text-only repository mutations.

## Migration

See [MIGRATION.md](MIGRATION.md) for legacy MetalHatsCats URL mappings. Redirect behavior must be verified externally because the redirects are implemented outside this repository.

## License

The original CBT Cards website content is licensed under [CC BY-NC-SA 4.0](LICENSE): attribution and the same license are required for sharing or adaptations, and commercial use is not permitted without prior written permission from MetalHatsCats. CBT Cards names and logos are not licensed for reuse.

The source CBT Toolkit v0.1.0 is also documented as CC BY-NC-SA 4.0. Any future change to the reuse license for machine-readable agent/RAG data must be explicit and publisher-approved rather than inferred from technical accessibility.
