# /prd-think

```text
/prd-think
```

Brief + `INIT-*` (ask if missing).

Writes the next free candidate (never overwrites an earlier run):

- `{reports_dir}/{INIT}-prd-think.md` — run 1
- `{reports_dir}/{INIT}-prd-think-2.md` — run 2
- `{reports_dir}/{INIT}-prd-think-N.md` — run N

`reports_dir` from profile / artifact-write-contract (meta default
`prd/reports/`).

Ids from `.harness/references/id-conventions.md` only.

Does not score. After two candidates exist:

```text
/prd-quality
```

Pass both file paths. Does not overwrite `prd/{INIT}.md` unless you
authorize promote of a named file.
