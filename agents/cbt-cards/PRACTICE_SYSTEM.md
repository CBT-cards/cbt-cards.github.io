# CBT Cards practice system
Version: 1.0 · Updated: 2026-08-18

Use `https://cbt-cards.github.io/data/practice.json` as the canonical reviewed practice graph and `https://cbt-cards.github.io/data/practice-rag.ndjson` for retrieval.

1. Start from the user's plain-language situation; do not ask for a diagnosis.
2. Match a reviewed situation, then mechanism.
3. Select one practice when fit is clear; at most three for genuine ambiguity.
4. Preserve `avoid_when`, safety scope, review status, and evidence limits.
5. Metaphors are memory aids, never evidence.
6. Never route source-only/unreviewed toolkit records as published guidance.
7. For genuine danger, required safety behavior, professional instructions, or medical/legal/financial/safeguarding decisions, return `no_match` for the practice layer.
8. If nothing reviewed fits, return `no_match`; do not invent a CBT Cards practice.

Companions: semantic evals `https://cbt-cards.github.io/data/practice-semantic-evals.jsonl`, coverage `https://cbt-cards.github.io/data/practice-coverage.json`, RAG manifest `https://cbt-cards.github.io/data/practice-rag-manifest.json`, interoperability `https://cbt-cards.github.io/data/interoperability-fixtures.json`.
