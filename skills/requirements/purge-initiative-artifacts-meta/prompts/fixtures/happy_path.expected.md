# Invoke: purge-initiative-artifacts-meta

You are executing the **purge-initiative-artifacts-meta** skill (PM-lane delete
of allowlisted meta working papers.).

## Bound context
- ticket: PURGE-META-1001
- initiative: INIT-PURGE-DEMO
- handoff_path: /tmp/handoff-baton.yaml
- workspace: /workspace/example-meta
- skill_id: purge-initiative-artifacts-meta

## Instruction
Follow the full procedure in this skill's `SKILL.md`. Treat `SKILL.md` as the
procedure SSOT; this brief is the invocation package only.

PM / meta lane only. Delete only Validation / Resolution for this initiative;
refuse PRD and Impact-Map. Do **not** write any `Purge-*.md` under
`reports_dir` — emit handoff (+ baton) with path lists in `signals`. Do not
merge. Never apply `*-lgtm`. Do not invoke or require app/eng purge — skills
are independent; pin owns orchestration. When pin next is `open_draft_pr`,
fill forge title/body from signals (ephemeral body outside reports) — never a
reports purge file.

## Envelope navigation (required)
Derive `next_candidates` and `human_checkpoint` from pinned `workflow.yaml` for
`(stage: purge-initiative-artifacts-meta, outcome)`. `human_checkpoint` is `true`
only when the resolved next node's `type` is `human-checkpoint`.

## Workspace
Root: `/workspace/example-meta` (meta repo).

## Handoff baton (required)
1. Do **not** persist a reports artifact. Emit `handoff:` with
   `artifact.path: null` and delete/refuse lists in `signals`.
2. Then **overwrite** the file at exactly `/tmp/handoff-baton.yaml` with the same
   `handoff:` envelope.
3. Do not leave `/tmp/handoff-baton.yaml` empty when bound.
