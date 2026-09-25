---
description: Spec-driven development — truth hierarchy and same-PR discipline for Python service repos.
alwaysApply: true
---

# Spec-driven development

## Truth hierarchy (read in this order)

| Priority | Location | Answers |
|----------|----------|---------|
| 1 | `.claude/rules/*.md` (this submodule) | **How** to build |
| 2 | `docs/specification/product/` | **What** to build |
| 3 | `docs/specification/adr/` | **Why** (accepted decisions) |
| 4 | `docs/specification/as-built/` | **What is live** |

## Before changing behavior

1. Read the relevant **product** spec (and **ADR** if architecture or contracts change)
2. Read **as-built** — do not assume a feature is live because the spec mentions it
3. Treat accepted ADRs as immutable during implementation — supersede with a new ADR when architecture changes

## Same PR discipline

When code changes, update together:

- **product** spec (if contract or capability changes)
- **pytest** — in-process tests per **`testing-verify-flows.md`**
- **verify** (`tests/verify/`) — live smoke per product feature
- **as-built** — verification rows; distinguish implemented / unit-tested / live-verified
- **`tests/README.md`** feature map

## PR traceability

Every PR should name (see repo `.github/pull_request_template.md` when present):

- **Initiative** (e.g. board epic or program id)
- **Issue #**
- **Spec paths** touched
- **Verify command** run (matches board **Verify** column when applicable)

## Constitution boundary

- Do **not** put product requirements in **`.claude/rules/`**
- Do **not** treat narrative docs as the primary contract when a product spec exists
- Do **not** infer implementation maturity from rules or specs without checking **as-built**
- Do **not** redesign accepted architecture opportunistically in an implementation task

## Execution chat rule

- Architecture and spec design happen in dedicated design chats
- Implementation chats execute one accepted ADR or one accepted phase slice at a time
- Implementation prompts should explicitly name the ADR or phase being executed
