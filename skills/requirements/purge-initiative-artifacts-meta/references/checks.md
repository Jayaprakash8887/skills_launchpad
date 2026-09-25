# Purge meta checks (M1–M6)

| ID | Check | Evidence |
|----|-------|----------|
| M1 | Initiative id resolved | `INIT-*` present |
| M2 | Allowlist only | Deletes ⊆ Validation-Report / Resolution for this INIT |
| M3 | KEEP refused | No PRD or Impact-Map deleted |
| M4 | Idempotent | Missing allowlisted files → `missing_ok` in signals |
| M5 | No reports artifact | No `Purge-*.md` (or other new file) written under `reports_dir` |
| M6 | Handoff | Envelope stage `purge-initiative-artifacts-meta`; `artifact.path` null; signals list paths |

Blocking: M2, M3, M5.
