# Cite Goose / ARWP adoption

This directory contains publisher-authored ARWP contracts for CBT Cards. They describe product intent and adoption state; they are not ranking, citation, diagnostic, clinical or efficacy certification.

Contract revision: 2026-09-11. Image Discovery is reviewed against ARWP revision `73bd2a64e2e746deeb8de792ca01f654f0a7d33a`.

## Current contracts

- `adoption.json` — retained discoverability/adoption experiment contract.
- `site-focus.json` — Cite Goose Site Focus v0.3 problem, scope, navigation, safety and experience contract.
- `image-discovery.json` — Image Discovery adoption record for the reviewed editorial visual cohort, preferred-image convergence, image sitemap coverage and final/live verification.
- `../ai/site-profile.json` — machine/agent service map for real published interfaces.

The Site Focus contract keeps CBT Cards centered on low-stakes structured reflection. It does not widen the reviewed practice-routing boundary and does not turn the public resource into a therapy or crisis product.

## Product boundary

IN: reviewed CBT-informed practices, low-stakes reflection, linked experiments/examples, worksheets and practical decision rules.

ADJACENT: learning guides, source-toolkit review, AI-assistant integration and research/evaluation.

OUT: diagnosis, treatment, crisis response, medical/legal/financial/safeguarding decisions, high-risk experiments and Search/AI guarantees.

## Validation

The Cite Goose Site Focus workflow validates the v0.3 declaration and compares it with the public site using a bounded Site Focus run. The report is retained as a workflow artifact for human review.

Image Discovery is deliberately scoped to the reviewed editorial visual registry in `scripts/apply_editorial_visuals.py`. The exact Pages artifact keeps responsive 560w/1024w WebP sources for efficient delivery, uses the corresponding 1536x1024 PNG as the ordinary `<img src>` fallback and preferred image, aligns `og:image`, `twitter:image`, `WebPage.primaryImageOfPage` and `Article.image`, and publishes image sitemap entries only for that reviewed cohort.

The visual descriptions are reused from the existing authored VISUALS registry. The image layer must not infer clinical meaning, safety, efficacy, emotions or unseen scene details from filenames. Discover-oriented large-image guidance is measured from the actual PNG bytes and remains separate from ordinary image crawl/index eligibility.

A focus or image-discovery warning never authorizes automatic deletion, clinical escalation or broader publication. Review the page role, safety boundary, publication state, visual authority and linked practice authority before changing anything.

## Evidence rule

Implementation evidence is separate from therapeutic or field outcomes. A passing focus audit or Image Discovery gate does not establish clinical benefit, user safety in every context, image indexing, Search thumbnail selection, Discover placement, ranking or AI citation. Missing evidence remains unknown, and `no_match` remains a valid outcome.
