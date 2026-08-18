# CBT Cards website

Official static website and public knowledge resource for CBT Cards.

The site is intentionally dependency-free: plain HTML, CSS, text, JSON, and product-owned assets deploy directly to GitHub Pages. There is no JavaScript application bundle or build step required to render public content.

## Public structure

Core product documentation:

- `/` — product overview and store links
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

Agent and machine-readable resources:

- `/agents/` — integration guide
- `/agents/cbt-cards/SKILL.md` — latest mutable skill alias
- `/agents/cbt-cards/manifest.json` — skill version manifest
- `/agents/cbt-cards/v1.1.0/SKILL.md` — immutable skill version
- `/llms.txt` — compact public index
- `/llms-full.txt` — extended source-priority and safety index
- `/data/catalog.json` — canonical public resource catalog with stable IDs

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

The checker verifies public HTML metadata, one H1 per indexed page, canonical uniqueness, JSON-LD parsing, internal links, sitemap coverage, sitemap targets, and machine-readable catalog targets.

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
- When adding or removing an indexed page, update `sitemap.xml`, `llms.txt`, `llms-full.txt`, and `data/catalog.json` where relevant.
- When changing the agent skill, publish an immutable version and update `agents/cbt-cards/manifest.json` before moving the latest alias.

## Assets

Product-owned images and fonts are stored in `/assets/`. Prefer optimized web formats for new imagery and include explicit dimensions and meaningful alt text where an image conveys content.

## Migration

See [MIGRATION.md](MIGRATION.md) for legacy MetalHatsCats URL mappings. Redirect behavior must be verified externally because the redirects are implemented outside this repository.

## License

The original CBT Cards website content is licensed under [CC BY-NC-SA 4.0](LICENSE): attribution and the same license are required for sharing or adaptations, and commercial use is not permitted without prior written permission from MetalHatsCats. CBT Cards names and logos are not licensed for reuse.
