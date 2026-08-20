#!/usr/bin/env python3
"""Keep website localization state separate from mobile/store language support claims."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT / "data" / "locales.json"
LANGUAGES_PAGE = ROOT / "languages" / "index.html"
AUDIT = ROOT / "MOBILE_LOCALE_AUDIT.md"
MOBILE_RELEASE = ROOT / "mobile-releases" / "index.html"
LOCALIZATION = ROOT / "LOCALIZATION.md"
LLMS_FULL = ROOT / "llms-full.txt"

SCOPE_TEXT = "Website publication status only; this does not assert mobile app/store language support."
APPLE_LANGUAGES = ("English", "French", "German", "Italian", "Portuguese", "Spanish")


def fail(message: str) -> None:
    raise SystemExit(f"mobile locale boundary check failed: {message}")


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
    for path in (LOCALES, LANGUAGES_PAGE, AUDIT, MOBILE_RELEASE, LOCALIZATION, LLMS_FULL):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    registry = json.loads(LOCALES.read_text(encoding="utf-8"))
    if registry.get("updated") != "2026-08-19":
        fail("locale registry must record the 2026-08-19 scope clarification")

    locales = registry.get("locales")
    if not isinstance(locales, list) or not locales:
        fail("locale registry has no locale records")
    for item in locales:
        if SCOPE_TEXT not in str(item.get("policy", "")):
            fail(f"locale {item.get('locale')} does not state the website/mobile scope boundary")

    languages_page = LANGUAGES_PAGE.read_text(encoding="utf-8")
    if languages_page.count(SCOPE_TEXT) != len(locales):
        fail("generated languages page does not expose website-only scope for every locale")

    mobile_release = MOBILE_RELEASE.read_text(encoding="utf-8")
    current_ios = current_ios_release(mobile_release)
    audit = AUDIT.read_text(encoding="utf-8")
    for fragment in (
        "mobile build verification pending",
        "19 August 2026",
        current_ios,
        "Google Play",
        "Android language support therefore remains **unverified**",
        "Use `data/locales.json` and `data/translations.jsonl` to answer questions about the public website/library.",
    ):
        if fragment not in audit:
            fail(f"mobile locale audit missing fragment: {fragment}")
    if "/mobile-releases/" not in audit:
        fail("mobile locale audit must name the mobile release-history source")
    for language in APPLE_LANGUAGES:
        if f"- {language}" not in audit:
            fail(f"mobile locale audit missing observed Apple language: {language}")

    localization = LOCALIZATION.read_text(encoding="utf-8")
    for fragment in (
        "website publication lifecycle",
        "MOBILE_LOCALE_AUDIT.md",
        "The website locale registry is intentionally not a mobile-app support matrix.",
        "Apple lists English, French, German, Italian, Portuguese, and Spanish",
    ):
        if fragment not in localization:
            fail(f"LOCALIZATION.md missing scope guidance: {fragment}")

    llms_full = LLMS_FULL.read_text(encoding="utf-8")
    if "Website locale status must not be used to infer current mobile-app language support." not in llms_full:
        fail("llms-full.txt no longer preserves the website/mobile locale boundary")

    print(
        f"mobile locale boundary check passed: {len(locales)} website locale states remain separate "
        f"from observed/unverified mobile-store language support; current iOS release is {current_ios}"
    )


if __name__ == "__main__":
    main()
