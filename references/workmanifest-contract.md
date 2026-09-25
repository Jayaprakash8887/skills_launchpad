# WorkManifest contract (`prayog/v1`)

Canonical, walker-neutral **approved execution intent** for an initiative.
Prayog owns this contract. Launchpad materializes the pinned harness only — it
does **not** define, parse, or execute WorkManifest. Humans (`/create-board-tickets`)
and Gateflow (BoardService / ForgeClient) **project** epic/wave summaries onto
the board; they do not become a second authority.

| Property | Rule |
|----------|------|
| Identity | `apiVersion: prayog/v1` + `kind: WorkManifest` |
| Nature | **Immutable** after coding-readiness approval of the plan package |
| Walk-time carrier | §9 YAML inside `Implementation-Plan-{INIT}.md` (PURGE at initiative closure) |
| Long-term home | Programme **board** issues after seed — not the plan file forever |
| Not in manifest | Board runtime status, observed evidence, mutable checkpoint fields |
| Walkers | Same task contract for human or Gateflow; legality comes from workflow dispatch/checkpoints — not a duplicated executor field on tasks |
| Deferred (not v1) | `parallel_safe`, `shared_files`, task-level concurrency / resource locks |

Normative producer: `/spec-implementation-plan` §9. Normative validator:
`scripts/workmanifest_contract.py`. Plan check **P16** requires a clean pass.
After `/create-board-tickets` (or Gateflow board create), **board projection** is
the long-term WorkManifest identity. `/pre-implement` spends against **board
wave + product-spec durable citations** (H1–H4 / G*), not “plan file digest
forever.” The plan path may be removed by `/purge-initiative-artifacts-app` at
initiative closure — see [artifact-write-contract.md](artifact-write-contract.md).

---

## Document shape

```yaml
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-{COMPONENT}-{NUMBER}
metadata:
  title: …
  summary: |
    …
  playbook:
    - {SPEC_PATH}   # durable product spec (KEEP) — prefer over plan path
    # Implementation-Plan-{INIT}.md is walk-time only (may be purged at closure)

# Projection hints for board seed (not runtime status)
target:
  org: {github-org}
  project: {programme board name from governance}

defaults:
  initiative: INIT-{COMPONENT}-{NUMBER}
  parent: EPIC
  labels:
    - {initiative-label}

epic:
  id: EPIC
  repo: {repo}
  title: "…"
  codebase: {repo}
  spec_path: {SPEC_PATH}
  verify_command: {live script or N/A — reason}
  body: |
    …

work:
  - id: W0
    kind: issue
    repo: {repo}
    title: "…"
    depends_on: []          # prior wave ids only (W0, W1, …)
    codebase: {repo}
    spec_path: {SPEC_PATH}
    verify_command: {live script under live_verify_dir, or N/A — reason}
    tasks: [ … ]            # see Task object
    verification: { … }     # see Wave verification
    body: |
      …
```

**Forbidden on the approved manifest:** `status`, `state`, board column ids,
`observed`, `evidence_actual`, build SHA / runtime head bindings filled at
checkpoint time, and any other mutable execution field. Those live in board
systems and stage artifacts (`Wave-Execution-*`, handoff, human
`wave-acceptance` / `wave-accepted`). Optional/legacy `Live-Verify-*` prose is
not required.

---

## Stable ids

| Field | Pattern | Notes |
|-------|---------|-------|
| Wave `id` | `W{n}` (`W0`, `W1`, …) | Contiguous from 0; one work entry per wave |
| Task `id` | `TASK-W{n}-{nn}` | `{n}` must match containing wave; `{nn}` zero-padded |
| Product req | `REQ-{nn}` (or programme `REQ-*`) | No shadow `REQ-W*` |
| Epic `id` | `EPIC` | Single epic per manifest |

Cross-wave `depends_on` lists **wave** ids. Task `depends_on` lists **task**
ids **within the same wave only**.

---

## Task object

```yaml
- id: TASK-W0-01
  implements: [REQ-01, REQ-02]
  depends_on: []                 # same-wave TASK-* only
  files:
    - path: src/service/foo.py   # repo-relative exact literal (no * / ?, no abs, no ../)
      action: create             # create | modify | delete | inspect
  exit:
    criteria:
      - "GET /health returns 200 with {\"ok\": true} on local stack"
    proof:
      kind: command              # command | review
      command: "make check && pytest tests/unit/test_foo.py -q"
      # review: "PE reviews ADR-012 diff against REQ-01"  # when kind: review
      expected: "exit 0; health assertion green"
      evidence_expected: "Wave-Execution-{INIT}-W0.md § TASK-W0-01"
```

| Field | Rule |
|-------|------|
| `implements` | Non-empty list of product `REQ-*`. Every in-scope REQ maps to ≥1 TASK. |
| `depends_on` | Same-wave `TASK-*` only. No missing targets, no self-reference, no cycles. |
| `files` | Non-empty unless the TASK is explicitly docs-only with `files: []` **and** exit criteria state docs-only. Each `path` is a repo-relative exact literal (no `*` / `?`, no abs, no `../`); `action ∈ {create, modify, delete, inspect}`. |
| `exit.criteria` | Non-empty list of **observable engineering results** (not “done”, “works”, or “implemented”). |
| `exit.proof.kind` | `command` (requires `command`) or `review` (requires `review`). |
| `exit.proof.expected` | Non-empty expected result of the proving step. |
| `exit.proof.evidence_expected` | Where proof will be recorded (artifact path / section). Not the observed result. |

