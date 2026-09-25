---
name: review-findings
description: "Interactively walks users through findings from any audit or validation report (validate-requirements, document-audit, or future skills). Reads the report file, detects its format, presents each finding as a decision brief (issue, example, recommendation+why, options with pros/cons) via AskQuestion, and produces a resolution summary with VF→CHG linkage. Use after any skill that generates a findings report, or standalone against any structured findings markdown file."
---

# Review Findings — Interactive Resolution Skill

## Purpose

Walks users through findings from audit/validation reports, collects decisions via structured questions, and produces a resolution summary. Works with any skill that generates a findings report — the report file is the interface.

**Key principle:** This skill does not re-run checks or read source documents. It reads ONE report file and presents its findings interactively. The heavy analysis was already done by the producing skill.

Conventions: `.harness/references/id-conventions.md`,
`.harness/references/artifact-write-contract.md`.

## When to Use

- After `validate-requirements` generates a validation report
- After `document-audit` generates an audit report
- When the user wants to systematically work through findings rather than handle them ad-hoc
- When collecting decisions for later batch application to the PRD or integration stubs

## Inputs

1. **Report file path** — the findings report to review (REQUIRED). Prefer canonical `prd/reports/Validation-Report-{INIT}.md`.
2. That's it. Everything else is in the report.

---

## Phase 1: Setup

### 1.1 Read the report file

Read the full report file using the Read tool.

### 1.2 Detect format

Determine which skill produced the report by checking the heading:

| Heading | Format | Producer |
|---|---|---|
| `# Requirements Review` | validate-requirements (combined semantic + structural) | `validate-requirements` skill |
| `# Requirements Accuracy Review` | validate-requirements (legacy) | `validate-requirements` skill |
| `# Document Audit Report` | document-audit | `document-audit` skill |
| Other | generic | Unknown — use fallback parsing |

### 1.3 Parse findings by category

**Do not treat `## Resolved` as open findings.** That section records items fixed since a prior report — parse for context only, never walk the user through resolved rows.

**validate-requirements format — 4 categories:**

| Category | Section header pattern | Severity | Id column | Table Columns |
|---|---|---|---|---|
| Critical | `## Critical` | MUST FIX | `VF` (or legacy `#`) | VF, Type, Location, Target, Check, Finding, Source Says, Doc Claims, Example, Recommendation |
| Should Fix | `## Should Fix` | SHOULD FIX | `VF` | VF, Type, Location, Target, Check, Finding, Recommendation |
| Verify | `## Verify` | VERIFY | `VF` | VF, Type, Location, Target, Check, Finding, Question for User |
| Gaps | `## Gaps` | GAP | `VF` | VF, Type, Location, Target, Check, Finding, Suggested Addition |

Legacy reports with only `#` instead of `VF`: assign stable `VF-{nn}` for this resolution pass (map `#1` → `VF-01`) and record the mapping in the resolution file.

Also parse the `## Clean` section to know which checks passed.

Skip sections that contain only prose like "*No Critical findings.*" with no table rows.

**document-audit format — 3 categories:**

| Category | Severity | Structure |
|---|---|---|
| Must Fix (HIGH) | MUST FIX | Text blocks: type (STALE/CONTRADICTION/BROKEN REF), marker, evidence, recommendation, confidence |
| Review Required (MEDIUM) | VERIFY | Same structure |
| Informational (LOW) | INFO | Same structure |

Assign `VF-{nn}` when missing.

**Generic fallback:**

- Look for markdown headers containing severity keywords (Critical, High, Medium, Low, Must Fix, Should Fix, etc.)
- Parse any tables or structured text blocks under each header
- Present raw content if parsing fails; still assign `VF-*`

### 1.4 Count findings

Build a summary: total **open** findings, count per category. Exclude resolved rows.

### 1.5 Resolve initiative id

From report front matter / filename / PRD path. Needed for canonical
`Resolution-{INIT}.md` output.

---

## Phase 2: Entry Gate (MANDATORY)

**Never start the interactive flow without asking first.**

Present the summary to the user:

```
Found [N] findings in [report filename] (report_revision [N] if present):
- [N] Critical / Must Fix
- [N] Should Fix
- [N] Verify / Review Required
- [N] Gaps / Informational
```

Then use AskQuestion to ask how to proceed. If AskQuestion is unavailable, present the same options in chat and wait for the user's choice.

