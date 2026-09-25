# Feasibility checks (F1–F14)

Run every check. SKIPPED = missing input (state reason).

**PASS semantics (severity-aware):** PASS means **zero unresolved blocking
findings**. Informational observations (Verify / Gap) and accepted residual
risk with an explicit default may remain in the report as signals. Do **not**
require a literally empty findings list.

Governance detail: [governance.md](governance.md).

| ID | Check | Evidence required |
|----|-------|-------------------|
| F1 | **Baseline snapshot** | Current test layout, toolchain config, live verify script inventory (`live_verify_dir`), as-built state |
| F2 | **Spec → code map** | Each spec capability/wave maps to a module under `source_roots` or SKIPPED if N/A |
| F3 | **Spec → verify map** | Named live verify / fixture artifacts exist or are planned under `live_verify_dir` / `fixtures_dir`; coverage for claimed `CAP-*` / `J-*` / `REQ-*` per `scripts/verify_coverage_query.py` (or self-declared markers) — not `tests/README.md` rows alone |
| F4 | **Spec → unit map** | Planned unit areas vs existing `unit_tests_dir` |
| F5 | **As-built drift** | Spec claims vs the as-built index row for this capability; open `Implementation-Status-{INIT}.md` for a prior initiative when deeper detail is needed |
| F6 | **Docs drift** | `CLAUDE.md`, `rules_glob`, `adr_dir` index vs spec. `tests_readme` is a fixed pointer, not a source of per-capability truth — do not flag its row count as drift |
| F7 | **Overlap risk** | Same user journey in unit and live smoke for same capability |
| F8 | **CI vs live boundary** | What runs in CI vs closure/live verify per spec and tests_readme |
| F9 | **Cross-service touch** | Integration specs / contracts referenced and files exist |
| F10 | **Assumptions** | Spec asserts facts not evidenced in repo |
| F11 | **Effort drivers** | Per wave: complexity drivers (not hour estimates) |
| F12 | **PM questions** | All blocking gaps have a numbered question |
| F13 | **ADR conformance** | Relevant Accepted ADRs cited; spec does not contradict ADR; `NEW-ADR` flagged when initiative needs an undocumented decision; the row's **Code evidence** column names the specific module/file this F1/F2 pass actually found relevant — not blank when something was found |
| F14 | **MDC conformance** | Spec wording does not conflict with `rules_glob` patterns; discrepancies listed in findings |

Severity: **Critical** (blocks progress — unresolved → blocking finding),
**Should fix** (blocking for PE-lane engineering unless explicitly deferred with
default), **Verify**, **Gap** (informational — report signals only).

**Critical** for F13 when spec contradicts an Accepted ADR.

Blocking findings select workflow outcome via the lane-to-outcome rubric in
`SKILL.md` (PE/ADR → `findings`; PM/domain → `needs-input`; gate → `blocked`).
