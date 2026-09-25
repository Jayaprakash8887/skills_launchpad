# Plan checks (P1–P16)

Governance detail: [governance.md](governance.md).

Before P1, verify the template's **Source freshness and command contract**
table. Any STALE source or MISSING required command fails the plan; do not run
P1–P16 against obsolete inputs.

| ID | Check |
|----|-------|
| P1 | Every product `REQ-*` in scope for this plan appears in §1; every wave that implements work cites those REQs via TASK **Implements** |
| P2 | Every in-scope `REQ-*` has ≥1 TASK; every TASK **Implements** ≥1 `REQ-*` (no shadow `REQ-W*`) |
| P3 | Every TASK has FILE paths or explicit "docs only" |
| P4 | Every TASK has objective exit evidence: (a) artifact/change under scope, (b) **observable** exit criteria (not “done/works”), (c) proving `command` or `review`, (d) **expected** result, (e) **evidence location** (`evidence_expected`). Same fields appear on the TASK row and in §9 `exit` |
| P5 | Test / verification layers are explicit: **unit**, **integration/contract** (when applicable), **smoke**, and **sandbox**. Unit/integration commands come from profile toolchain; smoke/sandbox are human-run live verify under `live_verify_dir`. **Integration** = exactly one named boundary/dependency exercised for real (or a contract test against both a fake and the real implementation) — not the whole stack; name the boundary, the word alone is not sufficient. Each acceptance criterion maps to a layer in the wave **Verification Coverage** table. **FAIL** if a wave changes product code and the Verification Coverage table has zero unit-layer rows, unless explicitly justified (docs-only / no logic change) — this is P15's live-verify floor mirrored in the opposite direction |
| P6 | No product scope beyond initiative spec |
| P7 | Feasibility blockers and accepted **operational risks** are addressed or explicitly deferred with owner + default-if-deferred; residual ops risk appears in RISK |
| P8 | Wave order and dependencies documented |
| P9 | As-built updates listed in same PR as code tasks: `Implementation-Status-{INIT}.md` (detail) + index row in `implementation-status.md`. **Not** satisfied by editing `tests/README.md` for live-verify coverage — that fact lives in the artifact's own marker (see P15) |
| P10 | Plan is self-contained (fresh agent can execute one wave); source digests/revisions and canonical check/test/verify/ground commands are populated; operational prerequisites for live verify (env class, safe data, cleanup/stop) are stated when live applies |
| P11 | **MDC conformance** — per `rules_glob`; discrepancies in TASK **MDC notes** and RISK table |
| P12 | **ADR conformance** — architectural TASKs cite Accepted ADR id from `{adr_dir}`; §0 "Resolved ADRs" links every TDD §4 `ADR_REQUIRED` file path with `Status: Accepted`; discrepancies in TASK **ADR notes** and RISK table. **FAIL** if any required ADR file is missing, still `Draft`, or only referenced from TDD §4 without a canonical `{adr_dir}` file. Do not add ADR promotion tasks — `/spec-technical-review` creates Draft files; PE acceptance happens before planning. |
| P13 | **Technical design reference** — §0 present; technical review path populated (the TDD file always exists once feasibility has run — see SKILL.md Inputs; "N/A" is only valid for the **ADR** row when zero `NEW-ADR` findings existed, never for the TDD path itself); PE sign-off status stated as `[x] complete — {date}` (not `[ ] required`) when TDD was produced; **FAIL** if TDD Status field in `Technical-Review-{initiative}.md` still reads `Draft`, or any required ADR file is not `Accepted`, or any cited Accepted ADR's `changes_user_visible_behavior` / `spec_amendment_required` field is `true` or missing, or the P13 lint re-check below fails. **Do not stop at the metadata fields** — they are self-declared by whoever accepted the ADR and can be wrong |
| P14 | **WorkManifest seed** — §9 present; wave IDs (`W0`, `W1`, …) match plan waves exactly; every TASK row has `codebase`, `spec_path`, `verify_command`, and **Implements `REQ-*`**; each wave has `tasks[]` + body task table with stable `TASK-*` ids; YAML is syntactically valid |
| P15 | **Co-ship capability/journey live prove** — if this wave's FILE list adds or materially changes a **product surface**, the same wave MUST include (a) ≥1 unit TEST/TASK and (b) live prove artifacts: ≥1 FILE under `live_verify_dir` **and** fixture pack path(s) under profile `fixtures_dir` (create/modify) for the **capability** (`CAP-*`) and/or **journey** (`J-*`) rung being shipped — extend existing artifacts when overlap exists. **Required overlap check:** before declaring a new FILE, run `scripts/verify_coverage_query.py --capability CAP-nn` / `--journey J-nn` / `--req` against `live_verify_dir` and record in the plan which existing artifacts were checked and, if none was extended, the specific reason a new FILE is warranted — **FAIL** if a new FILE is declared with no recorded overlap check. `verification.live.covers` MUST include the relevant `CAP-*` and/or `J-*` (plus `REQ-*` as needed). Prefer populating `dependencies`, `fixtures`, and `human_observations` when opaque. Wave `verify_command` / `verification.live` MUST be the **live** script entry (`smoke` or `sandbox`), not `{test_command}` / `make test`. **FAIL** if only unit ships, live is bare N/A when P15 applies, `verify_command` is unit-only, or covers lack CAP/J for the claimed live REQs. Agent = check+unit only; human runs prove at `wave-acceptance` (`wave-accepted` = ack including look-ats). Docs-only → `applicable: false` (**PASS**). Do **not** satisfy coverage-mapping by editing `tests/README.md` — see `.harness/references/live-verify-coverage-contract.md` and `live-fixture-contract.md` |
| P16 | **WorkManifest contract** — §9 validates via `scripts/workmanifest_contract.py` (`prayog/v1` + `WorkManifest`): stable IDs, same-wave dependency DAG (no missing/self/cycle), exact `files[]` path/action, exit criteria+proof, REQ mappings, wave order, and live-verification completeness (cleanup + stop when applicable). Reject `launchpad/v1` identity and mutable board/runtime fields. **PASS** requires the script to exit 0 on §9; a checklist tick without that run is not P16 |