```
AskQuestion:
  id: "review-mode"
  prompt: "How would you like to review the findings?"
  options:
    - id: "all"
      label: "Walk through all findings interactively"
    - id: "critical-only"
      label: "Walk through Critical / Must Fix only"
    - id: "verify-only"
      label: "Walk through Verify / Review Required only"
    - id: "bulk-approve"
      label: "Approve all recommendations — just apply them"
    - id: "skip"
      label: "Skip — I'll handle them manually"
```

**If "skip":** End the skill. No further action.

**If "bulk-approve":** Skip to Phase 4 — mark all findings as approved recommended option; assign `CHG-*` per finding; produce the resolution summary.

**If a specific category:** Only walk through that category in Phase 3, skip others.

**If "all":** Walk through every category in Phase 3.

---

## Phase 3: Interactive Review

Walk through findings in severity order: Critical/Must Fix first, Gaps/Informational last.

### Decision brief (REQUIRED for Critical and Verify)

For each finding, present in chat **before** AskQuestion:

```markdown
### [VF-id] — [severity]

**Issue:** [what is wrong — from Finding]
**Target:** [REQ-* / CAP-* / OQ-* / section]
**Location:** [section/line]
**Check:** [check #]
**Evidence / example:** [Source Says vs Doc Claims, or Example column, or a concrete illustration]
**Recommendation:** [recommended fix]
**Why this recommendation:** [1–2 sentences — risk if ignored, consistency with sources]

**Options:**
| Option | Summary | Pros | Cons |
|--------|---------|------|------|
| A (recommended) | [apply recommendation] | [pros] | [cons] |
| B | [plausible alternative] | [pros] | [cons] |
| C | Skip / leave as-is | [pros] | [cons] |
| D | Custom (user will specify) | — | — |
```

Should Fix / Gaps may use a shorter brief (issue + recommendation + why) and
batch up to 3 when there are 5+ findings — still include options with pros/cons
for the batch decision.

### 3.1 Critical / Must Fix Findings

Present each finding INDIVIDUALLY (never batch).

```
AskQuestion:
  id: "critical-[VF-id]"
  prompt: "[VF-id] [short issue]\n\nChoose an option:"
  options:
    - id: "A"
      label: "A — Apply recommendation"
    - id: "B"
      label: "B — [alternative summary]"
    - id: "C"
      label: "C — Skip / leave as-is"
    - id: "D"
      label: "D — Custom (I'll specify)"
```

If user selects B or D: capture their wording as the action text. Record
`chosen_option`, `rationale` (ask briefly if missing), and assign `CHG-{nn}`.

### 3.2 Should Fix Findings

Present in batches of up to 3 if there are many (5+). Otherwise individually.
Same option pattern (A/B/C/D); shorter brief allowed.

### 3.3 Verify / Review Required Findings

Present each finding INDIVIDUALLY with full decision brief.

```
AskQuestion:
  id: "verify-[VF-id]"
  prompt: "[VF-id] [question for user]"
  options:
    - id: "confirm"
      label: "Confirm — accurate as written (tag Source: User-confirmed)"
    - id: "reject"
      label: "Reject — remove or rewrite"
    - id: "context"
      label: "Needs more context — I'll explain"
    - id: "skip"
      label: "Skip for now"
```

If "confirm": record confirmed; action = add `(Source: User-confirmed)` when applied.
If "reject": ask replacement or confirm removal.
If "context": ask for context, then re-present.

### 3.4 Gaps / Informational Findings

Present in batches of up to 3 when many.

```
AskQuestion:
  id: "gap-[VF-id]"
  prompt: "[VF-id] [suggested addition]"
  options:
    - id: "add-requirement"
      label: "Add to requirements (assign REQ-* / CAP-* if needed)"
    - id: "add-oq"
      label: "Add as Open Question OQ-*"
    - id: "skip"
      label: "Skip — not needed"
    - id: "custom"
      label: "Custom"
```

---

## Phase 4: Resolution Summary

After all findings are reviewed (or bulk-approved), produce two outputs:

### Output 1: Chat Summary

