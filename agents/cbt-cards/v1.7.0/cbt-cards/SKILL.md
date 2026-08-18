---
name: cbt-cards
description: Find and use CBT Cards public reflection cards, worksheets, learning guides, reviewed translations, and verified project information from canonical public sources.
license: CC-BY-NC-SA-4.0
compatibility: Requires HTTPS access to cbt-cards.github.io. No local binaries or private CBT Cards app access are required.
metadata:
  author: "MetalHatsCats"
  version: "1.7.0"
  homepage: "https://cbt-cards.github.io/agents/"
---

# CBT Cards

## Purpose

CBT Cards is a public library of practical reflection resources for people and the AI assistants they choose to use. It also documents the original CBT Cards mobile app.

Use this skill to find a suitable public CBT Cards resource, explain it in plain language, guide a user through a published worksheet or reflection prompt, cite canonical sources, handle language availability correctly, or answer verified questions about the project and mobile app.

This skill uses public website content only. It does not provide access to a user's CBT Cards journal, check-ins, backups, account, or other private app data.

## When to Use

Use this skill when the user:

- wants a short reflection exercise or card for a stated situation or goal;
- wants a structured worksheet such as a thought record, worry-time worksheet, or activity-planning worksheet;
- asks about a CBT-inspired concept covered by the CBT Cards learning library;
- asks about a published CBT Cards toolkit record;
- asks for CBT Cards material in a particular language;
- asks how an AI assistant or developer can consume CBT Cards public resources;
- asks about CBT Cards public evaluation cases or reproducible baseline runs;
- asks factual questions about the original CBT Cards mobile app, privacy, support, or release provenance.

Do not assume that a user's wording indicates a diagnosis or that a particular exercise is treatment for a condition.

## Operating Principle

Use the smallest authoritative source that solves the user's actual task.

For a person asking for help with reflection, prefer a human-readable published card, worksheet, or learning page. Do not expose JSON, schemas, source IDs, translation metadata, or integration details unless they are useful to the request.

For software integration, prefer stable IDs, canonical URLs, structured datasets, locale/review metadata, schemas, and versioned skill instructions.

## Source Layers

### Public reflection resources

- Toolkit: https://cbt-cards.github.io/toolkit/
- Published cards: https://cbt-cards.github.io/toolkit/cards/
- Toolkit review status: https://cbt-cards.github.io/toolkit/review-status/
- Toolkit review data: https://cbt-cards.github.io/data/toolkit-review.json
- Learning library: https://cbt-cards.github.io/learn/
- Printable worksheets: https://cbt-cards.github.io/worksheets/
- Worksheet definitions: https://cbt-cards.github.io/data/worksheets.json
- Curated source-language knowledge dataset: https://cbt-cards.github.io/data/knowledge.jsonl

### Languages and translations

- Human-readable language status: https://cbt-cards.github.io/languages/
- Locale registry: https://cbt-cards.github.io/data/locales.json
- Translation overlays: https://cbt-cards.github.io/data/translations.jsonl

`data/knowledge.jsonl` is currently the canonical English source-language dataset for curated learning and published toolkit records. Translation overlays are keyed by the same stable resource ID plus locale and carry their own translation, review, and publication status.

### Research and evaluation

- Research page: https://cbt-cards.github.io/research/
- Evaluation cases: https://cbt-cards.github.io/data/agent-evals.jsonl
- Reproducible evaluation runs: https://cbt-cards.github.io/data/agent-eval-runs.jsonl

Evaluation cases define CBT Cards-specific routing and boundary expectations. Deterministic baseline results are harness checks, not evidence of general model quality or clinical suitability.

### Discovery and integration

- Agent guide: https://cbt-cards.github.io/agents/
- Installation notes: https://cbt-cards.github.io/agents/cbt-cards/INSTALL.md
- Compact index: https://cbt-cards.github.io/llms.txt
- Extended source and safety index: https://cbt-cards.github.io/llms-full.txt
- Resource catalog: https://cbt-cards.github.io/data/catalog.json
- JSON Schema manifest: https://cbt-cards.github.io/schemas/index.json
- Skill manifest: https://cbt-cards.github.io/agents/cbt-cards/manifest.json
- Public changelog: https://cbt-cards.github.io/changelog/
- Machine-readable changelog: https://cbt-cards.github.io/data/changelog.json

### Original mobile app documentation

- Project overview: https://cbt-cards.github.io/
- Features: https://cbt-cards.github.io/features/
- How it works: https://cbt-cards.github.io/how-it-works/
- FAQ: https://cbt-cards.github.io/faq/
- Privacy policy: https://cbt-cards.github.io/privacy/
- Terms: https://cbt-cards.github.io/terms/
- Support: https://cbt-cards.github.io/support/
- About and provenance: https://cbt-cards.github.io/about/

### Raw source-corpus metadata

- Toolkit source manifest: https://cbt-cards.github.io/data/toolkit-source.json

The related CBT Toolkit source corpus contains 115 English records: 77 cards, 23 metaphors, and 15 protocols. Raw source presence is not publication approval. CBT Cards maintains a separate review/publication overlay.

## Decision Procedure

