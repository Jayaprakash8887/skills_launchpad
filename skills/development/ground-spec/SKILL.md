---
name: ground-spec
description: >-
  Validate a completed wave against REQs assigned to that wave by the plan /
  WorkManifest, plus repo artifacts and cross-spec contracts. Produces a Ground
  Report (GF-* findings) including Contracts Produced for next-wave
  pre-implement. Writes locally and emits Forge readiness — never commits or
  merges. Use after Pass-2 learning-extract (closes the wave), before
  wave-done-action / human wave-signoff (merge only).
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/**, src/**, tests/**
metadata:
  background_eligible: true
  background_trigger: "Pass-2 closeout after learning-extract (post human wave-acceptance)"
---

# Ground spec

Validate implementation against the **product spec REQs assigned to this
completed wave** (plan / WorkManifest TASK `implements` lists) and **actual
repo artifacts** — not every future REQ in the full product spec, and not PRD
text alone. Produce a Ground Report that the **next wave's `/pre-implement`
consumes as a contract baseline**.

Content skills write locally and emit Forge readiness; they do not commit,
push, branch, open PRs, label, create issues, or merge.

Canonical artifact:
`{reports_dir}/Ground-Report-{SPEC}-W{N}.md`
([`.harness/references/artifact-write-contract.md`](.harness/references/artifact-write-contract.md)).
Checks: [references/checks.md](references/checks.md) (G1–G10).
Ids: `.harness/references/id-conventions.md` (`GF-*` for findings).

## NON-NEGOTIABLE

1. Resolve paths from `.harness/profile.yaml` or
   [references/layout-defaults.md](references/layout-defaults.md). Include
   `tests/**` in scope when mapping evidence.
2. Run the repo's automated ground check when `{ground_command}` is defined
   in the harness profile. Include full output in the report. If
   `{ground_command}` is not defined, perform manual REQ validation by reading
   `source_roots` and `tests/**` directly.
3. Check every **`REQ-*` assigned to this wave** via plan / WorkManifest TASK
   rows — map each to a verifiable artifact (test result, entry point, module
   boundary, verify script output). Do **not** require coverage of REQs owned
   only by future waves. Use engineering terms: "entry point", "module
   boundary", "output shape" — not language-specific terms.
4. Consume approved plan/manifest intent **plus** actual loop/unit evidence
   and human accept (`Wave-Execution-*`, unit results, `wave-accepted` /
   wave-acceptance). Optional/legacy `Live-Verify-*` is not required. Cite
   layers separately.
5. Check cross-spec contracts: modules from this wave may only consume
   interfaces from prior waves as documented in those waves' Ground Reports.
6. Check boundary rules per ADRs and domain-filtered MDC rules (G5/G6).
7. **Do not** mark spec `human_approved` — already set at `wave-acceptance`
   (only approval signal). This skill prepares the merge package for
   `wave-signoff` (merge/publish only).
8. **Populate the Contracts Produced section** — structured handoff for
   `/pre-implement` of the next wave. Without it, the chain is broken.
9. **Cite learning ids** — when
   `{reports_dir}/Learning-Extract-{initiative}-W{N}.md` exists, add a
   **Learning cited** table of `L-*` ids (do not re-author learning SSOT).
10. Discrepancy / blocker ids use stable **`GF-*`** — cite `REQ-*` in the row,
    not as the blocker primary key. Do **not** reuse feasibility `FF-*`.
11. Write Ground Report and as-built updates **locally**; prepare the
    exact-head merge package for `wave-signoff`; pin routes to
    `wave-done-action` then `wave-signoff` (merge only). Never commit or
    merge from this skill. As-built writes follow the split in
    `.harness/references/artifact-write-contract.md` —
    `Implementation-Status-{INIT}.md` for detail, one index row in
    `implementation-status.md` for the pointer; never append a new table to
    the shared index.
12. If a codegraph provider is available (MCP tool matching
    `.harness/references/codegraph-tool-contract.md`, or a local CLI), prefer
    it for cross-spec contract / boundary questions. Always fall back to
    direct `source_roots` reads when unavailable — never block or change
    outcome selection on its absence.

## Outcome selection

| Outcome | When |
|---------|------|
| `pass` | G1–G10 satisfied (or SKIPPED with reason); no open Blocking `GF-*`; Contracts produced complete; exact-head sign-off package ready |
| `findings` | One or more `GF-*` require code/spec fix before sign-off |
| `needs-input` | Authoritative wave assignment, evidence, or prior Ground Report absent/unreadable |
| `blocked` | Gate prevents grounding (e.g. Pass-1 incomplete, missing accept when required) |
| `failed` | Execution error running ground command or writing the report |

Happy path: `pass` → `wave-done-action` → `wave-signoff`.

## Chain position

Illustrative only — **transitions SSOT:** pinned root `workflow.yaml`
(`dispatch: orchestrated` on this node). Closeout path: `learning-extract`
→ this skill → `wave-done-action` → `wave-signoff`. Pass-1 does **not** route here from `loop-spec`.

```
/learning-extract (Pass-2 / Enter-at)
    ↓
/ground-spec                          ← YOU ARE HERE
  produces: Ground-Report-W{N}.md
            └── §Contracts produced   ← pre-implement for WN+1 reads this
            └── cites L-* from Learning-Extract when present
            └── GF-* findings (not FF-*)
    ↓
  wave-done-action (Forge update_board_status → Done)
  human checkpoint wave-signoff (exact head; merge/publish only)
  → human_approved already from wave-acceptance; record merge SHA
    ↓
/pre-implement (next wave)
  reads: Ground-Report-W{N}.md §Contracts produced
```

## Read order

1. `CLAUDE.md`
2. Plan / WorkManifest wave section — **assigned REQ set** for W{N}
3. Product spec: `docs/specification/product/` — only rows for assigned REQs
4. `docs/specification/as-built/implementation-status.md`
5. `Wave-Execution-{INIT}-W{N}.md`; accept signal (`wave-accepted` / wave-acceptance); optional/legacy `Live-Verify-*` when present
6. Ground reports of prior waves (for cross-spec contract baseline)
7. **Codegraph provider** — OPTIONAL — see `.harness/references/codegraph-tool-contract.md`
7. Relevant ADRs + domain-filtered MDC
8. Ground check output (`{ground_command}`) + unit verification (`{test_command}`)
9. `Learning-Extract-{INIT}-W{N}.md` when present

## Output format

Save report to `{reports_dir}/Ground-Report-{SPEC}-W{N}.md` using
[references/output-template.md](references/output-template.md). Run
[references/checks.md](references/checks.md).

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the saved Ground Report. Use stage `ground-spec`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates` and `human_checkpoint` from pinned root `workflow.yaml` for `(stage: ground-spec, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint` — never because the artifact "should be reviewed."
4. Happy path: `outcome: pass` → next `wave-done-action` (`type: external-action`,
   `forge.action: update_board_status`, `authorization: automated`) →
   `human_checkpoint: false`, `external_action: true`. Fill `handoff.forge`
   `ticket` when bound so ForgeClient can apply Done. Then pin routes to
   `wave-signoff` (human merge/publish only). Do **not** copy `human_checkpoint: true` into
   earlier implement-lane skills on skill→skill edges.


4. Follow `.harness/references/forge-side-effects.md#content-producers` when this stage's pin has `forge.commit_workspace` other than `disabled` or next is an `external-action` with `forge.requires` — fill `handoff.forge` / recommend the matching `/forge` skill; do not treat local CLI as skill success.


**Transitions:** pinned root `workflow.yaml` for this stage (SSOT). Human or
agent may run this skill; orchestrators may auto-dispatch when authorized.
Same legality for both invoke paths.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: {pass | findings | needs-input | blocked | failed}
  artifact:
    path: {reports_dir}/Ground-Report-{SPEC}-W{N}.md
    # digest omitted — walk-time PURGE report, not a durable identity
  blockers: []  # GF-* when findings
  signals:
    wave: W{N}
    contracts_produced: {count}
    assigned_reqs: [...]
  next_candidates:
    # Must match workflow.yaml for outcome — typically wave-done-action
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: {bound_wave_ticket}
```

The Ground Report is not complete without this handoff. Outcome routes follow
`workflow.yaml` (not hardcoded elsewhere). `next_candidates` never authorize
invoke.
