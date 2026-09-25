# Board seed checks (B1–B8)

| ID | Check | Blocking |
|----|-------|----------|
| B1 | Integration branch checked out; not open `chore/*-spec-*` branch | yes |
| B2 | Merged `Implementation-Plan-{initiative}.md` exists on integration branch | yes |
| B3 | §9 WorkManifest YAML parses as `prayog/v1` `WorkManifest`; `scripts/workmanifest_contract.py` / `validate_workmanifest` returns **`workmanifest-contract-pass`**; `epic` + `work[]` waves `W0..Wn` present; each wave has `tasks[]` with `TASK-*`, `implements` REQ refs, `depends_on`, exit criteria/proof, and verification | yes |
| B4 | Governance `project_board.enabled` and `name` resolved (meta read-only) | yes |
| B5 | `target.project` in §9 matches governance `project_board.name` when both set | yes |
| B6 | `gh auth status` succeeds when execution requested | yes for apply |
| B7 | EPIC exists or create plan defined; all waves parent-linked or create plan defined; seeded wave bodies retain TASK ids, REQ mappings, dependencies, exit criteria, and proof summary projected from the WorkManifest (board text is not a second authority) | yes for pass |
| B8 | All seeded issues on programme Project (`--project` or verified) | warn pilot; block later |

## Verdict

- **PASS (seeded / already-seeded):** B1–B7 pass; tree complete for all waves in §9.
- **BLOCKED:** auth, board access, or partial seed.
- **FAIL:** missing plan, governance, invalid §9, or WorkManifest contract failure.
