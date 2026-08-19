#!/usr/bin/env python3
"""Render a provenance-first Markdown summary for a completed practice-semantic model evaluation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DIMENSIONS = [
    "fit", "appropriateness", "safety_exclusions", "no_diagnosis", "evidence_fidelity",
    "publication_boundary", "micro_action_fidelity", "no_match", "locale_boundary", "canonical_citation",
]


def fail(message: str) -> None:
    raise SystemExit(f"practice semantic publication report build failed: {message}")


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path}: expected object")
    return value


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execution", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    execution = read(args.execution)
    report = read(args.report)
    coverage = report.get("coverage", {})
    deterministic = report.get("deterministic_contract_metrics", {})
    human = report.get("human_semantic_review", {})
    provenance = report.get("provenance", {})

    if coverage.get("complete_review_cases") != 41:
        fail("refuse to render publishable summary before 41 complete human reviews")
    if human.get("authority") != "human_contextual_review":
        fail("human contextual review authority missing")

    lines = [
        "# CBT Cards practice-semantic model evaluation",
        "",
        "> Benchmark performance is not clinical validation, treatment evidence, or proof that CBT Cards or the evaluated model is appropriate for every person or situation.",
        "",
        "## Execution provenance",
        "",
        f"- Provider: `{esc(execution.get('provider'))}`",
        f"- Runtime: `{esc(execution.get('runtime'))}`",
        f"- Requested model: `{esc(execution.get('requested_model'))}`",
        f"- Started: `{esc(execution.get('started'))}`",
        f"- Completed: `{esc(execution.get('completed'))}`",
        f"- Reasoning effort: `{esc(execution.get('reasoning_effort'))}`",
        f"- Max output tokens per response: `{esc(execution.get('max_output_tokens'))}`",
        f"- Provider storage enabled: `{esc(execution.get('store'))}`",
        f"- Web search enabled: `{esc(execution.get('web_search_enabled'))}`",
        f"- Evaluation manifest SHA-256: `{esc(execution.get('eval_manifest_sha256'))}`",
        f"- Semantic case dataset SHA-256: `{esc(execution.get('semantic_case_dataset_sha256'))}`",
        f"- Prompt SHA-256: `{esc(execution.get('prompt_sha256'))}`",
        f"- Agent Skill SHA-256: `{esc(execution.get('skill_sha256'))}`",
        f"- Responses SHA-256: `{esc(execution.get('responses_sha256'))}`",
        "",
        "Generation exposed only the declared user-message input and frozen CBT Cards context. Benchmark answer-key fields were hidden during generation and were read only after responses were captured.",
        "",
        "## Coverage",
        "",
        f"- Benchmark cases: **{coverage.get('benchmark_cases')}**",
        f"- Captured responses: **{coverage.get('response_cases')}**",
        f"- Complete human review cases: **{coverage.get('complete_review_cases')}**",
        f"- Human reviewer: `{esc(provenance.get('reviewer', {}).get('id'))}`",
        f"- Review date: `{esc(provenance.get('reviewer', {}).get('reviewed_on'))}`",
        "",
        "## Deterministic contract metrics",
        "",
        f"- Contract pass: **{deterministic.get('pass')} / {deterministic.get('cases')}**",
        f"- Contract fail: **{deterministic.get('fail')} / {deterministic.get('cases')}**",
        f"- Safety-critical contract pass: **{deterministic.get('safety_critical_contract_pass')} / {deterministic.get('safety_critical_cases')}**",
        "",
        "Safety-critical categories are reported separately: `genuine-risk`, `required-standard`, `publication-boundary`, and `professional-boundary`.",
        "",
        "### Contract metrics by category",
        "",
        "| Category | Cases | Pass |",
        "|---|---:|---:|",
    ]
    for category, counts in sorted(deterministic.get("by_category", {}).items()):
        lines.append(f"| {esc(category)} | {counts.get('cases', 0)} | {counts.get('contract_pass', 0)} |")

    lines += [
        "",
        "## Human semantic review",
        "",
        "These ratings are separate from deterministic routing/ID matching. They are human editorial/contextual benchmark judgments.",
        "",
        "| Dimension | Pass | Fail | Uncertain | N/A |",
        "|---|---:|---:|---:|---:|",
    ]
    dimensions = human.get("dimensions", {})
    for dimension in DIMENSIONS:
        counts = dimensions.get(dimension, {})
        lines.append(
            f"| {esc(dimension)} | {counts.get('pass',0)} | {counts.get('fail',0)} | "
            f"{counts.get('uncertain',0)} | {counts.get('not_applicable',0)} |"
        )

    lines += ["", "## Frozen context resources", "", "| Resource | SHA-256 | Bytes |", "|---|---|---:|"]
    for item in execution.get("context_resources", []):
        lines.append(f"| {esc(item.get('url'))} | `{esc(item.get('sha256'))}` | {esc(item.get('bytes'))} |")

    lines += ["", "## Limitations", ""]
    for limitation in report.get("limitations", []):
        lines.append(f"- {limitation}")
    lines += [
        "- The benchmark is a finite authored case set and may not represent real-world prevalence or all possible phrasing.",
        "- A result on this frozen generation does not establish generalization to future models, prompts, context revisions, or unseen situations.",
        "- Human semantic review can contain judgment error and should retain reviewer provenance rather than being presented as objective clinical ground truth.",
        "",
        "## Artifact hashes",
        "",
        f"- Review packet SHA-256: `{esc(provenance.get('packet_sha256'))}`",
        f"- Human reviews SHA-256: `{esc(provenance.get('reviews_sha256'))}`",
        f"- Scored report response SHA-256: `{esc(provenance.get('responses_sha256'))}`",
        "",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"practice semantic publication report built -> {args.output}")


if __name__ == "__main__":
    main()
