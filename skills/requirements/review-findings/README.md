# review-findings

Interactive workshop for validation / audit reports. **Collect decisions only**
— does not edit the PRD. Writes canonical
`prd/reports/Resolution-{INIT}.md` (overwrite; no `*-revN` siblings).

Findings use stable `VF-*` ids; decisions become `CHG-*` linked to those ids.
See `.harness/references/id-conventions.md` and `.harness/references/artifact-write-contract.md`.

**Original author:** rushikeshpol02 (ai-skills). **Maintainer:** drivestream-lab.

## Invoke

```
/review-findings prd/reports/Validation-Report-INIT-PRAYOG-001.md
```

Run after `validate-requirements`. Pair with `update-documents`, then re-run
validation in incremental mode against the **same** Validation-Report path.

See repo root README for install command.
