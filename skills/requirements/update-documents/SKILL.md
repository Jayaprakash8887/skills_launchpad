---
name: update-documents
description: "Propagates approved corrections, decisions, terminology changes, and scope changes across related documents. In Resolution mode it consumes a review-findings Resolution file without re-deciding semantic choices; in Ad-hoc mode it first confirms the user-provided change set. Both modes perform impact analysis, present an exact change manifest for approval, apply only approved edits, and run inline consistency verification. Use after review-findings or when the user supplies a verified change."
---

# Update Documents — Cross-Document Change Propagation

## Purpose

Propagates verified corrections and decisions across a set of related documents.
It determines **where an approved decision must be reflected**; it does not
decide **what the decision should be**.

**When to use:**
- A fact or assumption was wrong and multiple documents reference it
- New information (design, stakeholder input, discovery) must be reflected across existing docs
- Terminology is changing across a document set
- A feature or scope item is being added, deferred, or removed
- After `review-findings` — apply an approved `Resolution-*.md` across PRD + integration stubs

**Domain-agnostic.** Works on any document type — requirements, PRDs, meeting notes, design specs, technical docs.

**Lab handoff:** `review-findings` produces canonical
`prd/reports/Resolution-{INIT}.md`. Use the **Decisions** table (`CHG-*` →
`VF-*`) plus **Approved Fixes**, **Confirmed Items**, **Rejected Items**, and
**Added as Open Questions** as the change set (Phase 1). Typical scope:
`prd/INIT-*.md`, `docs/cross-service-lab.md`, per-repo `03-integrations.md` /
route maps. Prefer assigning/preserving `CAP-*` / `REQ-*` / `OQ-*` when the
resolution asks for product-id updates.

**Spec PR (app repo):** When drafting `docs/specification/product/INIT-*.md`, engineering uses `/spec-draft` on branch `chore/INIT-*-spec-{repo}`. Wave IDs must match PRD §4.0 / §4.5. Product ids use `REQ-*` (legacy `FR-*` ≡ same number). Gate: launchpad `playbook/delivery-workflow.md` + `playbook/spec-layout.md`.

Conventions: `.harness/references/id-conventions.md`,
`.harness/references/artifact-write-contract.md`.

---

## Operating modes

Select exactly one mode during intake.

### Resolution mode (preferred after `review-findings`)

Use when the input is canonical `Resolution-{INIT}.md` (or legacy `Resolution-*.md`).

- The Resolution file is the semantic decision source.
- Apply only rows with a `CHG-*` (or legacy approved sections):
  **Approved Fixes**, **Confirmed Items**, **Rejected Items**,
  **Added as Open Questions**, and **Modified / custom recommendations**.
- Exclude **Skipped** items.
- Preserve `source_finding: VF-*` on every change row.
- Do not ask the user to re-decide completed resolution rows.
- If a row lacks exact action text, ownership, or other information required to
  apply it, classify it `NEEDS DECISION` and return it to `review-findings`.
- Present the resolved change-set summary for visibility, then use the detailed
  change manifest as the single approval gate before editing.

### Ad-hoc mode

Use when the user directly supplies a verified correction or decision.

- Structure the proposed change set with `CHG-{nn}` ids.
- Require the Step 2 change-set approval.
- Require the Step 5 detailed manifest approval before editing.

### Decision boundary

This skill must not independently:

- create a new requirement or open question,
- assign or change an owner,
- choose product behaviour, priority, or scope,
- choose an engineering design,
- convert a finding into a requirement or deferral.

Those are semantic decisions. Route them to `review-findings` or obtain an
explicit user decision in Ad-hoc mode before impact analysis continues.

---

## Phase 1: Intake

### Step 1: Receive and structure the change set

Gather approved changes from the Resolution file or user. For each change, capture:

| Field | Description |
|-------|-------------|
| **ID** | `CHG-{nn}` (required). Legacy `C1`/`C2` → normalize to `CHG-01`/`CHG-02` |
| **source_finding** | `VF-{nn}` when from resolution; `adhoc` otherwise |
| **Type** | One of: Factual correction, Terminology change, Scope change, New information |
| **What is wrong / missing** | The current incorrect or absent content |
| **What is correct / new** | The verified replacement or addition |
| **Source / evidence** | Why the new information is correct — user statement, design file, meeting, data |
| **Decision source** | Resolution `CHG` row, explicit user statement, or other approved record |
| **Decision status** | APPROVED / NEEDS DECISION |
| **Target product id** | `REQ-*` / `CAP-*` / `OQ-*` when known |

#### Change type reference

| Type | Propagation pattern | Search strategy |
|------|---------------------|-----------------|
| **Factual correction** | Any section that assumed the wrong fact — personas, pain points, user flows, assumptions, goals, constraints, dependencies | Search for the incorrect fact AND for statements derived from it; also search `REQ-*` / `CAP-*` targets |
| **Terminology change** | All occurrences of the old term across all documents | Context-aware find-and-replace — match singular/plural, capitalization, possessive forms |
| **Scope change** | Scope sections, feature lists, future enhancements, assumptions, success metrics | Search for the feature/item name and product ids in scope tables, requirement lists, and roadmap references |
| **New information** | Additive — new content in contextually correct sections, new rows in tables, new references | Identify which sections in each document should contain the new information; assign `CAP-*`/`REQ-*`/`OQ-*` when the resolution requires it |

