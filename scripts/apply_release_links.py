#!/usr/bin/env python3
"""Apply cross-site links and small usability upgrades for the 22 Aug release."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "agents/index.html": [
        (
            '<section class="section alt"><div class="wrap prose agent-guide"><h2>Recommended flow</h2>',
            '<section class="section alt"><div class="wrap prose agent-guide"><div class="boundary-box"><strong>New to this?</strong> You do not need an account, API key, or installation. Follow the <a href="/agents/get-started/"><strong>three-step AI assistant guide →</strong></a> and copy one bounded prompt.</div><h2>Recommended flow</h2>',
        ),
    ],
    "support/index.html": [
        (
            '<h2>Contact</h2><p>Contact us through <a href="https://www.linkedin.com/in/metalhatcats/">LinkedIn</a>. Include your device model, operating-system version, app version, and a brief description of the issue. Do not include diary contents or other sensitive personal information in your message.</p>',
            '<h2>Contact</h2><p>Use the <a href="/contact/">CBT Cards contact page</a> to choose the right route. For app support, include your device model, operating-system version, app version, and a brief description of the issue. Do not include diary contents or other sensitive personal information.</p>',
        ),
        (
            '<nav><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="/faq/">FAQ</a></nav>',
            '<nav aria-label="Footer"><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="/faq/">FAQ</a></nav>',
        ),
    ],
    "faq/index.html": [
        (
            'Use the CBT Cards support page for current contact options and practical troubleshooting steps.',
            'Use the CBT Cards contact page to choose the right route, and the support page for practical troubleshooting steps.',
        ),
        (
            'Use the <a href="/support/">CBT Cards support page</a> for current contact options and practical troubleshooting steps.',
            'Use the <a href="/contact/">CBT Cards contact page</a> to choose the right route, and the <a href="/support/">support page</a> for practical troubleshooting steps.',
        ),
    ],
    "index.html": [
        ('href="/agents/">Use with an AI assistant', 'href="/agents/get-started/">Use with an AI assistant'),
        (
            '<a class="store" href="/features/">Explore the mobile app</a></div>',
            '<a class="store" href="/features/">Explore the mobile app</a><a class="store" href="/partnerships/">Work with CBT Cards</a></div>',
        ),
        (
            '<a href="/about/">About</a><a href="/privacy/">Privacy</a><a href="/support/">Support</a><a href="/agents/">For AI</a>',
            '<a href="/about/">About</a><a href="/contact/">Contact</a><a href="/partnerships/">Partnerships</a><a href="/agents/get-started/">AI guide</a>',
        ),
    ],
    "about/index.html": [
        (
            '<p>CBT Cards is published by MetalHatsCats. Public project data is read-only and does not expose a user\'s journal, check-ins, backups, or account.</p>',
            '<p>CBT Cards is published by MetalHatsCats. Public project data is read-only and does not expose a user\'s journal, check-ins, backups, or account.</p><p>For corrections, accessibility, support, or a private first contact, use <a href="/contact/">Contact</a>. For translation review, research, education, responsible AI integration, distribution, or licensing, see <a href="/partnerships/">Partnerships</a>.</p>',
        ),
        (
            '<a href="/privacy/">Privacy</a><a href="/agents/">For AI</a>',
            '<a href="/contact/">Contact</a><a href="/partnerships/">Partnerships</a><a href="/agents/">For AI</a>',
        ),
    ],
    "worksheets/cbt-thought-record/index.html": [],
    "worksheets/worry-time/index.html": [],
    "worksheets/activity-planning/index.html": [],
}

WORKSHEET_PRINT = (
    '<p><strong>Print or save as PDF:</strong> use your browser\'s Print command when you want a blank or completed copy.</p>',
    '<p><strong>Print or save as PDF:</strong> use the button when you want a blank or completed copy.</p><button type="button" onclick="window.print()">Print or save PDF</button><p class="source-note">Entries stay in this browser page only and clear when the page is refreshed or closed.</p>',
)


def transform(rel: str, source: str) -> str:
    result = source
    replacements = list(REPLACEMENTS[rel])
    if rel.startswith("worksheets/") and rel != "worksheets/index.html":
        replacements.append(WORKSHEET_PRINT)
    for old, new in replacements:
        if new in result:
            continue
        if old not in result:
            raise ValueError(f"{rel}: expected release-link anchor not found")
        result = result.replace(old, new, 1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale: list[str] = []
    for rel in REPLACEMENTS:
        path = ROOT / rel
        source = path.read_text(encoding="utf-8")
        expected = transform(rel, source)
        if expected == source:
            continue
        if args.write:
            path.write_text(expected, encoding="utf-8")
        else:
            stale.append(rel)
    if stale:
        raise SystemExit("release links are stale: " + ", ".join(stale))
    print("release links applied" if args.write else "release link check passed")


if __name__ == "__main__":
    main()