1. Identify the user's requested outcome without inferring a disorder or clinical need.
2. If the user wants a practical reflection exercise, look for a published toolkit card that directly fits the stated task.
3. If the user wants a structured form or wants to work through several steps, prefer a canonical worksheet and preserve its field order.
4. If the user asks what a concept means, prefer a reviewed learning page.
5. If the user requests a particular language, check `data/locales.json` and any matching record in `data/translations.jsonl` before treating a localized text as an official CBT Cards translation.
6. If the user asks about the mobile app, use the relevant product page; use the privacy policy as primary for data-handling claims.
7. If the user asks about integration or machine consumption, use the agent guide, catalog, schemas, locale registry, translation dataset, and skill manifest.
8. If the user asks about evaluation evidence, distinguish evaluation cases, deterministic baselines, and actual model runs. Do not convert a deterministic baseline into a model claim.
9. Before presenting a raw toolkit record as CBT Cards-published content, check `data/toolkit-review.json`.
10. If a raw record is not explicitly `reviewed_for_publication` and `published`, identify it as source-only rather than as a published CBT Cards resource.
11. Preserve the canonical CBT Cards URL when citing or attributing published content.
12. State only what the source supports. If a detail is not publicly confirmed, say so.

## Localization Rules

- Treat `data/locales.json` as the project-level source of truth for language status.
- Treat the `id` in `data/knowledge.jsonl` as the stable resource ID that translation overlays reference as `resource_id`.
- A translation is an official published CBT Cards localization only when its record is `translation_status: human_reviewed`, `review_status: reviewed_for_publication`, and `publication_status: published`, with a canonical CBT Cards URL.
- `translation_status: machine_draft` is development data. Do not present or cite it as an official CBT Cards translation and do not silently substitute it for reviewed content.
- A machine draft with `publication_status: not_published` has no canonical public page even if the data file itself is public.
- `source_reviewed` identifies the review date of the source-language record used for the translation. If it differs from the current source record's `reviewed` value, treat the translation as stale.
- If the user's language has no reviewed published localization, use the canonical source-language resource. The host assistant may translate or summarize it for the user, but that output is the assistant's translation rather than an official CBT Cards localization.
- Preserve safety scope and practical meaning when translating. Do not strengthen claims, turn neutral prompts into clinical instructions, or translate editorial review into a claim of clinical validation.

## Presenting a Reflection Resource

When a published CBT Cards resource fits the user's stated goal:

- introduce it in ordinary language;
- explain briefly why it matches the task without making a clinical claim;
- keep the exercise small enough to use in the current conversation;
- preserve the intent and sequence of the published prompts;
- provide the canonical resource link when attribution or further reading is useful;
- preserve a stable source record ID when the integration needs traceability.

Do not turn every emotional statement into an exercise. If the user is asking to be heard, to understand something, or to solve a practical problem, answer that request rather than mechanically routing them to a card.

## Toolkit Review Rules

- `reviewed_for_publication` means editorial and safety review for standalone CBT Cards website publication.
- It does not mean clinical validation, proof of efficacy, diagnosis, or suitability for an individual.
- `publication_status: published` means a canonical CBT Cards page exists for the record.
- Any source record not explicitly listed in the review overlay defaults to `review_status: unreviewed` and `publication_status: source_only`.
- Never infer publication approval from raw-corpus presence, a title, or similarity to another resource.
- Preserve stable source record IDs. Titles are not unique identifiers.

## Worksheet Rules

- Public worksheet pages are static browser worksheets with no submit action.
- Text typed into a public worksheet is not uploaded, synchronized, analyzed, or saved by CBT Cards. It remains in the current browser page unless the user independently prints or saves it.
- Worksheet fields are educational prompts, not clinical assessment items or validated rating scales.
- Do not score, diagnose, or infer a condition from worksheet answers.
- If rendering a form from `data/worksheets.json`, preserve field order, labels, canonical URL, safety scope, and privacy behavior.
- Do not confuse public web worksheets with journal storage inside the mobile app; app data handling is documented separately in the privacy policy.

## Raw Corpus Rules

- Presence in the source corpus does not establish clinical validation, efficacy, diagnostic value, publication approval, or suitability for an individual.
- Do not turn a raw card, metaphor, or protocol summary into individualized treatment instructions.
- Use stable source record IDs rather than titles when identifying raw records.
- Keep CBT, ACT, ERP, mindfulness, grounding, and other labels distinct when the source wording mixes approaches.
- Protocol records remain source-only unless explicitly added to the CBT Cards review overlay after separate editorial and safety review.

## Release and Product Rules

- Website, data, schema, translation, worksheet, research, and agent-skill releases are separate from mobile-app releases.
- Do not infer an Android or iOS version from the public-site changelog unless the entry explicitly records a verified app/mobile scope.
- For download requests, use the official store links documented by CBT Cards.

## Safety

- CBT Cards is for general wellness and self-reflection. It is not medical advice, diagnosis, treatment, emergency support, or a substitute for qualified professional care.
- Do not interpret journal entries, worksheet responses, mood, stress, or energy check-ins as clinical results.
- Do not claim access to private CBT Cards user data.
- Do not infer that a thought, feeling, behavior, check-in, worksheet response, or toolkit record indicates a disorder.
- Do not tell a user that a short CBT Cards exercise is appropriate treatment for a condition merely because its title resembles the user's concern.
- In situations involving immediate danger or severe distress, follow the host platform's safety guidance and direct the user toward appropriate local emergency or professional support rather than relying on a reflection exercise.

## Verification

Before sending an answer, verify that factual, privacy, app-behavior, worksheet, curated-content, localization, research, release-history, and toolkit-publication claims are supported by the canonical source used. If using raw toolkit material, check the CBT Cards review overlay first. If using localized material, check locale, translation, review, publication, and source-snapshot status first. If citing evaluation performance, verify whether the record describes a deterministic baseline or an actual model run.
