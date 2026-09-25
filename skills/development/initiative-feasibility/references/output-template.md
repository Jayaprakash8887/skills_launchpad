# Feasibility report — {INITIATIVE}

| Field | Value |
|-------|-------|
| Initiative | {INITIATIVE} |
| Spec | {SPEC_PATH} |
| PRD digest | `sha256:{hex}` |
| Impact map / revision | `{path}` / `{N}` |
| Repo scope digest | `sha256:{hex}` |
| Approved meta PR head | `{SHA}` |
| Impact-map approval | {review URL/id, approver, submitted_at} |
| Source freshness | CURRENT / STALE — reason |
| Repo | {REPO} |
| Date | {YYYY-MM-DD} |
| Branch | `chore/INIT-{COMPONENT}-{NUMBER}-spec-{repo}` — spec PR (single review surface) |
| Initiative segment | `INIT-{COMPONENT}-{NUMBER}` — COMPONENT is service branch_code from the resolved service catalog |
| Status | Draft |
| Review deadline | {YYYY-MM-DD + 3 business days} |
| Deciders | PM: {name} · Domain SME: {name or team} |

## Summary

{2–4 sentences: buildable? main gaps? merge recommendation}

**Findings:** {N} total ({critical} Critical, {should} Should fix, {verify} Verify, {gap} Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | {n} | {n} | {n} |
| PE / ADR | {n} | {n} | {n} |
| Domain | {n} | {n} | {n} |
| Auto-fix | {n} | {n} | {n} |

| Severity | Unresolved count |
|----------|------------------|
| Critical | {n} |
| Should fix | {n} |
| Verify / Gap (informational) | {n} |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `pass` / `findings` / `needs-input` / `blocked` / `stale` / `failed` |
| Rationale | {one sentence: first matching lane-to-outcome rule} |
| Next (from workflow) | {node id} |

Informational observations alone do **not** select `findings`. Unresolved
blocking PE/ADR → `findings`; blocking PM/domain → `needs-input`.

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | | |
| Live verify | | |
| As-built | | |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-{nn} / W{n} | | | | | exists / gap / partial / drift |

## ADR traceability (F13)

> **Finding must start with the literal prefix `ALTERNATIVE:`** followed by
> the unresolved *technical alternative* (see `governance.md` F13/P12) —
> e.g. `ALTERNATIVE: sync vs. async processing for this ingestion path`.
> Never a restatement of the REQ. This prefix is a machine-checkable marker,
> not decoration — run `validate_finding_marker` before handing this row
> off. **A `Finding` cell lacking the marker must be corrected here, in this
> report, before handoff.** `/spec-technical-review` must treat a malformed
> `Finding` as blocking upstream input and route it back to a re-run of this
> skill (outcome `blocked`) — it must **not** infer, guess, or re-derive the
> alternative from the REQ itself; doing so reconstructs architecture from
> product prose downstream of the very check meant to stop that.
> The **Spec quote** captured in "Governance findings" below is evidence the
> ambiguity exists — it is not the finding, and must be carried forward only
> as a `--source-text` input to `scripts/adr_boundary_lint.py` (proving the
> ADR does *not* contain it), never copied into ADR Context.
> **Code evidence** is the specific module/file path(s) from this row's F1/F2
> baseline inspection that the alternative actually concerns — not prose, a
> path. `/spec-technical-review` re-verifies and extends this before
> drafting; it must never be blank when F1/F2 found something relevant.

| Spec REQ / wave | Relevant ADR(s) | Status | Code evidence | Finding |
|-----------------|-----------------|--------|----------------|---------|
| REQ-{nn} / W{n} | ADR-… / NEW-ADR / N/A | aligned / conflict / missing ADR | `src/…` (module found during F1/F2, or "none found — new capability") | `ALTERNATIVE: {technical alternative, not a REQ restatement}` |

## Governance findings (F13–F14)

> **Spec quote** is a bounded, literal excerpt (quote marks required) used
> only as lint evidence — never prose that a downstream reader could mistake
> for pre-written ADR Context. Keep it short (one sentence) and verbatim so
> `/spec-technical-review` can pass it unmodified to `adr_boundary_lint.py
> --source-text` as the exact string to check the ADR against.

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-{nn} | F13 / F14 | "{verbatim one-sentence excerpt}" | ADR-… / rule file | `ALTERNATIVE: {…}` (F13) / {governance finding} (F14) |

## Findings by severity

### Critical
| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-{nn} | F{n} | | |

### Should fix
| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-{nn} | F{n} | | |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| | | |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|

## Recommended spec edits

- (bullet list for PR branch — no silent fixes)

---

## Open items by lane

> Routing rubric: product scope / UX → PM · engineering decisions / ADR → PE ·
> business source-of-truth → Domain SME · naming drift / inferred fixes → Auto-fix.
> Full rubric: `skills/development/spec-technical-review/references/governance.md`
> (in this pin; not a workspace-relative `.agents/skills/…` path).

This table is the canonical open-item handoff. The lane-specific sections
below may add narrative but must not contradict it.

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| {ID} | PM / PE / domain / auto-fix | {item} | yes/no | {owner} | open/resolved/deferred | spec merge / technical review / plan / wave | {safe default or none} | {spec/repo evidence} | {URL/path or pending} |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge
1. …

#### Defer — can proceed with documented assumption
1. …

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

> These are **not** for PM. Run `/spec-technical-review` to produce a Technical
> Design Document that resolves these before `/spec-implementation-plan`.

#### Blocking for implementation plan
1. …

#### Defer with default
1. …

### Domain clarifications (business source-of-truth)

> Route to the named SME or BU team, not to PM and not to engineering.

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| D-1 | … | | |

### Auto-fixable (agent resolves later — not inside this skill)

> Record these as findings/signals. Do **not** edit product source or commit
> fixes during feasibility. Later stages or an authorized forge publish may
> apply them.

| # | Item | Fix |
|---|------|-----|
| AF-1 | … | align to existing enum / schema doc |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1–F14 | PASS/FAIL/SKIPPED | |

**Check PASS** = zero unresolved blocking findings (informational OK).

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → post as numbered comments on the **meta PRD PR** (plain English).
  Link from a spec PR comment if helpful. PM answers on meta PRD PR.
  Unresolved blocking PM items → outcome `needs-input`.

**PE questions** → discuss on the **Draft spec PR**; run `/spec-technical-review` next.
  PE accepts TDD/ADRs in **files** (`Draft` → `Accepted`); do **not** set
  `spec-lgtm` until the full package includes the implementation plan.
  Unresolved blocking PE/ADR items → outcome `findings`.

**Domain clarifications** → meta PRD PR comment or tracked issue; record answers in
  `open-questions.md` and publish via Forge to the spec branch.
  Unresolved blocking domain items → outcome `needs-input`.

**Auto-fixable items** → leave in report; resolve in a later authorized edit —
  not during this read-only feasibility run.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `{reports_dir}/{feasibility_prefix}-{initiative}.md` |
| Target branch | `chore/INIT-{COMPONENT}-{NUMBER}-spec-{repo}` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-{COMPONENT}-{NUMBER}-spec-{repo}  (spec-pending)
When ready:
  [ ] Source freshness is CURRENT
  [ ] All blocking PM questions answered on meta PRD PR
  [ ] All blocking Domain clarifications answered and published via Forge
  [ ] Spec updated to reflect answers (same branch, via Forge)
  [ ] Incremental re-run of /initiative-feasibility on updated spec is clean
  [ ] Proceed: /spec-technical-review (always — pin routes pass and findings here)
  [ ] After spec + feasibility + TDD (if any) + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: `/create-board-tickets` from plan §9 — then /pre-implement → /loop-spec
```
