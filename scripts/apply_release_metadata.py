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
    """Keep the dated 22 Aug release entries stable without rewriting later releases."""
    result = source
    marker = "  <!-- BEGIN GENERATED LOCALIZED URLS -->"
    additions: list[str] = []
    for url in NEW_URLS:
        pattern = re.compile(
            rf"  <url><loc>{re.escape(url)}</loc><lastmod>2026-\d{{2}}-\d{{2}}</lastmod></url>"
        )
        replacement = f"  <url><loc>{url}</loc><lastmod>{DATE}</lastmod></url>"
        if pattern.search(result):
            result = pattern.sub(replacement, result, count=1)
        else:
            additions.append(replacement)
    if additions:
        result = result.replace(marker, "\n".join(additions) + "\n" + marker, 1)
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
