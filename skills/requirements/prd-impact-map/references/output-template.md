---
schema_version: 1
initiative: {INIT-id}
map_revision: {N}
source_prd: prd/{INIT-id}.md
source_prd_digest: sha256:{hex}
previous_revision: {N-1 or null}
previous_artifact_commit: {git SHA or null}
change_reason: {initial map or concise revision reason}
material_change: {true or false}
generated_at: {YYYY-MM-DDTHH:MM:SSZ}
---

# Impact map — {INIT-id} — revision {N}

> This file is generated locally before PR creation and becomes the scope source
> of truth when committed. Effective approval is derived from a tech-lead
> GitHub APPROVED review on the exact current meta PR head SHA; dynamic PR state
> is not stored in this artifact's frontmatter.

## T0 collision report (blocking alternative)

When detection is `same-initiative` or `ambiguous`, do **not** create this
impact-map artifact or render sections 1–12. Return only:

```yaml
identity_collision:
  detection: same-initiative | ambiguous
  evidence:
    - {PR/branch/file evidence}
  recommended_resolution: reconcile-existing | supersede-existing | unrelated-confirmed
  human_decision: pending
  external_action_authorized: false

handoff:
  contract: sdd-delivery/v2
  stage: prd-impact-map
  outcome: needs-input
  artifact:
    path: null
    digest: null
  blockers:
    - IDENTITY-COLLISION
  signals:
    collision_detection: {detection}
    recommended_resolution: {recommendation}
    human_decision: pending
  next_candidates:
    - requirements-human-decision  # must ⊆ workflow.yaml for outcome
  human_checkpoint: true
  external_action: false
```

## 1. Source and revision

| Field | Value |
|-------|-------|
| PRD | `prd/{INIT-id}.md` |
| PRD digest | `sha256:{hex}` |
| Map revision | `{N}` |
| Previous revision | `{N-1 or none}` |
| Previous artifact commit | `{SHA or none}` |
| Change reason | {reason} |
| Material change | {yes/no — rationale} |

## 2. Affected repositories

| Service | Repo | Team | Scope summary | Scope digest | Spec to create | Confidence |
|---------|------|------|---------------|--------------|----------------|------------|
| {name} | {org}/{repo} | @{org}/{team} | {repo-bounded capabilities and contracts} | `sha256:{hex}` | `INIT-{id}-{slug}.md` | High/Medium/Low |

For every affected repository, calculate `scope_digest` (**H2**) from the
canonical UTF-8/LF payload in
`.harness/references/artifact-write-contract.md` (Durable identity), with
sorted list values and exactly one final newline. Record **H1**
`source_prd_digest` and **H3** `map_revision` in front matter — these survive
initiative-closure purge; Validation/Resolution reports do not.
## 3. Deferred repositories

| Service | Repo | Reason | Revisit condition |
|---------|------|--------|-------------------|
| {name} | {org}/{repo} | {why deferred} | {phase/decision/event} |

## 4. Transitively affected repositories

| Service | Repo | Depends on | Potential impact | Disposition |
|---------|------|------------|------------------|-------------|
| {name} | {org}/{repo} | {repo} | {impact} | affected / monitor / not affected |

## 5. Not affected

| Service | Repo | Reason |
|---------|------|--------|
| {name} | {org}/{repo} | {catalog-backed reason} |

## 6. Cross-repository contracts

| Contract ID | Provider repo | Consumer repo | Capability | Owner | Status |
|-------------|---------------|---------------|------------|-------|--------|
| CTR-{NN} | {repo} | {repo} | {PRD ref} | {team} | new / changed / unchanged |

## 7. Dependency and build order

```text
{repo-A} → {repo-B} → {repo-C}
```

| Repo | Depends on | Reason |
|------|------------|--------|
| {repo} | {repo or none} | {catalog or contract evidence} |

## 8. Revision diff

Omit this section only for revision 1.

| Repo | Prior status | Current status | Scope digest changed? | Change |
|------|--------------|----------------|-----------------------|--------|
| {repo} | affected/deferred/not affected | affected/deferred/not affected | yes/no | added / removed / narrowed / widened / reordered / unchanged |

