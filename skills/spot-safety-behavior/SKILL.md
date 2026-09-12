---
name: spot-safety-behavior
description: Use only in objectively low-risk situations to identify an extra reassurance, checking, or protective behavior that may block learning. Never remove a genuine safety measure.
license: CC-BY-NC-SA-4.0
compatibility: Portable Agent Skills compatible. No local binaries or private CBT Cards data required.
metadata:
  author: "CBT Cards / MetalHatsCats"
  version: "1.0.0"
  homepage: "https://cbt-cards.github.io/skills/"
  source-id: "practice-spot-the-safety-behavior"
---

# Spot the Safety Behavior

## Purpose

Use this skill for one bounded self-reflection task. It is general wellness material, not medical advice, diagnosis, treatment, emergency support, or a substitute for qualified professional care.

## Use when

- The situation is objectively low risk.
- The behavior may be extra anxiety-management rather than a real safety requirement.

## Do not use when

- Real-world safety is uncertain.
- The behavior is required for safety, accessibility, medication, professional practice, law, compliance, or safeguarding.
- Removing the behavior could plausibly cause material harm.

## Procedure

1. Name the extra behavior neutrally.
2. Check whether it is genuinely protective in the real world.
3. If safety is unclear, stop and return `no_match`.
4. If clearly non-essential, explain what the behavior may prevent the user from learning. Do not instruct removal unless the user is choosing a bounded low-risk experiment.

## Response contract

Return: Possible safety behavior → Real protection check → Learning it may block. Prefer `no_match` when protection is uncertain.

Keep the response concrete and proportionate. Do not infer a disorder from the user's wording. Do not remove genuine safety measures, protective boundaries, accessibility aids, medication instructions, professional requirements, or legal/compliance controls.

## Source and review

- Source ID: `practice-spot-the-safety-behavior`
- Reviewed CBT Cards practice: https://cbt-cards.github.io/practice/#practice-spot-the-safety-behavior
- Marketplace record: https://cbt-cards.github.io/data/skill-marketplace.json
- Review authority: https://cbt-cards.github.io/data/toolkit-review.json
- License: CC BY-NC-SA 4.0

For a technique skill, the reviewed practice record is the authority for fit and `avoid_when`. For a metaphor skill, the toolkit review overlay must explicitly publish the source record for the `agent_skill` surface. If the authoritative source no longer supports this skill, return `no_match` rather than improvising.
