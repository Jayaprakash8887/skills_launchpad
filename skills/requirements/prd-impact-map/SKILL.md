---
name: prd-impact-map
description: >-
  Map a PRD to affected repos using the service catalog. Reads the PRD and
  the resolved config/service-catalog*.yaml from <client>-meta, matches PRD capabilities
  to service descriptions, generates a versioned impact-map artifact locally,
  and produces a PR-readiness handoff (handoff.forge for open_draft_pr).
  Publish via /open-draft-pr or orchestrator ForgeClient after authorization —
  not inside this skill. Run in <client>-meta after PRD validation and before
  app spec PRs.
disable-model-invocation: true
paths: prd/**, config/service-catalog*.yaml
background_eligible: true
background_trigger: "validated PRD is ready for impact mapping"
---

# PRD impact map

Identify which repos are affected by a PRD and produce an impact map for
tech lead confirmation. **Do not open spec PRs in app repos** — engineering
opens those after tech lead confirms the map.

## NON-NEGOTIABLE

1. Resolve **one** service catalog under `<client>-meta/config/` before reading
   the PRD. Prefer `service-catalog-<org>.yaml` when org is known (unique
   `governance-<org>.yaml` suffix). Otherwise accept exactly one of
   `service-catalog.yaml` or `service-catalog-*.yaml`. Fail closed on zero or
   multiple matches. Do not merge catalogs. Never hardcode a tenant org.
   Understand what each service owns before matching.
2. Match PRD capabilities to service `description` and `owns` fields
   semantically — do not rely on keyword matching alone.
3. Include transitively affected repos via `depends_on` chains. If repo B
   depends on repo A and the PRD touches A, flag B as potentially affected.
4. Explicitly list repos that are **not** affected and why — this is as
   important as the affected list.
5. Save the canonical map at `reports_dir/Impact-Map-{INIT-id}.md`. A PR
   comment or label is never the source of truth. **Never** write
   `Impact-Map-*-revN.md` / `*-v2` siblings — overwrite the canonical path and
   bump `map_revision` (see `.harness/references/artifact-write-contract.md`).
6. Increment `map_revision` for every changed map and record the prior
   revision plus change reason. Do not edit history to make a revision appear
   unchanged. If a legacy `*-revN` sibling exists, migrate into the canonical
   path and stop writing the sibling (purge siblings only via
   `/purge-initiative-artifacts-meta` allowlist — Impact-Map is KEEP).
7. **Mint durable identities H1–H3** per
   `.harness/references/artifact-write-contract.md`: **H1** `source_prd_digest`
   (PRD bytes), **H2** one `scope_digest` per affected repo (canonical payload
   recipe), **H3** `map_revision`. Prefer `CAP-*` / `REQ-*` in capability lists
   (legacy free-text or `FR-*` acceptable until next PRD edit — see
   `.harness/references/id-conventions.md`). A tech-lead approval (**G1**) is
   valid only for the exact meta PR head SHA carrying those values. Impact-Map
   is KEEP through initiative-closure purge; do not treat mid-lane app report
   digests as map identity.
8. Treat `impact-map-*` labels as projections. If artifact, review, and label
   disagree, the gate is closed.
9. A material PRD/map change or tech-lead revocation invalidates approval.
   Produce a downstream ripple action for every repo already in flight.
10. **No forge mutations in this skill.** Do not create a branch, commit, push,
    PR, comment, review request, or label here. Fill `handoff.forge` for
    `open_draft_pr` and recommend `/open-draft-pr` (or orchestrator ForgeClient
    on `prd-pr-action`). See `.harness/references/forge-side-effects.md#content-producers`.
11. Gate labels are a visible workflow projection, not authority. Exactly one
    PE gate label may be active: `impact-map-pending`, `impact-map-lgtm`, or
    `impact-map-blocked`. `impact-map-revised` and `impact-map-stale` are
    additional invalidation labels and always close the gate.

## Inputs

1. **PRD** — (REQUIRED) `prd/INIT-{id}.md` in `<client>-meta`
2. **Service catalog** — (REQUIRED) resolved file under `<client>-meta/config/`
   (`service-catalog-<org>.yaml` preferred; else exactly one
   `service-catalog.yaml` or `service-catalog-*.yaml`)
3. **Git state** — (REQUIRED) current branch/base, changed files, and whether a
   meta PR already exists; an existing PR is not required for the initial map
4. **Meta PR state** — (OPTIONAL) URL/head/reviews/labels when revising an open PR
5. **Prior impact map** — (OPTIONAL) required when revising an existing map
6. **In-flight app artifacts** — (OPTIONAL) spec/TDD/plan status for ripple actions
7. **Layout** — `reports_dir` from `.harness/profile.yaml`; default `prd/reports`

## Initiative identity and PR collision gate

Before mapping, search local files/branches and, when `gh` is configured, open
PRs for:

- the canonical initiative id,
- legacy/short initiative ids referenced by the PRD or filenames,
- PRD titles/slugs that may represent the same business initiative,
- prior `Impact-Map-*` artifacts.

Classify detection separately from the human decision:

| Detection | Meaning | T0 result |
|-----------|---------|-----------|
| `no-collision` | No competing initiative/PR found | Continue |
| `same-initiative` | Existing PR/branch represents this product initiative | `needs-input` |
| `unrelated` | Similar id/title is demonstrably a different initiative | Continue with evidence |
| `ambiguous` | Identity cannot be determined | `needs-input` |

For `same-initiative` or `ambiguous`, the agent may recommend—but never select—
one human resolution:

- `reconcile-existing`
- `supersede-existing`
- `unrelated-confirmed`

Persist the distinction in the response:

```yaml
identity_collision:
  detection: same-initiative
  evidence: [...]
  recommended_resolution: supersede-existing
  human_decision: pending
  external_action_authorized: false
```

Never propose a second PR while identity is unresolved. Closing, commenting on,
or updating an existing PR is an external action requiring explicit user
authorization.

**HARD STOP:** while `human_decision: pending`, do not execute T1–T5, assign
impact-map question ids, compute repo scope digests, write/update an impact-map
artifact, or produce PR readiness. Emit only the collision report and a
`needs-input` workflow handoff.

Choosing a resolution does not by itself authorize GitHub action. Present the
exact comment/close/update operations and obtain separate explicit
authorization. After reconciliation/supersession is complete, restart at T0;
do not resume a partial mapping run.

## Process

1. **T0 Gather and identity gate** — PRD, service catalog, local git state,
   optional meta PR state, prior map, in-flight app artifacts; run detection
   above and continue only for `no-collision`, evidenced `unrelated`, or a fully
   completed human resolution. Otherwise emit `needs-input` and stop.
2. **T1 Understand** — list PRD capability areas (data flows, user actions,
   integrations, storage, auth, notifications, etc.)
3. **T2 Match** — for each capability, match to service `description` + `owns`;
   include transitive via `depends_on`
4. **T3 Diff and order** — compare prior revision; derive build/merge order;
   classify each repo as added, removed, unchanged, narrowed, widened, or reordered
5. **T4 Output** — write the canonical artifact using
   [references/output-template.md](references/output-template.md); compute the
   PRD digest and per-repo scope digests from normalized content
6. **T5 Verify and hand off** — verify artifact completeness; present:
   - generated/changed files,
   - impact summary and blockers,
   - proposed branch, base, Draft PR title/body, reviewers, and initial labels,
   - `PR READY` or `PR BLOCKED` verdict.
   Stop without GitHub side effects.

## PR readiness (fill handoff.forge — do not open the PR here)

After T5, present readiness and ask whether to publish. On `outcome: pass`,
next is `prd-pr-action` (`open_draft_pr`). Fill `handoff.forge` with pin
`requires` at minimum (`title`, `body_path`, `action: open_draft_pr`,
`draft: true`, `apply_labels: [impact-map-pending]`). Recommend
`/open-draft-pr`. Do not run forge mutations inside `/prd-impact-map`.

See `.harness/references/forge-side-effects.md`.

## Output and approval contract

Generated canonical file:

`{reports_dir}/Impact-Map-{INIT-id}.md`

Use [references/output-template.md](references/output-template.md).

Before `/open-draft-pr` (or orchestrator forge), `meta_pr` and approval fields
are `pending`. After the authorized forge skill / ForgeClient run, the PR body
contains the impact summary, artifact path, map revision, PRD digest, Gate 1
checklist, and PE review request. Clarification comments may discuss the map,
but decisions must be committed to the PRD/map artifact.

Effective state is derived:

| State | Condition | Engineering gate |
|-------|-----------|------------------|
| `draft` | Artifact is being generated or revised | closed |
| `pending_review` | Local artifact is PR-ready or Draft PR awaits matching approval | closed |
| `approved` | Latest tech-lead APPROVED review matches current head SHA and artifact/PRD digests | open for affected repo scopes only |
| `stale` | PRD or map content changed after approval | closed for changed scope |
| `blocked` | Tech lead explicitly revoked or paused | closed |
| `superseded` | A newer map revision exists | permanently closed for old revision |

Labels mirror the effective state. PE controls the Gate 1 label:

- `impact-map-pending` — Draft PR awaits PE decision
- `impact-map-lgtm` — matching approval exists
- `impact-map-blocked` — PE requests changes or explicitly holds the handoff

Agent/PM invalidation labels:

- `impact-map-revised` — new map revision awaiting review
- `impact-map-stale` — source PRD changed after approval

Exactly one of `impact-map-pending`, `impact-map-lgtm`, or
`impact-map-blocked` may be active. `impact-map-revised` or
`impact-map-stale` always closes the gate even if `impact-map-lgtm` was not
removed. Any contradiction fails closed.

PE transitions:

| PE action | Remove | Add | Gate |
|-----------|--------|-----|------|
| Review starts / new revision | `impact-map-lgtm`, `impact-map-blocked` | `impact-map-pending` | closed |
| Request changes / hold | `impact-map-pending`, `impact-map-lgtm` | `impact-map-blocked` | closed |
| Approve exact current head | `impact-map-pending`, `impact-map-blocked`, `impact-map-revised`, `impact-map-stale` | `impact-map-lgtm` | open |

Never infer approval from labels alone; a matching GitHub APPROVED review and
current artifact/head values are also required.

## Material change and ripple policy

Any scope, capability, contract, dependency-order, affected/deferred status,
or acceptance-meaning change is material. A typo-only edit may retain the map
only when the artifact records `material_change: false` with a reason; the
current head still requires a matching review under the conservative pilot
policy.

For each prior affected repo, emit one action:

| Change | Required action |
|--------|-----------------|
| removed / deferred | `hold` or `close`; never run feasibility/TDD/plan |
| added | `open` after latest approval |
| unchanged scope digest | `continue` after recording revision check |
| narrowed / widened | `re-draft` then `re-feasibility` |
| dependency order changed | `re-plan` for affected dependents |
| removed scope already merged | human decision: revert, corrective PR, or follow-up initiative |

## Approval attestation

The requested GitHub review body is:

```text
Impact map approved
initiative: {INIT-id}
map_revision: {N}
meta_pr_head_sha: {SHA}
prd_digest: {DIGEST}
artifact: {reports_dir}/Impact-Map-{INIT-id}.md
```

Approval is stale when the latest approved review's commit SHA differs from
the current meta PR head SHA or any attested value differs from the artifact.

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the impact-map artifact. Use stage `prd-impact-map`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates`, `human_checkpoint`, and `external_action` from pinned root `workflow.yaml` for `(stage: prd-impact-map, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint`. Set `external_action: true` when next is `external-action` (e.g. `prd-pr-action` on `pass`).
4. On `pass`, fill complete `handoff.forge` for `open_draft_pr` per pin `requires`. Recommend `/open-draft-pr`. Follow `.harness/references/forge-side-effects.md#content-producers`.


**Transitions:** pinned root `workflow.yaml` for this stage (SSOT). Human or
agent may run this skill; legality and auto-dispatch follow `dispatch` +
delivery contract + latest handoff. On `pass` with `signals.pr_ready: true`,
the next node is typically `prd-pr-action` (external-action — explicit auth).

The handoff never authorizes forge mutation. `next_candidates` never authorize
invoke.
