# Invoke: create-board-tickets

You are executing the **create-board-tickets** skill (Create board tickets from plan §9 (preflight + authorize + seed).).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-FORGE-SSOT
- handoff_path: /tmp/handoff-baton.yaml
- workspace: /workspace/example-repo
- skill_id: create-board-tickets

## Instruction
Follow the full procedure in this skill's `SKILL.md`. Treat `SKILL.md` as the
procedure SSOT; this brief is the invocation package only.

This is a **human forge** skill (Gateflow BoardService / ForgeClient parity for
`create_board_tickets`). After spec merge: verify gate + board binding, validate
`prayog/v1` WorkManifest via `scripts/workmanifest_contract.py` before mutate,
present EPIC/waves/TASK summaries projected from plan §9 (board text is not a
second authority), then create tickets only after explicit authorization.
There is no separate `/board-seed` content skill. Never apply `*-lgtm`. Tooling is
agent-neutral. Orchestrators must not auto-dispatch this skill. Do not change
authorization, branch, commit, PR, label, or issue-creation behavior beyond
contract-gated projection.

## Envelope navigation (required)
Forge skills are **not** workflow graph nodes. After a successful seed, continue
at `wave-in-progress-action` then `pre-implement` per pinned `workflow.yaml`
`board-tickets-action` `pass`.
`human_checkpoint` is `true` only when a resolved next node's `type` is
`human-checkpoint`. Prefer re-reading the content-skill baton after mutation.

## Workspace
Root: `/workspace/example-repo`.

## Handoff baton (required)
1. Persist any durable note under `/workspace/example-repo` and append the `handoff:`
   envelope when the skill defines one.
2. Then **overwrite** the file at exactly `/tmp/handoff-baton.yaml` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `/tmp/handoff-baton.yaml` empty when bound.
