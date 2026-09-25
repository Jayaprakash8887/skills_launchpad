---
name: initiative-feasibility
description: >-
  After the dev team has written their spec slice from the PRD, review it
  against the current codebase — baseline, gaps, impact, test harness,
  architecture governance (ADR + MDC), risks, and 4-lane triage. Writes the
  report locally and emits Forge readiness for the open Draft spec PR while
  Gate 2 remains spec-pending. Use when the dev has drafted the spec and wants
  to check buildability before technical review and planning.
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/**, .claude/rules/**
background_eligible: true
background_trigger: "spec slice committed to spec PR branch (chore/INIT-*-spec-*)"
---

# Initiative feasibility

Assess whether the **dev team's spec slice** for this initiative is **buildable
in this repo as it exists today**. **Do not implement** — flag only.

The spec slice is written by the dev team after reading the PRD. This skill
reviews it for gaps, codebase alignment, and architecture governance.

Pattern borrowed from awesome-copilot `create-github-issues-for-unmet-specification-requirements` (extract → search code → classify). Evaluation discipline aligned with `validate-requirements`.

## NON-NEGOTIABLE

1. Never skip a check in [references/checks.md](references/checks.md). Mark SKIPPED with reason.
2. Evidence for every finding — spec quote + repo path (file, symbol, or test name).
3. Don't fix — flag. Do not edit product source or product specs unless the user explicitly asks after the report.
4. Dual output: chat summary + saved report file + 4-lane triage.
5. Run T0–T5 control loop (Gather → Understand → Analyze → Plan → Execute → Verify).
6. Verify **light source freshness** before F1: product-spec header citations
   (**H1** PRD digest, **H2** scope digest, **H3** map revision) and tip
   continuity; **G1** meta head + approval while Gate 1 still applies. See
   `.harness/references/artifact-write-contract.md`. Stop on authority drift.
   Do **not** require mid-lane report digests as staleness SSOT.
7. Every open item must record lane, blocking, owner, status, required-by
   stage, default-if-deferred, evidence, and resolution reference.
8. **Read-only content skill.** Persist the feasibility report locally and fill
   `handoff.forge` for `/commit-workspace` (or Gateflow ForgeClient) onto the
   **same Draft spec PR** branch opened by `/spec-draft`. Do **not** create
   branches, commit, push, open PRs, apply labels, create issues, merge, run
   probes, edit product source, or clean up environments. Gate 2 label stays
   **`spec-pending`** — do not set `spec-lgtm` during feasibility.
9. **Do not implement** product code. Spec-only artifacts; publication is Forge.
10. If a codegraph provider is available (MCP tool matching
    `.harness/references/codegraph-tool-contract.md`, or a local CLI), prefer
    it for architecture/impact/coverage questions. Always fall back to direct
    `source_roots` reads when unavailable — never block or change outcome
    selection on its absence.

## Inputs

Gather before starting. Resolve paths from `.harness/profile.yaml` or [references/layout-defaults.md](references/layout-defaults.md).

**Dual workspace (orchestrated / Gateflow):** `workspace` = app coding root
(spec slice + feasibility report). `meta_workspace` when bound = meta checkout
for PRD / impact-map freshness. Do not invent a meta path when empty.

1. **Initiative spec slice** — primary doc (REQUIRED); written by dev team, lives under `product_spec_dir` in `workspace`
2. **PRD** — upstream requirements from `<client>-meta/prd/` under
   `meta_workspace` when bound (OPTIONAL; for conformance context; link from spec header)
3. **Canonical impact map + approval evidence** — (REQUIRED) exact revision and
   tech-lead review referenced by the spec header (resolve under `meta_workspace` when bound)
4. **As-built** — `implementation-status.md` (REQUIRED)
5. **Tests** — `tests_readme`, `unit_tests_dir`, `live_verify_dir`, and toolchain config from profile (REQUIRED)
6. **Source** — modules under `source_roots` from profile (REQUIRED)
7. **Prior feasibility report** — for incremental re-run (OPTIONAL)
8. **Layout** — `.harness/profile.yaml` or [references/layout-defaults.md](references/layout-defaults.md)
9. **`rules_glob`** — workspace MDC rules (REQUIRED). Read before T2 Analyze.
10. **`adr_dir`** — architecture decision records (REQUIRED). Run relevant-ADR pass per [references/governance.md](references/governance.md) before T2 Analyze.
11. **Codegraph provider** — OPTIONAL — see `.harness/references/codegraph-tool-contract.md`

## When to use

- Dev has written spec slice and wants to check buildability before spec PR merge
- After dev updates spec — re-run on changed sections
- User asks: feasibility, impact, gap analysis, spec vs codebase

## Process

1. **T0 Gather and freshness gate** — inventory inputs; compare product-spec
   **H1–H3** citations (and **G1** when applicable) with live PRD/map/review.
   If the repo was removed, deferred, or its scope digest changed, stop and
   emit the map's ripple action. Feasibility report digests are walk-time only.
2. **T1 Understand** — initiative id, spec branch, review objective
3. **T2 Analyze** — read spec waves/capabilities; scan repo evidence; cross-reference `rules_glob` and relevant ADRs; flag spec wording that conflicts with MDC patterns or Accepted ADRs
4. **T3 Plan** — which checks run (full vs incremental)
5. **T4 Execute** — run checks F1–F14 per [references/checks.md](references/checks.md)
6. **T5 Verify** — save report locally; publish summary + 4-lane triage; select
   workflow outcome from the lane-to-outcome rubric; fill Forge readiness

## Outcome selection (lane → workflow)

Map evidence to exactly one outcome declared for `initiative-feasibility` in
pinned `workflow.yaml`. Prefer the first matching row:

| Outcome | When | Next (from workflow) |
|---------|------|----------------------|
| `stale` | Product-spec H1–H3 / G1 / tip authority drift | `spec-draft` |
| `failed` | Execution/analysis failure on otherwise valid inputs | `workflow-stop` |
| `blocked` | Explicit approval/policy gate prevents progress (repo held, gate closed) | `spec-human-decision` |
| `needs-input` | Unresolved blocking **PM** or **domain** item (missing product/SME answer) | `spec-human-decision` |
| `findings` | Unresolved blocking **PE** / ADR / engineering item (Critical or Should-fix PE-lane) | `spec-technical-review` |
| `pass` | Zero unresolved blocking findings; informational/Verify/Gap observations may remain | `spec-technical-review` |

Both `pass` and `findings` enter `/spec-technical-review` before plan (pin SSOT).
`pass` still means “no blocking PE findings at feasibility”; TDD may record
N/A / light confirmation. Do **not** skip technical review on clean feasibility.

Do **not** route PM/domain blockers to technical review via `findings`. Do **not**
emit `pass` while unresolved PE/ADR blockers remain. Informational observations
are report signals — they do not alone select `findings`.

## Impact-map revision handling

- `continue` — scope digest unchanged; record the newer revision check.
- `re-draft` / `re-feasibility` — scope digest changed; update the spec before
  running incremental feasibility.
- `hold` / `close` — repo removed, deferred, blocked, or approval stale.
- `re-plan` — dependency/build order changed; invalidate any existing plan.

Never carry a prior feasibility finding forward across changed **H1–H3**
authority without explicitly re-evaluating that finding. Feasibility report
files are PURGE at initiative closure.

## Output

Save to `{reports_dir}/{feasibility_prefix}-{initiative}.md` (from profile).

Use [references/output-template.md](references/output-template.md).

## Open items — 4-lane triage

End with four lanes (see output template):

- **PM questions** — product scope, UX, priority; comment on **meta PRD PR** (plain English)
- **PE questions** — engineering decisions, ADR gaps, test policy; comment on **spec PR**; resolved by `/spec-technical-review`
- **Domain clarifications** — business source-of-truth; route to named SME (meta PRD PR or issue)
- **Auto-fixable** — naming drift, inferred cross-references; record as findings/signals for later agent fix — do not mutate product source inside this skill

Do **not** route engineering decisions to PM. Apply the routing rubric in
the `spec-technical-review` skill's `references/governance.md`.

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the saved report. Use stage `initiative-feasibility`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates` and `human_checkpoint` from pinned root `workflow.yaml` for `(stage: initiative-feasibility, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint` — never because the artifact "should be reviewed."
4. Follow `.harness/references/forge-side-effects.md#content-producers` when this stage's pin has `forge.commit_workspace` other than `disabled` or next is an `external-action` with `forge.requires` — fill `handoff.forge` / recommend `/commit-workspace`; do not treat local CLI as skill success. Content skill success ≠ report published.


**Transitions:** pinned root `workflow.yaml` for this stage (SSOT) — including
`pass` vs `findings` routes. Human or agent may run this skill; legality and
auto-dispatch follow `dispatch` + delivery contract + latest handoff.

Put lane counts, NEW-ADR, selected outcome rationale, and ripple action in
`signals`; finding ids belong in `blockers` as **`FF-*`** (never bare `F-12`).
`next_candidates` never authorize invoke.
