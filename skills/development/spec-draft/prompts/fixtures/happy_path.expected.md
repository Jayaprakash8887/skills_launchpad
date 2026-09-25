# Invoke: spec-draft

You are executing the **spec-draft** skill (Spec draft (repo slice from PRD)).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-PRAYOG-SKILLS-003-PROMPTS
- handoff_path: prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md
- workspace: /workspace/example-repo
- meta_workspace: /workspace/example-meta
- skill_id: spec-draft

## Instruction
Translate the PRD into a repo-bounded product spec slice. Do not implement.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Write docs/specification/product/INIT-*.md in engineering terms (REQ-*), not PRD user-story prose.
2. Scope this repo only; every REQ-* must trace to a named PRD CAP-*/REQ-* or section.
3. Carry in-scope CAP-* and J-{nn} (or explicit out-of-repo N/A); live Evidence cites CAP and/or J.
4. Flag ambiguity — do not guess. Run the bounded clarification loop before `pass`; write answers into owning REQ rows and rerun D-checks.
5. Spec owns observable behavior (condition/event + result + evidence); do not decide architecture — route those questions.
6. Persist locally and fill `handoff.forge`; never commit, push, branch, open PRs, apply labels, create issues, or merge. Authorize `/commit-workspace` / `/open-draft-pr` separately.
7. Select workflow outcome (`pass` / `needs-input` / `blocked` / `stale` / `failed`) from the stage rubric — not every FAIL is `failed`.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: spec-draft, outcome)` per
`.harness/references/handoff-envelope.md` (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node's `type` is
`human-checkpoint` — never because the artifact should be reviewed.
Never set `true` on skill→skill edges (for example never on
`pre-implement` / `loop-spec` / `verify` `pass`).


## Forge (required awareness)
Content skills write local artifacts and fill `handoff.forge` when the pin
expects it; they do **not** execute forge mutations. Human forge skills
(`/commit-workspace`, `/open-draft-pr`, `/create-board-tickets`) or Gateflow
ForgeClient apply pin ⋉ handoff. Never apply `*-lgtm`. See
`.harness/references/forge-side-effects.md#content-producers`.

## Workspace
- **App coding root** (`workspace`): `/workspace/example-repo` — write product spec
  artifacts under this repo (`docs/specification/…`). Do not write product
  decisions only into meta unless procedure says so.
- **Meta checkout** (`meta_workspace`): `/workspace/example-meta` — read PRD /
  impact map / meta approval evidence from this root when bound (Gateflow
  spec start). Do not invent a meta path when this value is empty.

## Handoff baton (required)
1. Follow this skill's `SKILL.md`. Persist the usual durable artifact under
   `/workspace/example-repo` and append the `handoff:` envelope to that artifact.
2. Then **overwrite** the file at exactly `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. If `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` already contains a prior envelope, you may read it for
   context; your final write replaces it with this stage's envelope.
