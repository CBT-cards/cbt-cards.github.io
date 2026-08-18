# CBT Cards model-run protocol v1

This protocol records real AI-assistant evaluation runs without mixing generation with benchmark answers.

## Goals

A published model run should make five things independently inspectable:

1. the exact CBT Cards evaluation dataset bytes;
2. the provider/model/runtime used to generate answers;
3. the exact evaluation prompt bytes;
4. the raw user-facing answer and declared routing metadata for every case;
5. the deterministic evaluator version and resulting route/target/locale/boundary metrics.

The protocol deliberately does not turn one aggregate percentage into a general mental-health or assistant-quality claim.

## Two-stage execution

### Stage 1: generate responses

For each case, the model receives `user_message` plus the normal public CBT Cards sources and runtime instructions being evaluated. Benchmark-only fields must remain hidden from the model.

Use `research/model-run-prompt-v1.txt` as the evaluation instruction. Capture one response record per case using `schemas/agent-model-response-v1.schema.json`.

The response envelope contains the natural-language answer plus declared route, resource IDs, raw source IDs, and locale behavior. The envelope makes routing objectively scoreable without an LLM-as-judge.

Do not alter the model output after seeing expected benchmark fields. If parsing or transport fails, record or rerun the failure according to a declared run policy rather than silently repairing the answer.

### Stage 2: score responses

Run `scripts/evaluate_model_run.py` after generation is complete. Only at this stage does the evaluator read the expected benchmark fields.

The deterministic v1 evaluator scores:

- route accuracy;
- exact target-ID selection for cases with expected catalog/source IDs;
- locale behavior for locale-scored cases;
- boundary routing for source-only, private-access, immediate-safety, and answer-without-resource cases.

It does not automatically score the prose answer, empathy, clinical appropriateness, factual completeness, `expected_checks`, or `prohibited_claims`. A later semantic evaluator may add those dimensions, but must identify its own method/version and must not overwrite the deterministic routing metrics.

## Required provenance

A recorded model run must identify:

- `provider`;
- `model`;
- `version_or_snapshot` when the provider exposes one, otherwise `null`;
- `runtime` such as API, ChatGPT, OpenClaw, Hermes, or another integration;
- execution timestamp;
- prompt URL and SHA-256;
- evaluation dataset URL and SHA-256;
- input fields visible to the model;
- whether benchmark expected fields were hidden;
- evaluator ID, version, and implementation URL;
- one raw answer plus routing envelope per case.

Do not invent provider snapshots or decoding parameters that were not observable. Use `null` or omit optional runtime metadata instead.

## Starter vs held-out sets

The starter dataset is `data/agent-evals.jsonl`. The separate paraphrase/adversarial challenge set is `data/agent-evals-challenge.jsonl`.

A runner may be developed against the starter set. A challenge set is held out only while the tested runner/model/prompt has not been tuned using those challenge cases. Once a model prompt, adapter, router, or evaluator is deliberately tuned on a challenge generation, that generation must not be described as held-out for that system. Create a new untouched challenge generation for later generalization claims.

## Publishing a run

A future public model-run dataset should store one self-contained run object per line using `schemas/agent-model-run-v1.schema.json`. Keep model runs separate from deterministic baseline run files so a model result cannot inherit baseline provenance by accident.

Before publication:

1. validate every response envelope;
2. verify exact case-set equality with the selected eval dataset;
3. verify prompt and dataset hashes;
4. run the deterministic scorer;
5. inspect natural-language answers separately for prohibited claims and other semantic failures;
6. record the public change in the changelog;
7. label the result narrowly: this is a CBT Cards routing/source-boundary evaluation, not a clinical-safety certification or general model benchmark.

## Reproducibility caveats

Hosted models and consumer runtimes may not be perfectly reproducible even with identical prompts. Record the strongest provider/runtime identity that is actually available and preserve raw responses. If stochastic settings are exposed, record them in runtime metadata. If they are not exposed, do not pretend they were controlled.

The public protocol is designed so ChatGPT, OpenClaw, Hermes, API-based models, and future runtimes can all emit the same neutral response contract while retaining runtime-specific provenance.
