---
name: purge-initiative-artifacts-app
description: >-
  Engineering-lane purge: after initiative-closure judgment, delete allowlisted
  app working papers for one initiative (feas, TDD, plan, per-wave reports,
  Draft ADRs). Refuse KEEP paths (product INIT, Accepted ADRs, source/tests/
  verify scripts). Commit via Forge when pin requires it. No report file —
  success is handoff only. No authorize-before-delete. Use Enter-at or
  /purge-initiative-artifacts-app when the eng closure hop is due.
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/**, .harness/profile.yaml
metadata:
  background_eligible: true
  background_trigger: "initiative-closure.pass — purge app working papers"
---

# Purge initiative artifacts (app)

**Lane:** engineering / app repo (`profile: development`).

Delete **PURGE-set** files under the **app** repo for one initiative.
**Do not** delete durable KEEP roots. Git history remains the archive.

This skill is **independent** of meta/PM purge. Do not require, invoke, or
document `/purge-initiative-artifacts-meta` as a prerequisite or next step —
orchestration order lives only in pinned `workflow.yaml`.

Normative allowlist / refuse:
[`.harness/references/artifact-write-contract.md`](.harness/references/artifact-write-contract.md).

## NON-NEGOTIABLE

1. Resolve layout from `.harness/profile.yaml` or
   [references/layout-defaults.md](references/layout-defaults.md).
2. Require initiative id `INIT-*`. Scope deletes to that initiative only.
3. Delete **only** the app PURGE allowlist when present:
   - `{reports_dir}/Initiative-Feasibility-Report-{INIT}.md`
   - `{reports_dir}/Technical-Review-{INIT}.md`
   - `{reports_dir}/Implementation-Plan-{INIT}.md`
   - `{reports_dir}/Pre-Implement-{INIT}-W*.md`
   - `{reports_dir}/Wave-Execution-{INIT}-W*.md`
   - `{reports_dir}/Live-Verify-{INIT}-W*.md`
   - `{reports_dir}/Ground-Report-*-W*.md` for this initiative/spec
   - `{reports_dir}/Learning-Extract-{INIT}-W*.md`
   - `{adr_dir}/adr-*-*.md` that are still **Draft** (not Accepted)
4. **Refuse** (never delete): `{product_spec_dir}/INIT-*.md` for this
   initiative; **Accepted** ADRs; anything under `source_roots`,
   `unit_tests_dir`, `live_verify_dir` **scripts**, `fixtures_dir` packs;
   `.harness/`; product source;
   `{as_built_dir}/implementation-status.md` (index) and
   `{as_built_dir}/Implementation-Status-{INIT}.md` (this initiative's
   detail) — both `KEEP`, never on the PURGE allowlist.
5. Idempotent: missing allowlisted files → ok. Empty delete set → still `pass`
   with rationale in handoff signals.
6. Work on the **initiative-closure** head cut from integration (`develop`)
   when bound; do not invent a branch. Fill `handoff.forge` for
   `commit_workspace` when pin requires commit. When pin next is an
   `open_draft_pr` external-action (eng closure PR), fill title/body from
   signals **without** creating a reports/ file (see output template).
7. No Gateflow authorize-before-delete. No merge. Never apply `*-lgtm`.
8. **No report file.** Do **not** write `Purge-*.md` (or any new artifact)
   under `{reports_dir}`. Goal achieved = handoff envelope (+ baton when bound)
   with delete/refuse lists in `signals`. Chat may repeat the same summary.
9. Dual-walker: same procedure for human `/purge-initiative-artifacts-app` and
   Gateflow orch.

## Inputs

1. **Initiative id** — (REQUIRED)
2. **Workspace** — app repo root (REQUIRED)
3. **Layout** — profile or layout-defaults
4. **Handoff baton** — when `handoff_path` bound

## Process

1. **T0** — resolve INIT, reports_dir, adr_dir, product_spec_dir; build candidate
   list from allowlist globs.
2. **T1** — classify each path: delete / missing_ok / refused (if somehow KEEP).
3. **T2** — delete delete-set only.
4. **T3** — emit handoff only (`stage: purge-initiative-artifacts-app`); no
   reports file.
5. **T4** — fill `handoff.forge` for `commit_workspace` when pin expects it;
   when pin next is `open_draft_pr`, also fill that action (title + body from
   signals — no reports path).

## Outcome selection

Map evidence to pinned `workflow.yaml` for this stage. Do not hardcode sibling
skill names as procedure dependencies.

| Outcome | When |
|---------|------|
| `pass` | Allowlist processed; no KEEP deleted; handoff emitted with signals |
| `needs-input` | Initiative id or layout unreadable |
| `blocked` | Attempt would touch KEEP; refuse and stop |
| `failed` | Delete/IO error on otherwise valid allowlist |

## Output

Use [references/output-template.md](references/output-template.md) (handoff
only). Checks: [references/checks.md](references/checks.md).

## Workflow handoff

1. Emit envelope from `.harness/references/handoff-envelope.md`. Stage
   `purge-initiative-artifacts-app`. Set `artifact.path: null` (no durable
   report). Put path lists under `signals` (`deleted`, `missing_ok`, `refused`,
   counts). Optionally set `signals.pr_body` to a short markdown summary for
   Forge/PR consumers.
2. When `handoff_path` is bound, **overwrite** that path with the same
   `handoff:` envelope before exit.
3. Derive `next_candidates`, `human_checkpoint`, and `external_action` from
   pinned `workflow.yaml` for `(stage: purge-initiative-artifacts-app, outcome)`.
   Set `human_checkpoint: true` only when the resolved next node's `type` is
   `human-checkpoint`.
4. When next is an `external-action` with `open_draft_pr`, fill `handoff.forge`
   per pin `requires`. Prefer synthesizing PR body from `signals` / `pr_body`
   (runner may materialize an ephemeral body file **outside** `{reports_dir}`).
   Never create `Purge-*.md` under reports.
5. Follow `.harness/references/forge-side-effects.md#content-producers` when pin
   `forge.commit_workspace` is not `disabled` or next is an external-action.
