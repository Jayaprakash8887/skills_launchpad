# Invoke: commit-workspace

You are executing the **commit-workspace** skill (Commit workspace (publish tree to remote head).).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-FORGE-SSOT
- handoff_path: /tmp/handoff-baton.yaml
- workspace: /workspace/example-repo
- skill_id: commit-workspace

## Instruction
Follow the full procedure in this skill's `SKILL.md`. Treat `SKILL.md` as the
procedure SSOT; this brief is the invocation package only.

This is a **human forge** skill (Gateflow ForgeClient parity). Consume pin
policy ⋉ `handoff.forge` from the prior content skill. Do not invent labels or
required slots. Never apply `*-lgtm`. Tooling is agent-neutral (`gh`/API are
examples). Orchestrators must not auto-dispatch this skill.


## Envelope navigation (required)
Forge skills are **not** workflow graph nodes. Do not invent programme
`next_candidates` from a missing pin node. When emitting a forge-step
`handoff:`, set navigation fields only if continuing from the **prior content**
stage handoff and pinned `workflow.yaml`. `human_checkpoint` is `true` only
when that resolved next node's `type` is `human-checkpoint`. Prefer re-reading
the content-skill baton after mutation.

## Workspace
Root: `/workspace/example-repo`.

## Handoff baton (required)
1. This skill has no workspace artifact — do not create a note file.
   `artifact.path` is `null`; see `references/output-template.md`.
2. **Overwrite** the file at exactly `/tmp/handoff-baton.yaml` with the `handoff:`
   envelope (plain YAML or a single fenced yaml block).
3. Do not leave `/tmp/handoff-baton.yaml` empty when bound.
