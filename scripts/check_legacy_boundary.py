#!/usr/bin/env python3
"""Keep legacy MetalHatsCats CBT pages out of CBT Cards canonical/public resource surfaces."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "MIGRATION.md"
AUDIT = ROOT / "LEGACY_REDIRECT_AUDIT.md"

LEGACY_PREFIXES = (
    "https://metalhatscats.com/products/cbt-cards",
    "https://metalhatscats.com/cbt",
    "https://metalhatscats.com/news/cbt-cards-app",
)


def fail(message: str) -> None:
    raise SystemExit(f"legacy canonical boundary check failed: {message}")


def main() -> None:
    for path in (MIGRATION, AUDIT):
        if not path.exists():
            fail(f"missing required audit file: {path.relative_to(ROOT)}")

    migration = MIGRATION.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    migration_plain = migration.replace("**", "")

    for fragment in (
        "20 August 2026",
        "redirect not observed",
        "not verified",
        "https://cbt-cards.github.io/",
    ):
        if fragment not in migration_plain:
            fail(f"MIGRATION.md missing externally verified status fragment: {fragment}")

    if "| implemented |" in migration.lower():
        fail("MIGRATION.md still labels legacy redirects as implemented without deployment proof")

    for fragment in (
        "20 August 2026",
        "public HTTP/search behavior only",
        "Required external changes",
        "scripts/check_legacy_boundary.py",
    ):
        if fragment not in audit:
            fail(f"LEGACY_REDIRECT_AUDIT.md missing fragment: {fragment}")

    public_files: list[Path] = []
    public_files.extend(ROOT.rglob("*.html"))
    public_files.extend(
        [
            ROOT / "data" / "catalog.json",
            ROOT / "data" / "knowledge.jsonl",
            ROOT / "llms.txt",
            ROOT / "llms-full.txt",
            ROOT / "agents" / "cbt-cards" / "SKILL.md",
        ]
    )

    violations: list[str] = []
    for path in public_files:
        if not path.exists() or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for prefix in LEGACY_PREFIXES:
            if prefix in text:
                violations.append(f"{path.relative_to(ROOT)} contains {prefix}")
    if violations:
        fail("legacy product/CBT URL leaked into canonical public surface: " + "; ".join(violations))

    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    bad_catalog = [
        item.get("id")
        for item in catalog.get("resources", [])
        if any(str(item.get("url", "")).startswith(prefix) for prefix in LEGACY_PREFIXES)
    ]
    if bad_catalog:
        fail("catalog resources use legacy CBT canonical URLs: " + ", ".join(map(str, bad_catalog)))

    print(
        "legacy canonical boundary check passed: migration status is externally qualified; "
        "legacy CBT product URLs are absent from canonical public resource surfaces"
    )


if __name__ == "__main__":
    main()