If the user provides changes informally, reformat them into the structured table before proceeding.

---

### Step 2: Change-set presentation

Present the structured change set back to the user:

```
## Change Set for Review

| ID | Type | What is wrong / missing | What is correct / new | Source |
|----|------|------------------------|-----------------------|-------|
| C1 | ...  | ...                    | ...                   | ...   |
| C2 | ...  | ...                    | ...                   | ...   |

Mode: Ad-hoc
Is this complete and correct? Any changes to add, modify, or remove?
```

**Ad-hoc mode:** mandatory stop. Do not proceed until the user confirms.

**Resolution mode:** present the same table for visibility, with each Resolution
row cited under Decision source. Do not ask the user to reconfirm already
approved decisions. If any row is `NEEDS DECISION`, stop and produce a
supplemental finding for `review-findings`; do not infer the missing decision.

---

### Step 3: Identify document scope and dependency order

1. User specifies which folder(s) or file(s) are in scope.
2. List all documents found. For each, note:
   - Document name and path
   - Document type (meeting summary, stage artifact, requirements doc, design doc, etc.)
   - Position in dependency chain (if any)
3. If documents have a dependency chain (e.g., "Stage 2 informs Stage 5 which informs the requirements doc"), establish the update order: **upstream first, downstream last.**
4. If no dependency chain exists, order alphabetically or by the user's preference.

Present the document list and proposed update order to the user for confirmation. This is informational — not a mandatory stop — but the user may adjust scope.

---

## Phase 2: Execute

### Step 4: Impact analysis and search

For each change in the change set:

1. **Determine affected section types.** Based on the change type, identify which kinds of sections could be affected:
   - Factual correction → personas, pain points, user needs, business goals, user flows, assumptions, constraints, dependencies, known limitations, error handling
   - Terminology change → all sections (full document scan)
   - Scope change → executive summary, scope, feature lists, requirements, future enhancements, assumptions, success metrics
   - New information → depends on content; identify the most contextually appropriate sections

2. **Search all in-scope documents** for:
   - **DIRECT matches** — text that explicitly states the incorrect information or uses the old term
   - **DERIVED statements** — text that is based on or implies the incorrect information, even if it doesn't contain the exact words (e.g., a pain point that only makes sense if the wrong fact is true)
   - **CROSS-REFERENCES** — references to the incorrect information from other documents or sections

3. **Categorize each impact:**

| Category | Meaning | Action |
|----------|---------|--------|
| DIRECT | Text explicitly contains the incorrect information | Will be updated |
| DERIVED-ENTAILED | The edit is a necessary consequence of the approved decision and introduces no new semantic choice | Will be updated; cite the decision source |
| POTENTIAL-MECHANICAL | The approved decision is clear, but placement, formatting, or cross-reference handling is ambiguous | Ask a focused mechanical question in Step 5 |
| NEEDS-DECISION | Applying the edit requires new product, ownership, scope, priority, domain, or engineering judgment | Stop; route back to `review-findings` |

`DERIVED-ENTAILED` is not permission to invent. If the replacement is not
fully entailed by the approved decision, use `NEEDS-DECISION`.

4. Record each impact with: document path, section heading, line reference,
current text, proposed replacement, category, and decision source.

---

### Step 5: Change manifest and user review (MANDATORY STOP)

Present all planned changes, grouped by document in dependency order:

```
## Change Manifest

### Document: [path] (Update order: 1 of N)

| # | Section | Category | Current text | Proposed text | Change ID | Decision source |
|---|---------|----------|-------------|---------------|-----------|-----------------|
| 1 | ...     | DIRECT   | "..."       | "..."         | C1        | Resolution §… row … |
| 2 | ...     | DERIVED-ENTAILED | "..." | "..."       | C1        | Resolution §… row … |
| 3 | ...     | POTENTIAL-MECHANICAL | "..." | "..." (?) | C2      | Resolution §… row … |

### Document: [path] (Update order: 2 of N)
...

**Mechanical clarifications:**
- Item 3 in [document]: [placement/format/cross-reference question]

**NEEDS-DECISION items:**
- None. If any exist, stop before requesting manifest approval and send them
  back through `review-findings`.

Total: [N] changes across [M] documents.
Confirm to proceed, or adjust individual items.
```

**Do NOT apply any edits until the user approves the manifest.**

If the user answers a mechanical clarification, rejects, or modifies an item,
regenerate the full manifest and re-present it. If the answer introduces a new
semantic decision, stop and route it through the decision flow first.

---

### Step 6: Apply changes

Apply approved changes in dependency order (upstream documents first).

**For each document:**

