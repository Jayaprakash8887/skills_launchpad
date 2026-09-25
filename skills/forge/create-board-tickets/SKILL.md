---
name: create-board-tickets
description: >-
  After spec PR merge, seed the programme engineering board from Implementation
  Plan §9 WorkManifest: verify merge gate and board binding, present the EPIC/wave
  plan, then after explicit authorization create epic and wave issues. Human
  walker ForgeClient parity (create_board_tickets). Orchestrators use
  BoardService / ForgeClient on board-tickets-action — do not auto-invoke.
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/reports/**, .harness/profile.yaml
---

# Create board tickets

Human-walker equivalent of Gateflow **board create**
(`forge.action: create_board_tickets`).

**One command after merge:** read plan §9 → preflight → confirm → create.
There is no separate `/board-seed` content skill. At seed time WorkManifest
lives in the implementation plan §9 (**walk-time carrier**). After successful
seed, **board issues are the long-term WorkManifest home** — the plan file may
be purged at initiative closure
([`.harness/references/artifact-write-contract.md`](.harness/references/artifact-write-contract.md),
[`.harness/references/workmanifest-contract.md`](.harness/references/workmanifest-contract.md)).

**Do not run before spec merge.** **Do not write product code.**

## NON-NEGOTIABLE

1. Resolve layout from `.harness/profile.yaml` or
   [references/layout-defaults.md](references/layout-defaults.md).
2. **Spec merge gate first** — merged `Implementation-Plan-{initiative}.md` on
   integration branch; closed spec PR had `spec-lgtm` on merge head when
   verifiable.
3. **Board binding** — resolve programme board from **read-only meta** governance:
   `{workspace}/{meta_repo}/config/governance-*.yaml` → `project_board.name`.
   If missing, run `launchpad board-bind --client <id>` and stop. Governance
   **wins** over plan §9 `target.project` free text.
4. **Validate WorkManifest before mutate** — parse §9 YAML and run
   `scripts/workmanifest_contract.py` / `validate_workmanifest` for
   `apiVersion: prayog/v1` + `kind: WorkManifest`. Require
   `workmanifest-contract-pass` (plan P16). Reject unsupported
   `apiVersion`/`kind`. Do **not** create issues on a failing contract.
   Require `epic`, `work[]` with wave ids `W0`…`Wn`, and each wave's
   `tasks[]` with stable `TASK-*`, `implements`, `depends_on`, exit proof,
   and verification as defined in
   [`.harness/references/workmanifest-contract.md`](.harness/references/workmanifest-contract.md).
5. **Projection only** — project epic/wave/task **summaries** from the
   canonical WorkManifest into board issue titles/bodies. After seed, board
   holds long-term identity; do not invent TASK ids, REQ mappings,
   dependencies, exit criteria, or proof summaries that are absent from §9
   at seed time. Record created issue URLs/ids in the seed summary so
   `/pre-implement` can spend without requiring the plan file forever.
6. **Idempotent** — search existing issues by initiative label; create only
   missing items; link existing waves under EPIC when parent missing.
7. **Hierarchy** — EPIC first, then each wave as sub-issue on the same org
   Project. Initiative label on every issue. Wave bodies retain TASK ids,
   REQ mappings, dependencies, exit criteria, and proof summary from the
   manifest.
8. **Explicit authorization before mutate.** Present the seed plan; create only
   after the human confirms. Authorization, branch, commit, PR, label, and
   issue-creation behavior otherwise unchanged.
9. Never apply approval labels (`*-lgtm`). Tool-neutral Forge tooling (`gh`,
   project APIs, …) — examples only.
10. If tooling unavailable, print exact commands from
    [references/output-template.md](references/output-template.md) and stop —
    do not claim `seeded`.
11. Ids: `.harness/references/id-conventions.md`. Paths:
    `.harness/references/artifact-write-contract.md`. Checks: **B1–B8**.

## Inputs

1. **Initiative id** — (REQUIRED)
2. **Integration branch** — (REQUIRED) default `develop`
3. **Merged plan** — `{reports_dir}/{plan_prefix}-{initiative}.md` §9
4. **Meta governance** — (REQUIRED) sibling meta clone /
   `governance-<org>.yaml`

## Prerequisite

- Spec PR **merged**; WorkManifest contract pass on §9 (`workmanifest-contract-pass` / P16)
- Programme board configured (`project_board.enabled` + `name`)
- Pin next step: `board-tickets-action` (`forge.action: create_board_tickets`)

## Process

1. **T0 Gather** — initiative, plan path, §9 YAML, governance board, repo slug,
   integration HEAD
2. **T1 Verify merge gate** — plan on integration; optional closed spec PR with
   `spec-lgtm`; stop if still on open spec branch
3. **T1b Validate WorkManifest** — run shared contract validator; stop on any
   structured error (unsupported version, DAG/exit/live violations)
4. **T2 Dedupe search** — existing issues by initiative label (read-only)
5. **T3 Present seed plan** — EPIC + waves + preserved TASK metadata summary,
   board name/URL, create vs existing; ask for authorization
6. **T4 Execute** (authorized only) — create/update EPIC and waves; project
   links / sub-issues per board model; wave bodies carry projected TASK
   metadata from the manifest
7. **T5 Report** — issue URLs; preserved task metadata; `signals.seeded` /
   `already-seeded`; handoff

Use [references/output-template.md](references/output-template.md) and
[references/checks.md](references/checks.md) (B1–B8).

## Workflow handoff

1. Append/emit envelope from `.harness/references/handoff-envelope.md`. Stage id
   for this forge skill note: `create-board-tickets` (not a graph node).
2. Dual-write `handoff_path` when bound.
3. After successful seed, programme continues per pin
   (`board-tickets-action` `pass` → `wave-in-progress-action` → `pre-implement`).
   Do not invent graph edges.
4. Honor pin `requires` on `board-tickets-action` (spec merged, plan current,
   `workmanifest-contract-pass`).
