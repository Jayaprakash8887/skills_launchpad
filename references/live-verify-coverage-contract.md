# Live-verify coverage contract (SSOT)

What a `live_verify_dir` artifact must self-declare so its `CAP-*` / `J-*` /
`REQ-*` coverage survives after the `PURGE` plan that co-shipped it is gone,
and how planners check for reuse before writing a new artifact.

See also: [artifact-write-contract.md](artifact-write-contract.md),
[workmanifest-contract.md](workmanifest-contract.md),
[live-fixture-contract.md](live-fixture-contract.md),
[id-conventions.md](id-conventions.md),
[quality-confidence-ladder.md](quality-confidence-ladder.md).

## Why this exists

`verification.live.covers` in the WorkManifest is the only place a wave's live
coverage is declared today, and the WorkManifest lives in
`Implementation-Plan-{INIT}.md` — `PURGE` at initiative closure. Once purged,
nothing durable says what a given script or runbook actually verifies.

## The marker

One line, anywhere in the artifact's first ~20 lines:

```text
prayog:covers: CAP-01, J-01, REQ-01
```

Ids may be any mix of `CAP-{nn}`, `J-{nn}`, and `REQ-*`. Capability-rung
drivers should include ≥1 `CAP-*`; journey-rung drivers ≥1 `J-*`.

**Deliberately not a code-comment-specific format.** Plain text substring —
works in Python `#`, `//`, HTML comments, or visible markdown lines.

The artifact itself is `KEEP` (product source / unit tests / live-verify
**scripts** / **fixture packs**). The marker inherits that automatically.

## Resolution — via `files[]`, never by parsing `command`

Resolve via TASK `files[]` under `live_verify_dir` and/or `fixtures_dir`.

## Overlap check (P15)

Before a plan declares a new live/fixture FILE, run
`scripts/verify_coverage_query.py` with `--capability CAP-01`, `--journey J-01`,
or `--req REQ-01` and record overlap or why a new FILE is warranted.

## Query tool

```bash
python scripts/verify_coverage_query.py <live_verify_dir> --req REQ-01
python scripts/verify_coverage_query.py <live_verify_dir> --capability CAP-01
python scripts/verify_coverage_query.py <live_verify_dir> --journey J-01
python scripts/verify_coverage_query.py <live_verify_dir> --wave "INIT-X:W3"
python scripts/verify_coverage_query.py <live_verify_dir> --dump
```

`--req`, `--capability` (when value looks like `CAP-*`), and `--journey`
(`J-*`) match the marker. Other `--capability` / `--wave` strings still use
path/content keyword match for legacy queries.

## Cross-check at plan time

`workmanifest_contract.py` compares `live.covers` to marker ids when
`base_path` is supplied. Unmarked legacy artifacts are not an error.

## Non-goals

Not retrofitting all existing artifacts in one pass. New/extended artifacts
comply going forward.
