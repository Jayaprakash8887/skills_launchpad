# Technical Design Document — {INITIATIVE}

| Field | Value |
|-------|-------|
| Initiative | {INITIATIVE} |
| Spec | {SPEC_PATH} |
| Spec digest | `sha256:{hex}` |
| Feasibility report | {FEASIBILITY_PATH} |
| PRD digest | `sha256:{hex}` |
| Impact map / revision | `{path}` / `{N}` |
| Repo scope digest | `sha256:{hex}` |
| Approved meta PR head | `{SHA}` |
| Source freshness | CURRENT / STALE — reason |
| Repo | {REPO} |
| Date | {YYYY-MM-DD} |
| Branch | `chore/INIT-{COMPONENT}-{NUMBER}-spec-{repo}` (spec PR — TDD published via Forge) |
| Initiative segment | `INIT-{COMPONENT}-{NUMBER}` — COMPONENT is service branch_code from the resolved service catalog |
| Status | Draft |
| Review deadline | {YYYY-MM-DD + 5 business days} |
| Deciders | PE: {name} — explicit LGTM required, not approval by silence |

---

## 1. Problem statement

{1–3 sentences stating the **engineering** problem in engineering vocabulary
(data flow, module boundary, protocol, storage, concurrency) — reference
`REQ-*` ids for traceability, but do not lift or paraphrase the spec's
behavioral sentences. If you cannot state the problem without reusing the
spec's own phrasing, you have not yet identified the technical problem —
keep analyzing before writing this section.}

---

## 2. Module / package boundaries

{List each module/package affected. For each: current state, proposed change,
ownership.}

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `{module}` | exists / stub / new | create / extend / unchanged | {layer} |

**Boundary diagram (text):**

```
{caller} → [{module A}] → [{module B}] → [{storage}]
             ↑ contract       ↑ contract
```

---

## 3. Public interface contracts

For each boundary crossing in section 2, specify the contract in
engineering terms (stack-agnostic — describe shapes and invariants, not syntax).

### 3.{n} `{ModuleA}` → `{ModuleB}`

**Method / entry point:** `{name}`
**Arguments:**
- `{arg}`: {shape description} — {invariant}

**Return:**
- `{field}`: {shape description}
- Error: {what is raised / returned on failure}

**Invariants:**
- {e.g. "output must validate against SchemaType schema"}
- {e.g. "no fabricated values — absent row preserved as null"}

---

## 4. ADR resolutions

Every feasibility `NEW-ADR` appears once. `ADR_REQUIRED` rows link actual files
rendered from [adr-template.md](adr-template.md). **Do not embed ADR body content
in the TDD** — the canonical Draft lives in `{adr_dir}`; this section is an index
only.

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| FF-{nn} | ADR_REQUIRED | `{adr_dir}/adr-{NNN}-{slug}.md` | `[REQ-…]` | {short list / none} | {choice} | Draft | `sha256:{hex}` |
| FF-{nn} | TDD_ONLY | §9 row {id} | `[REQ-…]` | {short list / none} | {choice + rationale} | Resolved | N/A |
| FF-{nn} | DEFERRED_WITH_DEFAULT | §9 row {id} | `[REQ-…]` | {short list / none} | {default + revisit trigger} | Deferred | N/A |

**Derived counts:**

- ADR_REQUIRED: {N}
- TDD_ONLY: {N}
- DEFERRED_WITH_DEFAULT: {N}
- Draft ADR files created: {N}
- Missing/broken ADR files: {N}

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| `{module}` | {what is tested without I/O} | {what needs real deps} | {CLI/API smoke} | {exact / fuzzy / snapshot} |

