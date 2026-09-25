# {INIT-id} — spec slice for {REPO}

| Field | Value |
|-------|-------|
| Initiative | {INIT-id} |
| PRD | `{client-meta}/prd/{INIT-id}.md` |
| PRD digest (H1) | `sha256:{hex}` |
| Meta PR | {URL} |
| Meta PR approved head (G1) | `{SHA}` |
| Impact map | `{client-meta}/prd/reports/Impact-Map-{INIT-id}.md` |
| Impact-map revision (H3) | `{N}` |
| Repo scope digest (H2) | `sha256:{hex}` |
| Tech-lead approval | {review URL/id, approver, submitted_at; review commit_id must equal approved head} |
| Repo | {REPO} |
| Date | {YYYY-MM-DD} |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure — see
> `.harness/references/artifact-write-contract.md`.

## Overview

{2–3 sentences: what this repo delivers for this initiative.
Scope boundary: what is OUT of scope for this repo.
Ownership: observable behavior only — architecture questions routed, not decided.}

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| REQ-{nn} | {engineering statement of WHAT, not HOW — not a user story} | PRD `CAP-*` / `REQ-*` or §{section} | {Given/When or trigger that makes the REQ applicable} | {externally observable done condition} | unit / integration / live (cite `CAP-*` and/or `J-*`) / inspection |

> **Id convention:** `REQ-*` is canonical (`.harness/references/id-conventions.md`).
> Legacy display alias `FR-{nn}` ≡ `REQ-{nn}` (same number) — prefer `REQ-*` in
> new rows. Do not invent wave-scoped `REQ-W*` ids.
>
> **Behavioral acceptance vs evidence:** Condition/event + observable result are
> the product acceptance statement (implementation-neutral). Evidence layer
> names how it will be proved later — not the implementation design. Live
> evidence must cite capability and/or journey ids when the PRD defines them.

## Capabilities (carried from PRD)

| ID | Capability | Journeys | Notes |
|----|------------|----------|-------|
| CAP-{nn} | {from PRD; in-scope for this repo} | J-{nn}, … or defer | |

## Journeys (carried from PRD)

| ID | Actor | Trigger | Main flow | Primary edge | Abandon | Caps |
|----|-------|---------|-----------|--------------|---------|------|
| J-{nn} | | | | | | CAP-{nn} |

> **Do not drop** in-scope PRD `CAP-*` / `J-{nn}`. If a journey is out of repo
> scope, list it under Out of scope with the owning repo — do not omit silently.
> Capability and journey are **separate prove rungs**
> (`.harness/references/quality-confidence-ladder.md`).

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|-----------------|----------|
| REQ-{nn} | {invalid/empty/unavailable/timeout/unauthorized/partial} | {observable outcome, retry/idempotency rule} | {production failure/regression this prevents} | {test/verify/inspection} |

## Out of scope for this repo

- {capability that belongs to another repo — name which one}

## Cross-service contracts

Use “None — no cross-repository boundary” when not applicable.

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-{n} | {repo / team} | {repo / team} | {logical operation; concrete endpoint/event/method only when already approved} | {field meaning / accepts} | {field meaning / returns/emits} | {guarantees} | {failure semantics} | {policy} | {path or planned path} |

> Entry point is a **semantic** boundary: name the logical operation and field
> meaning. Transport, framework, and module realization belong to technical
> review — not this table.

## Non-functional requirements

Every row is required. Use N/A only with a concrete reason.

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | | |
| Reliability | | |
| Performance / capacity | | |
| Observability | | |
| Privacy / data handling | | |
| Migration / compatibility | | |
| Rollback / recovery | | |
| Operations / support | | |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-{n} | {statement} | {source or “unverified”} | {owner} | confirmed / open | {condition} |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-{n} | PM / PE / domain | {plain-English question + PRD ref} | {owner} | yes/no | feasibility / technical review / plan | {safe default or none} | open/resolved | {URL/path or pending} |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS/FAIL/NEEDS INPUT | |
| D2 Complete PRD traceability | | |
| D3 Repo-bounded scope | | |
| D4 Observable acceptance | | |
| D5 Negative/failure paths | | |
| D6 Assumptions/questions | | |
| D7 Cross-repository contracts | | |
| D8 NFR applicability | | |
| D9 As-built alignment | | |
| D10 Dependency order | | |
| D11 Zero unresolved blockers | | |
| D12 Output completeness | | |

**Draft verdict:** PASS / FAIL / NEEDS INPUT

**Selected workflow outcome:** `pass` / `needs-input` / `blocked` / `stale` / `failed`
**Outcome reason:** {one sentence mapping check verdict + gate state → outcome}

Do not advance to `/initiative-feasibility` unless the workflow outcome is
`pass`, the draft verdict is PASS, and the developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `{outcome}` — {reason} |
| Verdict | PR READY / PR BLOCKED |
| Existing spec PR | none / {URL} |
| Proposed branch | `chore/INIT-{COMPONENT}-{NUMBER}-spec-{repo}` |
| Proposed base | `develop` |
| Proposed title | `[INIT-{COMPONENT}-{NUMBER}] Spec — {repo}` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-{id}.md`, `docs/specification/README.md` if new |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then `/open-draft-pr` — do not commit/push/open PR inside this skill |
| Reviewer | @{pe-team} |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none / `spec-revised` / `spec-stale` |
| Blocking items | none / {IDs and reasons} |

**No GitHub side effects have occurred.** Persist the draft locally, present
this section in chat, and ask whether to authorize Forge publish
(`/commit-workspace` / `/open-draft-pr` or Gateflow ForgeClient). Continue only
after explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

{INIT-id} — {short title}

## Meta handoff

- Meta PRD PR: {URL}
- Approved meta head: `{SHA}`
- Impact-map revision: {N}
- PRD digest: `sha256:{hex}`
- Repo scope digest: `sha256:{hex}`

## Spec path

`docs/specification/product/INIT-{id}.md`

## Summary

- {bullet summary of FR count and scope}
- Open engineering questions: {Q-ids or none}

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `/open-draft-pr`)
- [ ] Feasibility report (later Forge publish)
- [ ] Technical design + ADRs (later Forge publish)
- [ ] Implementation plan §9 (later Forge publish)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @{pe-team}
```

## Developer review

- [ ] Scope matches the approved impact-map repo scope digest
- [ ] REQs have condition/event, observable result, and evidence layer
- [ ] Contracts are semantic (logical operation); no architecture decisions in REQs
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## After Draft PR creation

PE controls Gate 2 labels on the spec PR. Never infer approval from labels
alone — `spec-lgtm` requires matching artifacts on the exact PR head.

Provision labels before PR creation when missing:

```bash
launchpad apply-gates --repo <name> --apply
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

## References

- PRD: `{client-meta}/prd/{INIT-id}.md`
- Meta PRD PR: #{PR number or URL}
- Spec PR: #{PR number or URL}
- Service profile: `docs/specification/product/00-service-profile.md`
