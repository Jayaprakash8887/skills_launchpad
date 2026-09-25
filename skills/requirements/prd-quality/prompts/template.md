# Invoke: prd-quality

You are executing the **prd-quality** skill (Blind score PRD files against the delivery bar).

## Bound context
- ticket: {{ticket}}
- initiative: {{initiative}}
- handoff_path: {{handoff_path}}
- workspace: {{workspace}}
- skill_id: {{skill_id}}

## Instruction
Score two or more PRD paths independently against the delivery bar; write
`{INIT}-prd-quality.md`. Emit Handover per file (yes = zero material FAILs).
Do not edit input PRDs. Do not promote.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when
present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation
package only.

## Non-negotiables (summary)
1. ≥2 files — no singleton comparison.
2. Blind first — score each file in isolation before comparison.
3. Evidence on every bar (B1–B15) — id + quote.
4. Material bars include B14 (CAP↔J) and B15 (live cites CAP and/or J).
5. Handover is the validate signal; rank (`Ci-wins`) is secondary.
6. Do not invoke `/prd-think`, `/validate-requirements`, or forge from here.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: {{skill_id}}, outcome)` per
`.harness/references/handoff-envelope.md` (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node's `type` is
`human-checkpoint` — never because the artifact should be reviewed.
This skill is normally human-invoked outside the workflow graph; when not
orchestrated, skip envelope write unless `handoff_path` is bound.

## Workspace
Root: `{{workspace}}` (meta repo).

## Handoff baton (required)
1. Persist `{INIT}-prd-quality.md` under `{{workspace}}`.
2. When orchestrator-bound, **overwrite** the file at exactly
   `{{handoff_path}}` with the `handoff:` envelope (plain YAML or a single
   fenced yaml block).
3. Do not leave `{{handoff_path}}` empty when bound.
