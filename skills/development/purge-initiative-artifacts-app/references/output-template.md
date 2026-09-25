# Output template — purge initiative artifacts (app)

**No durable report file.** Do not write under `{reports_dir}`.

Chat may show a short summary of deleted / missing_ok / refused paths.

Emit handoff only (and overwrite `handoff_path` when bound):

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: purge-initiative-artifacts-app
  outcome: pass
  artifact:
    path: null
    digest: null
  blockers: []
  signals:
    lane: eng
    initiative: {INIT}
    deleted:
      - {path}
    missing_ok:
      - {path}
    refused:
      - {path}
    deleted_count: {n}
    missing_ok_count: {n}
    refused_count: {n}
    pr_body: |
      Initiative closure — app/eng purge for {INIT}.
      Deleted: {list or none}
      Missing (ok): {list or none}
      Refused (KEEP): {list or none}
  next_candidates:
    # from pinned workflow.yaml for (stage, outcome) — do not hardcode
    - {next_from_pin}
  human_checkpoint: false
  external_action: true   # when pin next is external-action
  forge:
    action: open_draft_pr
    draft: true
    apply_labels: []
    title: "Initiative closure purge (app): {INIT}"
    # body_path: ephemeral file outside reports_dir from signals.pr_body
    body_path: {ephemeral_or_runner_supplied}
```
