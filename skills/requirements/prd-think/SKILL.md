---
name: prd-think
description: >-
  Write a PRD by challenging the brief as a hypothesis, not by filling an
  outline. Grill job, actors, non-goals, and kill assumption; model the
  product; red-team; write a candidate as spec-draft input. Product ids from
  prayog-skills id-conventions. Writes reports_dir/{INIT}-prd-think.md (or
  -2, -3 on rerun). Use when starting or rewriting a PRD or when an outline
  must not be treated as baseline. Never overwrite prd/{INIT}.md unless the
  user authorizes promote. Never score candidates — use /prd-quality. Never
  run /prd, /prd-impact-map, or forge.
disable-model-invocation: true
---

# PRD think

Write a PRD that **`/spec-draft` can implement without guessing**.

The brief (outline, notes, or spoken ask) is a **hypothesis**. Expanding its
headings is a failed run. Architecture, routes, payloads, frameworks, and
module names are a failed run — park those for engineering.

This skill **authors**. It does **not** score. After one or more candidates
exist, run `/prd-quality` and pass the files.

**Pin contracts (read, do not fork):**

- Ids: `.harness/references/id-conventions.md`
- Paths / overwrite: `.harness/references/artifact-write-contract.md`

If the pin mount is missing, say so and still follow those rules from a
harness skill copy if present. Do not invent a second id vocabulary.

This skill does **not** unlock Gate 1. Typical next: `/prd-quality` on two
candidates, then user authorizes promote of one file to `prd/{INIT}.md`,
then `/validate-requirements`.

## Inputs (resolve, do not assume an INIT)

1. **Brief** — (REQUIRED) outline file, pasted ask, or conversation. Prefer
   `prd/INIT-*-outline.md` or `prd/*-outline.md` if the user points at one.
2. **Initiative id** — `INIT-*`. Ask if missing. Do not invent a programme
   prefix.
3. **Existing PRD** — (OPTIONAL) `prd/{INIT}.md`. Context only. Never input
   for T1. Never edit unless promote is authorized.
4. **Product context** — (OPTIONAL) whatever exists: `planning/`,
   `config/service-catalog*.yaml`, sibling `prd/INIT-*.md`, ADRs. Absence is
   not a blocker — record as skipped.
5. **Layout** — `reports_dir` from `.harness/profile.yaml` (meta default
   `prd/reports/` per artifact-write-contract). `prd_root` default `prd/`.

## Outputs

Live PRD filename is `prd/{INIT}.md`. Mark conductor output with suffix
`-prd-think` so it cannot be mistaken for KEEP product.

**Series (do not overwrite a previous think candidate):**

| First free path | Role |
|-----------------|------|
| `{reports_dir}/{INIT}-prd-think.md` | Run 1 |
| `{reports_dir}/{INIT}-prd-think-2.md` | Run 2 |
| `{reports_dir}/{INIT}-prd-think-N.md` | Run N |

Pick the lowest N whose file does not exist. Never clobber an earlier run.
Never write `prd/{INIT}.md` from T4.

This series is an experiment exception to “one path per concern”: the
candidates are the evidence `/prd-quality` compares. Do not use `*-revN`.

## NON-NEGOTIABLE

1. **Brief is not baseline.** Challenge it before filling it.
2. **Do not edit** the brief or an existing `prd/{INIT}.md` during the run.
3. **Do not invoke** `/prd`, `/prd-development`, `/to-prd`, `/prd-impact-map`,
   `/commit-workspace`, `/open-draft-pr`, `/prd-quality`, `/prd-critic`.
4. **WHAT not HOW.** No routes, payloads, token encoding, framework, cache, or
   module names in requirement text.
5. **Ids.** Assign **only** product ids from
   `.harness/references/id-conventions.md` (`CAP-*`, `J-{nn}`, `REQ-*`
   canonical, `CTR-*`, `OQ-*`). Do not mint `FR-*`, `D-*`, bare `J1`, or any
   other namespace. Discovery locks are a numbered table of statements, or
   they stay `OQ-*` until they become a CAP/REQ/J.
6. **Capability + journey first-class.** Every `CAP-*` lists ≥1 `J-{nn}` or
   explicit defer. Evidence containing **live** cites ≥1 `CAP-*` and/or
   `J-*` — not bare “live”. Capability and journey are **separate prove
   rungs** (`.harness/references/quality-confidence-ladder.md`).
