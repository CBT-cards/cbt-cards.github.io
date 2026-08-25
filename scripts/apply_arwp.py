#!/usr/bin/env python3
"""Advertise the Agent-Ready Web Profile in the deploy workspace."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = '<link rel="describedby" type="application/json" href="/ai/site-profile.json" title="Agent-Ready Web Profile">'


def transform(source: str) -> str:
    if "/ai/site-profile.json" in source or "</head>" not in source:
        return source
    return source.replace("</head>", f"{DISCOVERY}</head>", 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    stale: list[str] = []
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", ".codex", ".agents"} for part in path.parts):
            continue
        source = path.read_text(encoding="utf-8")
        expected = transform(source)
        if expected == source:
            continue
        if args.write:
            path.write_text(expected, encoding="utf-8")
            changed += 1
        else:
            stale.append(path.relative_to(ROOT).as_posix())

    if stale:
        raise SystemExit("ARWP discovery is stale: " + ", ".join(stale))
    print(f"ARWP discovery applied to {changed} HTML files" if args.write else "ARWP discovery check passed")


if __name__ == "__main__":
    main()
