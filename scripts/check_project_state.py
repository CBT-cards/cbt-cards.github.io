#!/usr/bin/env python3
"""Validate high-level CBT Cards project state against underlying source-of-truth data."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
RELEASE_ID = "data-2026-08-19-practice-agent-trust-hardening"


def fail(message: str) -> None:
    raise SystemExit(f"project state check failed: {message}")


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    required = [
        "README.md",
        "PROJECT_STATUS.md",
        "PERFORMANCE.md",
        "MOBILE_PRIVACY_AUDIT.md",
        "MOBILE_LOCALE_AUDIT.md",
        "LEGACY_REDIRECT_AUDIT.md",
        "SEARCH_DISTRIBUTION.md",
        "LICENSING_DECISION.md",
        "llms.txt",
        "llms-full.txt",
        "mobile-releases/index.html",
        "library/index.html",
        "library/guides/index.html",
        "about/index.html",
        "changelog/index.html",
        "research/practice-watch/index.html",
        "sitemap.xml",
        "data/catalog.json",
        "data/changelog.json",
        "data/practice.json",
        "data/practice-evidence.json",
        "data/content-library.json",
        "data/content-guides.json",
        "data/practice-semantic-evals.json",
        "data/content-review.json",
        "data/practice-watch.json",
        "data/search-measurement.json",
        "data/outreach-targets.json",
        "schemas/practice-watch-v1.schema.json",
        "agents/cbt-cards/manifest.json",
        "research/SEMANTIC_REVIEW_WORKSPACE.md",
        ".github/workflows/deploy-pages.yml",
        ".github/workflows/run-practice-semantic-model-eval.yml",
        ".github/workflows/semantic-review-workspace.yml",
        ".github/workflows/semantic-publication-pipeline.yml",
        "scripts/check_mobile_release_history.py",
        "scripts/build_semantic_review_workspace.py",
        "scripts/check_semantic_review_workspace.py",
        "scripts/check_practice_semantic_publication_candidate.py",
        "scripts/build_practice_semantic_publication_report.py",
        "scripts/check_practice_semantic_publication_pipeline.py",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            fail(f"missing state surface: {rel}")

    manifest = load_json("agents/cbt-cards/manifest.json")
    if manifest.get("latest") != "1.8.0":
        fail(f"unexpected latest Agent Skill: {manifest.get('latest')}")

    practices = load_json("data/practice.json")
    practice_items = practices.get("practices", [])
    if len(practice_items) != 11:
        fail(f"expected 11 reviewed practices, found {len(practice_items)}")
    if any(item.get("review_status") != "editorial_and_safety_reviewed_for_publication" for item in practice_items):
        fail("project status cannot call all practices reviewed while a practice lacks publication review status")
    practice_ids = {item.get("id") for item in practice_items}
    evidence_ids = {item.get("id") for item in load_json("data/practice-evidence.json").get("evidence", [])}

    content_library = load_json("data/content-library.json")
    if content_library.get("schema_version") != "1.0" or content_library.get("id") != "cbt-cards-content-library-v1":
        fail("owned content library identity/version mismatch")
    if content_library.get("rights_basis") != "cbt_cards_original" or content_library.get("clinical_validation_status") != "not_claimed":
        fail("owned content library provenance/clinical-claim boundary mismatch")
    if content_library.get("human_url") != f"{ORIGIN}/library/" or content_library.get("canonical") != f"{ORIGIN}/data/content-library.json":
        fail("owned content library canonical URLs mismatch")
    content_records = content_library.get("records", [])
    if len(content_records) != 24:
        fail(f"expected 24 owned content-library records, found {len(content_records)}")
    expected_content_counts = {"pattern": 6, "experiment": 6, "worked_example": 6, "script": 6}
    if dict(Counter(item.get("type") for item in content_records)) != expected_content_counts:
        fail("owned content library must contain six records in each of four formats")
    content_ids = [item.get("id") for item in content_records]
    if any(not isinstance(item_id, str) or not item_id for item_id in content_ids) or len(content_ids) != len(set(content_ids)):
        fail("owned content library has missing or duplicate record IDs")
    for item in content_records:
        record_id = item.get("id")
        related = item.get("related_practice_ids", [])
        linked_evidence = item.get("evidence_ids", [])
        if not related or not set(related).issubset(practice_ids):
            fail(f"owned content record {record_id} has missing/unknown reviewed-practice links")
        if not linked_evidence or not set(linked_evidence).issubset(evidence_ids):
            fail(f"owned content record {record_id} has missing/unknown evidence links")
        if item.get("type") == "experiment":
            avoid_text = " ".join(map(str, item.get("avoid_when", []))).lower()
            for marker in ("danger", "required", "high-stakes", "irreversible"):
                if marker not in avoid_text:
                    fail(f"experiment {record_id} missing safety marker: {marker}")
    library_page = (ROOT / "library/index.html").read_text(encoding="utf-8")
    if 'href="/data/content-library.json"' not in library_page:
        fail("owned content human page does not link machine-readable data")
    for record_id in content_ids:
        if f'id="{record_id}"' not in library_page:
            fail(f"owned content human page missing stable anchor {record_id}")

    content_guides = load_json("data/content-guides.json")
    if content_guides.get("schema_version") != "1.0" or content_guides.get("id") != "cbt-cards-content-guides-v1":
        fail("content guides identity/version mismatch")
    if content_guides.get("rights_basis") != "cbt_cards_original" or content_guides.get("clinical_validation_status") != "not_claimed":
        fail("content guides provenance/clinical-claim boundary mismatch")
    if content_guides.get("human_url") != f"{ORIGIN}/library/guides/" or content_guides.get("canonical") != f"{ORIGIN}/data/content-guides.json":
        fail("content guides canonical URLs mismatch")
    guide_records = content_guides.get("records", [])
    if len(guide_records) != 18:
        fail(f"expected 18 content-guide records, found {len(guide_records)}")
    expected_guide_counts = {"contrast": 6, "progression": 6, "decision_rule": 6}
    if dict(Counter(item.get("type") for item in guide_records)) != expected_guide_counts:
        fail("content guides must contain six contrasts, six progressions, and six decision rules")
    guide_ids = [item.get("id") for item in guide_records]
    if any(not isinstance(item_id, str) or not item_id for item_id in guide_ids) or len(guide_ids) != len(set(guide_ids)):
        fail("content guides have missing or duplicate record IDs")
    if set(content_ids) & set(guide_ids):
        fail("owned content stable IDs collide across content-library and content-guides datasets")
    for item in guide_records:
        record_id = item.get("id")
        related = item.get("related_practice_ids", [])
        linked_evidence = item.get("evidence_ids", [])
        if not related or not set(related).issubset(practice_ids):
            fail(f"content guide {record_id} has missing/unknown reviewed-practice links")
        if not linked_evidence or not set(linked_evidence).issubset(evidence_ids):
            fail(f"content guide {record_id} has missing/unknown evidence links")
        if item.get("type") == "contrast" and not str(item.get("common_mistake", "")).strip():
            fail(f"contrast {record_id} must state a common mistake/boundary")
        if item.get("type") == "progression" and not str(item.get("stop_condition", "")).strip():
            fail(f"progression {record_id} must state a stop condition")
        if item.get("type") == "decision_rule" and not str(item.get("safety_override", "")).strip():
            fail(f"decision rule {record_id} must state a safety override")
    guides_page = (ROOT / "library/guides/index.html").read_text(encoding="utf-8")
    if 'href="/data/content-guides.json"' not in guides_page:
        fail("content-guides human page does not link machine-readable data")
    for record_id in guide_ids:
        if f'id="{record_id}"' not in guides_page:
            fail(f"content-guides human page missing stable anchor {record_id}")

    semantic = load_json("data/practice-semantic-evals.json")
    if semantic.get("case_count") != 41:
        fail(f"expected 41 practice-semantic cases, found {semantic.get('case_count')}")

    review = load_json("data/content-review.json")
    summary = review.get("summary", {})
    if summary.get("covered_items") != 26 or summary.get("owned_practices") != 11:
        fail("editorial freshness summary no longer matches 26 trusted items / 11 owned practices")

    sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", ns) if node.text}
    if len(sitemap_urls) != 44:
        fail(f"expected reconciled sitemap size 44, found {len(sitemap_urls)}")
    if f"{ORIGIN}/mobile-releases/" not in sitemap_urls:
        fail("mobile release history is not indexed in sitemap")
    if f"{ORIGIN}/library/" not in sitemap_urls:
        fail("owned content library is not indexed in sitemap")
    if f"{ORIGIN}/library/guides/" not in sitemap_urls:
        fail("content navigation guides are not indexed in sitemap")
    if f"{ORIGIN}/research/practice-watch/" not in sitemap_urls:
        fail("monthly practice watch is not indexed in sitemap")

    measurement = load_json("data/search-measurement.json")
    if measurement.get("current", {}).get("sitemap_url_count") != len(sitemap_urls):
        fail("search measurement sitemap count drifted from sitemap.xml")

    outreach = load_json("data/outreach-targets.json")
    if outreach.get("schema_version") != "1.1" or outreach.get("requalified_on") != "2026-08-20":
        fail("outreach queue is not the requalified v1.1 state")
    outreach_statuses = {item.get("status") for item in outreach.get("targets", [])}
    if "ready_requires_fork" not in outreach_statuses or "blocked_by_catalog_license_policy" not in outreach_statuses:
        fail("project status cannot describe outreach blockers until they exist in machine-readable queue")

    catalog = load_json("data/catalog.json")
    if catalog.get("updated") != "2026-08-22":
        fail("resource catalog update date does not reflect the 22 Aug public release")
    resources = {item.get("id"): item for item in catalog.get("resources", [])}
    mobile = resources.get("mobile-releases")
    if not mobile or mobile.get("url") != f"{ORIGIN}/mobile-releases/":
        fail("catalog does not expose canonical mobile release history")
    for resource_id in ("changelog", "changelog-data"):
        if resources.get(resource_id, {}).get("updated") != "2026-08-19":
            fail(f"catalog {resource_id} update date is stale")

    changelog = load_json("data/changelog.json")
    entries = changelog.get("entries", [])
    if changelog.get("updated") != "2026-08-19":
        fail("machine-readable changelog update date is stale")
    if not entries or entries[0].get("id") != RELEASE_ID or entries[0].get("date") != "2026-08-19":
        fail("19 Aug project-state release is not the newest machine-readable changelog entry")
    changelog_page = (ROOT / "changelog/index.html").read_text(encoding="utf-8")
    if f'id="{RELEASE_ID}"' not in changelog_page or '"dateModified":"2026-08-19"' not in changelog_page:
        fail("public changelog page does not expose the 19 Aug reconciliation release")

    about = (ROOT / "about/index.html").read_text(encoding="utf-8")
    if 'href="/mobile-releases/"' not in about:
        fail("About page does not link mobile release history")
    mobile_boundary = "Public-site releases, dataset changes, or agent-skill versions do not imply a new Android or iOS release."
    if mobile_boundary not in about:
        fail("About page lost explicit website/data vs mobile release boundary")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for fragment in (
        "[PROJECT_STATUS.md](PROJECT_STATUS.md)",
        "11 reviewed practices",
        "41 practice-semantic cases",
        "v1.8.0",
        "PERFORMANCE.md",
        "MOBILE_PRIVACY_AUDIT.md",
        "MOBILE_LOCALE_AUDIT.md",
        "LEGACY_REDIRECT_AUDIT.md",
        "SEARCH_DISTRIBUTION.md",
        "LICENSING_DECISION.md",
        "/mobile-releases/",
        "No hosted-model result is currently published",
        "check_project_state.py",
    ):
        if fragment not in readme:
            fail(f"README missing current-state fragment: {fragment}")
    stale_readme = (
        "latest mutable skill alias, currently v1.7.0",
        "Large legacy PNG/TTF payload optimization is tracked separately",
        "Keep the v1.7.0 alias, compatibility immutable mirror",
    )
    for fragment in stale_readme:
        if fragment in readme:
            fail(f"README still contains stale project-state text: {fragment}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for fragment in (
        "Verified snapshot: **24 August 2026**",
        "Current Agent Skill: **v1.8.0**",
        "42 CBT Cards-owned content modules",
        "**No hosted model result is currently published as project evidence.**",
        "practice-semantic-review-workspace.html",
        "check_practice_semantic_publication_candidate.py",
        "build_practice_semantic_publication_report.py",
        "sitemap inventory: 44 public URLs",
        "ready_requires_fork",
        "blocked by current permissive-license requirements",
        "CC BY-NC-SA 4.0",
        "0 human-reviewed, 0 published",
    ):
        if fragment not in status:
            fail(f"PROJECT_STATUS.md missing verified snapshot fragment: {fragment}")

    reviewer_doc = (ROOT / "research/SEMANTIC_REVIEW_WORKSPACE.md").read_text(encoding="utf-8")
    for fragment in (
        "Publication-candidate gate",
        "check_practice_semantic_publication_candidate.py",
        "build_practice_semantic_publication_report.py",
        "does **not** require a perfect score",
    ):
        if fragment not in reviewer_doc:
            fail(f"semantic review operating doc missing current publication-path fragment: {fragment}")

    run_workflow = (ROOT / ".github/workflows/run-practice-semantic-model-eval.yml").read_text(encoding="utf-8")
    if "practice-semantic-review-workspace.html" not in run_workflow:
        fail("real semantic model-run artifact does not include offline review workspace")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    llms_full = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
    for name, text in (("llms.txt", llms), ("llms-full.txt", llms_full)):
        for fragment in ("v1.8.0", "mobile-releases", "No hosted model result is currently published"):
            if fragment not in text:
                fail(f"{name} missing current-state fragment: {fragment}")
    for fragment in ("/library/guides/", "/data/content-guides.json"):
        if fragment not in llms or fragment not in llms_full:
            fail(f"AI indexes missing owned content-guide discovery fragment: {fragment}")
    if "Updated: 2026-08-24" not in llms_full:
        fail("llms-full.txt update date is stale")

    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    for script in ("scripts/check_mobile_release_history.py", "scripts/check_project_state.py"):
        if script not in workflow:
            fail(f"main Pages quality workflow does not execute {script}")

    print(
        "project state check passed: skill 1.8.0, 11 reviewed practices, 42 owned content modules across seven formats, "
        "41 semantic cases, offline blinded review + final publication gate present, 26 freshness items, "
        "44 sitemap URLs, requalified outreach blockers, current changelog/catalog, "
        "mobile/repo release boundary reconciled"
    )


if __name__ == "__main__":
    main()
