---
name: cbt-cards
description: Find and use CBT Cards reviewed public reflection practices, worksheets, learning guides, language and review metadata, and verified project information from canonical public sources.
license: CC-BY-NC-SA-4.0
compatibility: Requires HTTPS access to cbt-cards.github.io. No local binaries or private CBT Cards app access are required.
metadata:
  author: "MetalHatsCats"
  version: "1.8.0"
  homepage: "https://cbt-cards.github.io/agents/"
---

# CBT Cards

## Skill Release

version: 1.8.0

The version is also recorded in `metadata.version`. The body label remains for backward compatibility while the frontmatter stays within the portable Agent Skills field set.

## Purpose

CBT Cards is a public library of practical reflection resources for people and the AI assistants they choose to use. It publishes a small CBT Cards-owned reviewed practice layer, curated learning pages and worksheets, a pinned source toolkit with separate publication and audit metadata, language status, evaluation data, and retrieval-ready public resources.

Use this skill to find a suitable published resource, explain it in plain language, guide a user through a small reviewed practice or worksheet, cite canonical sources, handle language and review status correctly, or answer verified questions about the project and the original mobile app.

This skill uses public website content only. It does not provide access to a user's CBT Cards journal, check-ins, backups, account, or other private app data.

## Source Priority

Use the smallest authoritative source that solves the task.

1. For a concrete reflection situation, start with the CBT Cards-owned reviewed practice system: https://cbt-cards.github.io/practice/ and https://cbt-cards.github.io/data/practice.json.
2. For a concept, prefer reviewed learning pages under https://cbt-cards.github.io/learn/.
3. For a structured blank form, prefer https://cbt-cards.github.io/worksheets/ and preserve the published field order.
4. For already curated source-toolkit content, use canonical published pages and verify https://cbt-cards.github.io/data/toolkit-review.json.
5. Treat the 115-record raw toolkit audit at https://cbt-cards.github.io/data/toolkit-audit.json as editorial triage metadata only. It is not permission to use or publish an unreviewed source record.
6. When freshness matters, check https://cbt-cards.github.io/data/content-review.json.
7. For language status, check https://cbt-cards.github.io/data/locales.json and https://cbt-cards.github.io/data/translations.jsonl.
8. For mobile-app behavior or privacy claims, use the official CBT Cards product pages, with https://cbt-cards.github.io/privacy/ primary for data-handling claims.

Do not infer a diagnosis from the user's wording.

## Reviewed Practice Routing

- Start from the user's plain-language situation, not a diagnostic label.
- Prefer one practice when fit is clear.
- Preserve `best_used_when`, `avoid_when`, safety scope, evidence limits, and canonical URL.
- Return `no_match` rather than inventing a practice when no reviewed fit exists.
- Genuine danger, required safety/professional/accessibility rules, and medical, legal, financial, or safeguarding decisions are outside practice routing.
- Do not reduce genuine protective boundaries, required checks, medication instructions, accessibility aids, workplace safety, or other real-world protections.
- Metaphors are memory aids, not evidence.

Practice system guide: https://cbt-cards.github.io/agents/cbt-cards/PRACTICE_SYSTEM.md

## Publication Review, Source Audit, and Freshness

### Publication review

`https://cbt-cards.github.io/data/toolkit-review.json` decides whether a raw source-corpus record has been explicitly reviewed for a standalone CBT Cards page.

- `reviewed_for_publication` is editorial and safety review for public web use.
- `publication_status: published` means a canonical CBT Cards page exists.
- Any source record not explicitly listed defaults to `unreviewed` and `source_only`.
- Publication review is not clinical validation, efficacy evidence, diagnosis, or individual suitability.

### Source-corpus audit

`https://cbt-cards.github.io/data/toolkit-audit.json` covers all 115 pinned source IDs and exposes editorial triage, framework buckets, quality flags, similarity groups, and a future review queue.

- Audit status is not publication approval.
- `candidate_for_editorial_review` means only that a record may be worth a future review.
- `do_not_promote_without_rework` means the raw wording or mechanism is not suitable for direct promotion.
- Every protocol requires a separate protocol-level evidence and safety review.
- Metaphor candidates are memory-aid candidates only.
- Never turn an audit candidate into CBT Cards guidance without the publication overlay.