## P13 lint invocation — source parity, not a bare re-run

For every cited Accepted ADR, re-run the lint **with the same source parity
T12 was supposed to have** — not a structure-only pass with zero sources:

```bash
python scripts/adr_boundary_lint.py <adr_file> --verify-lint-evidence \
  --source-text <req_text_reconstructed_from_spec> \
  --source-text <feasibility_evidence_reconstructed_from_report> \
  --approved-req-id <every approved REQ-* in the spec> \
  --require-sources
```

`--verify-lint-evidence` recomputes the digest recorded in the ADR's
`Lint evidence` row from the current file content + these sources and
compares it — a mismatch means the file changed since acceptance, or the
recorded hash was never genuinely computed, either way `FAIL`. A match
proves consistency at verification time; it does not retroactively prove
the original PE reviewer used correct sources.

Reconstruct the sources from the two **durable, still-available** canonical
artifacts — do not rely on a T12-time snapshot that may not exist. The two
sources are **not equally optional** — read them in this order and do not
let the second's absence excuse skipping the first:
1. `<req_text_reconstructed_from_spec>` — **always obtainable, always
   required.** Read the REQ row(s) named in the ADR's `product_constraints`
   field directly from the **initiative spec** (a required plan input; the
   spec cannot be absent at plan time — see P1). `--require-sources` is
   satisfied by this source alone if nothing else is available.
2. `<feasibility_evidence_reconstructed_from_report>` — **best-effort.**
   Read the "Spec quote" for the `NEW-ADR` finding named in the ADR's
   "Feasibility finding" (`FF-*`) field, directly from the **feasibility
   report** (a recommended, not required, plan input). If the report is
   genuinely unavailable (e.g. purged at a prior initiative closure), record
   that as a **Should-fix** note on this check, not a `FAIL` — but do not
   use its absence as a reason to also omit source 1.

**FAIL** on any lint violation, including a `--require-sources` failure from
supplying zero sources. This is required, not optional; `SKIPPED` only when
no Python runtime is available, with the reason stated.

## P12 / P13 failure → stage outcome

These checks FAIL when an authoritative artifact **exists** but shows an
unsatisfied gate (Draft ADR, unaccepted TDD, missing Accepted path). Map that
to workflow outcome **`blocked`** (not `failed`, not `needs-input`).

| Situation | Outcome |
|-----------|---------|
| Spec/TDD/feasibility path absent or unreadable | `needs-input` |
| TDD/ADR present but still Draft / not Accepted, or an Accepted ADR's product-boundary fields are `true`/missing (P12/P13 FAIL) | `blocked` |
| Digest/head/revision mismatch | `stale` |
| Plan render / WorkManifest contract validation fails (P16) or crashes on otherwise valid inputs | `failed` |
| Vague exit / missing proof / unit-as-live / missing live when P15 applies (P4/P15/P16) | `failed` |
| All P1–P16 PASS | `pass` |

## P15 examples (narrative)

| Scenario | Verdict |
|----------|---------|
| Wave adds an HTTP route; FILE list has unit tests only; `verify_command: make test` | **FAIL** — no `live_verify_dir` / fixtures; unit is not live |
| Wave adds a worker ingress; FILE list includes `tests/verify/verify_foo.py` + fixture under `tests/fixtures/…` + unit TEST; `covers: [CAP-01, REQ-…]`; `verify_command` points at that script | **PASS** |
| Wave adds a related surface; overlap check finds existing capability artifact; FILE list shows `action: modify` on that same file + fixture (marker grows to include new CAP/REQ) + unit TEST | **PASS** — extension, not duplication |
| Wave is docs-only / no new product surface; live `verify_command` N/A with reason | **PASS** (P15 does not apply) |
| Wave ships journey prove only with `covers: [J-02, …]` and journey fixture pack | **PASS** for journey rung — does **not** auto-prove capability rung |
