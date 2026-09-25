## Harness (managed by skills_launchpad — do not edit this block)

Profile: **{{PROFILE}}** · kit **v{{KIT_VERSION}}** · pin record: `.harness-pin.yaml`

{{RULES_SECTION}}

### Agent skills

Skills live in `.harness/skills/` (sources) and are exposed to Claude Code via
`.claude/skills/` — {{SKILLS_SLASH_LIST}}.

Skill changes go upstream in the harness kit, then re-run `harness apply`.
Do not edit `.claude/rules/` or `.harness/` in this repo.

### Delivery bootstrap

- Workflow: `.harness/references/workflow.yaml`
- Contract: `.harness/references/delivery-contract.yaml`
- Shared contracts (ids, handoffs, artifacts): `.harness/references/`
- Layout defaults for this repo: `.harness/profile.yaml`

When asked "what next?", read the latest persistent handoff and the pinned
workflow, then explain the current stage, blockers, and next candidate. Do not
perform file or GitHub mutations unless the user explicitly authorizes them.

Development content skills only change the local workspace and record Forge
readiness. Branch/commit/push/PR/issue/label/merge happen only via forge skills
(`/commit-workspace`, `/open-draft-pr`, `/create-board-tickets`) or the human.
Content skills must not apply labels, commit, push, open/merge PRs, or update
boards.

### Before changing behavior

1. Read `.claude/rules/code-guidelines-index.md` (when this repo has a constitution).
2. Read the relevant product spec and accepted ADRs under `docs/specification/`.
3. Read as-built; do not infer live behavior from a spec.
4. Use the repository's documented build/check/test commands exactly; do not invent them.
5. Resolve the current delivery stage from `.harness/references/workflow.yaml`.
