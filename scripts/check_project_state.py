#!/usr/bin/env python3
"""Validate high-level CBT Cards project state against underlying source-of-truth data."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"


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
        "sitemap.xml",
        "data/practice.json",
        "data/practice-semantic-evals.json",
        "data/content-review.json",
        "data/search-measurement.json",
        "agents/cbt-cards/manifest.json",
        ".github/workflows/deploy-pages.yml",
        "scripts/check_mobile_release_history.py",
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
        "sitemap inventory: 38 public URLs",
        "CC BY-NC-SA 4.0",
        "0 human-reviewed, 0 published",
    ):
        if fragment not in status:
            fail(f"PROJECT_STATUS.md missing verified snapshot fragment: {fragment}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    llms_full = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
    for name, text in (("llms.txt", llms), ("llms-full.txt", llms_full)):
        for fragment in (
            "v1.8.0",
            "mobile-releases",
            "No hosted model result is currently published",
        ):
            if fragment not in text:
                fail(f"{name} missing current-state fragment: {fragment}")
    if "Updated: 2026-08-19" not in llms_full:
        fail("llms-full.txt update date is stale")

    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    for script in ("scripts/check_mobile_release_history.py", "scripts/check_project_state.py"):
        if script not in workflow:
            fail(f"main Pages quality workflow does not execute {script}")

    print(
        "project state check passed: skill 1.8.0, 11 reviewed practices, "
        "41 semantic cases, 26 freshness items, 38 sitemap URLs, mobile/repo release boundary reconciled"
    )


if __name__ == "__main__":
    main()
