#!/usr/bin/env python3
"""Cross-file semantic validation for the reviewed CBT Cards practice system."""

from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
REVIEW_STATUS = "editorial_and_safety_reviewed_for_publication"
CLINICAL_STATUS = "not_claimed"
REQUIRED_CATEGORIES = {
    "fit",
    "ambiguity",
    "genuine-risk",
    "required-standard",
    "publication-boundary",
    "professional-boundary",
    "no-match",
    "progression",
}
SYMMETRIC_RELATIONS = {"pairs_with", "not_same_as"}
EXPECTED_CLIENTS = {
    "OpenAI/ChatGPT-compatible": "repository_runner_available",
    "OpenClaw-style Agent Skills consumer": "contract_fixture_documented",
    "Hermes Agent-style skill consumer": "contract_fixture_documented",
    "generic HTTP/RAG client": "ci_contract_exercised",
}


def fail(message: str) -> None:
    raise SystemExit("practice-system check failed: " + message)


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_jsonl(path: str):
    return [json.loads(line) for line in (ROOT / path).read_text(encoding="utf-8").splitlines() if line.strip()]


def unique(records, key: str, label: str) -> dict:
    values = [record.get(key) for record in records]
    if any(not isinstance(value, str) or not value for value in values):
        fail(f"{label} has missing/invalid {key}")
    if len(values) != len(set(values)):
        fail(f"duplicate {label} {key}")
    return {record[key]: record for record in records}