### Content freshness

`https://cbt-cards.github.io/data/content-review.json` tracks freshness for already published learning pages, worksheets, curated toolkit cards, and CBT Cards-owned reviewed practices.

- Use stable IDs to join a resource to its freshness entry.
- `last_reviewed` and `next_review_due` are editorial-maintenance metadata.
- Do not infer a newer review from sitemap `lastmod`, a newer skill version, translation activity, or Git history.
- Freshness review is not clinical validation.

## Raw Corpus Rules

The pinned source corpus has 77 cards, 23 metaphors, and 15 protocols.

- Raw source presence is not publication approval.
- Stable source IDs are authoritative because titles are not unique.
- Keep CBT, ACT-adjacent, DBT-adjacent, generic wellness, metaphor, and protocol material distinct when the source mixes frameworks.
- Do not turn treatment-like raw wording such as ERP, exposure, thought stopping, or emotion exposure into generic individualized instructions.
- Protocol records remain source-only unless an explicit future protocol review and publication decision says otherwise.
- Prefer the smaller reviewed owned-practice layer over a semantically similar raw record.

## Learning and Worksheet Rules

For conceptual questions, use reviewed learning pages and state only what their cited sources support.

Public worksheets have no submit action, keep typed text in the current browser page unless the user independently prints or saves it, and are educational prompts rather than validated assessment instruments. Do not score them or use them to infer a diagnosis.

## Localization Rules

English is the canonical source locale for the current curated knowledge dataset. A translation is official published CBT Cards content only when it is `human_reviewed`, `reviewed_for_publication`, and `published`, with a canonical CBT Cards localized URL. `machine_draft` is development data. A host assistant may translate the canonical source for a user, but that output is the assistant's translation rather than an official CBT Cards localization.

## Research and Evaluation

Research: https://cbt-cards.github.io/research/

- Deterministic baseline scores are harness results, not evidence of model quality or clinical quality.
- Generation and scoring must remain separate for model evaluations.
- Benchmark-only expected fields must remain hidden during generation.
- Semantic safety appropriateness remains separate from exact routing metrics.
- A model judge must not be the sole authority for safety appropriateness.

## Integration and Discovery

- Compact index: https://cbt-cards.github.io/llms.txt
- Extended index: https://cbt-cards.github.io/llms-full.txt
- Resource catalog: https://cbt-cards.github.io/data/catalog.json
- Schema manifest: https://cbt-cards.github.io/schemas/index.json
- Curated knowledge: https://cbt-cards.github.io/data/knowledge.jsonl
- Practice RAG distribution: https://cbt-cards.github.io/data/practice-rag.ndjson
- Practice RAG manifest: https://cbt-cards.github.io/data/practice-rag-manifest.json
- Skill manifest: https://cbt-cards.github.io/agents/cbt-cards/manifest.json
- Changelog: https://cbt-cards.github.io/changelog/

For reproducible integrations, resolve the skill manifest and pin its immutable version URL.

## Mobile App Boundary

- Website, dataset, schema, translation, research, practice-system, or skill releases do not imply a mobile-app release.
- Do not infer current mobile language support from website localization status.
- Do not claim access to private mobile-app data through this public interface.
- For current privacy claims, use the published privacy policy rather than inferring behavior from public datasets.

## Safety

CBT Cards is for general wellness and self-reflection. It is not medical advice, diagnosis, treatment, emergency support, or a substitute for qualified professional care.

Do not infer a disorder from a thought, feeling, worksheet answer, or check-in; present editorial review as clinical validation; remove real safety measures or protective boundaries; turn a raw source record into individualized treatment instructions; present machine-draft translations as official published content; or substitute a reflection practice for immediate safety action or qualified professional decisions.

## Verification

Before answering: verify the canonical resource and stable ID; verify publication status for source-toolkit material; verify freshness when the claim depends on current editorial review; verify locale and translation publication status; preserve safety exclusions and evidence limits; distinguish deterministic evals from real-model results; and state uncertainty rather than filling public-data gaps with confident prose.
