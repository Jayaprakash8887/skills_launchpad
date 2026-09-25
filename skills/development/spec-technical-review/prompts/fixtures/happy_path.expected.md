# Invoke: spec-technical-review

You are executing the **spec-technical-review** skill (Spec technical review (TDD / ADRs)).

## Bound context
- ticket: FORGE-1001
- initiative: INIT-PRAYOG-SKILLS-003-PROMPTS
- handoff_path: prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md
- workspace: /workspace/example-repo
- meta_workspace: /workspace/example-meta
- skill_id: spec-technical-review

## Instruction
Resolve engineering decisions that block planning. Produce TDD and draft ADRs. Do not implement.

Follow the full procedure in this skill's `SKILL.md` (and `references/` when present). Treat `SKILL.md` as the procedure SSOT; this brief is the invocation package only.

## Non-negotiables (summary)
1. Never skip checks in references/checks.md (T1–T12).
2. Every engineering decision resolved or explicitly deferred with risk + default.
3. Route only product-scope questions to the meta PRD PR — do not ask PM for architecture choices. ADR acceptance requires approved REQ-* bindings; never invent user-visible behavior (T12).
4. Cite REQ-* by id only in ADR Context/Recommendation/Consequences — never quote or paraphrase REQ/feasibility-evidence prose. One decision per ADR, ~150-400 words. Run `scripts/adr_boundary_lint.py` (vendored in this skill) against every Draft ADR before claiming T12 PASS — required, not optional — then still do the manual re-read (checks.md "T12 — run as an independent re-read").
5. T12 FAIL from unapproved product behavior → `needs-input` (spec amendment), never `findings`; T12 FAIL from citation/quality only → `findings`.
6. Persist TDD/ADRs locally and fill Forge readiness (`/commit-workspace`); never commit/push/open PRs/apply labels. Gate 2 stays spec-pending until plan exists.
7. Select workflow outcome from the stage rubric (`pass` / `findings` / `needs-input` / `blocked` / `stale` / `failed`).

## Envelope navigation (required)
After choosing `outcome`, derive `next_candidates` and `human_checkpoint` from
pinned `workflow.yaml` for `(stage: spec-technical-review, outcome)` per
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
- **App coding root** (`workspace`): `/workspace/example-repo` — write TDD/ADR drafts
  and review artifacts under this repo.
- **Meta checkout** (`meta_workspace`): `/workspace/example-meta` — read PRD /
  product-scope context from this root when bound; route product questions to
  the meta PRD PR. Do not invent a meta path when empty.

## Handoff baton (required)
1. Follow this skill's `SKILL.md`. Persist the usual durable artifact under
   `/workspace/example-repo` and append the `handoff:` envelope to that artifact.
2. Then **overwrite** the file at exactly `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` with the same
   `handoff:` envelope (plain YAML or a single fenced yaml block).
3. Do not leave `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. If `prd/reports/Impact-Map-INIT-PRAYOG-SKILLS-003-PROMPTS.md` already contains a prior envelope, you may read it for
   context; your final write replaces it with this stage's envelope.
