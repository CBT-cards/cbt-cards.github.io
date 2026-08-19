#!/usr/bin/env python3
"""Validate current CBT Cards licensing/provenance boundaries without granting new rights."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_ID = "CC-BY-NC-SA-4.0"
CURRENT_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
OWNED_IDS = {
    "cbt-thought-record",
    "automatic-thoughts",
    "thought-vs-fact",
    "worry-time",
    "activity-planning",
    "cbt-journaling",
}
DERIVED_IDS = {
    "source-card-4",
    "source-card-15",
    "source-card-16",
    "source-card-21",
    "source-card-27",
    "source-card-32",
}


def fail(message: str) -> None:
    raise SystemExit(f"license boundary check failed: {message}")


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL at {path.relative_to(ROOT)}:{line_number}: {exc}")
        if not isinstance(item, dict):
            fail(f"non-object JSONL record at {path.relative_to(ROOT)}:{line_number}")
        records.append(item)
    return records


def main() -> None:
    required_paths = [
        ROOT / "LICENSE",
        ROOT / "LICENSING_DECISION.md",
        ROOT / "data" / "catalog.json",
        ROOT / "data" / "knowledge.jsonl",
        ROOT / "data" / "toolkit-source.json",
        ROOT / "schemas" / "knowledge-record-v1.schema.json",
        ROOT / "agents" / "index.html",
        ROOT / "agents" / "cbt-cards" / "SKILL.md",
    ]
    for path in required_paths:
        if not path.exists():
            fail(f"missing required licensing surface: {path.relative_to(ROOT)}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    for fragment in (
        "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
        "Commercial use is not permitted under this public license without prior written permission",
        "Machine-readable accessibility does not imply a more permissive license.",
        "Trademark rights, including rights in the CBT Cards name and logo, are not granted",
        "LICENSING_DECISION.md",
        "It is not a license grant.",
    ):
        if fragment not in license_text:
            fail(f"LICENSE missing current-scope fragment: {fragment}")

    if "creativecommons.org/licenses/by/4.0" in license_text or "creativecommons.org/publicdomain/zero" in license_text:
        fail("LICENSE contains a permissive CC BY/CC0 grant while publisher decision is still pending")

    decision = (ROOT / "LICENSING_DECISION.md").read_text(encoding="utf-8")
    for fragment in (
        "pending publisher and legal approval",
        "has **not** been made yet",
        "It does not grant CC BY 4.0, CC0, commercial-use permission",
        "Option A: keep CC BY-NC-SA 4.0 everywhere",
        "Option B: CC BY 4.0 for explicitly enumerated CBT Cards-owned machine data",
        "Option C: CC0 for narrow factual metadata only",
        "mixed-provenance distribution",
        "six CBT Cards-owned learning records and six records adapted",
    ):
        if fragment not in decision:
            fail(f"LICENSING_DECISION.md missing non-grant/decision fragment: {fragment}")

    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    if catalog.get("license") != "https://cbt-cards.github.io/LICENSE":
        fail("catalog must continue pointing to the current repository LICENSE until a scoped change is approved")

    toolkit = json.loads((ROOT / "data" / "toolkit-source.json").read_text(encoding="utf-8"))
    if toolkit.get("license") != CURRENT_URL:
        fail("pinned toolkit source license no longer matches CC BY-NC-SA 4.0")

    records = load_jsonl(ROOT / "data" / "knowledge.jsonl")
    by_id = {item.get("id"): item for item in records}
    if len(by_id) != len(records):
        fail("knowledge.jsonl contains duplicate IDs")
    if set(by_id) != OWNED_IDS | DERIVED_IDS:
        fail("knowledge licensing groups do not match the canonical 6 owned + 6 toolkit-derived record set")

    for record_id in OWNED_IDS:
        item = by_id[record_id]
        if item.get("license_url") != CURRENT_URL:
            fail(f"owned knowledge record {record_id} does not expose current NC-SA license URL")
        if item.get("rights_basis") != "cbt_cards_original":
            fail(f"owned knowledge record {record_id} has wrong rights_basis")
        if "source_license_url" in item:
            fail(f"owned knowledge record {record_id} must not pretend to derive rights from toolkit source")
        if "source_record_id" in item:
            fail(f"owned knowledge record {record_id} unexpectedly has source_record_id")

    for record_id in DERIVED_IDS:
        item = by_id[record_id]
        if item.get("license_url") != CURRENT_URL or item.get("source_license_url") != CURRENT_URL:
            fail(f"toolkit-derived knowledge record {record_id} must expose current/source NC-SA license")
        if item.get("rights_basis") != "adapted_from_toolkit":
            fail(f"toolkit-derived knowledge record {record_id} has wrong rights_basis")
        if not str(item.get("source_record_id", "")).startswith("card-"):
            fail(f"toolkit-derived knowledge record {record_id} lacks stable source record ID")
        sources = item.get("sources", [])
        if "https://metalhatscats.com/datasets/cbt-toolkit" not in sources:
            fail(f"toolkit-derived knowledge record {record_id} lost toolkit source attribution")

    schema = json.loads((ROOT / "schemas" / "knowledge-record-v1.schema.json").read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    if not {"license_url", "rights_basis"}.issubset(required):
        fail("knowledge record schema does not require current license/provenance fields")
    properties = schema.get("properties", {})
    if properties.get("license_url", {}).get("const") != CURRENT_URL:
        fail("knowledge record schema license_url is not pinned to current NC-SA terms")
    if set(properties.get("rights_basis", {}).get("enum", [])) != {"cbt_cards_original", "adapted_from_toolkit"}:
        fail("knowledge record schema rights_basis enum changed unexpectedly")

    agents = (ROOT / "agents" / "index.html").read_text(encoding="utf-8")
    for fragment in (
        "Reuse and licensing",
        "commercial reuse is not currently granted by the public license without separate permission",
        "rights_basis",
        "adapted_from_toolkit",
        "/LICENSING_DECISION.md",
        "Mentioning those options is not a new license grant.",
    ):
        if fragment not in agents:
            fail(f"agents page missing current reuse guidance: {fragment}")

    skill = (ROOT / "agents" / "cbt-cards" / "SKILL.md").read_text(encoding="utf-8")
    if f"license: {CURRENT_ID}" not in skill:
        fail("latest Agent Skill license changed without a deliberate skill/license release")

    print(
        "license boundary check passed: current NC-SA terms explicit; "
        f"{len(OWNED_IDS)} owned and {len(DERIVED_IDS)} toolkit-derived knowledge records distinguished; "
        "permissive options remain proposals, not grants"
    )


if __name__ == "__main__":
    main()
