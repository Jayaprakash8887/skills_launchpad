# Invoke: purge-initiative-artifacts-app

You are executing the **purge-initiative-artifacts-app** skill (Engineering-lane
delete of allowlisted app working papers after initiative-closure.).

## Bound context
- ticket: PURGE-APP-1001
- initiative: INIT-PURGE-DEMO
- handoff_path: /tmp/handoff-baton.yaml
- workspace: /workspace/example-repo
- skill_id: purge-initiative-artifacts-app

## Instruction
Follow the full procedure in this skill's `SKILL.md`. Treat `SKILL.md` as the
procedure SSOT; this brief is the invocation package only.

Eng / app lane only. Delete only the app PURGE allowlist; refuse KEEP paths.
Do **not** write any `Purge-*.md` or other report under `reports_dir` — emit
handoff (+ baton) with path lists in `signals`. Do not open a merge. Never apply `*-lgtm`. No authorize-before-delete. Do not
invoke or require meta/PM purge — skills are independent; pin owns
orchestration. When pin next is `open_draft_pr`, fill forge title/body from
signals (ephemeral body outside reports) — never a reports purge file.

Publish is walker forge executor when pin `forge.commit_workspace` applies —
recommend `/commit-workspace` when needed.

## Envelope navigation (required)
Derive `next_candidates` and `human_checkpoint` from pinned `workflow.yaml` for
`(stage: purge-initiative-artifacts-app, outcome)`. `human_checkpoint` is `true`
only when the resolved next node's `type` is `human-checkpoint`.

## Workspace
Root: `/workspace/example-repo` (app repo).

## Handoff baton (required)
1. Do **not** persist a reports artifact. Emit `handoff:` with
   `artifact.path: null` and delete/refuse lists in `signals`.
2. Then **overwrite** the file at exactly `/tmp/handoff-baton.yaml` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `/tmp/handoff-baton.yaml` empty when bound.
