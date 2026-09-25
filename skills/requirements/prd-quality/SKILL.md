---
name: prd-quality
description: >-
  Score two or more PRD files independently against the spec-lane delivery
  bar, then compare. Use after /prd-think reruns, or whenever the user
  passes candidate paths (prd-think series or prd/{INIT}.md). Scientific:
  blind per-file PASS/FAIL with quoted evidence, then a comparison table.
  Optional companion /prd-critic is secondary and cannot override a material
  FAIL. Writes reports_dir/{INIT}-prd-quality.md. Never edits the PRDs.
  Never run /prd, /prd-think, /prd-impact-map, or forge.
disable-model-invocation: true
---

# PRD quality

Score **files the user passes**, not a mode inside `/prd-think`.

A good PRD here means `/spec-draft` can implement it **without guessing**.
Page count, tone, and “looks like a PRD” are not scores.

**Pin contracts (read, do not fork):**

- Ids: `.harness/references/id-conventions.md`
- Paths: `.harness/references/artifact-write-contract.md`

## Inputs (required)

1. **Two or more PRD paths** — e.g. `{INIT}-prd-think.md` and
   `{INIT}-prd-think-2.md`, or a think candidate vs `prd/{INIT}.md`.
   If the user names only an INIT, look under `reports_dir` for
   `{INIT}-prd-think*.md`. If fewer than two files exist, **ask** — do
   not invent a second document, do not score a singleton “vs imaginary A.”
2. **Initiative id** — from filenames or ask.
3. **Brief** — (OPTIONAL) outline used to author the candidates. Needed
   only for bar B12 (whole-product vs brief-shaped). If absent, score B12
   as `N/A — brief not supplied` (not a free PASS).
4. **Layout** — `reports_dir` from `.harness/profile.yaml` (meta default
   `prd/reports/`).

Do not read one candidate in order to fill gaps in the other.

## Outputs

| File | Role |
|------|------|
| `{reports_dir}/{INIT}-prd-quality.md` | Independent scores + comparison |

Overwrite that one report path. Never write `*-revN`. Never edit the
input PRDs or `prd/{INIT}.md`.

## NON-NEGOTIABLE

1. **≥2 files.** No comparison without both (or all) paths.
2. **Blind first.** Score each file in isolation against
   [references/delivery-bar.md](references/delivery-bar.md) before any
   winner language.
3. **Evidence.** Every bar is `PASS` / `FAIL` / `N/A` plus **id + quote**.
   If you would guess to fill a spec row, that bar is `FAIL`.
4. **Same rubric, same weights.** Do not add ad-hoc criteria mid-run.
   Do not prefer the later file, the longer file, or the one named
   `prd-think`.
5. **`/prd-critic` is secondary.** If installed, run it per file after
   the delivery-bar pass. Its Build Readiness cannot override a material
   FAIL. If missing, skip — do not inline a fake critic.
6. **Do not invoke** `/prd`, `/prd-think`, `/prd-development`,
   `/prd-impact-map`, `/validate-requirements`, `/commit-workspace`,
   `/open-draft-pr`.
7. **Do not promote.**

## Companion

| Skill | Role | If missing |
|-------|------|------------|
| `/prd-critic` | Prose / clarity / metrics second opinion | Skip |

## Process

### T0 Resolve files

List the paths. Label them `C1`, `C2`, … from **filenames only**.
Tell the user the output path.

### T1 Independent score (repeat per file)

For each `Ci`, in order, with **only that file + the rubric + optional brief**
in mind:

1. Fill B1–B15.
2. Count material FAILs.
3. List spec-lane guesses (rows `/spec-draft` could not fill).

Do not mention other candidates in this pass.

### T2 Secondary critic (optional)

If `/prd-critic` is installed, run it on each file. Record Strengths /
Gaps / Build Readiness under a **Secondary (prd-critic)** heading.
Discard critic claims that contradict a delivery-bar FAIL.

### T3 Handover, then compare

Write `{reports_dir}/{INIT}-prd-quality.md` from
[references/scorecard-template.md](references/scorecard-template.md).

**Handover** is the only signal for validate → review → update. It is
**per file**, not the comparison winner.

| Handover | When |
|----------|------|
| `yes` | That file has **zero material FAILs** (`ready-to-validate`) |
| `no` | Any material FAIL (`think-again` — keep looping `/prd-think`) |

A third (or Nth) think file is just another `Ci`. Score it the same way.
`yes` on two files with different jobs is not a tie-break — the human
picks which named file to promote.

**Rank** (secondary, after handover):

- `Ci` beats `Cj` only if fewer material FAILs on **B3, B4, B6, B9, B11**,
  **B12 PASS** (or both N/A for the same reason), and **B2 equal or better**.
- Rank must not override a `no`. A `Ci-wins` file with material FAILs is
  still `handover: no`.

Present the **Handover** table in chat first, then the comparison. A
third run is `C3`; do not overwrite earlier candidates.

## Verdict language

Header `Verdict` = comparative rank only (`C1-wins` / `C2-wins` / `tie`).
Header `Handover` = comma list `C{n}: yes|no`.
Never treat `Ci-wins` as permission to validate. Never `B-wins` vs a
hidden current PRD unless that file was an input.

## Workflow handoff

This skill is **human-invoked** — it is not a node in pinned `workflow.yaml`.
When orchestrator-bound:

1. Persist `{reports_dir}/{INIT}-prd-quality.md`.
2. **Overwrite** `handoff_path` with the `handoff:` envelope when bound.
   Leaving the baton empty is a failed stage for automated consumers.
3. Derive `next_candidates` and `human_checkpoint` from pinned root
   `workflow.yaml` for `(stage: prd-quality, outcome)` per
   `.harness/references/handoff-envelope.md` (**Derive from pinned
   workflow**). Set `human_checkpoint: true` only when the resolved next
   node's `type` is `human-checkpoint`.

When not orchestrated, skip baton write unless `handoff_path` is bound.
