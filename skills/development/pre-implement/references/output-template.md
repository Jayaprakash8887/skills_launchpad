## Pre-implement — {REPO} / {WAVE} — {SLICE TITLE}

| Field | Value |
|-------|-------|
| Artifact | `{reports_dir}/Pre-Implement-{INIT}-W{N}.md` |
| Initiative | {INIT} |
| Wave | W{N} |
| Date | {YYYY-MM-DD} |
| Outcome | `pass` / `needs-input` / `blocked` / `stale` / `failed` |
| Outcome reason | {one sentence} |
| Wave head context | Bound by Forge/human context: `{branch or ref}` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [ ] ok / blocked / unbound |
| Spec PR merged | Implementation plan on integration branch | [ ] yes / no |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [ ] verified / missing |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [ ] seeded / partial / missing |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [ ] pass / fail |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [ ] complete / missing |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` + fixtures under `fixtures_dir`; `covers` include `CAP-*` and/or `J-*`; deps/preflight; look-ats when opaque | [ ] contract / N/A / missing |
| Prove rungs (`CAP-*` / `J-*`) | Listed ids match plan/manifest live covers | [ ] listed / N/A / missing |
| Fixture packs | Paths under `fixtures_dir` present in FILE list / `fixtures[]` | [ ] path / N/A / missing |
| Human look-ats | `human_observations` when opaque; else N/A | [ ] listed / N/A / missing |
| Plan source freshness | all upstream rows `CURRENT` | [ ] current / stale |
| Impact-map repo scope | revision and scope digest match canonical handoff | [ ] match / stale |
| `check_command` | resolved | [ ] command / missing |
| `test_command` | resolved | [ ] command / missing |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [ ] command / N/A / missing |
| `ground_command` | resolved or N/A with reason | [ ] command / N/A / missing |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE under `live_verify_dir` + pack under `fixtures_dir`; covers CAP/J | [ ] path / N/A (no surface) / missing |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [ ] {wave id} = {status} |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [ ] exists / missing |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [ ] complete / pending |

**Gate verdict:** PASS / BLOCKED — {reason if blocked}

**Forge readiness (when seed / wave head absent):** fill `handoff.forge` /
recommend `/create-board-tickets` or wave-head binding — do **not** mutate.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-{SPEC}-W{N-1}.md §Contracts produced`.
> For each contract this slice depends on, confirm the actual built interface
> matches what this wave's spec assumes.
> Scan `source_roots` to confirm — do not rely on spec text alone.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| {what this wave assumes} | {module/component — entry point name} | {accepts} | {returns/emits} | Ground-Report-W{N-1} | [ ] yes / NO — drift detail |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- {list any contracts this wave needs that have no Ground Report backing}
  → Flag as risk before coding; wave head remains bound by Forge/human context.

---

### Must read

- [ ] `CLAUDE.md`
- [ ] MDC rules (domain-filtered — list files read for this slice's domains):
  - [ ] {rule file} — {domain it covers}
- [ ] ADRs (keyword-matched — list ids):
  - [ ] ADR-{N} — {what it governs for this slice}
- [ ] Spec: {path to product spec for this wave}
- [ ] Plan wave section / §9 WorkManifest: `reports/Implementation-Plan-{initiative}.md` W{N}
- [ ] Board wave issue: {URL} — TASK list (projected from WorkManifest; not a second authority):
  - [ ] TASK-W{N}-01 — implements REQ-… — depends_on: […] — files: […] — exit proof: …
  - [ ] TASK-W{N}-02 — …

---

### Governance alignment

- [ ] Slice spec does not contradict any listed ADR
- [ ] Plan TASK MDC notes and ADR notes for this wave reviewed
- [ ] Every initiative ADR cited for this wave is **Accepted** in `{adr_dir}`
  (created during `/spec-technical-review`, not promoted during planning)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — {path + section}
- [ ] `as-built/implementation-status.md` — verification row for this wave
- [ ] `tests_readme` — feature map row if verification coverage changes
- [ ] Unit verification scope — edges and boundary behaviour (mocked dependencies)
- [ ] Live verification — co-shipped script under `live_verify_dir` + fixture pack under `fixtures_dir` (`CAP-*` / `J-*`); human-run + look-ats at `wave-acceptance`
- [ ] ADR — update when this wave supersedes an Accepted ADR (requires PE review)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without
  first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts
- [ ] Assume a contract from a prior wave is correct without checking the
  Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board
  issues from this skill

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, or equivalent repository checks | `{check_command}` |
| Unit | Module logic, boundary behaviour, edge cases (no external I/O) | `{test_command}` |
| Live verify | Capability and/or journey prove on **real** infra (human-run at `wave-acceptance`) | `{verify_command}` + fixtures; covers CAP/J; look-ats when opaque |
| Ground check | Assigned wave REQs satisfied; boundaries respected | `{ground_command}` or N/A — reason |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate.
> Agent implements the script in `/loop-spec`; does **not** run it as success.
> Policy: [live-smoke-policy.md](live-smoke-policy.md).

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Run the documented `{verify_command}` (co-shipped script) in the sandbox,
  or accept P15 N/A
- [ ] Experience / inspect the feature to the depth env access allows
- [ ] Signal accept with GitHub label `wave-accepted` on the tip (phase-1) —
  content skills do **not** apply labels; that `pass` is **human approved**
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: {initiative id}
- Issue: #{board issue — from seed-work output}
- Spec path: {docs/specification/product/…}
- Verify command (human): {live script from plan / board — not make test}
- ADRs in scope: {ids}
- Wave head: bound by Forge/human context — {ref}

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — {reason} |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-{INIT}-W{N}.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

{document dependency order or N/A}