def local_url(url: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return None
    return ROOT / parsed.path.lstrip("/")


def require_date(value: str, label: str) -> None:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        fail(f"invalid date for {label}: {value!r}")


def validate_source_graph():
    practice = load_json("data/practice.json")
    practices = practice.get("practices", [])
    by_practice = unique(practices, "id", "practice")
    if len(practices) != 11:
        fail(f"expected current reviewed set of 11 practices, found {len(practices)}")
    if practice.get("review_status") != REVIEW_STATUS or practice.get("clinical_validation_status") != CLINICAL_STATUS:
        fail("practice root review/clinical boundary")
    if len(practice.get("safety_scope", "")) < 80:
        fail("practice root safety scope is unexpectedly weak")

    ontology = load_json("data/practice-ontology.json")
    mechanisms = ontology.get("mechanisms", [])
    situations = ontology.get("situations", [])
    by_mechanism = unique(mechanisms, "id", "mechanism")
    by_situation = unique(situations, "id", "situation")
    if len(by_mechanism) != 11 or len(by_situation) != 11:
        fail("current ontology must contain 11 unique mechanisms and 11 unique situations")
    for mechanism in mechanisms:
        if len(mechanism.get("label", "")) < 3 or len(mechanism.get("description", "")) < 20:
            fail("mechanism missing meaningful label/description: " + mechanism["id"])
    for situation in situations:
        refs = situation.get("mechanism_ids")
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
            fail("situation mechanism_ids invalid: " + situation["id"])
        if not set(refs) <= set(by_mechanism):
            fail("situation references unknown mechanism: " + situation["id"])
        if len(situation.get("label", "")) < 20:
            fail("situation label too weak: " + situation["id"])

    evidence = load_json("data/practice-evidence.json")
    evidence_rows = evidence.get("evidence", [])
    by_evidence = unique(evidence_rows, "id", "evidence")
    for item in evidence_rows:
        if item.get("evidence_class") not in {"guideline_supported", "authoritative_self_help", "clinical_resource", "practical_editorial"}:
            fail("unknown evidence class: " + item["id"])
        if not isinstance(item.get("url"), str) or not item["url"].startswith("https://"):
            fail("evidence URL must be HTTPS: " + item["id"])
        supports = item.get("supports")
        if not isinstance(supports, list) or not supports or len(supports) != len(set(supports)):
            fail("evidence supports invalid: " + item["id"])
        if not set(supports) <= set(by_mechanism):
            fail("evidence supports unknown mechanism: " + item["id"])
        if len(item.get("claim_scope", "")) < 30 or len(item.get("does_not_establish", "")) < 30:
            fail("evidence claim/limitation scope too weak: " + item["id"])
        require_date(item.get("reviewed_on"), "evidence " + item["id"])

    mechanism_practices = {mid: [] for mid in by_mechanism}
    situation_practices = {sid: [] for sid in by_situation}
    referenced_evidence = set()
    for item in practices:
        pid = item["id"]
        if item.get("review_status") != REVIEW_STATUS or item.get("clinical_validation_status") != CLINICAL_STATUS:
            fail("practice review boundary: " + pid)
        mechanism_id = item.get("mechanism_id")
        if mechanism_id not in by_mechanism:
            fail("practice mechanism ref: " + pid)
        mechanism_practices[mechanism_id].append(pid)
        situation_ids = item.get("situation_ids")
        if not isinstance(situation_ids, list) or not situation_ids or len(situation_ids) != len(set(situation_ids)):
            fail("practice situation_ids invalid: " + pid)
        if not set(situation_ids) <= set(by_situation):
            fail("practice situation ref: " + pid)
        for sid in situation_ids:
            situation_practices[sid].append(pid)
            if mechanism_id not in by_situation[sid]["mechanism_ids"]:
                fail(f"practice {pid} mechanism is not allowed by situation {sid}")
        evidence_ids = item.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids or len(evidence_ids) != len(set(evidence_ids)):
            fail("practice evidence_ids invalid: " + pid)
        if not set(evidence_ids) <= set(by_evidence):
            fail("practice evidence ref: " + pid)
        referenced_evidence.update(evidence_ids)
        if not any(mechanism_id in by_evidence[eid]["supports"] for eid in evidence_ids):
            fail(f"practice {pid} has no cited evidence supporting declared mechanism {mechanism_id}")
        for field in ("best_used_when", "avoid_when"):
            values = item.get(field)
            if not isinstance(values, list) or len(values) < 1 or len(values) != len(set(values)):
                fail(f"practice {pid} {field} invalid")
        if len(item["avoid_when"]) < 3:
            fail("practice exclusions too weak: " + pid)
        if item.get("canonical_url") != f"{ORIGIN}/practice/#{pid}":
            fail("practice canonical mismatch: " + pid)
        for field in ("title", "micro_action", "prompt", "reflection_question"):
            if not isinstance(item.get(field), str) or len(item[field].strip()) < 8:
                fail(f"practice {pid} missing meaningful {field}")

    orphan_mechanisms = [mid for mid, pids in mechanism_practices.items() if not pids]
    orphan_situations = [sid for sid, pids in situation_practices.items() if not pids]
    if orphan_mechanisms or orphan_situations:
        fail(f"orphan ontology entities mechanisms={orphan_mechanisms} situations={orphan_situations}")
    if set(by_evidence) != referenced_evidence:
        fail("orphan evidence entries: " + ", ".join(sorted(set(by_evidence) - referenced_evidence)))

    return practice, by_practice, by_mechanism, by_situation, by_evidence


def validate_recommendations(by_practice, by_situation):
    data = load_json("data/practice-recommendations.json")
    rules = data.get("behavior_rules")
    if not isinstance(rules, list) or len(rules) < 6 or len(rules) != len(set(rules)):
        fail("recommendation behavior rules")
    joined = " ".join(rules).lower()
    for fragment in ("no_match", "at most three", "avoid_when", "source-only", "not evidence", "do not diagnose"):
        if fragment not in joined:
            fail("recommendation rules missing boundary: " + fragment)
    examples = data.get("examples", [])
    unique(examples, "id", "recommendation example")
    for example in examples:
        result = example.get("result")
        pids = example.get("practice_ids")
        if result not in {"match", "ambiguous", "no_match"}:
            fail("recommendation result: " + example["id"])
        if not isinstance(pids, list) or len(pids) != len(set(pids)) or not set(pids) <= set(by_practice):
            fail("recommendation practice refs: " + example["id"])
        if result == "match" and len(pids) != 1:
            fail("match example must select exactly one practice: " + example["id"])
        if result == "ambiguous" and not 2 <= len(pids) <= 3:
            fail("ambiguous example must select 2-3 practices: " + example["id"])
        if result == "no_match" and pids:
            fail("no_match example cannot select practice IDs: " + example["id"])
        sid = example.get("situation_id")
        if sid is not None:
            if sid not in by_situation:
                fail("recommendation situation ref: " + example["id"])
            if result == "match" and sid not in by_practice[pids[0]]["situation_ids"]:
                fail("recommendation match does not fit declared situation: " + example["id"])
        if result != "match" and not isinstance(example.get("why"), str):
            fail("non-match/ambiguous recommendation example requires why: " + example["id"])


def validate_relations(by_practice):
    data = load_json("data/practice-relations.json")
    types = data.get("relation_types")
    if not isinstance(types, list) or len(types) != len(set(types)) or not set(SYMMETRIC_RELATIONS) <= set(types):
        fail("relation type vocabulary")
    seen = set()
    symmetric_seen = set()
    for relation in data.get("relations", []):
        source, target, kind = relation.get("from"), relation.get("to"), relation.get("type")
        if source not in by_practice or target not in by_practice or source == target or kind not in types:
            fail("invalid relation endpoint/type")
        key = (source, target, kind)
        if key in seen:
            fail("duplicate relation: " + repr(key))
        seen.add(key)
        if kind in SYMMETRIC_RELATIONS:
            normalized = (tuple(sorted((source, target))), kind)
            if normalized in symmetric_seen:
                fail("duplicate symmetric relation pair: " + repr(normalized))
            symmetric_seen.add(normalized)
        if len(relation.get("note", "")) < 20:
            fail("relation note too weak: " + repr(key))


def validate_semantic_evals(by_practice):
    manifest = load_json("data/practice-semantic-evals.json")
    cases = load_jsonl("data/practice-semantic-evals-a.jsonl") + load_jsonl("data/practice-semantic-evals-b.jsonl")
    unique(cases, "id", "semantic case")
    messages = [case.get("user_message") for case in cases]
    if len(messages) != len(set(messages)):
        fail("duplicate semantic user_message")
    if len(cases) != 41 or manifest.get("case_count") != len(cases):
        fail("semantic eval count must be exactly 41")
    categories = {case.get("category") for case in cases}
    if not REQUIRED_CATEGORIES <= categories:
        fail("semantic category coverage: missing " + repr(sorted(REQUIRED_CATEGORIES - categories)))
    for case in cases:
        outcome = case.get("expected_outcome")
        pids = case.get("acceptable_practice_ids")
        if outcome not in {"match", "ambiguous", "no_match"}:
            fail("semantic outcome: " + case["id"])
        if not isinstance(pids, list) or len(pids) != len(set(pids)) or not set(pids) <= set(by_practice):
            fail("semantic practice refs: " + case["id"])
        if outcome == "match" and not pids:
            fail("match semantic case needs acceptable practice: " + case["id"])
        if outcome == "ambiguous" and not 2 <= len(pids) <= 3:
            fail("ambiguous semantic case needs 2-3 acceptable practices: " + case["id"])
        if outcome == "no_match" and pids:
            fail("no_match semantic case cannot accept practice IDs: " + case["id"])
        notes = case.get("required_safety_notes")
        if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
            fail("semantic safety notes: " + case["id"])
        if case.get("category") in {"genuine-risk", "required-standard", "professional-boundary", "publication-boundary", "no-match"} and outcome != "no_match":
            fail("boundary semantic case must no_match: " + case["id"])
    risk = [case for case in cases if case["category"] in {"genuine-risk", "required-standard", "professional-boundary"}]
    if len(risk) < 12:
        fail("insufficient genuine-risk/required/professional boundary coverage")
    return cases


def validate_rag(practice, by_practice):
    text = (ROOT / "data/practice-rag.ndjson").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line]
    by_chunk = unique(rows, "chunk_id", "RAG chunk")
    by_resource = unique(rows, "resource_id", "RAG resource")
    if set(by_resource) != set(by_practice):
        fail("RAG resource set differs from reviewed practice set")
    for pid, row in by_resource.items():
        source = by_practice[pid]
        expected = {
            "chunk_id": f"{pid}:en:v1",
            "canonical_url": source["canonical_url"],
            "locale": "en",
            "mechanism_id": source["mechanism_id"],
            "review_status": REVIEW_STATUS,
            "clinical_validation_status": CLINICAL_STATUS,
            "safety_scope": practice["safety_scope"],
        }
        for key, value in expected.items():
            if row.get(key) != value:
                fail(f"RAG {pid} {key} drift")
        if "Avoid when:" not in row.get("text", "") or "not clinically validated" not in row.get("text", ""):
            fail("RAG safety/review text missing: " + pid)
        for exclusion in source["avoid_when"]:
            if exclusion not in row["text"]:
                fail(f"RAG {pid} lost exclusion: {exclusion}")
        if hashlib.sha256(row["text"].encode("utf-8")).hexdigest() != row.get("sha256"):
            fail("RAG text hash: " + pid)
    if len(by_chunk) != len(by_practice):
        fail("RAG chunk count")

    manifest = load_json("data/practice-rag-manifest.json")
    if manifest.get("record_count") != len(rows):
        fail("RAG manifest record_count")
    if manifest.get("distribution") != f"{ORIGIN}/data/practice-rag.ndjson":
        fail("RAG manifest distribution URL")
    if manifest.get("sha256") != hashlib.sha256(text.encode("utf-8")).hexdigest():
        fail("RAG manifest distribution hash")
    if manifest.get("chunk_id_format") != "{resource_id}:en:v1" or manifest.get("review_status") != REVIEW_STATUS or manifest.get("clinical_validation_status") != CLINICAL_STATUS:
        fail("RAG manifest version/review metadata")
    generated_from = manifest.get("generated_from")
    if not isinstance(generated_from, list) or len(generated_from) < 2:
        fail("RAG manifest generated_from provenance")
    for source in generated_from:
        path = local_url(source.get("url", ""))
        if path is None or not path.is_file():
            fail("RAG generated_from local target")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
            fail("RAG generated_from hash drift: " + source["url"])


