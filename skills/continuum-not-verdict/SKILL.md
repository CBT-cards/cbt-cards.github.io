---
name: continuum-not-verdict
description: Use when a user turns a graded result into a total success/failure verdict. Rate specific dimensions on a continuum instead of making one global judgment.
license: CC-BY-NC-SA-4.0
compatibility: Portable Agent Skills compatible. No local binaries or private CBT Cards data required.
metadata:
  author: "CBT Cards / MetalHatsCats"
  version: "1.0.0"
  homepage: "https://cbt-cards.github.io/skills/"
  source-id: "practice-continuum-not-verdict"
---

# Use a Continuum, Not a Verdict

## Purpose

Use this skill for one bounded self-reflection task. It is general wellness material, not medical advice, diagnosis, treatment, emergency support, or a substitute for qualified professional care.

## Use when

- Quality, progress, or performance can reasonably vary by degree.

## Do not use when

- The situation truly has a binary safety, legal, compliance, or eligibility requirement.

## Procedure

1. Identify the global verdict.
2. Choose two specific dimensions that actually matter.
3. Rate each dimension from 0–10 with one observable reason.
4. Describe what becomes visible when the result is not forced into one total label.

## Response contract

Return: Old verdict → Dimension 1 score/reason → Dimension 2 score/reason → More precise description.

Keep the response concrete and proportionate. Do not infer a disorder from the user's wording. Do not remove genuine safety measures, protective boundaries, accessibility aids, medication instructions, professional requirements, or legal/compliance controls.

## Source and review

- Source ID: `practice-continuum-not-verdict`
- Reviewed CBT Cards practice: https://cbt-cards.github.io/practice/#practice-continuum-not-verdict
- Marketplace record: https://cbt-cards.github.io/data/skill-marketplace.json
- Review authority: https://cbt-cards.github.io/data/toolkit-review.json
- License: CC BY-NC-SA 4.0

For a technique skill, the reviewed practice record is the authority for fit and `avoid_when`. For a metaphor skill, the toolkit review overlay must explicitly publish the source record for the `agent_skill` surface. If the authoritative source no longer supports this skill, return `no_match` rather than improvising.
