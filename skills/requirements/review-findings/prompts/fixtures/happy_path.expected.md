# Invoke: review-findings

You are executing the **review-findings** skill (Review findings (interactive resolution)).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-PRAYOG-SKILLS-003-PROMPTS
- handoff_path: prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md
- workspace: /workspace/example-repo
- skill_id: review-findings

## Instruction
Walk findings from one validation/audit report; collect decisions; write a Resolution summary.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Read ONE report file — do not re-run checks or re-read source documents.
2. Present each finding as a decision brief via structured questions.
3. Produce Resolution with VF→CHG linkage at canonical Resolution-{INIT}.md path.
4. Do not invent findings; work only from the report.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: review-findings, outcome)` per
`.harness/references/handoff-envelope.md` (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node's `type` is
`human-checkpoint` — never because the artifact should be reviewed.
Never set `true` on skill→skill edges (for example never on
`pre-implement` / `loop-spec` / `verify` `pass`).


## Forge (required awareness)
Content skills fill `handoff.forge` when the pin expects it; they do **not**
execute forge mutations. Human forge skills (`/commit-workspace`,
`/open-draft-pr`, `/create-board-tickets`) or Gateflow ForgeClient apply pin ⋉
handoff. Never apply `*-lgtm`. See `.harness/references/forge-side-effects.md#content-producers`.

## Workspace
Root: `/workspace/example-repo`.

## Handoff baton (required)
1. Follow this skill's `SKILL.md`. Persist the usual durable artifact under
   `/workspace/example-repo` and append the `handoff:` envelope to that artifact.
2. Then **overwrite** the file at exactly `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. If `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` already contains a prior envelope, you may read it for
   context; your final write replaces it with this stage's envelope.
