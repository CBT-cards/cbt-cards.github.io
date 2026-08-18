# Install the CBT Cards skill

Canonical mutable skill:

`https://cbt-cards.github.io/agents/cbt-cards/SKILL.md`

For reproducibility, resolve `manifest.json` and pin the immutable version URL recorded there.

The portable core uses `name`, `description`, `license`, `compatibility`, and string-valued `metadata`. Runtime-specific installation stays outside the core.

## OpenClaw

```bash
mkdir -p ~/.openclaw/skills/cbt-cards
curl -fsSL https://cbt-cards.github.io/agents/cbt-cards/SKILL.md \
  -o ~/.openclaw/skills/cbt-cards/SKILL.md
openclaw skills list
```

A workspace-scoped installation can use `skills/cbt-cards/`. Keep the immediate parent directory named `cbt-cards`.

## Hermes Agent

```bash
hermes skills install https://cbt-cards.github.io/agents/cbt-cards/SKILL.md --name cbt-cards
hermes skills list
```

Installed skills take effect in a new session.

## Generic Agent Skills clients

1. Create a directory named `cbt-cards` in a client skill root.
2. Store the canonical `SKILL.md` there.
3. Verify discovery of `name: cbt-cards`.
4. Keep HTTPS access to `https://cbt-cards.github.io/` available for live public resources.

Specification and reference validator:
- https://agentskills.io/specification
- `skills-ref validate ./cbt-cards`

## Version pinning

Manifest:

`https://cbt-cards.github.io/agents/cbt-cards/manifest.json`

Current immutable v1.8.0 compatibility URL:

`https://cbt-cards.github.io/agents/cbt-cards/v1.8.0/SKILL.md`

Strict directory/name-compatible copy:

`https://cbt-cards.github.io/agents/cbt-cards/v1.8.0/cbt-cards/SKILL.md`

The mutable alias and both v1.8.0 immutable copies contain identical skill content.

Historical releases remain at their original URLs. v1.7.0 was the first release deliberately restricted to the portable Agent Skills frontmatter profile; v1.8.0 keeps that portable contract and adds reviewed-practice priority, 115-record source-audit semantics, and content-review freshness rules.
