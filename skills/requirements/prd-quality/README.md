# /prd-quality

```text
/prd-quality
```

Pass **two or more** PRD paths (required). Example after two `/prd-think`
runs:

- `{reports_dir}/{INIT}-prd-think.md`
- `{reports_dir}/{INIT}-prd-think-2.md`

Writes (overwrite the report only):

- `{reports_dir}/{INIT}-prd-quality.md`

Scores each file **blind** against the delivery bar (B1–B15), including
material **B14** (CAP↔journey) and **B15** (live Evidence cites `CAP-*`
and/or `J-*`).

**Handover** (per file): `yes` = zero material FAILs → that named file
may be promoted, then validate. `no` = think again (`-3.md`, `-4.md`, …).
`Ci-wins` is rank only, not the validate signal.

`/prd-critic` is optional secondary. Does not edit the PRDs.
