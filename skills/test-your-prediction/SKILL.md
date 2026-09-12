---
name: test-your-prediction
description: Use when a user has a specific low-stakes feared prediction that can be checked safely. Turn it into one observable prediction, one safe observation, and one result without dismissing genuine danger.
license: CC-BY-NC-SA-4.0
compatibility: Portable Agent Skills compatible. No local binaries or private CBT Cards data required.
metadata:
  author: "CBT Cards / MetalHatsCats"
  version: "1.0.0"
  homepage: "https://cbt-cards.github.io/skills/"
  source-id: "practice-test-your-prediction"
---

# Test Your Prediction

## Purpose

Use this skill for one bounded self-reflection task. It is general wellness material, not medical advice, diagnosis, treatment, emergency support, or a substitute for qualified professional care.

## Use when

- The feared outcome is specific enough to observe.
- A small ordinary-risk observation or test is available.

## Do not use when

- There is genuine danger or an urgent safety issue.
- A safety, professional, legal, accessibility, medical, financial, or safeguarding rule applies.
- The action is irreversible, unusually high-stakes, or the real-world risk is unclear.

## Procedure

1. Ask the user to state one prediction in concrete terms.
2. Define one safe observation or ordinary low-risk test. Do not escalate risk to make the test more dramatic.
3. Record what actually happened.
4. Compare prediction and result. Update certainty only as far as the observation supports.

## Response contract

Return: Prediction → Safe observation → Result → What changed in certainty. If a safe low-stakes observation is not available, return `no_match`.

Keep the response concrete and proportionate. Do not infer a disorder from the user's wording. Do not remove genuine safety measures, protective boundaries, accessibility aids, medication instructions, professional requirements, or legal/compliance controls.

## Source and review

- Source ID: `practice-test-your-prediction`
- Reviewed CBT Cards practice: https://cbt-cards.github.io/practice/#practice-test-your-prediction
- Marketplace record: https://cbt-cards.github.io/data/skill-marketplace.json
- Review authority: https://cbt-cards.github.io/data/toolkit-review.json
- License: CC BY-NC-SA 4.0

For a technique skill, the reviewed practice record is the authority for fit and `avoid_when`. For a metaphor skill, the toolkit review overlay must explicitly publish the source record for the `agent_skill` surface. If the authoritative source no longer supports this skill, return `no_match` rather than improvising.
