# Semantic recommendation evaluation protocol v1.2

CBT Cards keeps semantic recommendation review separate from deterministic routing/contract scoring. The point is not to manufacture one flattering percentage. It is to make different failure modes visible.

## Dimensions

Report these independently: situation/mechanism fit, practice appropriateness, safety-exclusion preservation, no diagnosis/treatment overclaim, evidence fidelity, publication-boundary fidelity, micro-action fidelity, no-match behavior, locale/publication behavior, and canonical citation correctness.

The canonical dataset contains 41 separately authored situations across fit, ambiguity, genuine risk, required standards, publication boundaries, professional boundaries, no-match behavior, and progression.

## Frozen-context real-provider path

For a publishable practice-semantic provider run, CBT Cards uses the separate frozen-context adapter `scripts/run_practice_semantic_openai.py`. It does not enable web search. Every request receives only the case `user_message` plus the fixed semantic prompt, Agent Skill, and committed reviewed-practice context files.

The execution artifact records SHA-256 values for the semantic manifest and both case shards, the fixed prompt, the current Agent Skill, and each frozen context resource (`practice.json`, `practice-recommendations.json`, `practice-evidence.json`, and `practice-rag.ndjson`). It also records the explicitly requested model, `reasoning_effort`, and `max_output_tokens`. These request settings are part of benchmark provenance and must not be reconstructed from memory after a run.

`scripts/check_practice_semantic_execution.py` requires all 41 case IDs in canonical order before an execution is accepted as a full review candidate.

## Manual GitHub Actions safety boundary

`run-practice-semantic-model-eval.yml` is deliberately manual and has two modes:

- `dry-run` is the default. It builds and uploads the frozen request/provenance artifact **without an API call** and does not require `OPENAI_API_KEY`.
- `full-41` performs the real hosted-provider execution. It requires repository secret `OPENAI_API_KEY` **and** the separate confirmation string `RUN 41 CASES`.

The workflow also requires explicit `model`, `reasoning_effort`, and `max_output_tokens` inputs. The runner constrains this benchmark-specific output ceiling to 256–8192 tokens per response. A maintainer should choose settings deliberately and record why when comparing runs.

The confirmation gate is an operational guard, not a cost estimate. Actual provider cost depends on the selected model, token usage, account pricing, retries, and provider policy at execution time. Do not hard-code a dollar estimate into benchmark provenance as if it were an invariant.

A full run generates responses, validates execution provenance, builds the blinded human-review packet, and uploads artifacts. It does not publish or semantically score the run automatically.

## Stage 1: generation

Capture model/runtime responses before semantic benchmark annotations are opened. A practice semantic response contains only:

- `case_id`
- user-facing `answer`
- declared `outcome`: `match`, `clarify`, `no_match`, or `resource_not_practice`
- `selected_practice_ids`
- `canonical_urls`

Provider/model/runtime provenance belongs in the surrounding execution artifact. Benchmark-only fields such as `expected_outcome`, acceptable practice IDs, required safety notes, and benchmark category must not be supplied to the model.

`clarify` is intentionally different from the recommendation-contract word `ambiguous`: semantic generation uses `clarify` when the assistant should ask or preserve ambiguity among 2–3 plausible reviewed practices rather than prematurely selecting one. `resource_not_practice` is used when the right CBT Cards resource is outside the reviewed practice layer, such as a worksheet.

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

The v1 execution schema now permits explicit reasoning/output-token settings while retaining backward compatibility with earlier interface-only v1 records. The current runner and execution gate require those settings for new real runs.

These contracts support reproducible real-model runs but do not themselves claim that a hosted model has been evaluated.
