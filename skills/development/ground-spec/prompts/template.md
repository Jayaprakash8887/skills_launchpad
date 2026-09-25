# Invoke: ground-spec

You are executing the **ground-spec** skill (Ground spec (wave grounding)).

## Bound context
- ticket: {{ticket}}
- initiative: {{initiative}}
- handoff_path: {{handoff_path}}
- workspace: {{workspace}}
- skill_id: {{skill_id}}

## Instruction
Validate the completed wave against REQs assigned to that wave by the plan /
WorkManifest and against repo artifacts (including tests/**). Produce
`Ground-Report-{SPEC}-W{N}.md` with `GF-*` findings. Write locally and prepare
the exact-head merge package for wave-signoff; next is wave-done-action then
wave-signoff (merge only). Never commit or
merge.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Scope = wave-assigned REQs only (G1/G3) — not every future REQ in the full product spec.
2. Run ground_command when defined; otherwise manually map each assigned REQ-* to verifiable artifacts. Separate unit / ground / live evidence.
3. Check cross-spec contracts against prior waves' Ground Reports; populate Contracts Produced.
4. Findings use GF-* (never FF-*). Cite L-* from Learning-Extract when present.
5. Do not mark human_approved (already from wave-acceptance), commit, or merge — wave-signoff is merge/publish only.
6. Select outcome deterministically (`pass` / `findings` / `needs-input` / `blocked` / `failed`) per `SKILL.md`. Run G1–G10.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: {{skill_id}}, outcome)` per
`.harness/references/handoff-envelope.md` (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node's `type` is
`human-checkpoint` — never because the artifact should be reviewed.
Never set `true` on skill→skill edges (for example never on
`pre-implement` / `loop-spec` `pass`).
Example: `ground-spec` + `pass` → `wave-done-action` → `human_checkpoint: false`,
`external_action: true` (then pin → `wave-signoff`). Do not copy into earlier lane skills.


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
