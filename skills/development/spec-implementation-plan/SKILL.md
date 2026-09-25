---
name: spec-implementation-plan
description: >-
  After feasibility (and technical review when applicable), produce a
  wave-level implementation plan with REQ/TASK/FILE/TEST tables and a
  WorkManifest YAML seed section (§9). Runs while the spec PR is open,
  before spec merge. Board seeding (gh issue create) happens after spec
  PR merge — not before.
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/**, .claude/rules/**
metadata:
  background_eligible: true
  background_trigger: "spec PR branch: Accepted TDD/ADRs on head when required; spec-pending"
---

# Spec implementation plan

Turn an accepted initiative spec (+ feasibility report + technical review when
present) into an **executable plan with a WorkManifest artifact (§9)**. **Do not
implement** — plan only.

Persist the plan locally and emit Forge readiness for the **spec PR branch**
alongside spec, feasibility, and TDD. Table shape borrowed from awesome-copilot
`create-implementation-plan` (REQ/TASK/FILE/TEST/RISK). §9 WorkManifest YAML is
generated here; **dev seeds the board after spec PR merge**.

**Prayog owns the WorkManifest contract** (`apiVersion: prayog/v1`,
`.harness/references/workmanifest-contract.md`). Launchpad only materializes the pin —
it does not own, parse, or execute WorkManifest.

## NON-NEGOTIABLE

1. Never skip a check in [references/checks.md](references/checks.md). Mark SKIPPED with reason.
2. Every TASK has **objective exit evidence**: observable exit criteria, proving
   command or review, expected result, and evidence location — plus an
   **Implements** list of product `REQ-*` ids and toolchain commands where
   applicable. Do not invent shadow `REQ-W*` ids — see
   `.harness/references/id-conventions.md`.
3. Every acceptance criterion maps to a verification layer (unit,
   integration/contract, smoke, or sandbox) in the wave Verification Coverage
   table. Plan scope must not exceed the initiative spec.
4. Dual output: chat summary + saved plan file (local + Forge readiness).
5. Run T0–T5 control loop.
6. Wave IDs must use `W0`, `W1`, … (one GitHub Issue per wave; WorkManifest `id:`
   convention).
7. Every TASK row must include `codebase`, `spec_path`, `verify_command`,
   **Implements `REQ-*`**, `depends_on`, file path/action scope, and exit
   proof fields — required for WorkManifest generation. §9 wave entries must
   include `tasks[]`, `verification`, and a body table listing those TASK ids.
8. Spec product-spec **H1–H3** citations (and **G1** when applicable) must agree
   with live handoff; tip continuous. Stop on authority drift. Feas/TDD file
   digests are walk-time only — not long-term `stale` SSOT. Implementation-Plan
   is walk-time (§9 → board); may be purged at initiative closure.
9. Resolve canonical `check_command`, `test_command`, `verify_command`, and
   `ground_command` before planning. Required commands may come from the
   consumer profile, `CLAUDE.md`, or `tests_readme`; missing required commands
   block the plan. `verify_command` is the **live** script entry under
   `live_verify_dir` — never `{test_command}` / unit-only. Use N/A with reason
   only when a layer is not applicable. When P15 applies (new/material product
   surface), bare N/A or unit-as-live is invalid — co-ship the verify FILE **and**
   fixture pack path(s) under `fixtures_dir` for the capability (`CAP-*`) and/or
   journey (`J-*`) rung being shipped (see [references/checks.md](references/checks.md)
   P15; `.harness/references/live-fixture-contract.md`).
10. Persist the plan locally and fill `handoff.forge` for `/commit-workspace`
    onto the **same Draft spec PR**. Do **not** commit, push, branch, open PRs,
    apply labels, create issues, or merge inside this skill. Coding-readiness
    label stays **`spec-pending`**. After T5, present the **coding-readiness
    unlock checklist** from the output template so PE knows when to set
    `spec-lgtm`.
11. Select workflow outcome from the rubric below; map evidence deterministically.
12. Before coding-readiness, run a **read-only cross-artifact consistency pass**
    (spec ↔ plan REQ ids, plan ↔ §9 WorkManifest, Accepted ADR citations).
    Corrections belong in the **owning** artifact — do not invent a parallel
    truth in chat.
13. Live-verify coverage lives in the artifact's own marker, not in
    `tests/README.md` or as a growing table in `implementation-status.md` —
    see `.harness/references/live-verify-coverage-contract.md`. Run the
    required overlap check (P15) via `--capability` / `--journey` / `--req`
    before declaring a new `live_verify_dir` or fixture FILE. `covers` must
    include relevant `CAP-*` and/or `J-*` (plus `REQ-*`). As-built writes go to
    `Implementation-Status-{INIT}.md` (detail) + one index row in
    `implementation-status.md` (pointer) — never a new table appended to the
    shared index.
14. **Capability ≠ journey.** Plan separate prove artifacts/`covers` when both
    rungs ship; do not collapse journey proof into “all CAP journeys passed”.
    Populate `dependencies`, `fixtures`, and `human_observations` when opaque
    (logs alone are not pass evidence).
15. If a codegraph provider is available (MCP tool matching
    `.harness/references/codegraph-tool-contract.md`, or a local CLI), prefer
    it for architecture/impact/coverage questions. Always fall back to direct
    `source_roots` reads when unavailable — never block or change outcome
    selection on its absence.

## Inputs

Resolve paths from `.harness/profile.yaml` or [references/layout-defaults.md](references/layout-defaults.md).

**Dual workspace:** `workspace` = app coding root (plan / WorkManifest).
`meta_workspace` when bound = meta checkout for PRD / impact-map freshness.
Do not invent a meta path when empty.

1. **Initiative spec** — on spec branch (REQUIRED)
2. **Feasibility report** — if exists (RECOMMENDED)
3. **Technical review** — `Technical-Review-{initiative}.md` (REQUIRED). The
   pin always routes feasibility (`pass` or `findings`) into
   `/spec-technical-review` before planning — a genuinely absent file is a
   stale/skipped-stage condition (`needs-input`), not an optional input. A
   clean feasibility run may still produce a **light-confirmation** TDD with
   zero ADRs — that is a valid, present file, not the same thing as no file
   existing. Do not treat "no `NEW-ADR` findings" as license to skip reading
   this file.
4. **As-built**, **tests_readme**, **live_verify_dir** layout (REQUIRED for test tasks)
5. **Layout** — `.harness/profile.yaml` or [references/layout-defaults.md](references/layout-defaults.md)
6. **`rules_glob`** — workspace MDC rules (REQUIRED). Read before T2 Analyze.
7. **`adr_dir`** — architecture decision records (REQUIRED). Run relevant-ADR pass per [references/governance.md](references/governance.md) before T2 Analyze.
8. **Canonical handoff references** — product-spec H1–H3 (+ G1 when applicable)
   (REQUIRED; resolve under `meta_workspace` when bound)
9. **Command contract** — canonical check, test, live verify (`verify_command`), and ground
   commands or explicit N/A rationale (REQUIRED)
10. **Codegraph provider** — OPTIONAL — see `.harness/references/codegraph-tool-contract.md`

## Prerequisite

Run **while the Draft spec PR is open**, **before spec merge**, after:
- Feasibility accepted (no blocking PM questions on meta PRD PR)
- `/spec-technical-review` completed (pin always routes feasibility → TDD)
- **`technical-review-approval` satisfied in files** — TDD `Status: Accepted`
  and every required ADR file in `{adr_dir}` is `Accepted` on the current head
- Product-spec H1–H3 citations and approval references are CURRENT (authority,
  not feas/TDD digests as SSOT)

> **Artifact gate vs GitHub gate**
> Planning requires **Accepted TDD/ADR files** (P12/P13). It does **not**
> require `spec-lgtm`. PE sets **`spec-lgtm` + GitHub Approve + attestation**
> only after this plan is published via Forge — that unlocks merge and
> `/create-board-tickets`.

## Process

1. **T0 Gather and freshness gate** — spec waves, feasibility findings,
   technical review, H1–H3 / G1 references, command contract, repo layout; stop
   if durable authority is stale or a required command is unresolved
2. **T1 Understand** — initiative id, wave boundaries, PR granularity from spec
3. **T2 Analyze** — map each wave to concrete files and tests; cross-reference `rules_glob` and relevant ADRs; flag spec wording that conflicts with MDC patterns or Accepted ADRs as **MDC notes** / **ADR notes** in the TASK table
4. **T3 Plan** — build REQ/TASK/FILE tables per wave; verify every TDD §4
   `ADR_REQUIRED` row links an **Accepted** file in `{adr_dir}` (created by
   `/spec-technical-review`, accepted during PE review — do not add promotion
   tasks); cite those ADR ids in TASK **ADR notes**; collect
   `codebase`/`spec_path`/`verify_command`/depends_on/files/exit per TASK;
   map each acceptance criterion to a verification layer
5. **T4 Execute** — write plan; build WorkManifest seed section (`prayog/v1`);
   run P1–P16 checks including shared validator; persist locally and fill Forge
   readiness (do not commit here)
6. **T5 Verify** — self-contained plan readable by a fresh session; WorkManifest
   contract passes; read-only cross-artifact consistency; select workflow
   outcome; present coding-readiness unlock checklist (§10) in chat for PE

## Outcome selection (workflow edges)

Map evidence to exactly one outcome declared for `spec-implementation-plan` in
pinned `workflow.yaml` (this stage has no `findings` edge):

| Outcome | When | Next (from workflow) |
|---------|------|----------------------|
| `pass` | P1–P16 PASS; sources CURRENT; Accepted TDD/ADRs when required; plan ready for coding-readiness | `coding-readiness` |
| `needs-input` | Authoritative source is **absent or unreadable**, so the requirement cannot be determined | `spec-human-decision` |
| `blocked` | Authoritative source **exists** and shows an unsatisfied gate: Draft ADR, unaccepted TDD, missing PE approval, or unresolved blocker (P12/P13 FAIL) | `spec-human-decision` |
| `stale` | Product-spec H1–H3 / G1 / tip authority drift | `initiative-feasibility` |
| `failed` | Rendering/validation failure, or P4/P15/P16 contract failures (vague exit, dependency cycle, missing proof/live, unit-as-live) on otherwise present inputs | `workflow-stop` |

Check FAIL is not automatically `failed` — classify per the table (P12/P13 Draft
ADR → `blocked`; missing unreadable source → `needs-input`; mismatch → `stale`;
WorkManifest/exit/live contract → `failed`).

## Output

Save to `{reports_dir}/{plan_prefix}-{initiative}.md`.

Use [references/output-template.md](references/output-template.md).

## WorkManifest integration

The plan's final section (§9) emits a ready-to-use WorkManifest YAML stub under
the Prayog contract (`.harness/references/workmanifest-contract.md`). Validate
with `scripts/workmanifest_contract.py` before claiming P16 PASS.

**After spec PR merge** — not before — run **`/create-board-tickets`** (forge skill,
stack-agnostic). That skill reads §9, governance board binding from read-only
meta, creates EPIC + wave sub-issues on the programme Project, and hands off to
`/pre-implement`. Board text is a **projection**, not a second authority.

When authoring §9, set `target.org` and `target.project` from governance
(`project_board.name` in `{meta_repo}/config/governance-*.yaml`). Do not invent
board names. Do not put mutable board `status` or runtime evidence in §9.

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the plan. Use stage `spec-implementation-plan`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates` and `human_checkpoint` from pinned root `workflow.yaml` for `(stage: spec-implementation-plan, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint` — never because the artifact "should be reviewed."


4. Follow `.harness/references/forge-side-effects.md#content-producers` when this stage's pin has `forge.commit_workspace` other than `disabled` or next is an `external-action` with `forge.requires` — fill `handoff.forge` / recommend the matching `/forge` skill; do not treat local CLI as skill success.


**Transitions:** pinned root `workflow.yaml` for this stage (SSOT). Human or
agent may run this skill; legality and auto-dispatch follow `dispatch` +
delivery contract + latest handoff. `pass` resolves to human-checkpoint
`coding-readiness` (`purpose: coding-readiness`), then authorized `spec-merge`.

After the spec PR is merged, the workflow selects `board-tickets-action`
(`external-action`, `forge.action: create_board_tickets`); humans run
`/create-board-tickets`. Planning does not seed the board itself.
`next_candidates` never authorize invoke.
