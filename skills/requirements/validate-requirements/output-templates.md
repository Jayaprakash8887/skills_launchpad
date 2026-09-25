# Phase 3: Output Templates

**Called from:** `SKILL.md` (Phase 3: Generate Output)
**Produces:** Chat summary (displayed to user) + Full report file (saved to disk)

Conventions: `.harness/references/id-conventions.md`,
`.harness/references/artifact-write-contract.md`.

---

## Output 1: Chat Summary (displayed to user)

```
## Requirements Review — [INIT id]

**Document:** [filename]
**Report:** [canonical path] (report_revision [N])
**Sources checked:** [N]
**Findings:** [N] total ([N] Critical, [N] Should Fix, [N] Verify, [N] Gaps)
[If incremental mode, include the following block — omit entirely in full mode:]
**Mode:** Incremental (prior report: [same canonical path], revision [N-1], [date])
**Changes detected:** [N] sections modified, [N] REQ/CAP changed, [N] sources unchanged
**Checks re-run:** [list of check numbers]
**Checks carried forward:** [list of check numbers] (no relevant changes detected)
**Prior findings resolved:** [N] (fixed since last report)
**Prior findings carried forward:** [N] (same VF-* ids)
**New findings:** [N]

### Semantic Checks (content accuracy)

| Check | Findings | Status | Mode |
|-------|----------|--------|------|
| 1. Source Accuracy | [N] | PASS / FAIL | Re-run / Carried forward |
| 2. Inference Detection | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 3. Requirement Purity | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 4. Over-Generalization | [N] | PASS / FAIL | Re-run / Carried forward |
| 5. Scope Boundary | [N] | PASS / FAIL / SKIPPED | Re-run / Carried forward |
| 6. Testability | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 7. Ambiguity | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 8. Assumption-Req Dependency | [N] | PASS / FAIL | Re-run / Carried forward |
| 9. Negative Path Coverage | [N] | PASS / FAIL | Re-run / Carried forward |
| 10. Actor Capability | [N] | PASS / FAIL | Re-run / Carried forward |
| 11. Intra-Document Consistency | [N] | PASS / FAIL | Always re-run |

### Structural Checks (document integrity)

| Check | Findings | Status | Mode |
|-------|----------|--------|------|
| S1. Staleness | [N] | PASS / FAIL | Always re-run |
| S2. Contradictions | [N] | PASS / FAIL | Always re-run |
| S3. Cross-References | [N] | PASS / FAIL | Always re-run |
| S4. Completeness | [N] | PASS / FAIL | Always re-run |

[In full mode, omit the Mode column from both tables.]

### Top Issues
1. [VF-id] [Most critical finding — brief description]
2. [VF-id] [Second]
3. [VF-id] [Third]

**Full report saved to:** [canonical filepath] (overwritten; report_revision [N])

### Recommended Next Steps

1. **Review findings interactively** — use `review-findings` with this report to walk through each `VF-*`, collect decisions, and produce `Resolution-{INIT}.md`.
2. **Or resolve manually** — work through findings by category:
   a. Resolve Verify items first (quick yes/no confirmations)
   b. Batch-approve Should Fix items
   c. Fill Gaps (add to doc or convert to `OQ-*`)
   d. Fix Critical items immediately
3. **Apply fixes** — use `update-documents` with the resolution summary to apply all approved `CHG-*` in one pass.

Would you like to use `review-findings` to walk through these interactively?
```

---

## Output 2: Full Report File

**Canonical path (REQUIRED):**

`{reports_dir}/Validation-Report-{INIT}.md`

Default `{reports_dir}` = `prd/reports` (or harness `reports_dir`). Create the
folder if missing. **Overwrite** this path. Never write
`Validation-Report-*-revN.md` or other siblings.

**Legacy / pipeline exceptions only:**

1. **Parent skill provided a path** (e.g. `stage_output/Stage9-Validation-Report.md`) — still prefer migrating to the canonical INIT path when an initiative id is known.
2. Otherwise use the canonical path above.