```
## Resolution Summary — [INIT]

**Report:** [canonical validation path] (report_revision [N])
**Findings reviewed:** [N] of [total]
**Decisions:**
- Approved (option A or equivalent): [N]
- Alternative / custom: [N]
- Confirmed: [N]
- Rejected: [N]
- Skipped: [N]
- Added as OQ: [N]

**Resolution file:** [canonical Resolution path] (overwritten)

### Next Step
Apply approved `CHG-*` via `update-documents`, then re-run `validate-requirements`
in incremental mode against the **same** Validation-Report path.
```

### Output 2: Resolution File

**Canonical path:** `{reports_dir}/Resolution-{INIT}.md`

Overwrite this path. Never `Resolution-…-revN.md` or
`Resolution-Validation-Report-….md` long derivatives.

Format:

```markdown
# Resolution Summary

**Report:** [canonical Validation-Report path]
**Initiative:** [INIT]
**Reviewed on:** [date]
**resolution_revision:** [N]
**Findings reviewed:** [N] of [total]

## Decisions

| CHG | VF | Severity | Target | Chosen option | Rationale | Action to apply |
|-----|-----|----------|--------|---------------|-----------|-----------------|
| CHG-01 | VF-01 | Critical | REQ-07 | A | [why] | [exact apply text] |
| CHG-02 | VF-04 | Verify | CAP-02 | confirm | [why] | Add (Source: User-confirmed) |

## Approved Fixes (ready to apply)

| CHG | VF | Type | Location | Original Finding | Decision | Action |
|-----|-----|------|----------|------------------|----------|--------|
| CHG-01 | VF-01 | Semantic | [section] | [finding] | Option A | [recommendation to apply] |

## Confirmed Items (add source tags)

| CHG | VF | Type | Location | Finding | Action |
|-----|-----|------|----------|---------|--------|
| CHG-02 | VF-04 | … | … | … | Add `(Source: User-confirmed)` tag |

## Rejected Items (remove or rewrite)

| CHG | VF | Type | Location | Finding | User Direction |
|-----|-----|------|----------|---------|----------------|
| … | … | … | … | … | … |

## Added as Open Questions

| CHG | VF | Finding | OQ id | Open Question Text |
|-----|-----|---------|-------|---------------------|
| … | … | … | OQ-03 | … |

## Skipped (no action)

| VF | Type | Location | Finding | Reason |
|----|------|----------|---------|--------|
| … | … | … | … | User chose skip |

## Modified / custom recommendations

| CHG | VF | Original Recommendation | User's Alternative | Rationale |
|-----|-----|-------------------------|-------------------|-----------|
| … | … | … | … | … |
```

---

## Integration with Other Skills

| Context | How it's called |
|---|---|
| **After `validate-requirements`** | User runs validation → report generated → invoke with canonical Validation-Report path |
| **After `document-audit`** | Same pattern |
| **Lab workflow** | Resolution feeds PRD edits + stubs via `update-documents`; then incremental validate |
| **Standalone** | User points it at any findings report file |

---

## Critical Rules

1. **Always ask before starting.** Phase 2 Entry Gate is mandatory.
2. **Critical findings are always individual** with a full decision brief.
3. **Record everything.** Every decision (including skip) is in the resolution file with `VF` and `CHG` where applicable.
4. **Don't fix — collect decisions.** Only write the resolution summary file.
5. **Respect the user's choice.** Skip / category filters are honored.
6. **Canonical resolution path.** Overwrite `Resolution-{INIT}.md` only.
7. **Format-agnostic fallback.** Unrecognized format → raw text + generic options + assigned `VF-*`.
8. **Ignore resolved history.** Rows under `## Resolved` are not open findings.
9. **Options need pros/cons** in the brief so the user can choose deliberately.

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the Resolution file. Use stage `review-findings`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates` and `human_checkpoint` from pinned root `workflow.yaml` for `(stage: review-findings, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint` — never because the artifact "should be reviewed."


4. Follow `.harness/references/forge-side-effects.md#content-producers` when this stage's pin has `forge.commit_workspace` other than `disabled` or next is an `external-action` with `forge.requires` — fill `handoff.forge` / recommend the matching `/forge` skill; do not treat local CLI as skill success.


**Transitions:** pinned root `workflow.yaml` for this stage (SSOT). Human or
agent may run this skill; legality and auto-dispatch follow `dispatch` +
delivery contract + latest handoff.

Record unresolved `VF-*` under `blockers`; never encode a user decision
only in chat. `next_candidates` never authorize invoke.
