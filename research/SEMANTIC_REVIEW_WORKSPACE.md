# Blinded semantic review workspace

This document describes the human-review step after a real `full-41` practice-semantic model execution and the final publication-candidate checks that follow it.

## What the Actions artifact contains

A successful real run uploads one artifact containing:

- `practice-semantic-execution.json` — provider/model/runtime and frozen-input provenance;
- `practice-semantic-responses.jsonl` — captured model outputs before benchmark scoring;
- `practice-semantic-review-packet.json` — already-blinded reviewer packet;
- `practice-semantic-review-template.json` — empty review contract with provenance hashes;
- `practice-semantic-review-workspace.html` — offline browser UI generated from the blinded packet/template.

The HTML workspace is an ergonomics layer only. The JSON packet/template remain the authoritative review inputs.

## Review procedure

1. Download and unzip the full-run Actions artifact.
2. Open `practice-semantic-review-workspace.html` locally in a browser.
3. Enter a stable reviewer ID and review date.
4. Review each model answer without opening the benchmark shards or expected-answer fields.
5. Rate all ten dimensions independently for every case: `pass`, `fail`, `uncertain`, or `not_applicable`.
6. Use **Safety comment** for contextual safety concerns that should be visible in the final report. A `fail` or `uncertain` rating on `safety_exclusions` must have a non-empty safety comment before the result can become a publication candidate.
7. Use **Reviewer notes** for other rationale or ambiguity.
8. Export `practice-semantic-human-review.json`. Export is blocked while any case/dimension remains unrated.
9. Keep the original full-run artifact unchanged. The exported review file is a separate human judgment artifact.
10. Score only after review is complete:

```bash
python3 scripts/score_semantic_reviews.py \
  --responses practice-semantic-responses.jsonl \
  --packet practice-semantic-review-packet.json \
  --reviews practice-semantic-human-review.json \
  --output practice-semantic-review-report.json
```

## Publication-candidate gate

A scored result is not automatically publishable. Run the final integrity gate across the entire chain:

```bash
python3 scripts/check_practice_semantic_publication_candidate.py \
  --execution practice-semantic-execution.json \
  --responses practice-semantic-responses.jsonl \
  --packet practice-semantic-review-packet.json \
  --reviews practice-semantic-human-review.json \
  --report practice-semantic-review-report.json
```

The gate requires:

- all 41 captured responses;
- exactly one complete human review record per case;
- execution → response → packet → review → scored-report hashes to agree;
- the same reviewer provenance in the review and report;
- all ten semantic dimensions to have 41 explicit ratings;
- the safety-critical category subset to remain separate;
- human safety comments for `safety_exclusions` failures or uncertainty;
- explicit limitations preserving the distinction between benchmark results, human editorial judgment, and clinical validation.

The gate deliberately does **not** require a perfect score. A poor model result can be a valid publication candidate when it is complete, provenance-clean, honestly reported, and useful for diagnosing failures.

After the gate passes, render the deterministic human-readable summary:

```bash
python3 scripts/build_practice_semantic_publication_report.py \
  --execution practice-semantic-execution.json \
  --report practice-semantic-review-report.json \
  --output practice-semantic-model-result.md
```

The rendered summary includes provider/runtime/model settings, frozen hashes, contract metrics, the safety-critical subset, all human semantic-dimension counts, context-resource hashes, and limitations. It does not turn benchmark performance into a clinical claim.

## Blinding and privacy boundary

The generated HTML embeds only the already-blinded case surface plus review provenance hashes. It does not embed the benchmark answer key or hidden expected fields. It has no form submission, analytics, remote scripts, `fetch`, XHR, or beacon calls. Export uses a browser-local `Blob` download.

Do not open benchmark shards, expected outcomes, acceptable practice IDs, or required safety annotations while performing the blinded review. The scorer reads those benchmark annotations only after human review is finished.

## Interpretation boundary

A human benchmark review is an editorial/contextual judgment. It is not clinical validation, treatment evidence, an individualized safety assessment, or proof that a model is appropriate for every user or situation.