1. **Read the full document** before editing — understand its structure, tone, and conventions.
2. **Apply changes** using the edit tool:
   - Preserve the document's existing format, heading hierarchy, and section structure
   - Match the writing style of surrounding text (bullet style, sentence length, voice, level of detail)
   - For table updates: match column format, alignment, and row style
   - For new content: place it in the contextually correct section — do not create new sections unless the document structure requires it
   - For removals: remove cleanly without leaving orphaned references or empty sections
3. **Update change history** — only when the approved manifest includes it and
   the document has a version/changelog section:
   - Date, author (from the change set source), one-line summary of what changed
   - If the document has no changelog, skip — do not add one

**After each document is updated,** briefly confirm the edit was applied before moving to the next document.

---

## Phase 3: Verify

### Step 7: Verify consistency after edits

**If a requirements / PRD file was modified:** re-run `validate-requirements` in
**incremental mode** — pass the canonical
`prd/reports/Validation-Report-{INIT}.md` as the prior report (same path that
will be overwritten). Confirm applied `CHG-*` resolved the targeted `VF-*`.
Never create a new `Validation-Report-*-revN.md`.

**For all modified documents**, also perform an inline structural pass (no separate `document-audit` skill required):

- **Contradictions introduced by the changes** — does the updated text now conflict with an un-updated section?
- **Broken cross-references** — did a section rename or content removal break internal references?
- **Stale markers resolved** — did the new information answer a `[TBD]` or `[PENDING]` that was previously unresolvable?
- **Terminology inconsistencies** — are there sections that still use old terminology alongside updated sections?
- **Cascading staleness** — did updating an upstream document make a downstream document's reference or quote stale?

If many documents were updated (5+), prioritize the most downstream documents first — they are most likely to have inconsistencies.

---

### Step 8: Report and close

Present a final summary:

```
## Update Summary

**Documents updated:** [N]
**Total changes applied:** [M]
**Change history entries added:** [K]

### Changes by document:
| Document | Changes applied | Audit status |
|----------|----------------|-------------|
| [path]   | [N]            | Clean / [N] findings |

### Verification findings requiring attention:
[List structural inconsistencies or new validate-requirements findings]

### Resolved during verification:
[List issues fixed inline during the pass]
```

- Fix only contradictions or broken cross-references whose exact correction was
  already present in the approved manifest.
- For any newly discovered edit, produce a **Supplemental Change Manifest** and
  obtain approval before applying it.
- Route newly discovered semantic ambiguity to `review-findings`; do not decide
  it during verification.
- If `validate-requirements` reports new Critical findings, stop and resolve before sign-off.

---

## Critical Rules

1. **Never update without manifest approval.** Ad-hoc mode requires both Step 2
   change-set approval and Step 5 manifest approval. Resolution mode presents
   the approved change set for visibility and requires Step 5 manifest approval.
2. **Never invent corrected text.** If the user hasn't provided the correct information for a finding, flag it as "needs user input" — do not guess or fabricate replacements.
3. **Preserve document voice.** Each document may have a different tone, format, and level of detail. Match it. Do not impose a uniform style across documents.
4. **Dependency order matters.** If Document A is cited by Document B, update A first so B's references remain valid during the update process.
5. **Domain-agnostic.** Do not assume a specific industry, document format, or technology. The skill works on any structured document.
6. **Additive by default.** When adding new information, place it in the contextually correct existing section rather than creating new sections — unless the document's structure genuinely requires a new section.
7. **Manifest change history.** If a document has a version/changelog section,
   include its history entry in the manifest. If it has none, do not add one.
8. **Read before editing.** Always read the full document before making changes. Never edit from memory or partial reads.
9. **One change at a time.** Apply changes sequentially within each document. Do not batch multiple edits into a single operation that would be hard to verify or undo.
10. **DERIVED-ENTAILED is narrow.** Apply it only when the replacement is
    factually correct, preserves intent, and is fully entailed by the approved
    decision. Otherwise classify it `NEEDS-DECISION`.
11. **Propagation is not decision-making.** Never create an open question,
    assign ownership, choose scope, or make product/engineering decisions unless
    the exact choice appears in the Resolution file or an explicit approved
    Ad-hoc change set.
12. **No retrospective sign-off.** Do not make a semantic choice and then ask
    the user to approve it in the manifest. Ask first through the decision flow.
13. **Comments are not sufficient evidence.** Cite the committed Resolution
    artifact or explicit user-approved change set as the decision source.

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the Update Summary. Use stage `update-documents`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates` and `human_checkpoint` from pinned root `workflow.yaml` for `(stage: update-documents, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint` — never because the artifact "should be reviewed."


4. Follow `.harness/references/forge-side-effects.md#content-producers` when this stage's pin has `forge.commit_workspace` other than `disabled` or next is an `external-action` with `forge.requires` — fill `handoff.forge` / recommend the matching `/forge` skill; do not treat local CLI as skill success.


**Transitions:** pinned root `workflow.yaml` for this stage (SSOT). On `pass`,
consumers typically re-enter `validate-requirements` in incremental mode per
workflow. Human or agent may run this skill; legality and auto-dispatch follow
`dispatch` + delivery contract + latest handoff.

List any supplemental decision ids under `blockers`; do not continue into
validation when a semantic decision is still missing. `next_candidates` never
authorize invoke.
