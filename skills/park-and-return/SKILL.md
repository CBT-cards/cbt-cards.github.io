---
name: park-and-return
description: Use when a non-urgent worry keeps interrupting the current task. Capture it once, choose a realistic review time, and return attention without requiring the worry to disappear.
license: CC-BY-NC-SA-4.0
compatibility: Portable Agent Skills compatible. No local binaries or private CBT Cards data required.
metadata:
  author: "CBT Cards / MetalHatsCats"
  version: "1.0.0"
  homepage: "https://cbt-cards.github.io/skills/"
  source-id: "practice-park-and-return"
---

# Park and Return

## Purpose

Use this skill for one bounded self-reflection task. It is general wellness material, not medical advice, diagnosis, treatment, emergency support, or a substitute for qualified professional care.

## Use when

- The concern is non-urgent.
- A realistic later review point can be chosen.

## Do not use when

- Delaying action could materially worsen a concrete problem.
- There is danger, urgency, a deadline requiring action, or a professional/safety requirement.

## Procedure

1. Write the worry once in a short sentence.
2. Choose a specific later review point.
3. Name the current task to return to.
4. When the worry returns, refer to the captured note rather than reopening the full analysis.

## Response contract

Return: Captured worry → Review point → Current task. If postponement would be unsafe or irresponsible, return `no_match`.

Keep the response concrete and proportionate. Do not infer a disorder from the user's wording. Do not remove genuine safety measures, protective boundaries, accessibility aids, medication instructions, professional requirements, or legal/compliance controls.

## Source and review

- Source ID: `practice-park-and-return`
- Reviewed CBT Cards practice: https://cbt-cards.github.io/practice/#practice-park-and-return
- Marketplace record: https://cbt-cards.github.io/data/skill-marketplace.json
- Review authority: https://cbt-cards.github.io/data/toolkit-review.json
- License: CC BY-NC-SA 4.0

For a technique skill, the reviewed practice record is the authority for fit and `avoid_when`. For a metaphor skill, the toolkit review overlay must explicitly publish the source record for the `agent_skill` surface. If the authoritative source no longer supports this skill, return `no_match` rather than improvising.
