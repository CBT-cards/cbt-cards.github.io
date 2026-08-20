#!/usr/bin/env python3
"""Validate CBT Cards mobile privacy wording and store-disclosure reconciliation."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVACY_PATH = ROOT / "privacy" / "index.html"
AUDIT_PATH = ROOT / "MOBILE_PRIVACY_AUDIT.md"
MOBILE_RELEASE_PATH = ROOT / "mobile-releases" / "index.html"
CATALOG_PATH = ROOT / "data" / "catalog.json"
LLMS_FULL_PATH = ROOT / "llms-full.txt"
APPLE_URL = "https://apps.apple.com/us/app/cbt-cards-%D1%81bt-for-daily-use/id6737169041"
GOOGLE_URL = "https://play.google.com/store/apps/details?id=cbt.cbtcards.stressrelief"

BANNED_PUBLIC_CLAIMS = (
    r"\bno tracking\b",
    r"\bno personal data collection\b",
    r"\bno data collected\b",
    r"\bcollects no data\b",
    r"\bdoes not collect any data\b",
    r"\bwe do not collect any data\b",
)


def fail(message: str) -> None:
    raise SystemExit(f"privacy consistency check failed: {message}")


def require_fragments(text: str, fragments: tuple[str, ...], label: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        fail(f"{label} missing required reconciliation text: {', '.join(missing)}")


def current_ios_release(mobile_release: str) -> str:
    match = re.search(
        r"most recent version consistently observed.*?<strong>([^<]+)</strong>",
        mobile_release,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        fail("mobile release history does not expose a parseable current Apple release")
    value = match.group(1).strip()
    if not value:
        fail("mobile release history current Apple release is empty")
    return value


def main() -> None:
    for path in (PRIVACY_PATH, AUDIT_PATH, MOBILE_RELEASE_PATH, CATALOG_PATH, LLMS_FULL_PATH):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    privacy = PRIVACY_PATH.read_text(encoding="utf-8")
    audit = AUDIT_PATH.read_text(encoding="utf-8")
    mobile_release = MOBILE_RELEASE_PATH.read_text(encoding="utf-8")
    current_ios = current_ios_release(mobile_release)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    llms_full = LLMS_FULL_PATH.read_text(encoding="utf-8")

    require_fragments(
        privacy,
        (
            "14 July 2026",
            "19 August 2026",
            "Store reconciliation: <strong>open</strong>",
            current_ios,
            "Identifiers",
            "Usage Data",
            "9 March 2026",
            "App activity",
            "App info and performance",
            "Diary entries, check-in text, notes, and attached photos are reflection content.",
            "technical identifiers, crash diagnostics, performance telemetry, or aggregate usage events",
            "/mobile-releases/",
            APPLE_URL,
            GOOGLE_URL,
            "/MOBILE_PRIVACY_AUDIT.md",
        ),
        "privacy page",
    )

    require_fragments(
        audit,
        (
            "implementation verification pending",
            "19 August 2026",
            "14 July 2026",
            current_ios,
            "Identifiers",
            "Usage Data",
            "9 March 2026",
            "App activity",
            "App info and performance",
            "iOS source commit/tag",
            "Android source commit/tag",
            "App Store Connect privacy answers",
            "Google Play Data Safety answers",
            APPLE_URL,
            GOOGLE_URL,
        ),
        "mobile privacy audit",
    )

    if current_ios not in mobile_release:
        fail("current iOS release disappeared from mobile release history")
    if 'href="https://cbt-cards.github.io/privacy/"' not in privacy:
        fail("privacy page missing canonical CBT Cards URL")

    resources = catalog.get("resources")
    if not isinstance(resources, list):
        fail("catalog resources must be a list")
    privacy_resource = next((item for item in resources if item.get("id") == "privacy"), None)
    if not privacy_resource or privacy_resource.get("url") != "https://cbt-cards.github.io/privacy/":
        fail("catalog privacy resource does not point to canonical privacy page")

    source_priority = llms_full.split("## Reviewed practice system", 1)[0]
    if "app/privacy claims" not in source_priority or "/privacy/" not in source_priority:
        fail("llms-full.txt source priority no longer routes app/privacy claims to /privacy/")

    violations: list[str] = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in BANNED_PUBLIC_CLAIMS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                violations.append(f"{path.relative_to(ROOT)} matches {pattern}")
    if violations:
        fail("absolute privacy claims remain while store reconciliation is open: " + "; ".join(violations))

    print(
        "privacy consistency check passed: privacy reconciliation matches the current mobile release history; "
        "local reflection content is separated from technical telemetry; Apple/Google reconciliation remains open; "
        "absolute public privacy slogans are blocked"
    )


if __name__ == "__main__":
    main()
