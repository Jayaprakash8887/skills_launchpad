---
description: Prefer fail-fast over defensive coding; strong typing assumes validated invariants—no silent recovery without approval.
alwaysApply: true
---

# Fail fast (no silent defensive coding by default)

This codebase is **strongly typed** with validation at **edges** (settings, YAML, HTTP, repos). Inner layers should **assume contracts hold** and **surface violations immediately**, not paper over them.

## Prefer

- **Raise** on invalid input, broken invariants, or impossible state: typed project exceptions, **`ValueError`** / **`TypeError`** where appropriate, **`model_validate`** failures propagating (or wrapped once at a boundary with context).
- **Let failures propagate** from business code when the caller cannot meaningfully recover; handle only at **entrypoints** or **infra** boundaries where policy is explicit (e.g. HTTP 4xx/5xx, log + exit code).
- **Narrow, explicit handling** where the product requires it (retries for transient **infra** I/O, idempotency)—documented in that module or ADR.

## Avoid without explicit approval

- Broad **`except Exception`** (or bare **`except:`**) that swallows errors or substitutes **`None`** / sentinel defaults.
- **Silent fallbacks** ("if missing, use X") that hide misconfiguration or bad data.
- **Defensive** branches for types or shapes that **Pydantic / annotations** already guarantee—duplicated checks that mask real bugs.

If a case truly needs defensive or forgiving behavior, treat it like **`pydantic-schemas.md`** exceptions: **align with tech lead / product** and document (ticket, PR, ADR).

## Contrast: infra vs domain

- **Infra** may implement retries, circuit breakers, or mapped errors for **external** systems—still **fail fast** on programmer misuse (wrong URL, missing secret).
- **Business** code should not duplicate "maybe the dict is wrong" logic when the boundary already validated a **model**.

## Related rules

- **Typing & boundaries:** `strong-typing.md`
- **Validate at edges:** `pydantic-schemas.md`
- **Layering:** `architecture.md`
- **Errors & logging:** `logging-loguru.md`
