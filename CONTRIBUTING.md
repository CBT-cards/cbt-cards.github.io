# Contributing to CBT Cards

CBT Cards accepts proposals for reviewed practices, metaphors, evidence updates, safety-boundary corrections, translation review, and data/schema bugs. Submission is not publication, clinical validation, or evidence of efficacy.

## Editorial states

Content moves deliberately:

`proposed -> evidence_review -> safety_review -> editorial_review -> published`

or

`proposed -> ... -> rejected`

Only a maintainer can move a proposal to `published`. AI generation or AI self-review cannot self-certify a record as human reviewed. Source-only toolkit records remain governed by the toolkit publication overlay. Safety-critical changes require explicit maintainer review. Breaking data changes require a new versioned contract rather than silently changing an existing public contract.

## New reviewed practice proposals

Use the **New reviewed practice proposal** issue form. A proposal must include:

- a short title;
- an existing mechanism ID, or a clear case for a genuinely new mechanism;
- plain-language situations without diagnosis labels;
- `best_used_when` fit conditions;
- complete `avoid_when` / genuine-risk exclusions;
- proposed prompt wording;
- one bounded `micro_action`;
- a follow-up / reflection question;
- source URLs and a mechanism-level evidence claim scope;
- what those sources **do not establish**;
- whether the wording is original, adapted, or quoted;
- rights/source provenance for adapted or quoted material.

A reviewed practice is a small general-wellness reflection unit, not an autonomous treatment plan. Do not use the practice layer to override genuine danger, protective boundaries, accessibility aids, medication or professional instructions, mandatory safety checks, or medical/legal/financial/safeguarding decisions.

Before proposing a new mechanism or practice, check `data/practice-coverage.json` and existing reviewed practices. A larger page count is not an editorial goal. If an existing mechanism is already covered, explain the distinct user situation or function that justifies another practice instead of producing a near-duplicate.

## Metaphor proposals

Use the **New metaphor proposal** form.

A metaphor must attach to an already-reviewed concept/mechanism or clearly state what review dependency remains. Its job is to make an idea easier to remember or communicate. A metaphor:

- is a **memory aid, not evidence**;
- cannot bypass evidence, safety, or publication review;
- should state how it might be overgeneralized, literalized, or misused;
- must use original wording unless reuse rights for adapted/quoted wording are explicit;
- must not turn a source-only treatment protocol into published CBT Cards guidance by analogy.

## Evidence updates

Use the **Evidence / claim-scope update** form.

Keep the following separate:

1. what the source actually supports;
2. which CBT Cards mechanism(s) that support maps to;
3. what the source does **not** establish;
4. whether the source is current and when it was checked.

Evidence for a CBT mechanism does not automatically establish efficacy, safety, or clinical validation of the exact CBT Cards short-card format. Prefer primary guidelines, public-health guidance, or established clinical-resource sources. Link to sources rather than copying substantial text.

## Relations, RAG, coverage, and the human practice page

`data/practice.json`, ontology, evidence, relations, semantic evals, locale data, and source-audit data are source inputs. The following are deterministic outputs:

- `data/practice-rag.ndjson`
- `data/practice-rag-manifest.json`
- `data/practice-coverage.json`
- `practice/index.html`

After changing a relevant source file, regenerate them with:

```bash
python3 scripts/build_practice_artifacts.py --write
```

Then validate:

```bash
python3 scripts/build_practice_artifacts.py --check
python3 scripts/check_practice_contract.py
python3 scripts/check_practice_system.py
```

Do not hand-edit a generated practice artifact to make a check pass. Fix the source data or builder rule that produced the wrong output.

## Localization

Source-language content and translations are separate records. Machine drafts cannot become official merely because they exist.

After changing locale status or a human-reviewed/published translation, regenerate localized pages with:

```bash
python3 scripts/build_localized_pages.py --write
```

Only records explicitly marked human reviewed, reviewed for publication, and published may produce official localized resource pages. Website locale state does not imply mobile-app language support.

## Copyright and submission rights

Contributors must have the right to submit their wording. Do not paste copyrighted therapy manuals, books, paywalled clinical material, proprietary assessment instruments, or long source passages. Link to sources and write CBT Cards project copy in original words.

A quoted phrase is not made reusable merely by adding a citation. If exact third-party wording is genuinely necessary, identify the license or permission that authorizes reuse.

## Licensing boundary

Current public CBT Cards terms remain those stated in `LICENSE`. `LICENSING_DECISION.md` discusses possible future machine-data licensing approaches but is explicitly not a new grant. Do not describe a proposed future license as current permission.

## Quality checks

The main Pages workflow and the dedicated practice-system workflow enforce the same major publication boundaries. At minimum, run the targeted checks relevant to your change. A content change that requires weakening a safety/provenance check merely to pass CI is usually a sign that the content or contract needs review, not that the check should be deleted.
