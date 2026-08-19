#!/usr/bin/env python3
"""Validate high-level CBT Cards project state against underlying source-of-truth data."""

from __future__ import annotations

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
        "about/index.html",
        "changelog/index.html",
        "sitemap.xml",
        "data/catalog.json",
        "data/changelog.json",
        "data/practice.json",
        "data/practice-semantic-evals.json",
        "data/content-review.json",
        "data/search-measurement.json",
        "data/outreach-targets.json",
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
    if len(sitemap_urls) != 38:
        fail(f"expected reconciled sitemap size 38, found {len(sitemap_urls)}")
    if f"{ORIGIN}/mobile-releases/" not in sitemap_urls:
        fail("mobile release history is not indexed in sitemap")

    measurement = load_json("data/search-measurement.json")
    if measurement.get("baseline", {}).get("sitemap_url_count") != len(sitemap_urls):
        fail("search measurement sitemap count drifted from sitemap.xml")

    outreach = load_json("data/outreach-targets.json")
    if outreach.get("schema_version") != "1.1" or outreach.get("requalified_on") != "2026-08-19":
        fail("outreach queue is not the requalified v1.1 state")
    outreach_statuses = {item.get("status") for item in outreach.get("targets", [])}
    if "ready_requires_fork" not in outreach_statuses or "blocked_by_catalog_license_policy" not in outreach_statuses:
        fail("project status cannot describe outreach blockers until they exist in machine-readable queue")

    catalog = load_json("data/catalog.json")
    if catalog.get("updated") != "2026-08-19":
        fail("resource catalog update date does not reflect the 19 Aug reconciliation release")
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
        "Verified snapshot: **19 August 2026**",
        "Current Agent Skill: **v1.8.0**",
        "**No hosted model result is currently published as project evidence.**",
        "practice-semantic-review-workspace.html",
        "check_practice_semantic_publication_candidate.py",
        "build_practice_semantic_publication_report.py",
        "sitemap inventory: 38 public URLs",
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
    if "Updated: 2026-08-19" not in llms_full:
        fail("llms-full.txt update date is stale")

    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    for script in ("scripts/check_mobile_release_history.py", "scripts/check_project_state.py"):
        if script not in workflow:
            fail(f"main Pages quality workflow does not execute {script}")

    print(
        "project state check passed: skill 1.8.0, 11 reviewed practices, 41 semantic cases, "
        "offline blinded review + final publication gate present, 26 freshness items, 38 sitemap URLs, "
        "requalified outreach blockers, current changelog/catalog, mobile/repo release boundary reconciled"
    )


if __name__ == "__main__":
    main()