```markdown
# Requirements Review

**Document:** [filename]
**Initiative:** [INIT-id]
**Validated on:** [date]
**report_revision:** [N]
**previous_revision:** [N-1 or none]
**Sources checked:** [N] source documents
**Checks run:** 15 (11 semantic + 4 structural)
[If incremental mode, include the following block — omit entirely in full mode:]
**Mode:** Incremental (prior report: [canonical path], revision [N-1], [date])
**Changes detected:** [N] sections modified, [N] REQ/CAP changed, [N] sources unchanged
**Checks re-run:** [list — these checks ran fresh because their inputs changed]
**Checks carried forward:** [list — these checks were skipped because inputs are unchanged since [prior date]]
**Prior findings resolved:** [N] (fixed since last report)
**Prior findings carried forward:** [N]
**New findings:** [N]

### Semantic Checks (content accuracy)

| Check | Findings | Status | Mode |
|-------|----------|--------|------|
| 1. Source Accuracy | [N] | PASS / FAIL | Re-run / Carried forward |
| 2. Inference Detection | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 3. Requirement Purity | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 4. Over-Generalization | [N] | PASS / FAIL | Re-run / Carried forward |
| 5. Scope Boundary | [N] | PASS / FAIL / SKIPPED | Re-run / Carried forward |
| 6. Testability | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 7. Ambiguity | [N] | PASS / FAIL | Re-run / Scoped / Carried forward |
| 8. Assumption-Req Dependency | [N] | PASS / FAIL | Re-run / Carried forward |
| 9. Negative Path Coverage | [N] | PASS / FAIL | Re-run / Carried forward |
| 10. Actor Capability | [N] | PASS / FAIL | Re-run / Carried forward |
| 11. Intra-Document Consistency | [N] | PASS / FAIL | Always re-run |

### Structural Checks (document integrity)

| Check | Findings | Status | Mode |
|-------|----------|--------|------|
| S1. Staleness | [N] | PASS / FAIL | Always re-run |
| S2. Contradictions | [N] | PASS / FAIL | Always re-run |
| S3. Cross-References | [N] | PASS / FAIL | Always re-run |
| S4. Completeness | [N] | PASS / FAIL | Always re-run |

[In full mode, omit the Mode column from both tables.]

---

[If incremental mode, include a Resolved section before the findings:]

## Resolved (fixed since prior report)

[List prior findings whose problematic text no longer exists. Keep the same VF-* id.]

| VF | Prior Location | Prior Check | Prior Finding | Resolution |
|----|----------------|-------------|---------------|------------|
| VF-01 | [Section / REQ-*] | [Check #] | [Original finding description] | Text removed or rewritten |

---

## Critical (MUST FIX — factually wrong or misleading)

| VF | Type | Location | Target | Check | Finding | Source Says | Doc Claims | Example | Recommendation |
|----|------|----------|--------|-------|---------|-------------|------------|---------|----------------|
| VF-01 | Semantic | [section] | REQ-07 / CAP-02 / — | [Check #] | [Description] | [source] | [doc] | [concrete example] | [Fix] |
| VF-02 | Structural | [section] | REQ-03 / — | [Check S#] | [Description] | — | — | [example] | [Fix] |

## Should Fix (reframe, relocate, or make precise)

| VF | Type | Location | Target | Check | Finding | Recommendation |
|----|------|----------|--------|-------|---------|----------------|
| VF-03 | Semantic | [section] | REQ-* / — | [Check #] | [Description] | [Fix] |

## Verify (needs user confirmation)

| VF | Type | Location | Target | Check | Finding | Question for User |
|----|------|----------|--------|-------|---------|-------------------|
| VF-04 | Semantic | [section] | REQ-* / — | [Check #] | [Description] | [What to confirm] |

## Gaps (missing coverage)

| VF | Type | Location | Target | Check | Finding | Suggested Addition |
|----|------|----------|--------|-------|---------|-------------------|
| VF-05 | Semantic | [section] | CAP-* / — | [Check #] | [Description] | [What to add — may suggest CAP/REQ assignment] |

[For carried-forward findings, append `(carried from [prior report date])` to the Finding cell and keep the same VF id.]

## Clean (no issues found)

[List checks that passed with 0 findings and a brief note on what was verified]

---

## Recommended Next Steps

1. **Review findings interactively** — Use `review-findings` with this report to walk through each `VF-*`, collect decisions, and produce `Resolution-{INIT}.md`.
2. **Or resolve manually** — Work through findings by category: Verify items first, then Should Fix, then Gaps, then Critical.
3. **Apply fixes** — Use `update-documents` with the resolution summary (from `review-findings`) or apply changes directly.
4. **Re-run validation** — After fixes, re-run `validate-requirements` in incremental mode against this **same canonical path**.
```
