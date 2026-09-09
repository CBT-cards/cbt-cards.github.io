# AGENTS.md — CBT Cards

Use this file as the root entry point for ChatGPT and other repository agents. Keep the public reflection resource, data contracts, safety boundaries, and publication status consistent; do not create a parallel product model.

## Start here

Read only the context needed for the task:

1. `README.md` — current product surfaces, trusted layers, data contracts, validation commands, and boundaries.
2. `PROJECT_STATUS.md` — current verified snapshot and deliberately unresolved work.
3. `CONTRIBUTING.md` — review and contribution workflow.
4. Relevant source files from the task router below.

Do not begin by loading the whole repository. Generated/publication artifacts are outputs unless the repository explicitly documents them as sources.

## Task router

| Task | Canonical source | Coupled files to inspect | Verification |
| --- | --- | --- | --- |
| Reviewed practice or routing | `data/practice*.json`, `agents/cbt-cards/PRACTICE_SYSTEM.md` | `data/practice-rag.ndjson`, practice manifests, practice pages | `python3 scripts/check_practice_system.py` |
| Owned editorial module | `data/content-library.json`, `data/content-guides.json` | `data/content-review.json`, `/library/`, `/library/guides/` | `python3 scripts/check_content_review.py` and relevant site checks |
| Toolkit publication/audit | `data/toolkit-review.json`, `data/toolkit-audit.json` | toolkit pages and provenance metadata | `python3 scripts/check_toolkit_audit.py` |
| Localization | `data/locales.json`, `data/translations.jsonl` | generated `/<locale>/resources/` pages | `python3 scripts/check_localization.py` and `python3 scripts/build_localized_pages.py --check` |
| Agent Skill | `agents/cbt-cards/SKILL.md`, versioned skill source | `agents/cbt-cards/manifest.json`, install docs | `python3 scripts/check_skill_portability.py` |
| Evaluation/research | `data/*eval*.jsonl`, `research/` protocols | model-run inputs, review packets, provenance | relevant semantic/model runner checks from `README.md` |
| Site/discovery/SEO | human HTML/Markdown source plus discovery data | sitemap, feeds, crawl graph, search measurement | `python3 scripts/check_site.py`, `python3 scripts/check_crawl_graph.py`, `python3 scripts/check_search_distribution.py` |
| Privacy/licensing/mobile boundaries | canonical policy/audit files named in `README.md` | public copy and machine-readable records | relevant boundary checker from `scripts/` |

## Source and generated-output rules

- Preserve stable record IDs, provenance, review state, safety exclusions, and `no_match` behavior.
- Do not promote source-toolkit presence, audit candidacy, deterministic baselines, or generated fixtures into clinical/evidence claims.
- Do not machine-publish translations that are not explicitly reviewed for publication.
- Do not infer mobile releases from repository activity.
- Edit source data/scripts first when a generated page or artifact is wrong; regenerate through the documented builder rather than hand-editing output.
- Keep website content, mobile-product claims, toolkit trust layers, owned content, and model-evaluation evidence distinct as documented in `README.md`.

## GitHub / publication boundary

- `main` is the production GitHub Pages source. Do not push or merge to `main` unless the active user request authorizes it.
- The Pages workflow runs quality checks for pull requests, but its `deploy` job is skipped for `pull_request`; preserve that separation.
- Do not edit deployment triggers, Pages permissions, IndexNow behavior, or CI gates merely to make an agent run faster.
- A branch/PR validation result is not proof of production publication or external search impact.

## Verification

Prefer the smallest relevant checker first. Before publication-sensitive changes, use the repository's existing quality chain documented in `README.md` and `.github/workflows/deploy-pages.yml`. Useful focused checks include:

```bash
python3 scripts/check_practice_system.py
python3 scripts/check_semantic_review_pipeline.py
python3 scripts/check_content_review.py
python3 scripts/check_toolkit_audit.py
python3 scripts/check_localization.py
python3 scripts/build_localized_pages.py --check
python3 scripts/check_asset_budget.py
python3 scripts/check_privacy_consistency.py
python3 scripts/check_mobile_locale_boundary.py
python3 scripts/check_legacy_boundary.py
python3 scripts/check_search_distribution.py
python3 scripts/check_license_boundaries.py
python3 scripts/check_mobile_release_history.py
python3 scripts/check_project_state.py
python3 scripts/check_site.py
python3 scripts/check_crawl_graph.py
python3 scripts/check_schemas.py
```

Do not claim a check passed unless that exact check ran for the changed revision. Preserve existing safety, provenance, licensing, privacy, push, and deployment constraints over generic agent preferences.