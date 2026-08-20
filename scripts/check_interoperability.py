#!/usr/bin/env python3
"""Offline smoke test for CBT Cards provider-neutral agent interoperability."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
CLIENT = ROOT / "examples/cbt_cards_http_client.py"
FIXTURES = ROOT / "data/interoperability-fixtures.json"
EXPECTED_CLIENTS = {
    "OpenAI/ChatGPT-compatible": "repository_runner_available",
    "OpenClaw-style Agent Skills consumer": "contract_fixture_documented",
    "Hermes Agent-style skill consumer": "contract_fixture_documented",
    "generic HTTP/RAG client": "ci_contract_exercised",
}


def fail(message: str) -> None:
    raise SystemExit("interoperability check failed: " + message)


def local_path(url: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    return ROOT / parsed.path.lstrip("/")


def run_client(*args: str) -> dict:
    process = subprocess.run(
        [sys.executable, str(CLIENT), "--repo-root", str(ROOT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0:
        fail(f"reference client exited {process.returncode}: {process.stdout} {process.stderr}")
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        fail(f"reference client returned invalid JSON: {exc}")
    if not isinstance(payload, dict):
        fail("reference client output is not an object")
    return payload


def main() -> None:
    if not CLIENT.is_file():
        fail("missing generic reference client")
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.1":
        fail("interoperability fixture schema must be 1.1")
    fixtures = {item.get("client_class"): item for item in data.get("fixtures", [])}
    if set(fixtures) != set(EXPECTED_CLIENTS):
        fail("unexpected interoperability client set")

    for client_class, expected_status in EXPECTED_CLIENTS.items():
        item = fixtures[client_class]
        if item.get("status") != expected_status:
            fail(f"unexpected status for {client_class}")
        entrypoint = local_path(item.get("entrypoint", ""))
        if entrypoint is None or not entrypoint.is_file():
            fail(f"missing entrypoint for {client_class}")
        resources = item.get("expected_resources")
        if not isinstance(resources, list) or not resources or len(resources) != len(set(resources)):
            fail(f"invalid expected_resources for {client_class}")
        for url in resources:
            path = local_path(url)
            if path is None or not path.is_file():
                fail(f"missing canonical resource for {client_class}: {url}")

    for client_class in ("OpenClaw-style Agent Skills consumer", "Hermes Agent-style skill consumer"):
        if "not claimed as continuously CI-executed" not in fixtures[client_class].get("claim", ""):
            fail(f"runtime execution is overstated for {client_class}")

    generic = fixtures["generic HTTP/RAG client"]
    capabilities = set(generic.get("capabilities", []))
    required = {"manifest_hash_verification", "exact_practice_lookup", "mechanism_filter", "explicit_no_match"}
    if not required <= capabilities:
        fail("generic reference-client capabilities are incomplete")

    checked = run_client("--self-check")
    manifest = json.loads((ROOT / "data/practice-rag-manifest.json").read_text(encoding="utf-8"))
    if checked.get("ok") is not True or checked.get("record_count") != manifest.get("record_count"):
        fail("reference-client self-check did not validate the committed bundle")
    if checked.get("distribution_sha256") != manifest.get("sha256") or checked.get("mode") != "local":
        fail("reference-client provenance output drift")

    exact = run_client("--practice-id", "practice-park-and-return")
    record = exact.get("record", {})
    if exact.get("result") != "exact_record" or record.get("mechanism_id") != "worry-postponement":
        fail("exact practice lookup drift")
    if "Avoid when:" not in record.get("text", "") or not record.get("safety_scope"):
        fail("exact lookup dropped safety context")

    candidates = run_client("--mechanism", "worry-postponement")
    if candidates.get("result") != "candidate_set" or not candidates.get("records"):
        fail("mechanism filter drift")
    if "not a semantic or clinical recommendation" not in candidates.get("routing_note", ""):
        fail("mechanism filter overclaims routing")

    missing = run_client("--practice-id", "practice-does-not-exist")
    if missing.get("result") != "no_match" or "Do not invent one" not in missing.get("reason", ""):
        fail("missing practice must return explicit no_match")

    print(
        "interoperability check passed: generic reference client verified locally; "
        "OpenClaw/Hermes remain documentation-only runtime claims"
    )


if __name__ == "__main__":
    main()
