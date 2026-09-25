# Open Draft PR — result note

This skill mutates GitHub only — it has **no workspace artifact**. Do not
create a report file to hold this content; present it in chat and emit the
handoff below. `artifact.path` is `null` on every outcome.

## Result

| Field | Value |
|-------|-------|
| Content stage handoff consumed | `{stage}` / `outcome: {outcome}` |
| Action | created / updated |
| PR URL | {url} |
| PR number | {number} |
| Draft | true |
| Labels applied | {list from `apply_labels`} |
| Labels removed | {list from `remove_labels`, or none} |
| Head ref | {branch} |
| Base ref | {branch} |

## Blocked / incomplete (when applicable)

| Field | Value |
|-------|-------|
| Reason | missing `handoff.forge` required slot / tooling unavailable / user declined confirm |
| Missing slots | {list} |

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: open-draft-pr
  outcome: pass | blocked | failed
  artifact:
    path: null
  blockers: []
  signals:
    pr_url: {url}
    pr_number: {number}
    action: created | updated
    labels_applied: [...]
  next_candidates: []
  human_checkpoint: false
  external_action: false
```

Forge skills are not workflow graph nodes — do not invent `next_candidates`
beyond what the **prior content stage**'s handoff + pinned `workflow.yaml`
already resolved. Re-read that content-stage handoff to continue the
programme after this mutation.
