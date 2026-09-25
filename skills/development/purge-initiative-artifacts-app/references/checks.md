# Purge app checks (A1–A6)

| ID | Check | Evidence |
|----|-------|----------|
| A1 | Initiative id resolved | `INIT-*` present |
| A2 | Allowlist only | Every deleted path ∈ app PURGE set for this INIT |
| A3 | KEEP refused | No product INIT, Accepted ADR, source/test/verify script, fixture pack under `fixtures_dir`, as-built index, or `Implementation-Status-{INIT}.md` deleted |
| A4 | Idempotent | Missing allowlisted files recorded as `missing_ok` in signals |
| A5 | No reports artifact | No `Purge-*.md` (or other new file) written under `reports_dir` |
| A6 | Handoff | Envelope stage `purge-initiative-artifacts-app`; `artifact.path` null; signals list paths |

Blocking: A2, A3, A5. A1 missing → `needs-input`.
