# Install the CBT Cards skill

The canonical mutable skill is:

`https://cbt-cards.github.io/agents/cbt-cards/SKILL.md`

For reproducibility, resolve `manifest.json` and pin the immutable version URL recorded there.

The latest portable release follows the Agent Skills frontmatter contract: the required `name` and `description`, optional `license` and `compatibility`, and string-valued `metadata`. Runtime-specific installation is kept outside the portable core so one skill file does not need mutually incompatible frontmatter extensions.

## OpenClaw

OpenClaw follows the Agent Skills specification and scans several skill roots. One straightforward personal installation is to place the CBT Cards skill in a directory named `cbt-cards` under an OpenClaw skill root:

```bash
mkdir -p ~/.openclaw/skills/cbt-cards
curl -fsSL https://cbt-cards.github.io/agents/cbt-cards/SKILL.md \
  -o ~/.openclaw/skills/cbt-cards/SKILL.md
openclaw skills list
```

A workspace-scoped installation can use the workspace `skills/cbt-cards/` directory instead. Keep the immediate parent directory named `cbt-cards`; the Agent Skills specification requires the directory name to match the skill `name`.

The CBT Cards skill requires no executable helper and no API key. It needs HTTPS access to the public CBT Cards site when the assistant resolves live public resources.

OpenClaw documentation:

- https://docs.openclaw.ai/skills
- https://docs.openclaw.ai/tools/creating-skills

## Hermes Agent

Hermes supports installing a `SKILL.md` and its referenced files from an HTTPS URL:

```bash
hermes skills install https://cbt-cards.github.io/agents/cbt-cards/SKILL.md --name cbt-cards
hermes skills list
```

Installed skills take effect in a new session. Hermes can also use external skill directories or GitHub taps when a larger skill collection is needed.

Hermes documentation:

- https://hermes-agent.nousresearch.com/docs/guides/work-with-skills/
- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/

## Generic Agent Skills clients

For a client implementing the Agent Skills open specification:

1. Create a directory named `cbt-cards` in one of the client's skill roots.
2. Store the canonical `SKILL.md` in that directory.
3. Verify that the client can discover `name: cbt-cards` and the full description.
4. Keep network access to `https://cbt-cards.github.io/` available when live public sources are required.

Specification and reference validator:

- https://agentskills.io/specification
- Run `skills-ref validate ./cbt-cards` when the reference validator is available in the target environment.

## Version pinning

The mutable alias is convenient for interactive use. Reproducible integrations should read:

`https://cbt-cards.github.io/agents/cbt-cards/manifest.json`

The current manifest-pinned immutable v1.7.0 URL is:

`https://cbt-cards.github.io/agents/cbt-cards/v1.7.0/SKILL.md`

For strict Agent Skills directory/name validation, the same immutable v1.7.0 content is also distributed at:

`https://cbt-cards.github.io/agents/cbt-cards/v1.7.0/cbt-cards/SKILL.md`

The first URL preserves the versioned URL convention used by existing CBT Cards consumers. The second places `SKILL.md` under an immediate `cbt-cards/` directory so extracted or mirrored skill packages satisfy the portable directory/name contract. Both files and the mutable alias are required to contain identical v1.7.0 skill content.

Historical skill releases before v1.7.0 are preserved at their original URLs. v1.7.0 is the first release whose strict portable distribution places `SKILL.md` inside an immediate `cbt-cards/` parent directory and whose frontmatter is intentionally restricted to the portable Agent Skills field set.
