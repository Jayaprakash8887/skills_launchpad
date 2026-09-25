# Invoke: initiative-feasibility

You are executing the **initiative-feasibility** skill (Initiative feasibility).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-PRAYOG-SKILLS-003-PROMPTS
- handoff_path: prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md
- workspace: /workspace/example-repo
- meta_workspace: /workspace/example-meta
- skill_id: initiative-feasibility

## Instruction
Assess whether the repo spec slice is buildable against the current codebase. Flag only — do not implement.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Never skip checks in references/checks.md; evidence for every finding.
2. Verify source freshness (PRD digest, impact-map revision/scope, approval) before analysis.
3. Read-only: persist the report locally and fill Forge readiness (`/commit-workspace`); never commit, push, branch, probe, or edit product source. Keep Gate 2 as spec-pending.
4. `NEW-ADR` only when it clears the ADR qualification rubric (real trade-off, not a locally reversible choice). Every `NEW-ADR` Finding starts with the literal `ALTERNATIVE:` marker naming the technical alternative — never a REQ restatement. Spec quote is a short verbatim excerpt kept separate as lint evidence, not the finding.
5. 4-lane triage; map lanes to outcomes: PE/ADR blocker → findings; PM/domain → needs-input; gate → blocked; stale → stale; clean → pass. Informational findings do not block pass.
6. Do not set spec-lgtm.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: initiative-feasibility, outcome)` per
`.harness/references/handoff-envelope.md` (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node's `type` is
`human-checkpoint` — never because the artifact should be reviewed.
Never set `true` on skill→skill edges (for example never on
`pre-implement` / `loop-spec` / `verify` `pass`).


## Forge (required awareness)
Content skills write local artifacts and fill `handoff.forge` when the pin
expects it; they do **not** execute forge mutations. Human forge skills
(`/commit-workspace`, `/open-draft-pr`, `/create-board-tickets`) or Gateflow
ForgeClient apply pin ⋉ handoff. Never apply `*-lgtm`. See
`.harness/references/forge-side-effects.md#content-producers`.

## Workspace
- **App coding root** (`workspace`): `/workspace/example-repo` — read/write this repo's
  spec slice and feasibility report here.
- **Meta checkout** (`meta_workspace`): `/workspace/example-meta` — read PRD /
  impact-map freshness evidence from this root when bound. Do not invent a
  meta path when empty.

## Handoff baton (required)
1. Follow this skill's `SKILL.md`. Persist the usual durable artifact under
   `/workspace/example-repo` and append the `handoff:` envelope to that artifact.
2. Then **overwrite** the file at exactly `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. If `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` already contains a prior envelope, you may read it for
   context; your final write replaces it with this stage's envelope.
