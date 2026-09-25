# Live smoke policy

Resolve paths from `.harness/profile.yaml` or [layout-defaults.md](layout-defaults.md).

Layer ownership for Pass-1 prove. There is **no** `/verify` content skill —
human smoke runs at checkpoint `wave-acceptance`. Content skills never apply
labels, commit, or merge (Forge / human / orch only).

Ladder SSOT: `.harness/references/quality-confidence-ladder.md`.
Fixture packs: `.harness/references/live-fixture-contract.md`.

## Layer ownership

| Layer | Who owns / runs | Location / evidence | Proves | Must not |
|-------|-----------------|---------------------|--------|----------|
| **Unit** | Agent (`/loop-spec`) | `unit_tests_dir` | Deterministic logic, branches, edge cases with mocked dependencies | Require a deployed/running stack; substitute for smoke/sandbox |
| **Integration / contract** | Agent or CI when the harness defines it | Contract/integration suite from `tests_readme` / profile | Cross-module wiring and interface shapes without full product UX | Duplicate unit-only assertions; substitute for live smoke/sandbox |
| **Capability prove** | Human at `wave-acceptance` | `live_verify_dir` + `fixtures_dir` (CAP pack) | **One** ability at ingress + **real** infra | Collapse into “all journeys”; unit-as-live; mock Postgres/Redis/Kafka |
| **Journey prove** | Human at `wave-acceptance` | `live_verify_dir` + `fixtures_dir` (J pack) | Multi-step orchestration across abilities | Treat as auto-proof of each CAP; log-only opaque pass |
| **Smoke / sandbox** | Human (checkpoint `wave-acceptance`) | Drivers under `live_verify_dir` | Critical path / env-dependent behavior with safe data | Leave fixtures/processes running; skip cleanup/stop; duplicate unit-only assertions |
| **Debug** | Exploratory | `debug_tests_dir` | Exploration and diagnosis | Gate Pass-1 or Pass-2 |

**Co-ship (P15):** when a wave adds or materially changes a product surface, the
same wave ships ≥1 unit TEST, ≥1 FILE under `live_verify_dir`, and fixture
pack path(s) under `fixtures_dir` for the **capability** (`CAP-*`) and/or
**journey** (`J-*`) rung being shipped. Agent implements; human executes at
`wave-acceptance`. WorkManifest `verification.live` (when applicable) declares
mode, command, `covers` (CAP/J/REQ), `dependencies`, `fixtures`, prerequisites,
expected observations, optional `human_observations`, cleanup, and stop
conditions. Observed results are human prove; the gate is checkpoint `pass` /
label `wave-accepted` (acks script + look-ats) — not a Live-Verify skill artifact.

**Opaque / cloud sinks:** use `human_observations` (`locus`, `expect`, `covers`).
Logs alone are **not** sole pass evidence.

**No overlap / forbid unit-as-live:** do not assert the same behavior in unit and
live smoke for the same feature. Wave `verify_command` /
`verification.live.command` must not be unit-only (`make test`, bare `pytest`,
`{test_command}`).

## Pass-1 gate

After `/loop-spec` + `wave-pr-action`, human-checkpoint `wave-acceptance`:

1. Run co-shipped `{verify_command}` with declared fixtures/deps (or accept P15 N/A).
2. Complete any listed look-ats (`human_observations`).
3. Signal accept with GitHub label `wave-accepted` on the tip (phase-1) —
   humans or Gateflow consume this; **content skills do not apply labels**.
4. `pass` = **human approved** for this wave tip (only approval signal) —
   including look-ats when declared.
5. Park at `wave-awaiting-closeout`; Pass-2 closeout closes the wave.

## Content / Forge boundary

Running the smoke script is verification tooling, not Forge. Skills never
commit, label, or merge. Tracker/PR publication is ForgeClient / human forge
skills / human GitHub only.