Do **not** put `parallel_safe` or `shared_files` on tasks in v1.

Consumers MUST pass `files[].path` to direct path APIs as a literal and MUST
NOT apply shell, glob, or wildcard expansion. `*` and `?` are forbidden.
Bracketed segments are ordinary path characters, not globs.

---

## Wave verification

Every wave declares agent-run layers plus a live-verification intent block.
Actual build SHA and observed evidence are bound at human checkpoint
`wave-acceptance`, not during planning. `evidence_expected` records where
human prove will be attested (typically `wave-accepted on tip` / human
wave-acceptance) — optional/legacy `Live-Verify-*` paths are not required.

```yaml
verification:
  check: "{check_command}"
  unit: "{test_command}"
  live:
    applicable: true
    mode: smoke                 # smoke | sandbox when applicable
    command: "python tests/verify/verify_foo.py"
    covers: [CAP-01, J-01, REQ-01]   # ≥1 CAP-{nn} and/or J-{nn} required when applicable
    dependencies:                    # optional; when present must be non-empty
      - postgres
      - redis
    fixtures:                        # required when live.applicable: true
      - tests/fixtures/cap-01-health/stimulus.json
    prerequisites:
      - "Stack up via docker compose"
    safe_test_data:
      - "synthetic tenant id TENANT-SMOKE-01"
    steps:
      - "Run verify_foo.py against local stack"
    expected_observations:
      - "Script exits 0; prints PASS for /v1/foo"
    human_observations:              # when opaque sinks; empty/omit if fully scriptable
      - locus: "Cloud console → tenant TENANT-SMOKE-01 → deployments"
        expect: "Revision visible"
        covers: [CAP-01]
    evidence_expected: "wave-accepted on tip"
    cleanup:
      - "Remove TENANT-SMOKE-01"
    stop_conditions:
      - "Any non-zero exit or unexpected 5xx → stop; do not proceed to Pass-2"
```

When live verify does **not** apply (docs-only / no new product surface):

```yaml
verification:
  check: "{check_command}"
  unit: "{test_command}"
  live:
    applicable: false
    reason: "Docs-only wave — no new/changed product surface (P15 N/A)"
```

| Rule | Fail closed when |
|------|------------------|
| Unit-as-live | `live.applicable: true` but `command` is unit-only (`make test`, bare `pytest`, `{test_command}`, etc.) |
| Missing live | P15 applies (new/material product surface) and live is bare N/A / missing / `applicable: false` without valid reason |
| Incomplete live | `applicable: true` and any of `mode`, `command`, `covers`, `prerequisites`, `expected_observations`, `cleanup`, `stop_conditions`, **`fixtures`** is missing or empty |
| Covers ids | Any `covers` entry not matching `CAP-{nn}`, `J-{nn}`, or `REQ-*` (exactly two digits for CAP/J; no shadow `REQ-W*`; reject `J1` / `J-1` / `CAP-1`) |
| Prove rung | `applicable: true` and `covers` has **no** `CAP-{nn}` and **no** `J-{nn}` (REQ-only covers fail) |
| Mode | `mode` not in `smoke` \| `sandbox` when applicable |
| Optional lists | `dependencies` present but empty or non-string; `human_observations` present but missing `locus`/`expect`/`covers` |
| Log-only sole evidence | Every `expected_observations` entry is log/stdout/grep-shaped **and** `human_observations` absent/empty **and** `fixtures` absent/empty |

`dependencies` and `human_observations` remain optional. **`fixtures` is required**
whenever `live.applicable: true`. Populate per
[live-fixture-contract.md](live-fixture-contract.md) and
[quality-confidence-ladder.md](quality-confidence-ladder.md) — plan P15 and this
validator both enforce the prove floor.

Wave-level `verify_command` MUST equal `verification.live.command` when
applicable, or an explicit `N/A — {reason}` matching `live.reason` when not.

See also: [live-fixture-contract.md](live-fixture-contract.md).

---

## Wave ordering

- `work[].id` values are exactly `W0`…`W{n}` with no gaps.
- Wave `depends_on` may list only earlier wave ids (e.g. `W1` → `[W0]`).
- Task dependency DAGs are per-wave and independent across waves.

---

## Parsing and validation

1. Extract the fenced `yaml` block under plan §9 (`## 9. WorkManifest seed`),
   or accept a standalone YAML document.
2. Run `scripts/workmanifest_contract.py` (CLI or `validate_workmanifest`).
3. Fail closed on any structured error — do not seed the board or open
   coding-readiness on a failing manifest.

```bash
python scripts/workmanifest_contract.py path/to/Implementation-Plan-INIT.md
python scripts/workmanifest_contract.py path/to/manifest.yaml
```

Import:

```python
from scripts.workmanifest_contract import validate_workmanifest, extract_workmanifest_yaml

errors = validate_workmanifest(text_or_mapping)
# → list[{"code": str, "message": str, "path": str}]
```

---

## Versioning

| Change | Action |
|--------|--------|
| Additive field that **raises** the prove floor (`fixtures` required; CAP/J in covers) | Document in CHANGELOG as a **breaking** pin bump for re-validation of old live waves; keep `apiVersion: prayog/v1` |
| Breaking field rename/removal or semantic change | Bump `apiVersion` (e.g. `prayog/v2`) and reject older pins fail-closed |

Unsupported `apiVersion` / `kind` pairs MUST be rejected by Gateflow and by the
shared validator before remounting a pin that expects this contract.
