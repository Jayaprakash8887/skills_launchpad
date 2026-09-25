# update-documents

Propagates approved corrections across related documents.

- **Resolution mode:** consumes canonical `Resolution-{INIT}.md`, applies
  `CHG-*` rows linked to `VF-*`, presents a change manifest for approval.
- **Ad-hoc mode:** user-supplied change set (still uses `CHG-*` ids).

Does not invent product decisions — route ambiguity back to `review-findings`.

Typical input: `prd/reports/Resolution-INIT-PRAYOG-001.md`.

After PRD edits, re-run `/validate-requirements` incremental against
`prd/reports/Validation-Report-{INIT}.md` (same path).

See `.harness/references/id-conventions.md` and `.harness/references/artifact-write-contract.md`.
