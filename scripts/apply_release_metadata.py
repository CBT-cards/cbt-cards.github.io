#!/usr/bin/env python3
"""Apply and verify the 22 Aug public-release discovery metadata."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"
NEW_URLS = (
    "https://cbt-cards.github.io/contact/",
    "https://cbt-cards.github.io/partnerships/",
    "https://cbt-cards.github.io/agents/get-started/",
)


def expected(source: str) -> str:
    result = re.sub(r"<lastmod>2026-\d{2}-\d{2}</lastmod>", f"<lastmod>{DATE}</lastmod>", source)
    marker = "  <!-- BEGIN GENERATED LOCALIZED URLS -->"
    additions = "\n".join(f"  <url><loc>{url}</loc><lastmod>{DATE}</lastmod></url>" for url in NEW_URLS)
    if NEW_URLS[0] not in result:
        result = result.replace(marker, additions + "\n" + marker, 1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    target = expected(source)
    if target != source:
        if args.write:
            path.write_text(target, encoding="utf-8")
        else:
            raise SystemExit("release sitemap metadata is stale")
    print("release sitemap metadata applied" if args.write else "release sitemap metadata check passed")


if __name__ == "__main__":
    main()
