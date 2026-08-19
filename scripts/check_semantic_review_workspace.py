#!/usr/bin/env python3
"""Build and inspect the offline semantic-review workspace using synthetic non-model data."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ["expected_outcome", "acceptable_practice_ids", "required_safety_notes", "\"category\""]
NETWORK_PATTERNS = ["<script src=", "fetch(", "XMLHttpRequest", "sendBeacon", "<form", "action="]


def fail(message: str) -> None:
    raise SystemExit(f"semantic review workspace check failed: {message}")


def load_cases() -> list[dict]:
    rows = []
    for name in ("practice-semantic-evals-a.jsonl", "practice-semantic-evals-b.jsonl"):
        for raw in (ROOT / "data" / name).read_text(encoding="utf-8").splitlines():
            if raw.strip():
                rows.append(json.loads(raw))
    return rows


def main() -> None:
    cases = load_cases()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        responses = tmp / "responses.jsonl"
        packet = tmp / "packet.json"
        template = tmp / "template.json"
        workspace = tmp / "workspace.html"
        with responses.open("w", encoding="utf-8") as fh:
            for case in cases:
                fh.write(json.dumps({
                    "case_id": case["id"],
                    "answer": "Synthetic fixture. This is not a model result.",
                    "outcome": "no_match",
                    "selected_practice_ids": [],
                    "canonical_urls": [],
                }, separators=(",", ":")) + "\n")
        subprocess.run([
            sys.executable, str(ROOT / "scripts/build_semantic_review_packet.py"),
            "--responses", str(responses), "--packet-out", str(packet),
            "--review-template-out", str(template),
        ], check=True)
        subprocess.run([
            sys.executable, str(ROOT / "scripts/build_semantic_review_workspace.py"),
            "--packet", str(packet), "--review-template", str(template), "--output", str(workspace),
        ], check=True)
        text = workspace.read_text(encoding="utf-8")
        low = text.lower()
        for token in FORBIDDEN:
            if token.lower() in low:
                fail(f"benchmark-only field token leaked into workspace: {token}")
        for pattern in NETWORK_PATTERNS:
            if pattern.lower() in low:
                fail(f"workspace contains disallowed network/submit pattern: {pattern}")
        required = [
            "human_contextual_review",
            "Export completed review JSON",
            "cases complete",
            "Safety comment",
            "Situation / mechanism fit",
            "Canonical citation correctness",
            "URL.createObjectURL",
        ]
        for token in required:
            if token not in text:
                fail(f"workspace missing required behavior/text: {token}")
        if text.count("Synthetic fixture. This is not a model result.") != len(cases):
            fail("workspace does not contain exactly one blinded answer per case")
    print(f"semantic review workspace check passed: {len(cases)} blinded cases; no benchmark labels/network submit hooks")


if __name__ == "__main__":
    main()
