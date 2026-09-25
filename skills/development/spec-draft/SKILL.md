---
name: spec-draft
description: >-
  Translate the PRD into a spec slice for this repo. Reads the PRD from the
  meta PRD PR branch or merged develop, extracts capabilities relevant to this
  repo, drafts docs/specification/product/INIT-*.md locally, and produces a
  Draft-PR readiness handoff (handoff.forge for open_draft_pr). Publish via
  /open-draft-pr or orchestrator ForgeClient (spec-pr-action is authorization:
  automated) — not inside this skill. Run after Gate 1 approval and before
  /initiative-feasibility.
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/**, .claude/rules/**
background_eligible: true
background_trigger: "Gate 1 approved for this repo scope; spec slice not yet on a Draft spec PR"
---

# Spec draft

Translate the **PRD** into a **spec slice** for this repo. The spec slice is
the engineering team's interpretation of what the PRD means for their codebase.

**Do not implement.** Produce `docs/specification/product/INIT-{id}.md` only.

## Why this skill exists

PM writes PRD in feature language. Engineers own the spec.
This skill bridges the gap — it reads the PRD and drafts structured spec
`REQ-*` rows that the dev team can review, edit, and then run
`/initiative-feasibility` on.

## NON-NEGOTIABLE

1. The spec draft is a **starting point** — dev must review and edit before
   committing. Do not present it as authoritative without dev review.
2. Language in the spec must be **engineering terms** — `REQ-*`, acceptance
   criteria, module scope — not copied PRD user-story language. Ids follow
   `.harness/references/id-conventions.md` (`REQ-*` canonical; legacy `FR-*`
   ≡ same number).
3. Scope must be **bounded to this repo** only. Do not write REQs for other repos.
4. Every `REQ-*` must trace to a named PRD `CAP-*` / `REQ-*` or section/bullet.
5. Flag anything in the PRD that is **ambiguous for this repo** — do not guess.
   Put ambiguities in a "Spec questions" section at the bottom.
6. **Handoff gate first (Gate 1 / G1 + H1–H3).** The canonical impact-map
   artifact, source PRD digest (**H1**), current meta PR head SHA, and
   tech-lead APPROVED review must match. A label or old LGTM alone is not
   approval. **Open `IM-{nn}` with `Blocking: yes` fails closed** (D1b) —
   do not draft the spec until resolved or deferred with default.
7. This repo must be `affected` in the latest map and not deferred or blocked.
   Record the repo's `scope_digest` (**H2**) and map revision (**H3**) in the
   spec header (**H4** citations). If any gate fails: stop.
8. **No forge mutations in this skill.** Do not create a branch, commit, push,
   PR, comment, review request, apply labels, create issues, or merge here.
   Persist the spec locally and fill `handoff.forge` readiness for
   `open_draft_pr`; recommend `/open-draft-pr` or `/commit-workspace` (or wait
   for the orchestrator ForgeClient on `spec-pr-action`). See
   `.harness/references/forge-side-effects.md#content-producers`.
9. Treat `spec-*` labels as projections. If artifact, review, and label
   disagree, the gate is closed. Exactly one PE gate label may be active:
   `spec-pending`, `spec-lgtm`, or `spec-blocked`. `spec-revised` and
   `spec-stale` are additional invalidation labels and always close the gate.
10. **Ownership boundary.** The spec owns observable product behavior,
    acceptance, field meaning, invariants, errors, and compatibility. It may
    cite existing architectural constraints from `adr_dir` but must **not**
    choose implementation architecture. Architecture questions are recorded
    for feasibility / technical review — not decided here.
11. **Outcome vocabulary.** Emit only `pass`, `needs-input`, `blocked`,
    `stale`, or `failed` (this stage has no `findings` edge). Map evidence to
    the outcome rubric below; do not invent lane-specific outcomes.
12. If a codegraph provider is available (MCP tool matching
    `.harness/references/codegraph-tool-contract.md`, or a local CLI), prefer
    it for architecture/impact questions. Always fall back to direct
    `source_roots` reads when unavailable — never block or change outcome
    selection on its absence.
13. **Carry Capabilities and Journeys.** In-scope PRD `CAP-*` and `J-{nn}`
    appear in the spec tables (or explicit out-of-repo N/A). Do not drop
    journeys silently. Live evidence REQs cite `CAP-*` and/or `J-*` when the
    PRD defines those namespaces (`quality-confidence-ladder.md`).

## Prerequisites

- Meta PRD PR exists (merged or open) with a committed
  `prd/reports/Impact-Map-{INIT}.md`
- Latest tech-lead APPROVED review is bound to the current meta PR head SHA
  carrying that map revision and PRD digest
- This repo is affected in that revision and has a `scope_digest`
- An existing Draft spec PR is optional when revising; it is not required to
  start `/spec-draft`

## Inputs

Resolve paths from `.harness/profile.yaml` or [references/layout-defaults.md](references/layout-defaults.md).

**Dual workspace (orchestrated / Gateflow):** when the invocation binds
`meta_workspace`, treat it as the prayog-meta (client-meta) checkout root for
PRD and impact-map reads. Treat bound `workspace` as this app repo root for
product spec writes (`docs/specification/…`). Do not invent a meta path when
`meta_workspace` is empty; do not write product decisions only into meta unless
procedure explicitly says so.

1. **PRD** — (REQUIRED) from `<client>-meta/prd/INIT-*.md` under
   `meta_workspace` when bound (else resolve meta checkout as today). Read from
   the meta PRD PR branch or merged `develop`. Do not assume PRD is on develop
   if PR is still open — use PR branch when iterating in parallel.
2. **Impact map** — (REQUIRED) canonical
   `<client>-meta/prd/reports/Impact-Map-{INIT}.md` from the exact approved meta
   PR head (under `meta_workspace` when bound); PR comments are summaries only.
3. **Approval evidence** — (REQUIRED) meta PR number/URL, current head SHA, and
   latest tech-lead APPROVED review `commit_id`; all must match.
4. **As-built** — `implementation-status.md` (REQUIRED) under `workspace` —
   understand what already exists before writing FRs.
5. **Source** — `source_roots` from profile — understand current module structure.
6. **Service profile** — `docs/specification/product/00-service-profile.md` if
   it exists — understand the repo's existing domain.
7. **`adr_dir`** — existing ADRs constrain what this spec can propose.
8. **Layout** — `.harness/profile.yaml` or [references/layout-defaults.md](references/layout-defaults.md)
9. **Codegraph provider** — OPTIONAL — see `.harness/references/codegraph-tool-contract.md`

## Process

1. **T0 Gather and gate** — PRD, canonical impact map, approval review, as-built,
   source, service profile. Verify full Gate 1 and mint **H4** citations:
   - current meta PR head SHA = approved review `commit_id` (**G1**)
   - impact-map `source_prd_digest` = digest of the PRD read (**H1**)
   - impact-map `map_revision` / path = approval attestation (**H3**)
   - this repo is affected, not deferred/blocked, with a `scope_digest` (**H2**)
   Write H1–H3 + G1 into the product spec header (see output template). Stop on
   any mismatch. `stale` = authority drift on these identities — not mid-lane
   report digests.
2. **T1 Understand** — initiative id; approved map revision and scope digest;
   what capabilities land in this repo; what already exists (as-built + source scan)
3. **T2 Scope** — list ONLY what this repo owns. Explicitly exclude what belongs
   to other repos. Cross-service contracts are noted but not spec'd here.
4. **T3 Draft** — write INIT-*.md using [references/output-template.md](references/output-template.md)
5. **T4 Flag and clarify** — list ambiguities and open questions. Before any
   `pass` attempt, run the **bounded clarification loop** below.
6. **T5 Verify and hand off** — run D1–D12 from
   [references/checks.md](references/checks.md); select the workflow outcome
   from the rubric; present in chat:
   - generated/changed files,
   - gate verification summary,
   - spec summary and open questions,
   - selected workflow outcome + reason,
   - proposed branch, base, Draft PR title/body, reviewers, and initial labels,
   - `PR READY` or `PR BLOCKED` verdict (PR READY only when outcome is `pass`).
   Stop without GitHub side effects.

## Bounded clarification loop (before pass)

Before T5 can emit `pass`:

1. Classify every open Spec question as material (blocks acceptance or scope)
   or non-blocking (safe default + revisit trigger).
2. Ask only material questions; write each accepted answer into the owning
   `REQ-*` / acceptance / NFR / contract row — do not leave answers only in chat.
3. Preserve unresolved non-blockers with owner, default-if-deferred, and
   revisit trigger (D6).
4. Rerun affected D-checks after incorporating answers.
5. If any material ambiguity remains unresolved → do **not** emit `pass`;
   select `needs-input` or `blocked` per the outcome rubric.

## Outcome selection (workflow edges)

Map evidence to exactly one outcome declared for `spec-draft` in pinned
`workflow.yaml`. Do not emit `findings` or `skipped` from this stage.

| Outcome | When | Next (from workflow) |
|---------|------|----------------------|
| `pass` | D1–D12 PASS, zero unresolved material questions, PR READY, sources CURRENT | `spec-pr-action` |
| `needs-input` | Required handoff/source input missing or unreadable; or material PM/domain ambiguity remains after the clarification loop | `spec-human-decision` |
| `blocked` | Explicit gate closure (approval/label/artifact disagree; repo deferred/blocked; PE gate closed) | `spec-human-decision` |
| `stale` | Authority drift: H1–H3 / G1 / head mismatch vs approved handoff | `prd-impact-map` |
| `failed` | Execution/render error on otherwise valid inputs | `workflow-stop` |

Check verdicts (PASS/FAIL/NEEDS INPUT) feed this rubric — a FAIL on a blocking
check is usually `needs-input` or `blocked`, not automatically `failed`.
Permit complete `handoff.forge` for `open_draft_pr` **only** on `pass`.

## PR readiness (fill handoff.forge — do not open the PR here)

After T5, **always** present the PR readiness section from
[references/output-template.md](references/output-template.md), including the
selected workflow outcome and reason. On `outcome: pass`, next node is
`spec-pr-action` (`open_draft_pr`). Fill `handoff.forge` with pin `requires`
at minimum:

- `action: open_draft_pr`
- `draft: true`
- `apply_labels: [spec-pending]` (match pin; never `*-lgtm`)
- `title`, `body_path` (and any other pin `requires`)

Recommend `/commit-workspace` when local publication is needed. On `pass`, next
is `spec-pr-action` with pin `authorization: automated` — Gateflow ForgeClient
opens the Draft PR without interactive STOP when requires are complete. Human
walkers may still run `/open-draft-pr` after user confirm. Do **not** run forge
mutations inside `/spec-draft`. If Forge tooling is unavailable, readiness in
the handoff is still the durable package for a later forge skill or Gateflow
ForgeClient.

See `.harness/references/forge-side-effects.md`.

## Output

Draft saved to `{product_spec_dir}/INIT-{id}.md` (from profile).

Use [references/output-template.md](references/output-template.md).

Before `/open-draft-pr` (or orchestrator forge), `spec_pr` and Gate 2 fields
are `pending`. After the authorized forge skill / ForgeClient run, the PR body
contains the spec summary, artifact path, meta handoff digests, Gate 2
checklist, and PE review request.

## Revision handling

When a newer approved impact-map revision appears:

- Same repo `scope_digest`: record the new revision check; existing spec may
  continue if its PRD digest is unchanged.
- Changed `scope_digest`: mark this spec stale, revise affected sections, and
  re-run `/initiative-feasibility`.
- Repo removed/deferred/blocked: stop and mark the spec PR held or out of scope.
- Dependency/order-only change: update cross-service dependencies and invalidate
  the implementation plan when ordering changes.

## Next step

After dev reviews the local draft:

1. on `pass` / `PR READY`, let the orchestrator execute `spec-pr-action`
   (`authorization: automated`), or authorize and run `/open-draft-pr` as a
   human walker
2. ensure the spec slice is on the Draft spec PR head via `/commit-workspace`
   and/or `/open-draft-pr` / ForgeClient (Forge — not this content skill)
3. run `/initiative-feasibility` on the published spec on that branch

Do not skip the PR-readiness handoff or jump straight to feasibility on a local
file only — the Draft spec PR is the engineering review surface for the whole
lane.

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the saved spec. Use stage `spec-draft`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates`, `human_checkpoint`, and `external_action` from pinned root `workflow.yaml` for `(stage: spec-draft, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint`. Set `external_action: true` when next is `external-action` (e.g. `spec-pr-action` on `pass`).
4. On `pass`, fill complete `handoff.forge` for `open_draft_pr` per pin `requires` (`.harness/references/forge-side-effects.md#content-producers`). Orchestrator: `spec-pr-action` is `authorization: automated`. Human walker: recommend `/open-draft-pr` after confirm.
5. Follow `.harness/references/forge-side-effects.md#content-producers` — content skill success ≠ PR opened.

**Transitions:** pinned root `workflow.yaml` for this stage (SSOT). Human or
agent may run this skill; legality and auto-dispatch follow `dispatch` +
delivery contract + latest handoff.

Record D-check findings and source freshness under blockers/signals.
`next_candidates` never authorize invoke.
