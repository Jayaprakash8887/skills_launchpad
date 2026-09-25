# Invoke: learning-extract

You are executing the **learning-extract** skill (Extract structured wave learning (SPEC/SKILL/HARNESS/ENV) after wave-acceptance.).

## Bound context
- ticket: LEARN-1001
- initiative: INIT-LEARN-EXTRACT
- handoff_path: /tmp/handoff-baton.yaml
- workspace: /workspace/example-repo
- skill_id: learning-extract

## Instruction
Follow the full procedure in this skill's `SKILL.md`. Treat `SKILL.md` as the
procedure SSOT; this brief is the invocation package only.

Closeout hop after human wave-acceptance: infer learning from workspace + tip fixes;
write `Learning-Extract-*-W*.md` with markdown table and fenced
`learning_extract:` YAML. Do not write the Ground Report. Do not call Gateflow
HTTP/DB as success. Never apply `*-lgtm`.

Publish is walker forge executor when pin `forge.commit_workspace` applies —
recommend `/commit-workspace` when needed; do not treat local CLI as skill
success (`/open-draft-pr`, `/commit-workspace`, `/create-board-tickets`) or
Gateflow ForgeClient apply pin ⋉ `handoff.forge`.

## Envelope navigation (required)
Derive `next_candidates` and `human_checkpoint` from pinned `workflow.yaml` for
`(stage: learning-extract, outcome)`. `human_checkpoint` is `true` only when the resolved
next node's `type` is `human-checkpoint`. Happy path `pass` → `ground-spec`.

## Workspace
Root: `/workspace/example-repo`.

## Handoff baton (required)
1. Persist any durable note under `/workspace/example-repo` and append the `handoff:`
   envelope when the skill defines one.
2. Then **overwrite** the file at exactly `/tmp/handoff-baton.yaml` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `/tmp/handoff-baton.yaml` empty when bound.
