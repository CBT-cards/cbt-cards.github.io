# CBT Cards project status

Verified snapshot: **19 August 2026**

This file is the concise maintainer-facing state of the public CBT Cards repository. It describes what is actually present in `main` and what remains intentionally unresolved. CI checks the key invariants so this page does not quietly turn into archaeology.

## Public product direction

CBT Cards is now primarily a public reflection-resource and agent-readable knowledge project. The original Android/iOS app remains documented and downloadable, but website/data/agent work is not treated as a mobile release unless separately verified from store metadata.

## Trusted content snapshot

- 11 CBT Cards-owned reviewed practices.
- 11 corresponding mechanisms in the practice ontology.
- 41 practice-semantic evaluation cases.
- 11 stable practice RAG chunks with safety exclusions kept in-chunk.
- 26 trusted items in the editorial freshness registry.
- 115 pinned source-toolkit records: 77 cards, 23 metaphors, 15 protocols.
- Raw source records remain source-only unless explicitly published by the review overlay.

The practice layer is general wellness/self-reflection material. It is not clinical validation, diagnosis, treatment, emergency support, or evidence that a practice is suitable for every person or situation.

## Agent/research snapshot

Current Agent Skill: **v1.8.0**.

The repository includes deterministic starter/held-out routing baselines, a frozen-context provider runner for all 41 practice-semantic cases, execution provenance checks, and contracts for raw responses/reviews/reports.

The real-model review path is now complete on the repository side:

- `full-41` provider execution is manual and spend-guarded; dry-run is the default.
- generated responses are frozen and validated before benchmark annotations are read.
- `practice-semantic-review-workspace.html` is an offline, no-submit blinded reviewer UI for all 41 cases and ten semantic dimensions.
- a human review export remains hash-bound to the original packet/responses.
- `check_practice_semantic_publication_candidate.py` verifies the final execution → responses → packet → human review → scored-report provenance chain.
- `build_practice_semantic_publication_report.py` renders a deterministic result summary with a separate safety-critical subset and explicit limitations.
- CI exercises the entire publication chain with data that is visibly labeled as a synthetic non-model fixture.

**No hosted model result is currently published as project evidence.** The remaining evidence-producing work is no longer missing repository machinery: it requires an intentionally dispatched real `full-41` provider execution and actual blinded human semantic/safety review. Synthetic fixtures remain CI plumbing only.

## Localization snapshot

Website localization:

- `en`: canonical source/public locale.
- `ru`: 12 machine-draft overlays, 0 human-reviewed, 0 published.
- `de`: planned.

Website locale state is not mobile-app locale state. See `MOBILE_LOCALE_AUDIT.md` for the separate mobile/store reconciliation boundary.

## Mobile-product snapshot

- `/mobile-releases/` is the separate store-sourced mobile release history.
- Apple public history currently reaches `3.1 CBT IN ACTION`.
- Google Play public metadata supplies a reliable update date but not a version name/code that this repository can safely infer.
- `/privacy/` and `MOBILE_PRIVACY_AUDIT.md` distinguish private journal/check-in content claims from technical analytics/identifier telemetry and store disclosure metadata.

Final privacy/store reconciliation still requires inspecting current mobile builds/SDK configuration and the corresponding App Store Connect / Play Console answers. Repository text cannot substitute for that verification.

## Performance snapshot

Runtime body imagery uses responsive WebP sources and WOFF2 fonts under a committed asset-budget gate. Controlled mobile Lighthouse medians documented in `PERFORMANCE.md` improved from:

- performance score: 0.72 → 0.91
- LCP: 18.98 s → 3.38 s
- transferred bytes: 4.47 MB → 478 KB

These are lab measurements, not field Core Web Vitals.

## Search/distribution snapshot

- sitemap inventory: 41 public URLs after adding Contact, Partnerships, and the AI get-started guide; noindex localization previews are excluded.
- `OAI-SearchBot` is explicitly allowed.
- IndexNow runs after deployment and produces an observable receipt rather than hiding failures behind `continue-on-error`.
- an eight-week search measurement ledger exists.
- 12 researched outreach targets exist and now use explicit execution/eligibility states rather than treating every target as merely `not_contacted`.
- two high-fit mental-health lists are currently `ready_requires_fork`; the connected GitHub environment cannot perform the required external fork/PR operation.
- multiple agent-skill catalogs are explicitly blocked by current permissive-license requirements rather than being submitted with a mislabeled CBT Cards license.
- Search Console/Bing account metrics remain external and are not invented from `site:` search samples.

See `SEARCH_DISTRIBUTION.md` and `data/outreach-targets.json`.

## Legacy-host snapshot

The legacy MetalHatsCats product/toolkit URLs remain an external-host migration dependency. `LEGACY_REDIRECT_AUDIT.md` records the observed state. This repository must not claim those redirects are implemented until the legacy host actually sends them.

## Licensing snapshot

Active public terms remain **CC BY-NC-SA 4.0**. `data/knowledge.jsonl` contains six CBT Cards-original records and six toolkit-derived records with explicit record-level rights provenance. `LICENSING_DECISION.md` is a pending publisher/legal decision memo, not a permissive grant.

A future commercial-agent/RAG license change must identify the exact covered datasets and respect mixed provenance rather than assigning one permissive label to source-derived material by implication. The distribution recheck has now demonstrated a practical consequence: some agent catalogs will not accept the current skill/provider under their stated permissive-license policies.

## Remaining evidence-producing work

The highest-value next evidence step is now external execution rather than more benchmark plumbing: run one real hosted model through the frozen 41-case practice-semantic workflow, then perform the blinded human semantic/safety review and pass the final publication-candidate gate. That will expose failures in routing, safety abstention, canonical citation, mechanism fit and instruction following more usefully than simply adding more cards.

Search/distribution also needs time-based external evidence: Search Console/Bing baselines, inspected production IndexNow receipts, weekly measurements and actual accepted citations/outreach placements. Some high-fit open-source lists are ready for a human fork/PR; some agent catalogs remain blocked by the unresolved licensing decision.

## Maintainer invariant

When this snapshot changes, update the underlying source-of-truth data first. `PROJECT_STATUS.md`, README, llms indexes and public pages should describe that data. They must not become an alternative editorial universe.
