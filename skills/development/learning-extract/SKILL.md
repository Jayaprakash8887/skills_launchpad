---
name: learning-extract
description: >-
  After human wave-acceptance / tip fixes on a wave PR, extract structured programme
  learning (SPEC / SKILL / HARNESS / ENV) with stable L-* ids for Gateflow to
  persist and for ground-spec to cite. Closeout hop — does not write the Ground
  Report. Use Enter-at or /learning-extract after Pass-1 stop at wave-acceptance.
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/**, .harness/profile.yaml
metadata:
  background_eligible: true
  background_trigger: "wave closeout Enter-at after human wave-acceptance"
---

# Learning extract

Producer of **structured learning** after Pass-1 (implement) and human
wave-acceptance / tip fixes. Gateflow may persist records in a global DB; this skill
only writes a workspace artifact + handoff. **`/ground-spec`** still owns the
wave Ground Report and §Contracts produced.

**Do not** require humans to write learning essays. Infer from repo + bind
context. Ask taxonomy chips only when classification is ambiguous.

## NON-NEGOTIABLE

1. Resolve layout from `.harness/profile.yaml` or
   [references/layout-defaults.md](references/layout-defaults.md).
2. Inspect the wave under test: bound ticket/initiative/wave/PR/run context when
   present; Pass-1 tip vs human-fix window (`git` log/diff); spec/plan/TASK
   rows; verify scripts / `tests_readme`; prior Ground Reports as needed.
3. Emit learning items with closed taxonomy: **`SPEC`**, **`SKILL`**,
   **`HARNESS`**, optional **`ENV`**. One primary class per item. Prefer **SPEC**
   over **SKILL** when both fit.
4. Assign stable ids `L-01`, `L-02`, … (see `.harness/references/id-conventions.md`).
5. Each item includes: summary, evidence (paths/commits), **codify hint**
   (suggested skill / spec area / harness home), status `open` | `codified`.
   Do **not** open auto-merge codify PRs.
6. Write durable artifact
   `{reports_dir}/Learning-Extract-{initiative}-W{N}.md` with a human table
   **and** a fenced `learning_extract:` YAML block (machine payload). This file
   is **PURGE** at initiative closure (see artifact-write-contract).
7. Empty `items: []` only when there is **no** human-fix signal and the tip
   matches intent — state that rationale explicitly. If human fixes clearly
   exist and zero items → do not `pass` (use `findings` / fail-closed).
8. **Do not** author the full Ground Report REQ matrix or §Contracts produced —
   that remains `/ground-spec`.
9. Do **not** call Gateflow HTTP / DB as skill success. Worker ingest is the
   consumer (H6). Follow `.harness/references/forge-side-effects.md#content-producers`
   for optional workspace publish.
10. Ids / paths: `.harness/references/id-conventions.md`,
    `.harness/references/artifact-write-contract.md`.

## Taxonomy

| Class | Use when |
|-------|----------|
| `SPEC` | Upstream product/TDD/acceptance incomplete or wrong |
| `SKILL` | Playbook/prompt/procedure miss (agent followed process, still wrong) |
| `HARNESS` | Verify/assert/setup wrong — harness would mislead |
| `ENV` | Infra/secrets/cluster only — not product learning |

## Inputs

1. **Initiative + wave** — (REQUIRED)
2. **Workspace / PR tip** — run head after human wave-acceptance
3. **Optional bind** — ticket, PR/run ids from orchestrator

## Prerequisite

- Pass-1 complete enough that a tip exists (typically after `wave-acceptance` park
  or equivalent human prove + patch)
- Pin next on `pass`: `ground-spec`

## Process

1. **T0 Gather** — initiative, wave N, plan/spec paths, tip SHA, fix window
2. **T1 Diff signal** — detect human_fix_detected yes/no
3. **T2 Classify** — draft `L-*` rows; chip-ask only if ambiguous
4. **T3 Write artifact** — markdown + YAML fence per
   [references/output-template.md](references/output-template.md)
5. **T4 Handoff** — `pass` → `ground-spec`; dual-write baton when bound

## Chain position

Illustrative — **transitions SSOT:** pinned `workflow.yaml`.

```text
Pass-1: … → loop-spec → wave-acceptance (human) → wave-awaiting-closeout
Pass-2 Enter-at /human:
  /learning-extract  ← YOU ARE HERE
       ↓
  /ground-spec → wave-done-action → wave-signoff (merge only)

Pass-2 closeout (`learning-extract` → `ground-spec`) closes the wave;
`wave-signoff` is merge/publish only — not a second human approve.
```

## Workflow handoff

1. Append/emit envelope from `.harness/references/handoff-envelope.md`. Stage
   `learning-extract`.
2. When `handoff_path` is bound, **overwrite** that path with the same
   `handoff:` envelope before exit.
3. Derive `next_candidates` and `human_checkpoint` from pinned `workflow.yaml`
   for `(stage: learning-extract, outcome)`. Set `human_checkpoint: true` only
   when the resolved next node's `type` is `human-checkpoint`.
4. Happy path: `outcome: pass` → next `ground-spec` → `human_checkpoint: false`.
5. Follow `.harness/references/forge-side-effects.md#content-producers` when pin
   `forge.commit_workspace` is not `disabled`.