def validate_coverage(by_practice, by_mechanism, cases):
    data = load_json("data/practice-coverage.json")
    rows = data.get("mechanisms", [])
    by_row = unique(rows, "mechanism_id", "coverage mechanism")
    if set(by_row) != set(by_mechanism):
        fail("coverage mechanism set drift")
    for mid, row in by_row.items():
        expected_pids = [pid for pid, practice in by_practice.items() if practice["mechanism_id"] == mid]
        if row.get("practice_ids") != expected_pids:
            fail("coverage practice IDs drift: " + mid)
        expected_count = sum(bool(set(case.get("acceptable_practice_ids", [])) & set(expected_pids)) for case in cases)
        if row.get("eval_case_count") != expected_count:
            fail("coverage eval count drift: " + mid)
    summary = data.get("summary", {})
    if summary.get("mechanisms") != len(by_mechanism) or summary.get("published_practices") != len(by_practice) or summary.get("semantic_eval_cases") != len(cases):
        fail("coverage summary counts")
    queue = data.get("editorial_queue", {})
    if set(queue.get("status_definitions", {})) != {"covered_single_practice", "covered_multiple_practices", "needs_practice", "needs_evidence", "needs_eval_coverage"}:
        fail("coverage editorial queue taxonomy")
    qrows = queue.get("items", [])
    if {row.get("mechanism_id") for row in qrows} != set(by_mechanism):
        fail("coverage editorial queue mechanism set")
    pressure = queue.get("source_audit_pressure", {})
    for key in ("similarity_groups", "flagged_source_records", "owned_practice_overlap_practices", "priority_source_review_items", "note"):
        if key not in pressure:
            fail("coverage duplicate-pressure signal missing: " + key)


