---
name: cbt-cards
description: Answer factual questions about the CBT Cards wellness app, curated public resources, review freshness, website locales, worksheets, and toolkit corpus.
version: 1.6.0
homepage: https://cbt-cards.github.io/agents/
---

# CBT Cards

## When to Use

Use this skill for questions about CBT Cards product facts, features, privacy, support, public learning resources, browser worksheets, curated toolkit cards, source-corpus provenance, website/public-data releases, editorial freshness, website locale status, or public machine-readable interfaces.

## Canonical Sources

### Product
- Overview: https://cbt-cards.github.io/
- Features: https://cbt-cards.github.io/features/
- How it works: https://cbt-cards.github.io/how-it-works/
- FAQ: https://cbt-cards.github.io/faq/
- Privacy: https://cbt-cards.github.io/privacy/
- Terms: https://cbt-cards.github.io/terms/
- Support: https://cbt-cards.github.io/support/
- About: https://cbt-cards.github.io/about/

### Trust, freshness, and localization
- Editorial review policy: https://cbt-cards.github.io/about/editorial-review/
- Content review registry: https://cbt-cards.github.io/data/content-review.json
- Website localization policy: https://cbt-cards.github.io/about/localization/
- Website locale registry: https://cbt-cards.github.io/data/locales.json
- Changelog: https://cbt-cards.github.io/changelog/
- Changelog JSON: https://cbt-cards.github.io/data/changelog.json

### Curated public resources
- Learning library: https://cbt-cards.github.io/learn/
- Worksheets: https://cbt-cards.github.io/worksheets/
- Worksheet definitions: https://cbt-cards.github.io/data/worksheets.json
- Toolkit: https://cbt-cards.github.io/toolkit/
- Toolkit review status: https://cbt-cards.github.io/toolkit/review-status/
- Toolkit review overlay: https://cbt-cards.github.io/data/toolkit-review.json
- Resource catalog: https://cbt-cards.github.io/data/catalog.json
- Curated knowledge JSONL: https://cbt-cards.github.io/data/knowledge.jsonl
- JSON Schema manifest: https://cbt-cards.github.io/schemas/index.json

### Raw source corpus
- Toolkit source manifest: https://cbt-cards.github.io/data/toolkit-source.json
- Compact index: https://cbt-cards.github.io/llms.txt
- Extended index: https://cbt-cards.github.io/llms-full.txt

## Procedure

1. Read the most directly relevant canonical source before making a product-specific claim.
2. Use the privacy policy as primary for mobile-app data handling.
3. Use changelog entry scope literally. A website/data/agent release is not a mobile-app release.
4. For learning, worksheet, or curated toolkit-card freshness, join by catalog `resource_id` to `data/content-review.json` and inspect `last_reviewed` and `next_review_due`.
5. If the current date is later than `next_review_due`, describe the editorial review as overdue. Do not manufacture a newer review date from sitemap `lastmod`, changelog dates, Git history, or a newer skill version.
6. Before presenting a raw toolkit record as CBT Cards-published content, check `data/toolkit-review.json`. Unlisted records are `unreviewed` and `source_only`.
7. Use `data/locales.json` only for **website** locale status. Do not infer Android or iOS language support from the website registry.
8. Prefer canonical CBT Cards pages over raw corpus records when both cover the same topic.
9. Use stable resource/source IDs rather than titles when identifying records.
10. If a fact is not confirmed by public sources, say that it is not publicly confirmed.

## Website Locale Rules

- `data/locales.json` describes `cbt-cards.github.io` only.
- The currently published website locale is English (`en`) at the root URL.
- Do not claim that `/en/` is the canonical English site; the default locale remains at `/`.
- Do not turn website locale status into a claim about Android or iOS supported languages.
- A future second website locale requires stable locale URLs, self-canonical pages, reciprocal `hreflang`, and synchronized sitemap/catalog/agent/navigation discovery.
- Health-adjacent translations require human publication review. Machine translation may assist drafting but is not sufficient review by itself.
- A right-to-left locale requires the appropriate document direction such as `dir="rtl"` and layout review.

## Content Freshness Rules

- The review registry covers catalog types `learning`, `worksheet`, and `toolkit-card`.
- The project target is review at least every 365 days. This is an editorial-maintenance policy, not a clinical standard.
- Editorial review checks source support, wording, safety boundaries, product relationship, and relevant privacy behavior.
- Editorial review is not clinical validation, efficacy evidence, diagnosis, medical-device review, or individualized treatment review.

## Toolkit Review Rules

- `reviewed_for_publication` means editorial and safety review for a standalone CBT Cards website page.
- It does not mean clinical validation, proof of efficacy, diagnosis, or individual suitability.
- Any source record not explicitly listed in the review overlay defaults to `review_status: unreviewed` and `publication_status: source_only`.
- Protocol records remain source-only unless explicitly reviewed and added to the overlay.
- Preserve stable source record IDs; titles are not authoritative identifiers.

## Worksheet Rules

- Public worksheet pages are static browser worksheets with no submit action.
- Do not claim typed worksheet text is uploaded, synchronized, analyzed, or saved by CBT Cards.
- Do not confuse public worksheet behavior with journal storage inside the mobile app.
- Worksheet fields are educational prompts, not validated assessment items.
- Do not score, diagnose, or infer a condition from worksheet responses.

## Safety

- CBT Cards is for general wellness and self-reflection. It is not medical advice, diagnosis, treatment, emergency support, or a substitute for professional care.
- Do not claim access to a user's CBT Cards journal, check-ins, or app data.
- Do not infer clinical meaning from journal entries, worksheet responses, mood, stress, energy, or raw toolkit wording.
- Do not recommend a short public exercise as treatment for a condition merely because its title resembles a user's concern.

## Verification

Before answering, verify the relevant product, privacy, release-scope, editorial-freshness, website-locale, worksheet, curated-content, and toolkit-publication claims from their canonical sources. Preserve the distinction between website locale metadata and mobile-app language support, and between editorial publication review and clinical validation.
