# Output template — ground report

Save to `{reports_dir}/Ground-Report-{SPEC}-W{N}.md`
([`.harness/references/artifact-write-contract.md`](.harness/references/artifact-write-contract.md)).

Run checks G1–G10 per [checks.md](checks.md). Findings use **`GF-*`**.

```markdown
# Ground report — {SPEC} W{N}

| Field | Value |
|-------|-------|
| Wave | W{N} — {wave title} |
| Spec | {SPEC_PATH} |
| Initiative | {INIT} |
| Date | {YYYY-MM-DD} |
| Wave head (exact) | `{branch or ref}` @ `{sha}` — reviewed head for sign-off |
| PR URL (if any) | {url or n/a} — read-only context |
| Status | Draft |
| Review deadline | {YYYY-MM-DD + 2 business days} |
| Deciders | Tech lead / reviewer: {name} — explicit LGTM required |
| Outcome | pass / findings / needs-input / blocked / failed |
| Outcome reason | {one sentence} |
| Assigned REQs | {REQ list from plan / WorkManifest wave TASK implements — not full future spec} |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `{test_command}` / Wave-Execution proof | … |
| Ground | `{ground_command}` or manual source+tests scan | … |
| Accept | `wave-accepted` on tip / wave-acceptance (script + CAP/J look-ats when declared; optional/legacy Live-Verify-* only) | … |

## Automated ground check output
(paste full output of `{ground_command}` when defined)

## REQ checklist (wave-assigned only)
| REQ | Spec claim | Verified artifact | CAP/J covers | Look-ats | Status |
|-----|-----------|-------------------|--------------|----------|--------|
| REQ-{nn} | {claim} | {entry point / test / verify + fixture} | CAP-… / J-… / N/A | locus→expect / N/A | pass / fail / partial |

## Boundary checks
(Derived from domain-filtered ADRs and MDC rules for this repo — G5/G6.)
| Rule | Source | Status |
|------|--------|--------|

## Cross-spec contracts consumed
(What this wave assumed from prior waves — confirm each still matches.)
| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| {entry point / schema / command} | Ground-Report-W{N-1} | yes / NO — drift |

## Discrepancies (must fix before human checkpoint)
| ID | REQ | Finding | Severity |
|----|-----|---------|---------|
| GF-{nn} | REQ-{nn} | | |

## Learning cited
(From Learning-Extract-{INIT}-W{N}.md when present — cite only.)
| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| L-01 | … | … |

## Contracts produced by this wave
(REQUIRED — this section is the input for /pre-implement of the next wave.
Describe in engineering terms: module, entry point name, input shape,
output shape, invariants. Do NOT use language-specific syntax.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| {name} | {module} | {callable/command/endpoint} | {accepts} | {returns/emits} | {guarantees} | W{N+1} |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge
> readiness for publication. Do **not** commit, push, merge, or apply labels
> from this skill. Human approved was `wave-acceptance`. At `wave-signoff`
> the human merges/publishes the **exact wave head** only.

- PR URL / wave head: {url} @ `{sha}` — **expected reviewed head SHA**
- Ground Report path: `{reports_dir}/Ground-Report-{SPEC}-W{N}.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `{reports_dir}/Wave-Execution-{INIT}-W{N}.md`
- Optional/legacy Live-Verify path: `{reports_dir}/Live-Verify-{INIT}-W{N}.md` (not required)
- As-built: W{N} `human_approved` from wave-acceptance (do not re-mark here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)
- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (do not re-mark)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?
yes / no — reason
```

Append handoff envelope (stage `ground-spec`) per
`.harness/references/handoff-envelope.md`.
