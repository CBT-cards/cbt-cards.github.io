#!/usr/bin/env python3
"""Dependency-free reference consumer for the CBT Cards reviewed practice RAG distribution.

This client deliberately does not perform free-text semantic routing. It verifies the
published retrieval bundle and supports exact practice lookup or mechanism filtering so
agent runtimes can add their own retrieval layer without silently dropping provenance or
safety metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlparse
from urllib.request import urlopen

ORIGIN = "https://cbt-cards.github.io"
MANIFEST_URL = f"{ORIGIN}/data/practice-rag-manifest.json"
REVIEW_STATUS = "editorial_and_safety_reviewed_for_publication"
CLINICAL_STATUS = "not_claimed"


def _read_bytes(url: str, repo_root: Path | None) -> bytes:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        raise ValueError(f"refusing non-canonical URL: {url}")
    if repo_root is not None:
        path = repo_root / parsed.path.lstrip("/")
        if not path.is_file():
            raise FileNotFoundError(path)
        return path.read_bytes()
    with urlopen(url, timeout=20) as response:
        return response.read()


def _json_bytes(raw: bytes, label: str) -> dict:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def load_bundle(repo_root: Path | None = None) -> tuple[dict, list[dict]]:
    manifest = _json_bytes(_read_bytes(MANIFEST_URL, repo_root), "manifest")
    distribution_url = manifest.get("distribution")
    if not isinstance(distribution_url, str):
        raise ValueError("manifest distribution URL is missing")
    raw = _read_bytes(distribution_url, repo_root)
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != manifest.get("sha256"):
        raise ValueError("distribution SHA-256 does not match the manifest")

    rows = []
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid NDJSON line {line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"NDJSON line {line_number} is not an object")
        rows.append(row)

    if len(rows) != manifest.get("record_count"):
        raise ValueError("distribution record count does not match the manifest")

    seen_chunks = set()
    seen_resources = set()
    for row in rows:
        chunk_id = row.get("chunk_id")
        resource_id = row.get("resource_id")
        if not isinstance(chunk_id, str) or not chunk_id or chunk_id in seen_chunks:
            raise ValueError(f"invalid or duplicate chunk_id: {chunk_id!r}")
        if not isinstance(resource_id, str) or not resource_id or resource_id in seen_resources:
            raise ValueError(f"invalid or duplicate resource_id: {resource_id!r}")
        seen_chunks.add(chunk_id)
        seen_resources.add(resource_id)

        canonical = row.get("canonical_url")
        if not isinstance(canonical, str) or not canonical.startswith(f"{ORIGIN}/practice/#"):
            raise ValueError(f"non-canonical practice URL for {resource_id}")
        if row.get("locale") != "en":
            raise ValueError(f"unexpected locale for {resource_id}")
        if row.get("review_status") != REVIEW_STATUS:
            raise ValueError(f"unexpected review status for {resource_id}")
        if row.get("clinical_validation_status") != CLINICAL_STATUS:
            raise ValueError(f"unexpected clinical-validation status for {resource_id}")
        safety_scope = row.get("safety_scope")
        text = row.get("text")
        if not isinstance(safety_scope, str) or len(safety_scope) < 80:
            raise ValueError(f"missing safety scope for {resource_id}")
        if not isinstance(text, str) or "Avoid when:" not in text:
            raise ValueError(f"safety metadata is not preserved in chunk {resource_id}")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != row.get("sha256"):
            raise ValueError(f"chunk text SHA-256 mismatch for {resource_id}")

    if manifest.get("review_status") != REVIEW_STATUS:
        raise ValueError("manifest review status drift")
    if manifest.get("clinical_validation_status") != CLINICAL_STATUS:
        raise ValueError("manifest clinical-validation status drift")
    return manifest, rows


def _record_view(row: dict) -> dict:
    return {
        "resource_id": row["resource_id"],
        "chunk_id": row["chunk_id"],
        "mechanism_id": row["mechanism_id"],
        "canonical_url": row["canonical_url"],
        "locale": row["locale"],
        "review_status": row["review_status"],
        "clinical_validation_status": row["clinical_validation_status"],
        "safety_scope": row["safety_scope"],
        "text": row["text"],
        "sha256": row["sha256"],
    }


def exact_practice(rows: list[dict], practice_id: str) -> dict:
    matches = [row for row in rows if row["resource_id"] == practice_id]
    if not matches:
        return {
            "result": "no_match",
            "reason": "No reviewed practice exists for that exact practice ID. Do not invent one.",
            "practice_id": practice_id,
        }
    return {"result": "exact_record", "record": _record_view(matches[0])}


def mechanism_candidates(rows: list[dict], mechanism_id: str) -> dict:
    matches = [_record_view(row) for row in rows if row["mechanism_id"] == mechanism_id]
    if not matches:
        return {
            "result": "no_match",
            "reason": "No reviewed practice exists for that exact mechanism ID. Do not infer a diagnosis or invent a practice.",
            "mechanism_id": mechanism_id,
        }
    return {
        "result": "candidate_set",
        "mechanism_id": mechanism_id,
        "records": matches,
        "routing_note": "These are exact mechanism candidates, not a semantic or clinical recommendation.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="Read canonical resources from a local repository checkout instead of HTTPS.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--practice-id", help="Return one exact reviewed practice record by stable ID.")
    group.add_argument("--mechanism", help="Return reviewed records mapped to one exact mechanism ID.")
    group.add_argument("--list", action="store_true", help="List stable IDs and mechanisms without semantic ranking.")
    group.add_argument("--self-check", action="store_true", help="Verify manifest, distribution, record hashes and safety metadata.")
    args = parser.parse_args()

    try:
        manifest, rows = load_bundle(args.repo_root.resolve() if args.repo_root else None)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    if args.practice_id:
        payload = exact_practice(rows, args.practice_id)
    elif args.mechanism:
        payload = mechanism_candidates(rows, args.mechanism)
    elif args.list:
        payload = {
            "result": "inventory",
            "records": [
                {"resource_id": row["resource_id"], "mechanism_id": row["mechanism_id"], "canonical_url": row["canonical_url"]}
                for row in rows
            ],
        }
    else:
        payload = {
            "ok": True,
            "bundle_id": manifest.get("id"),
            "record_count": len(rows),
            "distribution_sha256": manifest.get("sha256"),
            "mode": "local" if args.repo_root else "https",
            "routing_scope": "exact IDs/mechanisms only; no free-text semantic routing",
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
