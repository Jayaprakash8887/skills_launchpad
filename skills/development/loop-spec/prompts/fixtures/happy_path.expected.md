# Invoke: loop-spec

You are executing the **loop-spec** skill (Loop spec (per-wave implement loop)).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-PRAYOG-SKILLS-003-PROMPTS
- handoff_path: /tmp/handoff-baton.yaml
- workspace: /workspace/example-repo
- skill_id: loop-spec

## Instruction
Implement one TASK at a time against the product spec; check/test; fix; record
local TASK proof. Never commit or push. After the wave is green, write
`Wave-Execution-{INIT}-W{N}.md`, emit completed TASK ids/evidence, and fill one
stage-level `commit_workspace` Forge package and complete `handoff.forge` for
`wave-pr-action` (`open_draft_pr`). Next is wave-pr-action then wave-acceptance.
Do not self-approve or ground.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Prerequisites: pre-implement checklist PASS; plan on develop (spec package merged); wave head bound by Forge/human context; WorkManifest already contract-valid.
2. Consume WorkManifest TASKs in dependency order; remain within declared file scope. Persist actual command/evidence in Wave-Execution/handoff — do not mutate approved WorkManifest intent.
3. After each TASK run check_command and test_command only; fix before advancing. Implement planned live FILE TASKs under live_verify_dir **and** fixture packs under fixtures_dir (stimulus+probes) — never run smoke/sandbox or claim human live / look-at success. Handoff lists verify_command, CAP/J covers, fixtures, look-ats.
4. Bind each iteration to TASK-* + wave issue + implements REQ-* from the manifest.
5. When green: write Wave-Execution-*; fill commit_workspace readiness and
   wave-pr-action open_draft_pr slots; hand off pass → wave-pr-action with
   human verify_command. Closeout is separate.
6. Select outcome deterministically (`pass` / `findings` / `blocked` / `failed`) per `SKILL.md`.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: loop-spec, outcome)` per
`.harness/references/handoff-envelope.md` (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node's `type` is
`human-checkpoint` — never because the artifact should be reviewed.
Never set `true` on skill→skill edges (for example never on
`pre-implement` / `loop-spec` `pass` when next is another skill).
Example: `loop-spec` + `pass` → `wave-pr-action` (`external-action`) →
`human_checkpoint: false`, `external_action: true`.


## Forge (required awareness)
Content skills fill `handoff.forge` when the pin expects it; they do **not**
execute forge mutations. Human forge skills (`/commit-workspace`,
`/open-draft-pr`, `/create-board-tickets`) or Gateflow ForgeClient apply pin ⋉
handoff. Never apply `*-lgtm`. See `.harness/references/forge-side-effects.md#content-producers`.
After a green wave: `commit_workspace` publishes code to the bound head; then
`wave-pr-action` opens/updates the Draft PR (checklist already on tip from
pre-implement publish).

## Workspace
Root: `/workspace/example-repo`.

## Handoff baton (required)
1. Follow this skill's `SKILL.md`. Persist the usual durable artifact under
   `/workspace/example-repo` and append the `handoff:` envelope to that artifact.
2. Then **overwrite** the file at exactly `/tmp/handoff-baton.yaml` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `/tmp/handoff-baton.yaml` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. If `/tmp/handoff-baton.yaml` already contains a prior envelope, you may read it for
   context; your final write replaces it with this stage's envelope.
