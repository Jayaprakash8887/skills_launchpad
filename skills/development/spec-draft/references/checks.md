# Spec draft checks (D1–D12)

Run every check. SKIPPED requires a missing input and an explicit reason; a
check that is not applicable should PASS with the applicability rationale.
D1, D1b, D2, D3, D4, D7, and D11 are blocking.

Check-level PASS/FAIL/NEEDS INPUT feed the stage **outcome rubric** in
`SKILL.md` — not every FAIL is workflow `failed`.

| ID | Check | Evidence required |
|----|-------|-------------------|
| D1 | **Approved handoff is current** | Canonical impact-map path/revision (**H3**), PRD digest (**H1**), current meta PR head SHA + matching tech-lead APPROVED review (**G1**); repo is affected with **H2** `scope_digest` and not deferred/blocked |
| D1b | **No open blocking IM-*** | Impact-map § Open questions: every `IM-{nn}` with `Blocking: yes` is **resolved** or deferred with an explicit default. Any **open** blocking `IM-*` → **FAIL** (Gate 1 / coding-readiness closed). Non-blocking open IM may remain as questions |
| D2 | **Complete PRD traceability** | Every in-scope PRD `CAP-*` / capability maps to at least one `REQ-*`; every `REQ-*` cites a named PRD section/bullet or `CAP-*`/`REQ-*` |
| D2b | **Journeys carried** | Every in-scope PRD `J-{nn}` appears in the spec Journeys table (or explicit out-of-repo N/A). Live evidence REQs cite `CAP-*` and/or `J-*` when PRD defines those namespaces |
| D3 | **Repo-bounded scope** | In-scope, out-of-scope, deferred, and other-repo responsibilities agree with the approved repo scope digest |
| D4 | **Observable acceptance** | Every applicable REQ states: (1) condition/event (Given/When or equivalent), (2) observable result the system shall produce, (3) proving evidence type. Acceptance remains **implementation-neutral** — no module, framework, transport, or ADR choice. Simple invariants may omit EARS syntax when clearer, but must still name condition, result, and evidence |
| D5 | **Negative and failure paths** | Error, empty, unavailable, timeout, authorization, retry/idempotency, and partial-success behavior are specified or N/A with reason. Each specified path states **why it matters** (the production failure/regression it prevents) — not just the mechanical behavior |
| D6 | **Assumptions and questions** | Every assumption has evidence/status; every question has lane, owner, blocking, required-by stage, default-if-deferred, and resolution link/status |
| D7 | **Cross-repository contracts (semantic)** | Every boundary has contract ID, provider/consumer owner, **logical operation** (concrete endpoint/method only when already approved), field meaning, invariants, errors, and compatibility/versioning; contract-test location when known. Transport, framework, and module realization belong to technical review. PASS with “no cross-repo boundary” when none |
| D8 | **NFR applicability** | Security, reliability, performance, observability, privacy, migration, rollback, and operations are specified or N/A with reason |
| D9 | **As-built alignment** | Proposed changes distinguish existing, changed, and new behavior using as-built/source evidence |
| D10 | **Dependency order** | Consumed contracts and dependency/build order agree with the approved impact map; discrepancies are blocking questions |
| D11 | **Zero unresolved blockers** | No open blocking PM, PE, or domain question remains; safe defaults are explicit only for non-blocking deferrals |
| D12 | **Output completeness** | Required header references, tables, check summary, selected workflow outcome, PR readiness handoff, and explicit dev-review status are present with no placeholders presented as facts |

## Check verdict → stage outcome

| Check verdict | Typical stage outcome | Notes |
|---------------|----------------------|-------|
| All D1–D12 PASS; zero material blockers; PR READY | `pass` | Fill `handoff.forge` for `open_draft_pr` |
| Required handoff/source missing or unreadable | `needs-input` | Do not draft as authoritative; do not advance |
| Material ambiguity remains after clarification loop | `needs-input` | Answers must be written into owning REQ rows |
| Explicit gate closed (approval/label/artifact disagree; repo held) | `blocked` | |
| Digest / head / revision mismatch (H1–H3 / G1) | `stale` | |
| Blocking D-check FAIL on present, readable inputs (traceability, scope, acceptance shape, contracts, blockers) | `needs-input` or `blocked` | Choose by whether human input vs gate closure is required — **not** `failed` |
| Execution/render error on otherwise valid inputs | `failed` | |

## Verdict (check summary)

- **PASS:** D1–D12 pass and no blocking question remains.
- **FAIL:** any blocking check fails or any blocking question remains.
- **NEEDS INPUT:** a required handoff/source input is missing; do not draft or
  advance to feasibility.

Map the check verdict through the table above before setting `handoff.outcome`.