def validate_interoperability():
    data = load_json("data/interoperability-fixtures.json")
    fixtures = data.get("fixtures", [])
    by_client = unique(fixtures, "client_class", "interoperability fixture")
    if set(by_client) != set(EXPECTED_CLIENTS):
        fail("interoperability client class set")
    for client, expected_status in EXPECTED_CLIENTS.items():
        fixture = by_client[client]
        if fixture.get("status") != expected_status:
            fail("interoperability status drift: " + client)
        entry = local_url(fixture.get("entrypoint", ""))
        if entry is None or not entry.is_file():
            fail("interoperability entrypoint missing: " + client)
        resources = fixture.get("expected_resources")
        if not isinstance(resources, list) or not resources or len(resources) != len(set(resources)):
            fail("interoperability expected_resources: " + client)
        for url in resources:
            target = local_url(url)
            if target is None or not target.is_file():
                fail(f"interoperability resource missing for {client}: {url}")
        claim = fixture.get("claim", "")
        if len(claim) < 30:
            fail("interoperability claim too weak: " + client)
    if "not claimed as continuously CI-executed" not in by_client["OpenClaw-style Agent Skills consumer"]["claim"]:
        fail("OpenClaw fixture overstates execution")
    if "not claimed as continuously CI-executed" not in by_client["Hermes Agent-style skill consumer"]["claim"]:
        fail("Hermes fixture overstates execution")
    install = (ROOT / "agents/cbt-cards/INSTALL.md").read_text(encoding="utf-8")
    if "OpenClaw" not in install or "Hermes" not in install:
        fail("portable client install notes missing")


def validate_public_page(by_practice):
    page = (ROOT / "practice/index.html").read_text(encoding="utf-8")
    for fragment in ('id="finder"', 'id="methodology"', "local-only", "no_match", "Evidence and limitations", "Best used when", "Avoid when"):
        if fragment not in page:
            fail("practice page missing: " + fragment)
    if page.count("<details><summary>Evidence and limitations</summary>") != len(by_practice):
        fail("practice page must expose evidence/limitations for every practice")
    for pid in by_practice:
        if f'id="{pid}"' not in page:
            fail("practice page missing article: " + pid)


def main() -> None:
    practice, by_practice, by_mechanism, by_situation, _ = validate_source_graph()
    validate_recommendations(by_practice, by_situation)
    validate_relations(by_practice)
    cases = validate_semantic_evals(by_practice)

    subprocess.run([sys.executable, str(ROOT / "scripts/build_practice_artifacts.py"), "--check"], check=True)
    validate_rag(practice, by_practice)
    validate_coverage(by_practice, by_mechanism, cases)
    validate_interoperability()
    validate_public_page(by_practice)

    print(
        f"practice-system check passed: {len(by_practice)} practices, {len(by_mechanism)} mechanisms, "
        f"{len(by_situation)} situations, {len(cases)} semantic cases; generated RAG/coverage/page in sync"
    )


if __name__ == "__main__":
    main()
