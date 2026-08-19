#!/usr/bin/env python3
"""Validate search-distribution measurement, outreach, crawler controls, and IndexNow observability."""

from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io/"
MEASUREMENT = ROOT / "data" / "search-measurement.json"
OUTREACH = ROOT / "data" / "outreach-targets.json"
DOC = ROOT / "SEARCH_DISTRIBUTION.md"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"
INDEXNOW = ROOT / "scripts" / "notify_indexnow.py"
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-pages.yml"


def fail(message: str) -> None:
    raise SystemExit(f"search distribution check failed: {message}")


def main() -> None:
    for path in (MEASUREMENT, OUTREACH, DOC, ROBOTS, SITEMAP, INDEXNOW, WORKFLOW):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    measurement = json.loads(MEASUREMENT.read_text(encoding="utf-8"))
    outreach = json.loads(OUTREACH.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")
    robots = ROBOTS.read_text(encoding="utf-8")
    indexnow = INDEXNOW.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    if measurement.get("schema_version") != "1.0":
        fail("unexpected search measurement schema version")
    if measurement.get("canonical_site") != ORIGIN:
        fail("unexpected canonical site in measurement data")
    if measurement.get("baseline_date") != "2026-08-19":
        fail("search baseline date must remain explicit")

    sitemap_root = ET.parse(SITEMAP).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [node.text for node in sitemap_root.findall("s:url/s:loc", ns) if node.text]
    baseline = measurement.get("baseline", {})
    if baseline.get("sitemap_url_count") != len(sitemap_urls):
        fail(
            f"baseline sitemap count {baseline.get('sitemap_url_count')} does not match current sitemap {len(sitemap_urls)}"
        )

    sample = baseline.get("public_search_sample", {})
    method = str(sample.get("method", ""))
    if "not Search Console or Webmaster Tools" not in method:
        fail("public search sample must not be presented as an official index count")
    if sample.get("cbt_cards_results_observed") != len(sample.get("observed_urls", [])):
        fail("public search sample result count does not match observed URL list")
    for url in sample.get("observed_urls", []):
        if not str(url).startswith(ORIGIN):
            fail(f"public search sample contains non-CBT Cards URL: {url}")

    for provider in ("google_search_console", "bing_webmaster_tools"):
        item = baseline.get(provider, {})
        if item.get("status") != "external_account_required":
            fail(f"{provider} must remain externally qualified until account data is imported")
        if item.get("indexed_urls") is not None:
            fail(f"{provider} indexed_urls must remain null until provider data is recorded")

    indexnow_state = baseline.get("indexnow", {})
    if indexnow_state.get("success_receipt_required") is not True:
        fail("IndexNow success receipt must be required")
    if indexnow_state.get("verified_success_receipt") not in {True, False}:
        fail("IndexNow verified_success_receipt must be boolean")

    checkpoints = measurement.get("weekly_checkpoints")
    if not isinstance(checkpoints, list) or len(checkpoints) != 8:
        fail("measurement ledger must define exactly eight initial weekly checkpoints")
    first = date(2026, 8, 26)
    for index, item in enumerate(checkpoints, start=1):
        expected_date = first + timedelta(days=7 * (index - 1))
        if item.get("week") != index or item.get("date") != expected_date.isoformat():
            fail(f"weekly checkpoint {index} date/number is not the intended seven-day cadence")
        if item.get("status") not in {"pending_external_console_data", "recorded", "partial"}:
            fail(f"weekly checkpoint {index} has unsupported status")
        for field in ("google", "bing", "referrals", "content", "citations"):
            if field not in item:
                fail(f"weekly checkpoint {index} missing {field}")

    if outreach.get("schema_version") != "1.0" or outreach.get("researched_on") != "2026-08-19":
        fail("outreach research version/date mismatch")
    targets = outreach.get("targets")
    if not isinstance(targets, list) or len(targets) < 10:
        fail("at least ten outreach targets must be researched")
    seen_ids = set()
    high_priority = 0
    allowed_statuses = {
        "not_contacted",
        "needs_format_adaptation",
        "monitor_auto_index",
        "blocked_by_license_decision",
        "needs_org_eligibility_check",
        "needs_submission_path_check",
        "submitted",
        "accepted",
        "declined",
    }
    for target in targets:
        target_id = target.get("id")
        if not isinstance(target_id, str) or not target_id or target_id in seen_ids:
            fail(f"invalid or duplicate outreach target id: {target_id}")
        seen_ids.add(target_id)
        if not str(target.get("evidence_url", "")).startswith("https://"):
            fail(f"outreach target {target_id} lacks HTTPS evidence URL")
        if not str(target.get("target_canonical_url", "")).startswith(ORIGIN):
            fail(f"outreach target {target_id} does not point to a CBT Cards canonical URL")
        if target.get("status") not in allowed_statuses:
            fail(f"outreach target {target_id} has unsupported status")
        if target.get("priority") == "A":
            high_priority += 1
        for field in ("evidence", "outreach_method", "fit_note"):
            if not str(target.get(field, "")).strip():
                fail(f"outreach target {target_id} missing {field}")
    if high_priority < 5:
        fail("outreach queue should contain at least five high-fit priority A targets")

    required_robots = (
        "User-agent: OAI-SearchBot\nAllow: /",
        "User-agent: *\nAllow: /",
        "Sitemap: https://cbt-cards.github.io/sitemap.xml",
    )
    for fragment in required_robots:
        if fragment not in robots:
            fail(f"robots.txt missing discovery fragment: {fragment}")

    for fragment in (
        "--receipt",
        'status="success"',
        "status not in {200, 202}",
        "IndexNow/1.1",
    ):
        if fragment not in indexnow:
            fail(f"IndexNow script missing receipt/result behavior: {fragment}")

    notify_section = workflow.split("  notify-indexnow:", 1)
    if len(notify_section) != 2:
        fail("Pages workflow missing notify-indexnow job")
    notify = notify_section[1]
    if "continue-on-error: true" in notify:
        fail("IndexNow failures are hidden by continue-on-error")
    for fragment in (
        "--receipt artifacts/indexnow-receipt.json",
        "actions/upload-artifact@v4",
        "if: always()",
        "indexnow-receipt-${{ github.run_id }}",
    ):
        if fragment not in notify:
            fail(f"IndexNow workflow missing observable receipt fragment: {fragment}")

    for fragment in (
        "Eight-week measurement window",
        "A missing metric is `null`, not zero.",
        "The list is a queue, not a mail merge.",
        "Closing the issue still requires external observations over time",
    ):
        if fragment not in doc:
            fail(f"SEARCH_DISTRIBUTION.md missing policy fragment: {fragment}")

    print(
        f"search distribution check passed: {len(sitemap_urls)} sitemap URLs, "
        f"8 weekly checkpoints, {len(targets)} researched outreach targets, observable IndexNow receipts"
    )


if __name__ == "__main__":
    main()
