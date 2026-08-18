# Semantic recommendation evaluation protocol v1.1

CBT Cards keeps semantic recommendation review separate from deterministic routing/contract scoring. The point is not to manufacture one flattering percentage. It is to make different failure modes visible.

## Dimensions

Report these independently: situation/mechanism fit, practice appropriateness, safety-exclusion preservation, no diagnosis/treatment overclaim, evidence fidelity, publication-boundary fidelity, micro-action fidelity, no-match behavior, locale/publication behavior, and canonical citation correctness.

The canonical dataset contains 41 separately authored situations across fit, ambiguity, genuine risk, required standards, publication boundaries, professional boundaries, no-match behavior, and progression.

## Frozen-context real-provider path

For the first publishable practice-semantic provider run, CBT Cards uses a separate frozen-context adapter: `scripts/run_practice_semantic_openai.py`. It does not enable web search. Every request receives only the case `user_message` plus the fixed semantic prompt, Agent Skill, and committed reviewed-practice context files.

The execution artifact records SHA-256 values for the semantic manifest and both case shards, the fixed prompt, the current Agent Skill, and each frozen context resource (`practice.json`, `practice-recommendations.json`, `practice-evidence.json`, and `practice-rag.ndjson`). `scripts/check_practice_semantic_execution.py` requires all 41 case IDs in canonical order before an execution is accepted as a full review candidate.

The manual GitHub Actions workflow `run-practice-semantic-model-eval.yml` requires repository secret `OPENAI_API_KEY`, generates responses, validates execution provenance, then builds the blinded human-review packet. It uploads artifacts and does not publish or semantically score the run automatically.

## Stage 1: generation

Capture model/runtime responses before semantic benchmark annotations are opened. A practice semantic response contains only:

- `case_id`
- user-facing `answer`
- declared `outcome`: `match`, `clarify`, `no_match`, or `resource_not_practice`
- `selected_practice_ids`
- `canonical_urls`

Provider/model/runtime provenance belongs in the surrounding execution artifact. Benchmark-only fields such as `expected_outcome`, acceptable practice IDs, required safety notes, and benchmark category must not be supplied to the model.

## Stage 2: blinded human review

Run `scripts/build_semantic_review_packet.py` on captured response JSONL. The packet joins each answer back to the user message but explicitly excludes:

- `category`
- `expected_outcome`
- `acceptable_practice_ids`
- `required_safety_notes`

The generated review template records packet, response, and semantic-dataset SHA-256 values. A reviewer supplies an ID, review date, and one rating per dimension: `pass`, `fail`, `uncertain`, or `not_applicable`.

Human contextual review is the authority for semantic/safety appropriateness. An LLM judge may assist only if its prompt/model/provenance are declared, disagreements remain inspectable, and it is not the sole safety authority.

## Stage 3: scoring

After review is complete, run `scripts/score_semantic_reviews.py`. Only this stage opens the hidden benchmark annotations.

The resulting report contains two separate blocks:

1. `deterministic_contract_metrics`: declared outcome plus selected-practice IDs compared with benchmark contract fields.
2. `human_semantic_review`: reviewer ratings by dimension.

The report also breaks out genuine-risk, required-standard, publication-boundary, and professional-boundary cases as safety-critical categories rather than hiding them inside one aggregate score.

Deterministic contract matching does not establish prose quality or contextual safety. Human semantic review is an editorial benchmark judgment, not clinical validation or a clinical outcome.

## Incomplete review

The scorer fails on incomplete reviews by default. `--allow-incomplete` may be used for work-in-progress analysis, but missing case IDs remain explicit in the report and must not be silently imputed.

## Synthetic CI fixture

`scripts/check_semantic_review_pipeline.py` creates synthetic non-model responses solely to test blinding, hashes, review completeness, and report structure. The fixture is deliberately labeled as synthetic and must never be reported as a model benchmark result.

## Contracts

- `contracts/practice-semantic-response-v1.schema.json`
- `contracts/practice-semantic-review-v1.schema.json`
- `contracts/practice-semantic-review-report-v1.schema.json`
- `contracts/practice-semantic-execution-v1.schema.json`

These contracts support reproducible real-model runs but do not themselves claim that a hosted model has been evaluated.
