---
name: purge-initiative-artifacts-meta
description: >-
  PM-lane purge: delete allowlisted meta working papers (Validation-Report,
  Resolution) for one initiative. Refuse KEEP paths (PRD, Impact-Map). Commit
  via Forge when pin requires it. No report file — success is handoff only.
  Independent of app/eng purge. No authorize-before-delete. Use Enter-at or
  /purge-initiative-artifacts-meta when the meta closure hop is due.
disable-model-invocation: true
paths: prd/**, .harness/profile.yaml
metadata:
  background_eligible: true
  background_trigger: "initiative-closure lane — purge meta working papers"
---

# Purge initiative artifacts (meta)

**Lane:** PM / meta repo (`profile: meta-pm`).

Delete **PURGE-set** files under the **meta** repo for one initiative.
**Do not** delete durable KEEP roots. Git history remains the archive.

This skill is **independent** of app/engineering purge. Do not require, invoke,
or document `/purge-initiative-artifacts-app` as a prerequisite or prior step —
orchestration order lives only in pinned `workflow.yaml`.

Normative allowlist / refuse:
[`.harness/references/artifact-write-contract.md`](.harness/references/artifact-write-contract.md).

## NON-NEGOTIABLE

1. Resolve layout from `.harness/profile.yaml` or
   [references/layout-defaults.md](references/layout-defaults.md).
2. Require initiative id `INIT-*`. Scope deletes to that initiative only.
3. Delete **only** when present:
   - `{reports_dir}/Validation-Report-{INIT}.md`
   - `{reports_dir}/Resolution-{INIT}.md`
4. **Refuse** (never delete): `prd/INIT-*.md` for this initiative;
   `{reports_dir}/Impact-Map-{INIT}.md`; service catalog; governance.
5. Idempotent: missing allowlisted files → ok. Empty delete set → still `pass`
   with rationale in handoff signals.
6. Workspace is the **meta** checkout (Gateflow binds meta root; human runs in
   meta clone). Fill `handoff.forge` for `commit_workspace` when pin requires
   it. When pin next is an `open_draft_pr` external-action, fill title and
   forge requires **without** creating a reports/ purge file (see output
   template).
7. No Gateflow authorize-before-delete. No merge. Never apply `*-lgtm`.
8. **No report file.** Do **not** write `Purge-*.md` (or any new artifact)
   under `{reports_dir}`. Goal achieved = handoff envelope (+ baton when bound)
   with delete/refuse lists in `signals`. Chat may repeat the same summary.
9. Dual-walker parity with human `/purge-initiative-artifacts-meta`.

## Inputs

1. **Initiative id** — (REQUIRED)
2. **Workspace** — meta repo root (REQUIRED)
3. **Layout** — profile or layout-defaults
4. **Handoff baton** — when `handoff_path` bound

## Process

1. **T0** — resolve INIT and reports_dir; list allowlist candidates.
2. **T1** — classify delete / missing_ok / refused.
3. **T2** — delete delete-set only.
4. **T3** — emit handoff only (`stage: purge-initiative-artifacts-meta`); no
   reports file.
5. **T4** — fill `handoff.forge` for `commit_workspace` and, when pin next is
   `open_draft_pr`, for that action (title + body from signals — no reports
   path).

## Outcome selection

Map evidence to pinned `workflow.yaml` for this stage. Do not hardcode sibling
skill names as procedure dependencies.

| Outcome | When |
|---------|------|
| `pass` | Allowlist processed; no KEEP deleted; handoff emitted with signals |
| `needs-input` | Initiative id or layout unreadable |
| `blocked` | Attempt would touch KEEP |
| `failed` | Delete/IO error |

## Output

Use [references/output-template.md](references/output-template.md) (handoff
only). Checks: [references/checks.md](references/checks.md).

## Workflow handoff

1. Emit envelope from `.harness/references/handoff-envelope.md`. Stage
   `purge-initiative-artifacts-meta`. Set `artifact.path: null` (no durable
   report). Put path lists under `signals` (`deleted`, `missing_ok`, `refused`,
   counts). Optionally set `signals.pr_body` to a short markdown summary for
   Forge/PR consumers.
2. When `handoff_path` is bound, **overwrite** that path with the same
   `handoff:` envelope before exit.
3. Derive `next_candidates`, `human_checkpoint`, and `external_action` from
   pinned `workflow.yaml` for `(stage: purge-initiative-artifacts-meta, outcome)`.
   Set `human_checkpoint: true` only when the resolved next node's `type` is
   `human-checkpoint`.
4. When next is an `external-action` with `open_draft_pr`, fill `handoff.forge`
   per pin `requires`. Prefer synthesizing PR body from `signals` / `pr_body`
   (runner may materialize an ephemeral body file **outside** `{reports_dir}`).
   Never create `Purge-*.md` under reports.
5. Follow `.harness/references/forge-side-effects.md#content-producers` when pin
   `forge.commit_workspace` is not `disabled` or next is an external-action.
