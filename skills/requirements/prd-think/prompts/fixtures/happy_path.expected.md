# Invoke: prd-think

You are executing the **prd-think** skill (Author PRD candidates by grilling the brief).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-PRAYOG-SKILLS-004-THINK
- handoff_path: prd/reports/INIT-PRAYOG-SKILLS-004-THINK-prd-think.md
- workspace: /workspace/example-meta
- skill_id: prd-think

## Instruction
Challenge the brief as a hypothesis; model the product; red-team; write the
next free `{INIT}-prd-think(-N).md` candidate under `reports_dir`. Do not
score. Do not promote unless the user authorizes.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when
present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation
package only.

## Non-negotiables (summary)
1. Brief is not baseline — grill before filling.
2. WHAT not HOW — no routes, payloads, or module names in REQs.
3. Product ids only from `.harness/references/id-conventions.md`
   (`CAP-*`, `J-{nn}`, `REQ-*`, `CTR-*`, `OQ-*`).
4. CAP↔J binding; live Evidence cites CAP and/or J (separate prove rungs).
5. Never overwrite earlier think candidates or `prd/{INIT}.md` without promote.
6. Do not invoke `/prd-quality`, `/validate-requirements`, or forge from here.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: prd-think, outcome)` per
`.harness/references/handoff-envelope.md` (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node's `type` is
`human-checkpoint` — never because the artifact should be reviewed.
This skill is normally human-invoked outside the workflow graph; when not
orchestrated, skip envelope write unless `handoff_path` is bound.

## Workspace
Root: `/workspace/example-meta` (meta repo).

## Handoff baton (required)
1. Persist the candidate under `/workspace/example-meta` at the path resolved in T0.
2. When orchestrator-bound, **overwrite** the file at exactly
   `prd/reports/INIT-PRAYOG-SKILLS-004-THINK-prd-think.md` with the `handoff:` envelope (plain YAML or a single
   fenced yaml block).
3. Do not leave `prd/reports/INIT-PRAYOG-SKILLS-004-THINK-prd-think.md` empty when bound.
