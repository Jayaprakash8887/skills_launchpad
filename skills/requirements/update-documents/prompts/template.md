# Invoke: update-documents

You are executing the **update-documents** skill (Update documents (propagate approved changes)).

## Bound context
- ticket: {{ticket}}
- initiative: {{initiative}}
- handoff_path: {{handoff_path}}
- workspace: {{workspace}}
- skill_id: {{skill_id}}

## Instruction
Propagate verified decisions across related documents. Decide where, not what.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Resolution mode: consume approved Resolution without re-deciding semantics.
2. Present an exact change manifest; apply only approved edits.
3. Run inline consistency verification after edits.
4. Preserve product ids (CAP-*/REQ-*/OQ-*) when the resolution requires it.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: {{skill_id}}, outcome)` per
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
Root: `{{workspace}}`.

## Handoff baton (required)
1. Follow this skill's `SKILL.md`. Persist the usual durable artifact under
   `{{workspace}}` and append the `handoff:` envelope to that artifact.
2. Then **overwrite** the file at exactly `{{handoff_path}}` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `{{handoff_path}}` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. If `{{handoff_path}}` already contains a prior envelope, you may read it for
   context; your final write replaces it with this stage's envelope.
