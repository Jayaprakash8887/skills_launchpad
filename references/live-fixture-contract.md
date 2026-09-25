# Live fixture contract (SSOT)

What a capability or journey **fixture pack** must contain so live prove is
stimulus + observe, not a bare health curl.

Layout roots come from the consumer profile:

| Key | Default | Role |
|-----|---------|------|
| `fixtures_dir` | `tests/fixtures` | Stimulus + expected packs |
| `live_verify_dir` | `tests/verify` | Drivers that apply fixtures and probe |
| `unit_tests_dir` | (profile) | Mocks only — not this contract |

See [quality-confidence-ladder.md](quality-confidence-ladder.md),
[workmanifest-contract.md](workmanifest-contract.md).

## Pack kinds

| Kind | Directory hint | `covers` must include | Stimulus |
|------|----------------|----------------------|----------|
| **Capability** | `{fixtures_dir}/cap-{nn}-…/` or named by CAP | ≥1 `CAP-*` | Minimal ingress hit for one ability |
| **Journey** | `{fixtures_dir}/j-{nn}-…/` or named by J | ≥1 `J-*` | Ordered multi-step stimulus |

Both may also list related `REQ-*` on the marker / WM `covers`.

## Required contents (per pack)

| Piece | Required | Notes |
|-------|----------|-------|
| **Stimulus** | Yes | Payload(s), messages, HTTP bodies, UI seed — enough to trigger the black box |
| **Expected SoT** | Yes* | Declarative expected rows/topics/responses **or** pointer that expected is human-only |
| **Cleanup** | Yes | How to remove safe test data / drain keys |
| **Deps list** | Yes (in WM or pack README) | Infra the preflight must check (postgres, kafka, …) |

\*When expected is opaque: pack documents **look-ats** and WM carries
`human_observations[]` — do not invent log greps as Expected SoT.

## Driver (`live_verify_dir`)

The verify script/runbook:

1. Runs or assumes preflight for declared deps.
2. Applies the fixture stimulus at the **ingress**.
3. Probes owned SoT **or** prints the human look-at list and exits for human.
4. Self-declares `prayog:covers: …` per [live-verify-coverage-contract.md](live-verify-coverage-contract.md).
5. Exits 0 only for scriptable success — never 0 solely because a log line matched.

## WorkManifest linkage

When `verification.live.applicable: true` (P15 / validator fail-closed):

- `covers` lists ≥1 `CAP-{nn}` and/or `J-{nn}` (and `REQ-*` as needed).
- `fixtures` lists non-empty repo-relative paths under `fixtures_dir`
  (**required** — enforced by `workmanifest_contract.py`).
- `dependencies` lists infra names/topics the preflight must see (optional
  field; when present must be non-empty).
- `human_observations` when any covered outcome is opaque.

## Non-goals

Not unit fixtures under `unit_tests_dir`. Not replacing real infra with mocks
for capability/journey. Not a `/verify` auto-pass skill.
