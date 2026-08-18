#!/usr/bin/env python3
"""Validate the repository-level CITATION.cff fields CBT Cards relies on."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "CITATION.cff"


def fail(message: str) -> None:
    raise SystemExit(f"citation check failed: {message}")


def main() -> None:
    if not PATH.exists():
        fail("missing CITATION.cff")
    text = PATH.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    required_fragments = {
        "CFF version": "cff-version: 1.2.0",
        "dataset type": "type: dataset",
        "project author entity": 'name: "MetalHatsCats"',
        "license": "license: CC-BY-NC-SA-4.0",
        "repository": 'repository-code: "https://github.com/CBT-cards/cbt-cards.github.io"',
        "homepage": 'url: "https://cbt-cards.github.io/"',
        "release date": 'date-released: "2026-08-18"',
    }
    for label, fragment in required_fragments.items():
        if fragment not in text:
            fail(f"missing {label}: {fragment}")
    if any(line.startswith("doi:") or line == "type: doi" for line in lines):
        fail("do not publish a DOI before an archive has actually assigned one")
    if any(line.startswith("version:") for line in lines):
        fail("do not invent a project-wide semantic version before one is deliberately released")
    print("citation check passed: CFF 1.2.0 dataset metadata without invented DOI or project version")


if __name__ == "__main__":
    main()
