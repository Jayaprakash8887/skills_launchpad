# Invoke: spec-implementation-plan

You are executing the **spec-implementation-plan** skill (Spec implementation plan).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-PRAYOG-SKILLS-003-PROMPTS
- handoff_path: prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md
- workspace: /workspace/example-repo
- meta_workspace: /workspace/example-meta
- skill_id: spec-implementation-plan

## Instruction
Produce a wave-level plan with REQ/TASK/FILE/TEST tables and §9 WorkManifest seed. Do not implement.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Never skip checks (P1–P16); every TASK has observable exit criteria, proof (command|review), expected, evidence_expected, Implements REQ-*, depends_on, files path/action, and toolchain commands.
2. No shadow REQ-W* ids; wave ids W0, W1, … only. §9 WorkManifest is `prayog/v1` (Prayog-owned); validate with `scripts/workmanifest_contract.py` (P16).
3. Technical review is REQUIRED input (pin always routes feasibility into `/spec-technical-review`) — a genuinely missing TDD file is `needs-input`, not "N/A". P13: re-verify every cited Accepted ADR's `changes_user_visible_behavior`/`spec_amendment_required` are false AND re-run `scripts/adr_boundary_lint.py` (vendored in this skill) against the ADR content at plan time — do not trust Accepted status or self-declared metadata alone.
4. Persist plan locally and fill Forge readiness (`/commit-workspace`); never commit/push/open PRs/apply labels. Board seeding happens after merge via `/create-board-tickets`.
5. Verify source freshness against canonical handoff before planning. Map outcomes: missing source → needs-input; Draft ADR / unaccepted TDD / failed ADR re-check → blocked; digest mismatch → stale; P4/P15/P16 contract failure or render failure → failed; clean → pass.
6. P15: new/material product surface ⇒ co-ship unit TEST + FILE under `live_verify_dir` **and** fixture pack under `fixtures_dir`; `covers` include `CAP-*` and/or `J-*`; `verify_command` / live block is smoke|sandbox (not unit / N/A when P15 applies). Map every acceptance criterion to a verification layer; name CAP/J live rung in Verification Coverage.

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: spec-implementation-plan, outcome)` per
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
- **App coding root** (`workspace`): `/workspace/example-repo` — write the implementation
  plan / WorkManifest under this repo.
- **Meta checkout** (`meta_workspace`): `/workspace/example-meta` — read PRD /
  impact-map freshness evidence from this root when bound. Do not invent a
  meta path when empty.

## Handoff baton (required)
1. Follow this skill's `SKILL.md`. Persist the usual durable artifact under
   `/workspace/example-repo` and append the `handoff:` envelope to that artifact.
2. Then **overwrite** the file at exactly `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. If `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` already contains a prior envelope, you may read it for
   context; your final write replaces it with this stage's envelope.