**AI-output determinism policy (when applicable):**
- {e.g. "row count and schema validity: exact; extracted text fields: fuzzy
  match with configurable threshold; test approves snapshot manually on first run"}

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| {e.g. malformed xlsx} | extraction | raised to CLI boundary | terminal — exit non-zero, structured error message |
| {e.g. LLM timeout} | extraction | retry N times then raise | recoverable — configurable retry |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| `{module}` | INFO/WARNING/ERROR | {e.g. `file_path`, `schema_type`, `row_count`} | |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| `{SchemaType}` | {module} | {edge / repository / both} | {immutable / semver / amend-by-PE} |

---

## 9. Resolved engineering decisions

All items from feasibility routed to PE lane. Every row must show a resolution.

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| {C1/G1/…} | {PE} | resolved/deferred | {engineering question} | {option chosen / defer reason} | plan | {safe default} | {finding/ADR/comment} |

---

## 10. Routed out — product questions (PM)

These items remain open and require PM input before the implementation plan
is considered unblocked.

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| PM-{n} | {PM} | open/resolved/deferred | {product question — user-visible behaviour or scope} | yes/no | {plan wave/stage} | {safe default or none} | {spec/PRD ref} | {meta PR URL or pending} |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| D-{n} | {SME/team} | open/resolved/deferred | {business source-of-truth question} | yes/no | {plan wave/stage} | {safe default or none} | {source ref} | {URL/path or pending} |

---

## 12. Fix disposition

Use `auto-fixed` only when the target artifact was actually edited. Otherwise
use `planned-auto-fix` or `suggested-fix`.

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-{n} | auto-fixed / planned-auto-fix / suggested-fix | {item} | {path + before/after or future task} | {digest or N/A} |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | {PASS / FAIL — list blocking items} |
| Engineering decisions resolved | {N resolved, N deferred with defaults} |
| Draft ADR files written | {N files / N required} |
| Product-boundary integrity (T12) | {PASS / FAIL} |
| PM questions outstanding | {derived row count — list} |
| Domain questions outstanding | {derived row count — list} |
| Selected workflow outcome | `{outcome}` — {reason} |
| Ready for PE review | YES / NO |
| **Ready for /spec-implementation-plan** | **NO — final exact-head PE approval required** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS/FAIL/SKIPPED | |
| T2 Interface contracts | | |
| T3 NEW-ADR dispositions | | |
| T4 Test policy | | |
| T5 Error handling | | |
| T6 Observability | | |
| T7 Data contract ownership | | |
| T8 Dependency graph | | |
| T9 Engineering questions zero | | |
| T10 PE review readiness | | |
| T11 ADR artifact integrity | | |
| T12 Product-boundary integrity | | |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch. Do **not** commit, push, open
> PRs, or apply labels inside this skill. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by publishing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet. CODEOWNERS may request PE review on `Technical-Review-*`.

```
Branch:   chore/INIT-{COMPONENT}-{NUMBER}-spec-{repo}
PR title: "[INIT-{COMPONENT}-{NUMBER}] Spec — {repo}"
PR body:  link meta PRD PR; paste §13 Implementation readiness verdict when TDD is ready

Required reviewers (enforced by CODEOWNERS when TDD file is present):
  @{pe-name-or-pe-team}  ← must give explicit Approve, not just silence

Review deadline: {date from report header}
PE review checklist (PE works through this on the spec PR):
  [ ] T1 Module boundaries — can I draw the box?
  [ ] T2 Interface contracts — are shapes and invariants specified?
  [ ] T3 ADR dispositions — required Draft files exist; TDD-only/deferred rationales are valid
  [ ] T4 Test policy — is determinism policy acceptable?
  [ ] T9 Zero unresolved PE items?
  [ ] T11 ADR artifact integrity — every required file/link/digest is valid
  [ ] T12 Product-boundary integrity — every user-visible statement cites approved REQ-*
  [ ] T12 mechanical: `scripts/adr_boundary_lint.py` run on every ADR (with
      --require-sources and --approved-req-id) AND on the TDD (--tdd) —
      confirm `Lint evidence` on each Accepted ADR, don't just take PASS on faith
  [ ] T12 manual (lint cannot see these — see checks.md "three gaps"):
      loose paraphrase in unfamiliar vocabulary; invented behavior under a
      real REQ with flags left false; multiple decisions narrated in one
      un-duplicated Recommendation section

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → developer updates TDD/ADR files
  Explicitly state when decisions are ready for acceptance
  Developer/PE updates ADR metadata Draft → Accepted and TDD Status → Accepted
    (only when changes_user_visible_behavior and spec_amendment_required are false,
    Approval evidence / Approved head are populated, and Lint evidence is recorded —
    not a placeholder)
  Publish acceptance package via Forge to spec branch (label remains spec-pending)

After artifact acceptance:
  → /spec-implementation-plan may run on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
  → Ready for review → merge → `/create-board-tickets` from merged plan §9
```
