#!/usr/bin/env python3
"""Deterministically build CBT Cards practice RAG, coverage and human page artifacts."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
REVIEW_STATUS = "editorial_and_safety_reviewed_for_publication"
CLINICAL_STATUS = "not_claimed"
RELATION_LABELS = {
    "pairs_with": "Pairs with",
    "often_precedes": "Often precedes",
    "follow_up_with": "Follow up with",
    "alternative_when": "Alternative when",
    "not_same_as": "Not the same as",
}


def read_bytes(path: str) -> bytes:
    return (ROOT / path).read_bytes()


def load_json(path: str) -> dict[str, Any]:
    return json.loads(read_bytes(path))


def load_jsonl(path: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (ROOT / path).read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def compact_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def title_sentence(title: str) -> str:
    return title if title.endswith((".", "?", "!")) else title + "."


def build_rag() -> tuple[str, dict[str, Any]]:
    practice = load_json("data/practice.json")
    ontology_bytes = read_bytes("data/practice-ontology.json")
    practice_bytes = read_bytes("data/practice.json")
    rows: list[dict[str, Any]] = []
    for item in practice["practices"]:
        text = (
            f"{title_sentence(item['title'])} {item['prompt']} "
            f"Action: {item['micro_action']} "
            f"Avoid when: {'; '.join(item['avoid_when'])}. "
            "Editorial/safety reviewed; not clinically validated."
        )
        rows.append(
            {
                "chunk_id": f"{item['id']}:en:v1",
                "resource_id": item["id"],
                "canonical_url": item["canonical_url"],
                "locale": "en",
                "mechanism_id": item["mechanism_id"],
                "review_status": item["review_status"],
                "clinical_validation_status": item["clinical_validation_status"],
                "safety_scope": practice["safety_scope"],
                "text": text,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )
    distribution = compact_jsonl(rows)
    ontology = load_json("data/practice-ontology.json")
    manifest = {
        "schema_version": "1.0",
        "id": "cbt-cards-practice-rag-v1",
        "generated": max(practice.get("updated", "2026-08-18"), ontology.get("updated", "2026-08-18")),
        "record_count": len(rows),
        "distribution": f"{ORIGIN}/data/practice-rag.ndjson",
        "sha256": hashlib.sha256(distribution.encode("utf-8")).hexdigest(),
        "chunk_id_format": "{resource_id}:en:v1",
        "review_status": REVIEW_STATUS,
        "clinical_validation_status": CLINICAL_STATUS,
        "generated_from": [
            {"url": f"{ORIGIN}/data/practice.json", "sha256": sha256_bytes(practice_bytes)},
            {"url": f"{ORIGIN}/data/practice-ontology.json", "sha256": sha256_bytes(ontology_bytes)},
        ],
        "rule": "one reviewed practice per chunk; safety exclusions and safety scope stay in the same chunk; embeddings are not canonical",
    }
    return distribution, manifest


def build_coverage() -> dict[str, Any]:
    practice = load_json("data/practice.json")
    ontology = load_json("data/practice-ontology.json")
    evidence = load_json("data/practice-evidence.json")
    relations = load_json("data/practice-relations.json")
    locales = load_json("data/locales.json")
    translations = load_jsonl("data/translations.jsonl")
    audit = load_json("data/toolkit-audit.json")
    cases = load_jsonl("data/practice-semantic-evals-a.jsonl") + load_jsonl("data/practice-semantic-evals-b.jsonl")

    practice_by_id = {item["id"]: item for item in practice["practices"]}
    evidence_by_id = {item["id"]: item for item in evidence["evidence"]}
    practices_by_mechanism: dict[str, list[str]] = {item["id"]: [] for item in ontology["mechanisms"]}
    for item in practice["practices"]:
        practices_by_mechanism[item["mechanism_id"]].append(item["id"])

    mechanism_rows: list[dict[str, Any]] = []
    queue_items: list[dict[str, Any]] = []
    for mechanism in ontology["mechanisms"]:
        mechanism_id = mechanism["id"]
        pids = practices_by_mechanism[mechanism_id]
        eval_count = sum(bool(set(case.get("acceptable_practice_ids", [])) & set(pids)) for case in cases)
        evidence_complete = bool(pids) and all(
            any(mechanism_id in evidence_by_id[eid].get("supports", []) for eid in practice_by_id[pid]["evidence_ids"])
            for pid in pids
        )
        if not pids:
            queue_status = "needs_practice"
        elif not evidence_complete:
            queue_status = "needs_evidence"
        elif eval_count == 0:
            queue_status = "needs_eval_coverage"
        elif len(pids) == 1:
            queue_status = "covered_single_practice"
        else:
            queue_status = "covered_multiple_practices"
        mechanism_rows.append(
            {
                "mechanism_id": mechanism_id,
                "status": "covered" if queue_status.startswith("covered_") else "needs_work",
                "practice_ids": pids,
                "eval_case_count": eval_count,
                "evidence_complete": evidence_complete,
            }
        )
        queue_items.append(
            {
                "mechanism_id": mechanism_id,
                "status": queue_status,
                "practice_ids": pids,
                "eval_case_count": eval_count,
                "evidence_complete": evidence_complete,
            }
        )

    published_locales = [item["locale"] for item in locales["locales"] if item.get("public_html")]
    draft_locales = sorted({row["locale"] for row in translations if row.get("translation_status") == "machine_draft"})
    planned_locales = [item["locale"] for item in locales["locales"] if item.get("status") == "planned"]
    audit_summary = audit["summary"]
    generated = max(
        practice.get("updated", "2026-08-18"),
        ontology.get("updated", "2026-08-18"),
        evidence.get("updated", "2026-08-18"),
        relations.get("updated", "2026-08-18"),
        locales.get("updated", "2026-08-18"),
        audit.get("updated", "2026-08-18"),
    )
    return {
        "schema_version": "1.0",
        "generated": generated,
        "purpose": "Editorial planning only; not a claim that CBT is complete.",
        "mechanisms": mechanism_rows,
        "editorial_queue": {
            "status_definitions": {
                "covered_single_practice": "Mechanism has one reviewed practice, supporting evidence provenance, and at least one semantic case; expand only for a distinct user need, not page count.",
                "covered_multiple_practices": "Mechanism has multiple reviewed practices; check overlap before adding another.",
                "needs_practice": "Ontology mechanism has no reviewed practice.",
                "needs_evidence": "A reviewed practice lacks evidence provenance that supports its declared mechanism.",
                "needs_eval_coverage": "Mechanism has a reviewed/evidenced practice but no semantic case that accepts it.",
            },
            "items": queue_items,
            "source_audit_pressure": {
                "similarity_groups": audit_summary.get("similarity_groups", len(audit.get("similarity_groups", []))),
                "flagged_source_records": audit_summary.get("flagged_records"),
                "owned_practice_overlap_practices": len(audit.get("owned_practice_overlaps", {})),
                "priority_source_review_items": len(audit.get("priority_review_queue", [])),
                "note": "Source-corpus similarity and overlap are duplicate-pressure signals only. They do not create or publish practices.",
            },
        },
        "summary": {
            "mechanisms": len(ontology["mechanisms"]),
            "published_practices": len(practice["practices"]),
            "semantic_eval_cases": len(cases),
            "relation_edges": len(relations["relations"]),
            "published_locales": published_locales,
            "machine_draft_locales": draft_locales,
            "planned_locales": planned_locales,
        },
    }


def li(values: list[str]) -> str:
    return "".join(f"<li>{html.escape(value)}</li>" for value in values)


def build_page() -> str:
    practice = load_json("data/practice.json")
    ontology = load_json("data/practice-ontology.json")
    evidence = load_json("data/practice-evidence.json")
    relations = load_json("data/practice-relations.json")
    practice_by_id = {item["id"]: item for item in practice["practices"]}
    evidence_by_id = {item["id"]: item for item in evidence["evidence"]}
    outgoing: dict[str, list[dict[str, Any]]] = {pid: [] for pid in practice_by_id}
    for relation in relations["relations"]:
        outgoing[relation["from"]].append(relation)

    options = "".join(
        f'<option value="{html.escape(situation["id"])}">{html.escape(situation["label"])}</option>'
        for situation in ontology["situations"]
    )
    summary_items = "".join(
        f'<li><a href="#{item["id"]}">{html.escape(item["title"])}</a> — {html.escape(item["micro_action"])}</li>'
        for item in practice["practices"]
    )
    articles: list[str] = []
    for item in practice["practices"]:
        evidence_items = []
        for evidence_id in item["evidence_ids"]:
            ev = evidence_by_id[evidence_id]
            evidence_items.append(
                f'<li><a href="{html.escape(ev["url"])}">{html.escape(ev["title"])}</a> '
                f'<span class="source-note">({html.escape(ev["evidence_class"])})</span><br/>'
                f'{html.escape(ev["claim_scope"])}<br/><strong>Does not establish:</strong> {html.escape(ev["does_not_establish"])}</li>'
            )
        relation_items = []
        for relation in outgoing[item["id"]]:
            target = practice_by_id[relation["to"]]
            relation_items.append(
                f'<li><strong>{RELATION_LABELS[relation["type"]]}:</strong> '
                f'<a href="#{target["id"]}">{html.escape(target["title"])}</a> — {html.escape(relation["note"])}</li>'
            )
        relation_html = f'<h4>Related / next</h4><ul>{"".join(relation_items)}</ul>' if relation_items else ""
        articles.append(
            f'<article id="{item["id"]}"><h3>{html.escape(item["title"])}</h3>'
            f'<p>{html.escape(item["prompt"])}</p>'
            f'<p><strong>Action:</strong> {html.escape(item["micro_action"])}</p>'
            f'<h4>Best used when</h4><ul>{li(item["best_used_when"])}</ul>'
            f'<h4>Avoid when</h4><ul>{li(item["avoid_when"])}</ul>'
            f'<p><strong>Reflection:</strong> {html.escape(item["reflection_question"])}</p>'
            f'<details><summary>Evidence and limitations</summary><ul>{"".join(evidence_items)}</ul></details>'
            f'{relation_html}</article>'
        )

    situation_map: dict[str, list[str]] = {}
    for situation in ontology["situations"]:
        allowed = set(situation["mechanism_ids"])
        situation_map[situation["id"]] = [
            item["id"] for item in practice["practices"] if item["mechanism_id"] in allowed and situation["id"] in item["situation_ids"]
        ]
    title_map = {item["id"]: item["title"] for item in practice["practices"]}
    mapping_js = json.dumps(situation_map, ensure_ascii=False, separators=(",", ":"))
    titles_js = json.dumps(title_map, ensure_ascii=False, separators=(",", ":"))

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Practice Finder & reviewed cards — CBT Cards</title><meta name="description" content="Situation-first reviewed CBT-inspired reflection practices with explicit safety boundaries, evidence provenance and agent-ready data."/><meta name="robots" content="index,follow,max-image-preview:large"/><link rel="canonical" href="{ORIGIN}/practice/"/><link rel="stylesheet" href="/styles.css?v=20260818"/><link rel="icon" href="/assets/app-icon.png"/></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap nav"><a class="brand" href="/"><img src="/assets/app-icon.webp" width="42" height="42" alt="" decoding="async"/>CBT Cards</a><nav class="nav-links"><a href="/learn/">Learn</a><a href="/practice/">Practice</a><a href="/worksheets/">Worksheets</a><a href="/toolkit/">Toolkit</a><a href="/about/">About</a></nav></div></header>
<main id="main"><section class="page-hero"><div class="wrap"><h1>Start with the situation, not a diagnosis.</h1><p class="lede">{len(practice['practices'])} reviewed practices. Same mechanism map for people and agents. Genuine safety rules outrank a reflection exercise.</p></div></section>
<section class="section alt"><div class="wrap prose" id="finder"><h2>Practice Finder</h2><p>This finder is <strong>local-only</strong>; your selection is not submitted. It is navigation, not assessment.</p><label for="s">Situation</label> <select id="s"><option value="">Choose a situation…</option>{options}</select> <button id="go" type="button">Find</button><div id="out" aria-live="polite"><p>No JavaScript? Browse below. If nothing fits, the correct practice-layer result is <code>no_match</code>, not an invented card.</p></div></div></section>
<section class="section"><div class="wrap prose"><h2>Reviewed practices</h2><p>{html.escape(practice['safety_scope'])}</p><ul>{summary_items}</ul>{''.join(articles)}</div></section>
<section class="section alt"><div class="wrap prose" id="methodology"><h2>Evidence and editorial method</h2><p>Reviewed means claim scope, sources and safety boundaries were checked for public use. It does not mean the short card format has independent efficacy evidence or that it suits an individual. Evidence may be guideline-supported, authoritative self-help, clinical-resource, or practical editorial synthesis. No numeric truth score is used. Metaphors are memory aids, not evidence.</p><p>Each practice above exposes the same <strong>best used when</strong>, <strong>avoid when</strong>, evidence-provenance and reviewed relation data that agents receive. Source limitations are shown alongside evidence so a citation is not mistaken for validation of the exact card format.</p><p>Do not use this layer to override genuine danger, protective boundaries, accessibility aids, medication/professional instructions, required safety checks, or medical/legal/financial/safeguarding decisions. Agents return <code>no_match</code> in those cases.</p><p>Data: <a href="/data/practice.json">practice records</a>, <a href="/data/practice-ontology.json">ontology</a>, <a href="/data/practice-evidence.json">evidence</a>, <a href="/data/practice-relations.json">relations</a>, <a href="/data/practice-semantic-evals.json">semantic eval manifest</a>, <a href="/data/practice-rag.ndjson">RAG</a>, <a href="/data/practice-coverage.json">coverage</a>.</p></div></section></main>
<footer class="footer"><div class="wrap footer-grid"><div>© 2026 CBT Cards</div><nav><a href="/learn/">Learn</a><a href="/practice/">Practice</a><a href="/agents/">For agents</a></nav></div></footer>
<script>const M={mapping_js},T={titles_js};document.getElementById('go').onclick=()=>{{const key=document.getElementById('s').value;const found=M[key]||[];document.getElementById('out').innerHTML=found.length?'<p>'+found.map(x=>'<a href="#'+x+'">'+T[x]+'</a>').join(', ')+' — read best-use, exclusions, evidence and related-practice notes below.</p>':'<p><code>no_match</code></p>';}};</script></body></html>
'''


def expected_outputs() -> dict[str, str]:
    rag, manifest = build_rag()
    return {
        "data/practice-rag.ndjson": rag,
        "data/practice-rag-manifest.json": canonical_json(manifest),
        "data/practice-coverage.json": canonical_json(build_coverage()),
        "practice/index.html": build_page(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write deterministic artifacts")
    mode.add_argument("--check", action="store_true", help="fail if committed artifacts differ")
    args = parser.parse_args()
    outputs = expected_outputs()
    if args.write:
        for path, content in outputs.items():
            (ROOT / path).write_text(content, encoding="utf-8")
        print("wrote deterministic practice RAG/manifest/coverage/page artifacts")
        return
    stale = []
    for path, expected in outputs.items():
        actual = (ROOT / path).read_text(encoding="utf-8")
        if actual != expected:
            stale.append(path)
    if stale:
        raise SystemExit(
            "practice artifact generation check failed; run "
            "`python3 scripts/build_practice_artifacts.py --write`; stale: " + ", ".join(stale)
        )
    print("practice artifact generation check passed: RAG, manifest, coverage and page match source data")


if __name__ == "__main__":
    main()
