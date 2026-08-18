#!/usr/bin/env python3
"""Validate the latest CBT Cards skill against the portable Agent Skills profile."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
ALLOWED_TOP_LEVEL = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise SystemExit(f"skill portability check failed: {message}")


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, str], dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{path.relative_to(ROOT)}: missing opening frontmatter marker")
    try:
        closing = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        fail(f"{path.relative_to(ROOT)}: missing closing frontmatter marker")

    top: dict[str, str] = {}
    metadata: dict[str, str] = {}
    in_metadata = False

    for number, raw in enumerate(lines[1:closing], start=2):
        if not raw.strip():
            continue
        if raw.startswith("  "):
            if not in_metadata:
                fail(f"{path.relative_to(ROOT)}:{number}: nested field outside metadata")
            stripped = raw.strip()
            if ":" not in stripped:
                fail(f"{path.relative_to(ROOT)}:{number}: malformed metadata field")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = unquote(value)
            if not key or not value:
                fail(f"{path.relative_to(ROOT)}:{number}: metadata keys and values must be non-empty strings")
            if key in metadata:
                fail(f"{path.relative_to(ROOT)}:{number}: duplicate metadata key {key}")
            metadata[key] = value
            continue
        if raw[0].isspace():
            fail(f"{path.relative_to(ROOT)}:{number}: only two-space metadata indentation is supported")
        in_metadata = False
        if ":" not in raw:
            fail(f"{path.relative_to(ROOT)}:{number}: malformed frontmatter field")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = unquote(value)
        if key not in ALLOWED_TOP_LEVEL:
            fail(f"{path.relative_to(ROOT)}:{number}: non-portable top-level field {key}")
        if key in top:
            fail(f"{path.relative_to(ROOT)}:{number}: duplicate top-level field {key}")
        if key == "metadata":
            if value:
                fail(f"{path.relative_to(ROOT)}:{number}: metadata must be a mapping")
            top[key] = ""
            in_metadata = True
        else:
            if not value:
                fail(f"{path.relative_to(ROOT)}:{number}: {key} must be a non-empty scalar")
            top[key] = value

    body = "\n".join(lines[closing + 1 :])
    return top, metadata, body


def main() -> None:
    manifest_path = ROOT / "agents" / "cbt-cards" / "manifest.json"
    catalog_path = ROOT / "data" / "catalog.json"
    install_path = ROOT / "agents" / "cbt-cards" / "INSTALL.md"
    for path in (manifest_path, catalog_path, install_path):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    latest = manifest.get("latest")
    if latest != "1.7.0":
        fail(f"expected portability release 1.7.0 to be latest, found {latest}")

    alias = ROOT / "agents" / "cbt-cards" / "SKILL.md"
    mirror = ROOT / "agents" / "cbt-cards" / f"v{latest}" / "SKILL.md"
    portable = ROOT / "agents" / "cbt-cards" / f"v{latest}" / "cbt-cards" / "SKILL.md"
    for path in (alias, mirror, portable):
        if not path.exists():
            fail(f"missing latest skill distribution: {path.relative_to(ROOT)}")

    alias_text = alias.read_text(encoding="utf-8")
    if alias_text != mirror.read_text(encoding="utf-8"):
        fail("latest mutable alias differs from backward-compatible immutable mirror")
    if alias_text != portable.read_text(encoding="utf-8"):
        fail("latest mutable alias differs from strict portable immutable distribution")

    for path in (alias, portable):
        top, metadata, body = parse_frontmatter(path)
        if set(top) - ALLOWED_TOP_LEVEL:
            fail(f"{path.relative_to(ROOT)}: unsupported top-level frontmatter")
        for required in ("name", "description"):
            if required not in top:
                fail(f"{path.relative_to(ROOT)}: missing required field {required}")
        name = top["name"]
        if len(name) > 64 or not NAME_RE.fullmatch(name):
            fail(f"{path.relative_to(ROOT)}: invalid portable skill name {name}")
        if path.parent.name != name:
            fail(f"{path.relative_to(ROOT)}: immediate parent directory must match skill name {name}")
        if len(top["description"]) > 1024:
            fail(f"{path.relative_to(ROOT)}: description exceeds 1024 characters")
        if "compatibility" in top and len(top["compatibility"]) > 500:
            fail(f"{path.relative_to(ROOT)}: compatibility exceeds 500 characters")
        if top.get("license") != "CC-BY-NC-SA-4.0":
            fail(f"{path.relative_to(ROOT)}: unexpected license")
        expected_metadata = {
            "author": "MetalHatsCats",
            "version": latest,
            "homepage": f"{ORIGIN}/agents/",
        }
        if metadata != expected_metadata:
            fail(f"{path.relative_to(ROOT)}: metadata differs from expected string map: {metadata}")
        if len(body.splitlines()) > 500:
            fail(f"{path.relative_to(ROOT)}: skill body exceeds 500-line portability budget")
        if "version:" in "\n".join(path.read_text(encoding="utf-8").split("---", 2)[1].splitlines()):
            # metadata.version is expected; reject only an unindented top-level version key.
            frontmatter_lines = path.read_text(encoding="utf-8").split("---", 2)[1].splitlines()
            if any(line.startswith("version:") for line in frontmatter_lines):
                fail(f"{path.relative_to(ROOT)}: version must not be a top-level frontmatter field")
        if any(line.startswith("homepage:") for line in path.read_text(encoding="utf-8").split("---", 2)[1].splitlines()):
            fail(f"{path.relative_to(ROOT)}: homepage must not be a top-level frontmatter field")

    versions = {item.get("version"): item.get("url") for item in manifest.get("versions", []) if isinstance(item, dict)}
    expected_mirror_url = f"{ORIGIN}/agents/cbt-cards/v{latest}/SKILL.md"
    if versions.get(latest) != expected_mirror_url:
        fail("manifest latest immutable URL does not preserve backward-compatible mirror")

    resources = catalog.get("resources", [])
    by_id = {item.get("id"): item for item in resources if isinstance(item, dict)}
    expected_catalog = {
        "agent-skill-latest": (f"{ORIGIN}/agents/cbt-cards/SKILL.md", latest),
        f"agent-skill-v{latest}": (expected_mirror_url, latest),
        f"agent-skill-v{latest}-portable": (f"{ORIGIN}/agents/cbt-cards/v{latest}/cbt-cards/SKILL.md", latest),
        "agent-skill-install": (f"{ORIGIN}/agents/cbt-cards/INSTALL.md", None),
    }
    for resource_id, (url, version) in expected_catalog.items():
        resource = by_id.get(resource_id)
        if not resource:
            fail(f"catalog missing {resource_id}")
        if resource.get("url") != url:
            fail(f"catalog URL mismatch for {resource_id}")
        if version is not None and resource.get("version") != version:
            fail(f"catalog version mismatch for {resource_id}")

    install = install_path.read_text(encoding="utf-8")
    required_install_fragments = (
        "OpenClaw",
        "~/.openclaw/skills/cbt-cards",
        "openclaw skills list",
        "Hermes Agent",
        "hermes skills install https://cbt-cards.github.io/agents/cbt-cards/SKILL.md --name cbt-cards",
        "https://agentskills.io/specification",
        "skills-ref validate ./cbt-cards",
        expected_mirror_url,
    )
    for fragment in required_install_fragments:
        if fragment not in install:
            fail(f"INSTALL.md missing portability/install fragment: {fragment}")

    print(
        "skill portability check passed: "
        f"v{latest} alias, compatibility mirror, and strict cbt-cards/ distribution are aligned"
    )


if __name__ == "__main__":
    main()