## 9. Downstream ripple ledger

Every repository from the prior revision must have a row.

| Repo | In-flight artifact | Required action | Reason | Owner | Blocking |
|------|--------------------|-----------------|--------|-------|----------|
| {repo} | none / spec / feasibility / TDD / plan / implementation / merged | continue / open / hold / close / re-draft / re-feasibility / re-plan / human-decision | {revision evidence} | {team/person} | yes/no |

## 10. Open questions

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status |
|----|------|----------|-------|----------|-------------|---------------------|--------|
| IM-{nn} | PM / PE / domain | {question} | {owner} | yes/no | {stage} | {safe default or none} | open/resolved |

> **Gate 1:** any row with `Blocking: yes` and `Status: open` **closes**
> coding-readiness / Gate 1 until resolved or deferred with default
> (`.harness/references/id-conventions.md`). Spec-draft D1b fails closed.

## 11. PR readiness handoff

| Item | Value |
|------|-------|
| Verdict | PR READY / PR BLOCKED |
| Collision detection | no-collision / unrelated |
| Collision evidence | {PRs, branches, files searched} |
| Human resolution | none / reconcile-existing / supersede-existing / unrelated-confirmed |
| Resolution completed | yes — T0 was rerun after completion |
| Existing PR | none / {URL} |
| Proposed branch | `chore/{INIT-id}-prd` |
| Proposed base | `develop` |
| Proposed title | `[{INIT-id}] PRD — {short title}` |
| Files to commit | `prd/{INIT-id}.md`, this impact map, approved reports |
| Reviewer | @{tech-lead} |
| Initial Gate 1 label | `impact-map-pending` |
| Additional invalidation label | none / `impact-map-revised` / `impact-map-stale` |
| Blocking items | none / {IDs and reasons} |

**No GitHub side effects have occurred.** Ask the user whether to create or
update the Draft PR. Continue only after explicit authorization.

### Proposed Draft PR body

```markdown
## Product change
{2–4 sentence PRD summary}

## Impact-map summary
- Revision: {N}
- PRD digest: `sha256:{hex}`
- Affected repos: {list}
- Deferred repos: {list or none}
- Blocking questions: {list or none}
- Artifact: `prd/reports/Impact-Map-{INIT-id}.md`

## Gate 1 — engineering handoff readiness
- [ ] Product/domain blocking questions are resolved in committed artifacts
- [ ] Impact-map scope and dependency order are complete
- [ ] PRD digest and map revision match this PR head
- [ ] PE/tech lead has reviewed the exact current head

Requested reviewer: @{tech-lead}
Initial label: `impact-map-pending`
```

## 12. Approval request (after Draft PR creation)

Tech lead must review this artifact on the meta PR and submit GitHub
**Approve** on the exact PR head SHA using:

```text
Impact map approved
initiative: {INIT-id}
map_revision: {N}
meta_pr_head_sha: {SHA after this artifact is committed}
prd_digest: sha256:{hex}
artifact: prd/reports/Impact-Map-{INIT-id}.md
```

The gate remains closed until the review, current PR head SHA, PRD digest, map
revision, and artifact path all match.

All Gate 1 labels must be provisioned before PR creation/update:

```bash
launchpad apply-gates --meta --apply
```

Apply labels through the GitHub REST issues-label endpoint and request team
review through the REST `requested_reviewers` endpoint. Do not use `gh pr edit`
for these operations because its GraphQL path may fail on deprecated Projects
Classic fields.

PE updates labels as follows:

| Decision | Remove | Add |
|----------|--------|-----|
| Pending/new revision | `impact-map-lgtm`, `impact-map-blocked` | `impact-map-pending` |
| Request changes/hold | `impact-map-pending`, `impact-map-lgtm` | `impact-map-blocked` |
| Approve current head | `impact-map-pending`, `impact-map-blocked`, `impact-map-revised`, `impact-map-stale` | `impact-map-lgtm` |
