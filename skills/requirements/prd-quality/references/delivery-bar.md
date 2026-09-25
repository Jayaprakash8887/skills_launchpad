# Delivery bar — PRD as spec-lane input

Score **each file in isolation**. Quote id + sentence. If you would guess
to fill a spec row, that is FAIL.

**Material FAIL** = would force spec-draft `needs-input`.

| ID | Bar | Material? | PASS when |
|----|-----|-----------|-----------|
| B1 | Job is explicit | Yes | Named user-world outcome; if-we-do-nothing; solution aligned or rejected |
| B2 | CAP → REQ coverage | Yes | Every CAP has ≥1 REQ; every REQ cites a CAP |
| B3 | Observable acceptance | Yes | Each REQ: condition/event + observable result + evidence type. No fast/intuitive. No module/transport in the REQ |
| B4 | Negative paths | Yes | Per happy-path CAP: error/empty/unavailable/unauthorized/partial or N/A with why it matters in production |
| B5 | Actors can do it | Yes | Actor/action pairs are possible (or `OQ-*`) |
| B6 | Seams / contracts | Yes | Cross-repo or cross-actor boundary has `CTR-*` seed (logical op + field meaning + errors) or explicit "no boundary" |
| B7 | NFR applicability | No* | Security, reliability, performance, observability, privacy, migration, rollback, operations: specified or N/A. *Material if an obvious surface is omitted |
| B8 | Assumptions have status | Yes | Status + dependent REQs + default-if-false |
| B9 | OQ are first-class | Yes | Guess-points are `OQ-*` with owner, blocking, required-by stage, default |
| B10 | Non-goals are load-bearing | Yes | Adjacent surfaces we will not change, and why |
| B11 | WHAT not HOW | Yes | Zero solution-prescriptive REQs |
| B12 | Whole-product, not brief-shaped | Yes | At least one journey/actor/negative/adjacent **not in the brief** was considered. TOC == brief TOC → FAIL. Brief not supplied → `N/A — brief not supplied` |
| B13 | Impact-map ready | No | Capabilities matchable to service catalog `owns` / `description` |
| B14 | CAP ↔ journey binding | Yes | Every CAP lists ≥1 `J-{nn}` **or** explicit defer; every `J-*` cites Caps exercised |
| B15 | Live-prove shaped | Yes | Any REQ Evidence containing `live` cites ≥1 `CAP-*` and/or `J-*`; capability and journey remain **separate** rungs (see quality-confidence-ladder) |

## Handover (the validate signal)

Per file, after the independent score:

- `handover: yes` = **zero material FAILs** = that named file may be
  promoted, then `/validate-requirements`.
- `handover: no` = any material FAIL = run `/prd-think` again (next free
  `-N.md`). Do not start validate → review → update on that file.

This does not pick the product. Two `yes` files with different jobs both
qualify; the human names which file to promote.

## Rank (secondary)

`Ci` wins only if fewer material FAILs on B3/B4/B6/B9/B11/B14/B15, B12 PASS
(or both N/A for the same reason), and B2 equal or better.

Page count, tone, `/prd-critic` Build Readiness, and `Ci-wins` are not
the handover signal.
