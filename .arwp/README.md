# Cite Goose / ARWP adoption

This directory contains publisher-authored ARWP contracts for CBT Cards. They describe product intent and adoption state; they are not ranking, citation, diagnostic, clinical or efficacy certification.

Contract revision: 2026-09-11. General ARWP validation and Internal Discovery & Distribution are pinned to revision `793483e3404a97f7892e86bcda3fd317d5c7427c`. The Image Discovery review remains pinned to its reviewed source revision `73bd2a64e2e746deeb8de792ca01f654f0a7d33a`.

## Current contracts

- `adoption.json` — retained discoverability/adoption experiment contract.
- `site-focus.json` — Cite Goose Site Focus v0.3 problem, scope, navigation, safety and experience contract.
- `image-discovery.json` — Image Discovery adoption record for the reviewed editorial visual cohort, preferred-image convergence, image sitemap coverage and final/live verification.
- `internal-discovery.json` — Internal Discovery & Distribution record for reviewed Learn, Worksheet and Toolkit continuation, canonical page utilities and graph regression checks.
- `../ai/site-profile.json` — machine/agent service map for real published interfaces.

The Site Focus contract keeps CBT Cards centered on low-stakes structured reflection. It does not widen the reviewed practice-routing boundary and does not turn the public resource into a therapy or crisis product.

## Product boundary

IN: reviewed CBT-informed practices, low-stakes reflection, linked experiments/examples, worksheets and practical decision rules.

ADJACENT: learning guides, source-toolkit review, AI-assistant integration and research/evaluation.

OUT: diagnosis, treatment, crisis response, medical/legal/financial/safeguarding decisions, high-risk experiments and Search/AI guarantees.

## Validation

The Cite Goose Site Focus workflow validates the v0.3 declaration and compares it with the public site using a bounded Site Focus run. The report is retained as a workflow artifact for human review.

Image Discovery is deliberately scoped to the reviewed editorial visual registry in `scripts/apply_editorial_visuals.py`. The exact Pages artifact keeps responsive image delivery, converged preferred-image metadata and image sitemap coverage for that reviewed cohort.

Internal Discovery & Distribution is deliberately narrower than a recommendation engine. It reuses explicit educational relationships between Learn pages, Worksheets and reviewed Toolkit cards; it does not infer a user's symptoms, diagnosis, risk state or treatment need. The existing crawl-graph gate remains authoritative for sitemap reachability and depth. `scripts/apply_internal_discovery.py` adds browser-local Save, Share, Copy link and conservative Cite utilities plus curated `Continue from here` paths; `scripts/check_internal_discovery.py` rejects non-indexed continuation targets and missing final markers; the live check verifies a bounded production sample after Pages deploys.

A focus, image-discovery or internal-discovery warning never authorizes automatic deletion, clinical escalation or broader publication. Review page role, safety boundary, publication state and linked-practice authority before changing anything.

## Evidence rule

Implementation evidence is separate from therapeutic or field outcomes. A passing focus, Image Discovery or Internal Discovery gate does not establish clinical benefit, user safety in every context, indexing, Search thumbnail selection, Discover placement, ranking or AI citation. Missing evidence remains unknown, and `no_match` remains a valid outcome.
