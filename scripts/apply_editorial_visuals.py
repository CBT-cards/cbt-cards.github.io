#!/usr/bin/env python3
"""Apply page-specific editorial images to human-facing CBT Cards resources."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"


VISUALS = {
    "learn/cbt-thought-record/index.html": ("technique-thought-evidence", "The CBT Cards mascot sorts blank cards beside an open notebook while examining one card with a magnifying glass.", "A thought record separates the parts of one moment so each can be examined more clearly."),
    "learn/automatic-thoughts/index.html": ("technique-thought-evidence", "The CBT Cards mascot notices and examines one passing blank card beside an open notebook.", "Noticing a thought is different from immediately treating it as a fact or command."),
    "learn/thought-vs-fact/index.html": ("technique-thought-evidence", "The CBT Cards mascot sorts blank cards into several evidence groups beside an open notebook.", "Observable information and interpretation can be considered separately without assuming either is unimportant."),
    "learn/worry-time/index.html": ("technique-worry-time", "The CBT Cards mascot places a blank worry card into a coral box beside a simple clock.", "Worry time gives a concern a deliberate place to return to instead of the whole day."),
    "learn/activity-planning/index.html": ("technique-small-steps", "The CBT Cards mascot climbs four small paper-card steps toward an open notebook.", "A concrete first step can make a larger activity easier to start."),
    "learn/cbt-journaling/index.html": ("technique-thought-evidence", "The CBT Cards mascot examines blank reflection cards beside an open notebook and pencil.", "Structured journaling keeps parts of an experience visible without forcing a quick verdict."),
    "worksheets/cbt-thought-record/index.html": ("technique-thought-evidence", "The CBT Cards mascot sorts blank reflection cards beside an open notebook.", "The worksheet provides the words; the visual stays blank so your own situation remains yours."),
    "worksheets/worry-time/index.html": ("technique-worry-time", "The CBT Cards mascot places a blank card into a paper box beside a clock.", "Use the worksheet to park a worry and choose when to review it."),
    "worksheets/activity-planning/index.html": ("technique-small-steps", "The CBT Cards mascot takes the first of four small paper steps toward an open notebook.", "Plan one visible step with a time and place rather than an entire project at once."),
    "toolkit/cards/index.html": ("technique-thought-evidence", "The CBT Cards mascot examines and sorts blank reflection cards beside an open notebook.", "The source collection contains many records; publication and review status determine which ones become standalone CBT Cards resources."),
    "toolkit/cards/challenge-your-thoughts/index.html": ("technique-thought-evidence", "The CBT Cards mascot examines one blank thought card and sorts evidence into several groups.", "Challenge a thought by looking at the available information, not by forcing a positive answer."),
    "toolkit/cards/thoughts-are-not-facts/index.html": ("technique-thought-evidence", "The CBT Cards mascot holds a magnifying glass over one blank card while other cards remain separate.", "A thought can be noticed and examined without being treated as direct observation."),
    "toolkit/cards/socratic-questioning/index.html": ("technique-thought-evidence", "The CBT Cards mascot examines a blank card with a magnifying glass beside an open notebook.", "Socratic questions explore evidence, alternatives, and useful next steps."),
    "toolkit/cards/worry-box/index.html": ("technique-worry-time", "The CBT Cards mascot places a blank worry card into a coral box beside a simple clock.", "The Worry Box gives a repeated concern a place and a planned return time."),
    "toolkit/cards/big-goals-small-steps/index.html": ("technique-small-steps", "The CBT Cards mascot climbs small blank paper-card steps toward an open notebook.", "A large goal becomes more workable when the first action is small and visible."),
    "toolkit/cards/ground-yourself/index.html": ("technique-grounding", "The CBT Cards mascot sits among a stone, felt circle, paper leaf, pencil, and ceramic cup.", "Grounding returns attention to concrete present-moment information."),
    "toolkit/metaphors/index.html": ("metaphor-library", "The CBT Cards mascot explores a paper lighthouse, repaired cup, mended book, and partly cleared window.", "Metaphors can make an idea easier to remember, but they are memory aids rather than evidence."),
    "agents/index.html": ("ai-agent-public-private", "The CBT Cards mascot passes one blank public practice card to a neutral assistant device while a closed personal notebook stays separate.", "Public CBT Cards resources can be read by an assistant; private journal content is not part of that public exchange."),
}


def figure(asset: str, alt: str, caption: str) -> str:
    return (
        '\n<figure class="article-visual">'
        '<picture>'
        f'<source type="image/webp" srcset="/assets/{asset}-560w.webp 560w, /assets/{asset}.webp 1024w" sizes="(max-width: 760px) calc(100vw - 28px), 1180px" />'
        f'<img src="/assets/{asset}.webp" width="1024" height="683" alt="{html.escape(alt, quote=True)}" fetchpriority="high" decoding="async" />'
        '</picture>'
        f'<figcaption>{html.escape(caption)}</figcaption>'
        '</figure>\n'
    )


def transform(rel: str, source: str) -> str:
    asset, alt, caption = VISUALS[rel]
    result = source
    result = re.sub(
        r'<body(?![^>]*\bdata-visual=)([^>]*)>',
        f'<body data-visual="{asset}"\\1>',
        result,
        count=1,
    )
    image_url = f"{ORIGIN}/assets/{asset}.png"
    og_image = f'<meta property="og:image" content="{image_url}" />'
    og_alt = f'<meta property="og:image:alt" content="{html.escape(alt, quote=True)}" />'
    if re.search(r'<meta property="og:image"[^>]*>', result):
        result = re.sub(r'<meta property="og:image"[^>]*>', og_image, result, count=1)
    else:
        result = result.replace('</head>', f'{og_image}\n{og_alt}\n</head>', 1)
    if re.search(r'<meta property="og:image:alt"[^>]*>', result):
        result = re.sub(r'<meta property="og:image:alt"[^>]*>', og_alt, result, count=1)
    else:
        result = result.replace(og_image, f'{og_image}\n{og_alt}', 1)
    result = re.sub(r'<meta property="og:image:width"[^>]*>', '<meta property="og:image:width" content="1536" />', result, count=1)
    result = re.sub(r'<meta property="og:image:height"[^>]*>', '<meta property="og:image:height" content="1024" />', result, count=1)
    if 'class="article-visual"' not in result:
        match = re.search(r'(<section class="[^"]*\bpage-hero\b[^"]*".*?</section>)', result, flags=re.S)
        if not match:
            raise ValueError(f"{rel}: page hero not found")
        result = result[:match.end()] + figure(asset, alt, caption) + result[match.end():]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    stale: list[str] = []
    for rel in sorted(VISUALS):
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"editorial visual target missing: {rel}")
        source = path.read_text(encoding="utf-8")
        expected = transform(rel, source)
        if expected == source:
            continue
        if args.write:
            path.write_text(expected, encoding="utf-8")
        else:
            stale.append(rel)

    if stale:
        raise SystemExit("editorial visuals are stale: " + ", ".join(stale))
    print("editorial visuals applied" if args.write else "editorial visual check passed")


if __name__ == "__main__":
    main()
