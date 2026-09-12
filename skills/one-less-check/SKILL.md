---
name: one-less-check
description: Use only in ordinary objectively low-risk situations when a user is doing a clearly non-essential extra check or reassurance request. Skip one extra check and observe uncertainty without replacing it.
license: CC-BY-NC-SA-4.0
compatibility: Portable Agent Skills compatible. No local binaries or private CBT Cards data required.
metadata:
  author: "CBT Cards / MetalHatsCats"
  version: "1.0.0"
  homepage: "https://cbt-cards.github.io/skills/"
  source-id: "practice-one-less-check"
---

# One Less Check

## Purpose

Use this skill for one bounded self-reflection task. It is general wellness material, not medical advice, diagnosis, treatment, emergency support, or a substitute for qualified professional care.

## Use when

- The situation is ordinary and objectively low risk.
- The selected check is clearly non-essential and not required.

## Do not use when

- The check prevents plausible material harm.
- The check is required by safety, law, compliance, accessibility, medication, professional instructions, or safeguarding.
- Risk is unclear.

## Procedure

1. Identify exactly one extra check.
2. Verify it is not a real safety or quality requirement.
3. If clearly non-essential, choose to skip only that check.
4. Observe both the outcome and the urge for certainty without adding a substitute reassurance behavior.

## Response contract

Return: Extra check → Why it is non-essential → Observation. If necessity is unclear, return `no_match`.

Keep the response concrete and proportionate. Do not infer a disorder from the user's wording. Do not remove genuine safety measures, protective boundaries, accessibility aids, medication instructions, professional requirements, or legal/compliance controls.

## Source and review

- Source ID: `practice-one-less-check`
- Reviewed CBT Cards practice: https://cbt-cards.github.io/practice/#practice-one-less-check
- Marketplace record: https://cbt-cards.github.io/data/skill-marketplace.json
- Review authority: https://cbt-cards.github.io/data/toolkit-review.json
- License: CC BY-NC-SA 4.0

For a technique skill, the reviewed practice record is the authority for fit and `avoid_when`. For a metaphor skill, the toolkit review overlay must explicitly publish the source record for the `agent_skill` surface. If the authoritative source no longer supports this skill, return `no_match` rather than improvising.
