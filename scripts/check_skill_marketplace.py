#!/usr/bin/env python3
"""Validate the CBT Cards individual Agent Skill marketplace."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise SystemExit("skill marketplace check failed: " + message)


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def local_path(url: str) -> Path:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        fail("outside canonical origin: " + url)
    return ROOT / parsed.path.lstrip("/")


def frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\n\"']+)[\"']?\s*$", text)
    return match.group(1).strip() if match else None


def main() -> None:
    market = load("data/skill-marketplace.json")
    discovery = load(".well-known/agent-skills/index.json")
    groupings = load("skills.sh.json")
    review = load("data/toolkit-review.json")

    if market.get("schema_version") != "1.0" or market.get("canonical") != f"{ORIGIN}/data/skill-marketplace.json":
        fail("marketplace identity")
    items = market.get("skills", [])
    if market.get("summary") != {"skills": 15, "techniques": 11, "metaphors": 4} or len(items) != 15:
        fail("marketplace summary/count")

    names: set[str] = set()
    by_name: dict[str, dict] = {}
    source_ids: set[str] = set()
    digests: dict[str, str] = {}
    for item in items:
        name = item.get("name")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name) or name in names:
            fail("invalid/duplicate name: " + str(name))
        names.add(name); by_name[name] = item
        source_id = item.get("source_id")
        if not source_id or source_id in source_ids:
            fail("invalid/duplicate source_id: " + str(source_id))
        source_ids.add(source_id)
        if item.get("kind") not in {"technique", "metaphor"} or item.get("version") != "1.0.0":
            fail("kind/version: " + name)
        if item.get("review_status") != "reviewed_for_publication" or item.get("publication_surface") != "agent_skill":
            fail("review/publication surface: " + name)
        if item.get("license") != "CC-BY-NC-SA-4.0":
            fail("license: " + name)
        expected_url = f"{ORIGIN}/skills/{name}/SKILL.md"
        if item.get("skill_url") != expected_url:
            fail("skill URL: " + name)
        path = local_path(expected_url)
        if not path.exists():
            fail("missing SKILL.md: " + name)
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if not text.startswith("---\n"):
            fail("frontmatter: " + name)
        if frontmatter_value(text, "name") != name or frontmatter_value(text, "license") != "CC-BY-NC-SA-4.0":
            fail("frontmatter identity/license: " + name)
        if 'version: "1.0.0"' not in text or f"`{source_id}`" not in text:
            fail("version/source id: " + name)
        if "return `no_match`" not in text:
            fail("no_match contract: " + name)
        if item.get("kind") == "metaphor" and "memory aid" not in text.lower():
            fail("metaphor boundary: " + name)
        digests[name] = hashlib.sha256(raw).hexdigest()

    if sum(1 for x in items if x["kind"] == "technique") != 11 or sum(1 for x in items if x["kind"] == "metaphor") != 4:
        fail("kind counts")

    if discovery.get("$schema") != "https://schemas.agentskills.io/discovery/0.2.0/schema.json":
        fail("discovery schema")
    discovered = discovery.get("skills", [])
    if {x.get("name") for x in discovered} != names or len(discovered) != 15:
        fail("discovery set")
    for entry in discovered:
        name = entry["name"]
        if entry.get("type") != "skill-md" or entry.get("url") != f"/skills/{name}/SKILL.md":
            fail("discovery URL/type: " + name)
        if entry.get("digest") != "sha256:" + digests[name]:
            fail("discovery digest: " + name)
        if entry.get("description") != by_name[name].get("description"):
            fail("discovery description drift: " + name)

    grouped: list[str] = []
    for group in groupings.get("groupings", []):
        grouped.extend(group.get("skills", []))
    if len(grouped) != 15 or set(grouped) != names:
        fail("skills.sh grouping coverage")

    review_by_source = {x.get("source_record_id"): x for x in review.get("records", [])}
    expected_metaphors = {"metaphor-4", "metaphor-5", "metaphor-18", "metaphor-19"}
    actual_metaphors = {x["source_id"] for x in items if x["kind"] == "metaphor"}
    if actual_metaphors != expected_metaphors:
        fail("metaphor source set")
    for item in items:
        if item["kind"] != "metaphor":
            continue
        record = review_by_source.get(item["source_id"], {})
        if record.get("publication_status") != "published" or record.get("publication_surface") != "agent_skill":
            fail("metaphor review status: " + item["name"])
        if record.get("skill_name") != item["name"] or record.get("catalog_resource_id") != item["id"]:
            fail("metaphor review mapping: " + item["name"])
        if record.get("canonical_url") != item.get("canonical_human_url"):
            fail("metaphor canonical review URL: " + item["name"])

    page = (ROOT / "skills/index.html").read_text(encoding="utf-8")
    for fragment in ("/data/skill-marketplace.json", "/.well-known/agent-skills/index.json", "/skills.sh.json", "Hermes Agent", "OpenClaw"):
        if fragment not in page:
            fail("marketplace HTML missing " + fragment)
    for name in names:
        if f'id="{name}"' not in page or f'/skills/{name}/SKILL.md' not in page:
            fail("marketplace HTML missing skill: " + name)

    print("skill marketplace check passed: 15 skills (11 techniques, 4 reviewed metaphor memory aids), discovery digests aligned")


if __name__ == "__main__":
    main()
