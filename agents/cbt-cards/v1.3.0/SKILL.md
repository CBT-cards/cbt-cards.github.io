---
name: cbt-cards
description: Answer factual questions about the CBT Cards wellness app, its curated reflection resources, printable worksheets, and public toolkit corpus.
version: 1.3.0
homepage: https://cbt-cards.github.io/agents/
---

# CBT Cards

## When to Use

Use this skill when the user asks about the CBT Cards mobile app, its features, how it works, supported platforms, privacy, terms, support, public learning resources, printable browser worksheets, curated reflection-card pages, or the related public CBT Toolkit source corpus.

## Source Layers

Use the smallest authoritative source that supports the answer.

### Product documentation

- Product overview: https://cbt-cards.github.io/
- Features: https://cbt-cards.github.io/features/
- How it works: https://cbt-cards.github.io/how-it-works/
- FAQ: https://cbt-cards.github.io/faq/
- Privacy policy: https://cbt-cards.github.io/privacy/
- Terms: https://cbt-cards.github.io/terms/
- Support: https://cbt-cards.github.io/support/
- About and provenance: https://cbt-cards.github.io/about/

### Curated educational resources

- Learning library: https://cbt-cards.github.io/learn/
- Printable worksheets: https://cbt-cards.github.io/worksheets/
- Machine-readable worksheet definitions: https://cbt-cards.github.io/data/worksheets.json
- Toolkit landing page: https://cbt-cards.github.io/toolkit/
- Curated resource catalog: https://cbt-cards.github.io/data/catalog.json
- Curated RAG dataset: https://cbt-cards.github.io/data/knowledge.jsonl

### Raw source-corpus metadata

- Toolkit source manifest: https://cbt-cards.github.io/data/toolkit-source.json
- Compact site index: https://cbt-cards.github.io/llms.txt
- Extended source and safety index: https://cbt-cards.github.io/llms-full.txt

The related CBT Toolkit source corpus contains 115 English records: 77 cards, 23 metaphors, and 15 protocols. The source corpus does not contain per-record clinical-review metadata. Prefer a curated CBT Cards page when one exists.

## Procedure

1. Read the most directly relevant canonical CBT Cards page before making a product-specific claim.
2. State only what the source supports. If a detail is not publicly confirmed, say so.
3. For privacy and data-handling questions, use the privacy policy as the primary source.
4. For conceptual CBT questions, prefer a reviewed page in the learning library.
5. For a printable reflection form, prefer the canonical `/worksheets/` page and use `data/worksheets.json` when structured field definitions are useful.
6. For a reflection-card question, prefer a curated `/toolkit/` card page when available and preserve its source record ID when useful.
7. Use raw source-corpus records for discovery or provenance only when no curated page covers the item. Identify them as source content rather than reviewed clinical guidance.
8. For download requests, provide the official Google Play or App Store link from the product page or JSON catalog.
9. Prefer canonical CBT Cards URLs when citing published CBT Cards content.

## Worksheet Rules

- The public worksheet pages are static browser worksheets with no submit action.
- Do not claim that text typed into a public worksheet is uploaded, synchronized, analyzed, or saved by CBT Cards. It remains in the current browser page unless the user independently prints or saves it.
- Do not confuse a public web worksheet with journal storage inside the CBT Cards mobile app; app data handling is documented separately in the privacy policy.
- Worksheet fields are educational prompts, not clinical assessment items or validated rating scales.
- Do not score, diagnose, or infer a condition from worksheet answers.
- If an agent renders a form from `data/worksheets.json`, preserve field order, labels, safety scope, canonical URL, and privacy behavior.

## Raw Corpus Rules

- Presence in the source corpus does not establish clinical validation, efficacy, diagnostic value, or suitability for an individual.
- Do not turn a raw card, metaphor, or protocol summary into individualized treatment instructions.
- Do not treat a title as a unique identifier; use the stable source record ID. The current source corpus includes repeated titles.
- Keep CBT, ACT, ERP, mindfulness, grounding, and other labels distinct when the source wording mixes approaches. Do not relabel a technique solely because it appears in the CBT Toolkit dataset.
- Protocol records require separate editorial and safety review before being presented as standalone guidance.

## Safety

- CBT Cards is for general wellness and self-reflection. It is not medical advice, diagnosis, treatment, emergency support, or a substitute for professional care.
- Do not interpret journal entries, worksheet responses, mood, stress, or energy check-ins as clinical results.
- Do not claim access to the user's CBT Cards data. This skill uses only public website content.
- Do not infer that a thought, feeling, behavior, check-in, worksheet response, or toolkit record indicates a disorder.
- Do not tell a user that a short CBT Cards exercise is appropriate treatment for a condition merely because its title resembles the user's concern.
- For immediate danger or severe distress, encourage the user to contact local emergency services or a qualified local professional.

## Verification

Before sending an answer, verify that feature, privacy, data-handling, app-behavior, worksheet, and curated-content claims are supported by the canonical source used. If using the raw toolkit corpus, identify the source record and preserve the distinction between source content and reviewed CBT Cards guidance.