7. **Silent gaps are failures.** If spec-draft would guess, emit `OQ-*` or
   grill. Do not invent a REQ; do not omit the gap.
8. **One question at a time** in T1 (or one `/grilling` frontier round).
   Recommend an answer every time. Wait.
9. **Locks are outputs of this grill.** Confirm or reopen locks that are
   already in the brief. Do not copy another INIT's lock table.
10. **Whole-product.** If the candidate TOC equals the brief's TOC, fail the
    run. Consider at least one journey, actor, negative path, or adjacent
    surface the brief did not list (keep / `OQ-*` / non-goal).
11. **Do not score.** No delivery-bar table, no winner. Point at `/prd-quality`.

## Companion skills (use if installed)

| Phase | Skill | If missing |
|---|---|---|
| T1 | `/grilling` | Inline § Challenge |
| T2 | `/domain-modeling` | Inline § Model |
| T2 | `/opportunity-solution-tree` | Inline § Model (OST fork) |
| T3 | `/strategy-red-team` | Inline § Stress |

After a companion, **return here**. Companions must not write the PRD.
Write the candidate with [references/candidate-schema.md](references/candidate-schema.md).

## Process

### T0 Gather

Inventory: brief, INIT id, existing PRD, catalog, planning/siblings, existing
`{INIT}-prd-think*.md` files.

Resolve the next free output path. Tell the user that path and that
`prd/{INIT}.md` will not be touched.

### T1 Challenge

Prefer `/grilling` on the brief + available context.

Must resolve or park as `OQ-*`:

- Job / done-in-the-world (who hurts — do not assume hats from a prior INIT)
- Why now / if we do nothing
- Solution vs job (is the ask a proxy?)
- Actors who can actually do what we might assign
- Load-bearing non-goals
- Kill assumption: `Fails if ___`

**Hard stop:** if the job and the proposed solution disagree, do not draft
REQs. Present the fork and wait.

### T2 Model

Prefer `/domain-modeling` then `/opportunity-solution-tree`.

Before any REQ table:

- Domain terms (from T1, not from a template)
- Journeys including ones the brief omitted
- Adjacent surfaces: keep / defer / non-goal
- Seams (`CTR-*` seeds) after the split is decided — logical operation +
  meaning + errors, not URLs
- NFR map: specify or N/A with reason

If multiple outcomes could be this INIT, name them and recommend **one**.

### T3 Stress

Prefer `/strategy-red-team`. Cap ~5 load-bearing claims.

Steelmans → `Fails if ___` → cheapest test → kill criteria.
Survivors → REQ or assumption. Casualties → `OQ-*` or non-goal.

### T4 Draft candidate

Write the path from T0 using
[references/candidate-schema.md](references/candidate-schema.md).

Mint product ids per id-conventions. Do not copy another INIT, an existing
PRD, or an earlier think candidate to fill the page.

Stop. Recommend `/prd-quality` with this file and at least one other PRD
path (earlier think candidate, or `prd/{INIT}.md` if the user wants that
comparison).

## Promote (explicit authorization only)

On user request only: copy **the file they name** → `prd/{INIT}.md`, then
recommend `/validate-requirements`. Do not run impact-map or forge from
this skill.

## Inline protocol (companions missing)

**Challenge:** job → why now → solution vs job → actors → non-goals → kill
assumption. One question at a time; recommend an answer.

**Model:** terms, journeys (incl. omitted), adjacent keep/defer/non-goal,
seams, NFR map. OST fork if multiple outcomes.

**Stress:** ≤5 load-bearing claims; `Fails if ___`; cheapest test.

Thinking is done when each `REQ-*` has condition + observable result without
guessing — or you can name the `OQ-*` that blocks that row.

## Workflow handoff

This skill is **human-invoked** — it is not a node in pinned `workflow.yaml`.
When orchestrator-bound:

1. Persist the candidate at the T0 path under `reports_dir`.
2. **Overwrite** `handoff_path` with the `handoff:` envelope when bound.
   Leaving the baton empty is a failed stage for automated consumers.
3. Derive `next_candidates` and `human_checkpoint` from pinned root
   `workflow.yaml` for `(stage: prd-think, outcome)` per
   `.harness/references/handoff-envelope.md` (**Derive from pinned
   workflow**). Set `human_checkpoint: true` only when the resolved next
   node's `type` is `human-checkpoint`.

When not orchestrated, skip baton write unless `handoff_path` is bound.
