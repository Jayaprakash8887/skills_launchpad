---
name: open-draft-pr
description: >-
  Open or update a Draft pull request and apply projection labels from pin ⋉
  handoff.forge (human walker). Use after content skills such as spec-draft,
  prd-impact-map, or pre-implement (wave Draft PR) when the user authorizes
  publish. Orchestrators use ForgeClient on external-action nodes instead —
  do not auto-invoke this skill.
disable-model-invocation: true
---

# Open Draft PR

Human-walker equivalent of Gateflow `ForgeClient` **open/update Draft PR**
(`forge.action: open_draft_pr`).

## NON-NEGOTIABLE

1. Require a complete `handoff.forge` from the content skill (pin `requires`
   filled). Incomplete → ask or block; do not invent title/body/labels.
2. Merge pin policy with handoff: **pin wins** on `action`, `draft`,
   `apply_labels`, `remove_labels`.
3. `action` must be `open_draft_pr`. Open or update a **Draft** PR when
   `draft: true`.
4. Apply only projection labels from policy. **Never** apply `*-lgtm`.
5. When **you** (human) run this skill: explicit user confirmation before
   mutate (chat yes / UI). Content skill recommendation is not authorization
   by itself. When the pin sets `authorization: automated` on the matching
   `external-action` (`spec-pr-action`, `wave-pr-action`), **Gateflow
   ForgeClient** may open/update the Draft PR without interactive STOP —
   that path does not invoke this skill. This skill remains human-confirm.
6. Tool-neutral Forge tooling (`gh`, REST, …) — examples only.

## Inputs

1. Content-skill handoff with `external_action: true` and `forge:`
2. Pin node for the next `external-action` (`prd-pr-action`, `spec-pr-action`,
   or `wave-pr-action`)
3. Workspace files referenced by `body_path` / artifact

## Process

1. Validate `handoff.forge` against pin `requires` and label policy.
2. Ensure branch exists / matches readiness (without inventing policy).
   For `wave-pr-action`, require `head_ref` and `base_ref` from the handoff
   (wave branch → integration base).
3. Create or update Draft PR (title, body from readiness).
4. Apply `apply_labels`; remove `remove_labels` / obsolete projection labels
   per pin. Wave Draft PRs typically carry no auto labels from the pin.
5. Report PR URL; emit forge-step handoff using
   [references/output-template.md](references/output-template.md) —
   `artifact.path` is `null` (this skill has no workspace artifact); do not
   invent a note file to hold the result.
6. Never merge. Never apply `*-lgtm`. Wave merge stays human-only at
   `wave-signoff`.

## Workflow handoff

1. Emit the envelope from [references/output-template.md](references/output-template.md)
   in chat; stage id: `open-draft-pr`. `artifact.path: null` — there is no
   workspace file to persist for this stage.
2. Dual-write `handoff_path` when bound.
3. Not a graph node — resume programme from the content handoff’s
   `next_candidates` after successful PR action (human records auth).
