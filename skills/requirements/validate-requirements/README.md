# validate-requirements

Semantic + structural review of requirements / PRD documents. **Flag only** —
does not edit source docs.

Writes the **canonical** report
`prd/reports/Validation-Report-{INIT}.md` (overwrite; bump `report_revision`;
no `*-revN` siblings). Findings use stable **`VF-*`** ids.

See `.harness/references/id-conventions.md` and `.harness/references/artifact-write-contract.md`.

## Invoke

```
/validate-requirements prd/INIT-PRAYOG-001.md
```

After fixes, re-run incremental mode against the **same** Validation-Report path.
Next: `/review-findings` → `/update-documents`.
