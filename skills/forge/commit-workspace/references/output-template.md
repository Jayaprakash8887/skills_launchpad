# Commit workspace — result note

This skill mutates the git tree only — it has **no workspace artifact**. Do
not create a report file to hold this content; present it in chat and emit
the handoff below. `artifact.path` is `null` on every outcome, including the
justified no-op case (policy `optional`, clean tree).

## Result

| Field | Value |
|-------|-------|
| Content stage handoff consumed | `{stage}` / `outcome: {outcome}` |
| `forge.commit_workspace` policy | disabled / optional / required |
| Published | yes / no — justified no-op (clean tree, policy `optional`) |
| Head ref | {branch} |
| Commit SHA | {sha or N/A} |
| Paths included | {list or N/A} |

## Fail-closed (when applicable)

| Field | Value |
|-------|-------|
| Reason | policy `required` and nothing includable / policy `disabled` |

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: commit-workspace
  outcome: pass | failed
  artifact:
    path: null
  blockers: []
  signals:
    published: true | false
    head_ref: {branch}
    commit_sha: {sha or null}
  next_candidates: []
  human_checkpoint: false
  external_action: false
```

Forge skills are not workflow graph nodes — do not invent `next_candidates`
beyond what the **prior content stage**'s handoff + pinned `workflow.yaml`
already resolved. Re-read that content-stage handoff to continue the
programme after this mutation.
