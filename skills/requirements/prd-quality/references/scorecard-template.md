# {INIT}-prd-quality

| Field | Value |
|-------|-------|
| Initiative | {INIT} |
| Date | {YYYY-MM-DD} |
| Files | C1 `{path}` / C2 `{path}` / C3 `{path}` / … |
| Brief | {path or "not supplied"} |
| Companions | prd-critic / none |
| **Handover** | C1: yes\|no; C2: yes\|no; … |
| Rank | C1-wins / C2-wins / tie — **not** the validate signal |

## Handover

`yes` = zero material FAILs on that file → may promote **that named
file**, then `/validate-requirements`. `no` = keep looping `/prd-think`.

| File | Material FAILs | Handover | Blocking bars |
|------|----------------|----------|---------------|
| C1 `{filename}` | {n} | yes / no | |
| C2 `{filename}` | {n} | yes / no | |
| C3 `{filename}` | {n} | yes / no | |

If two or more are `yes` and the jobs disagree, do not auto-pick. Human
names the file.

## Independent scores

One subsection per file. Written **before** the comparison table.

### C{n} `{filename}`

Material FAIL count: {n}
Handover: yes / no

| Bar | Result | Material FAIL? | Evidence (id + quote) |
|-----|--------|----------------|------------------------|
| B1 Job | PASS / FAIL / N/A | | |
| B2 CAP→REQ | | | |
| B3 Observable | | | |
| B4 Negative paths | | | |
| B5 Actors | | | |
| B6 Seams | | | |
| B7 NFR | | | |
| B8 Assumptions | | | |
| B9 OQ | | | |
| B10 Non-goals | | | |
| B11 WHAT not HOW | | | |
| B12 Whole-product | | | |
| B13 Impact-map ready | | | |
| B14 CAP ↔ journey | | | |
| B15 Live-prove shaped | | | |

#### Spec-lane simulation

Rows `/spec-draft` cannot fill without guessing. Each must already be an
`OQ-*` in this file, or it is a B9 FAIL.

## Comparison

| Bar | C1 | C2 | C3 | … |
|-----|----|----|----|---|
| B1 | | | | |
| B2 | | | | |
| B3 | | | | |
| B4 | | | | |
| B5 | | | | |
| B6 | | | | |
| B7 | | | | |
| B8 | | | | |
| B9 | | | | |
| B10 | | | | |
| B11 | | | | |
| B12 | | | | |
| B13 | | | | |
| B14 | | | | |
| B15 | | | | |
| **Material FAILs** | | | | |
| **Handover** | yes/no | yes/no | yes/no | |

Rank rule: fewer material FAILs on B3/B4/B6/B9/B11/B14/B15, B12 PASS (or same
N/A), B2 equal or better. Rank does not grant handover.

## Secondary (prd-critic)

Skip this section if `/prd-critic` was not installed.

| File | Build Readiness | Notes (cannot override material FAIL) |
|------|-----------------|----------------------------------------|
| C1 | Ready / Needs Revision | |
| C2 | | |

## Next (human)

- `handover: no` → `/prd-think` again (writes `-3.md`, `-4.md`, …)
- `handover: yes` → promote **only** the named file the human authorizes
  → then `/validate-requirements`
- Do not start review / update until that promote
