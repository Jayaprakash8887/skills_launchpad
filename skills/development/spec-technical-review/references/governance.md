# Technical review — ADR and MDC read strategy

## When to read ADRs in this skill

Technical review is the **one skill where ADR scope must be wider than
keyword-match**. Feasibility uses keyword-match to detect violations. Technical
review uses ADRs to **constrain the design space** — a NEW-ADR recommendation
must not conflict with any existing Accepted ADR, including ones that don't
mention the spec domain by name.

### ADR read order

1. **T0 Gather** — list all ADR titles + status (one line each). Note which are
   Accepted, Draft, Superseded.
2. **T1 Understand** — list every `NEW-ADR` finding from the feasibility report.
   List every engineering decision to be resolved.
3. **T2 Analyze (full ADR read)** — read ALL Accepted ADRs. Rationale: when
   drafting a new architectural decision, an agent that only read keyword-matched
   ADRs may unknowingly recommend an option that conflicts with an existing
   decision in an adjacent domain. Full read is the only safe strategy here.
   - Mark each existing ADR as: **constrains** (limits which NEW-ADR options are
     valid) or **independent** (no interaction with current decisions).
   - The "constrains" set becomes the design constraint table in TDD §4.

### MDC read order

Same domain-filter approach as feasibility and plan (see feasibility
`governance.md` MDC pass). Read only files matching the engineering domains of
the decisions being resolved. The full `.claude/rules/` set is available via
`paths:` in the SKILL.md front matter — load selectively.

---

# Routing rubric — PE / PM / Domain / Auto-fix

Use this table to classify every open item from the feasibility report before
writing the TDD. Do not route engineering decisions to PM. Do not route product
decisions to PE.

## Routing table

| If the gap is about… | Route to | Why |
|----------------------|----------|-----|
| Module/package boundaries, layer ownership | **PE** | Architecture — only engineering can make this call |
| Public interface contracts (method shapes, types, invariants) | **PE** | Interface design — engineering decision |
| Which ADR option to adopt (NEW-ADR) | **PE** | Architecture — PE recommends, stakeholders confirm |
| Test policy (unit vs integration, golden tests, fuzzy vs exact) | **PE** | Verification strategy — engineering quality bar |
| Error propagation, failure modes, circuit breakers | **PE** | Reliability design |
| Observability hooks, log levels, structured fields | **PE** | Operational design |
| Schema ownership, validation layer, versioning policy | **PE** | Data contract design |
| Import layering, dependency graph | **PE** | Architecture enforcement |
| User-visible behaviour: "should users run one command or four?" | **PM** | UX and scope — product decision |
| Feature scope: "is this in Phase 1 or deferred?" | **PM** | Priority — product decision |
| Acceptance criteria: "what does done look like for the user?" | **PM** | Definition of done — product responsibility |
| Business source-of-truth: tab names, BU terminology, data rules | **Domain SME** | Only the BU/finance team can confirm |
| Third-party API contract: exact payload shapes from external systems | **Domain SME** | Cannot be inferred from spec |
| Naming drift where spec uses wrong enum value or wrong CLI flag | **Auto-fix** | Agent can correct against schema doc — no human needed |
| Missing spec cross-reference that can be inferred | **Auto-fix** | Agent adds reference — note in TDD |
| Typos, formatting inconsistencies | **Auto-fix** | Trivial — note in TDD without escalating |

## Examples

Derive examples from the actual initiative-feasibility report findings for
this repo. Apply the routing table above to classify each finding.
Do not use examples from other repos or stacks.

## Ownership rule

- **PRD / product spec** owns: user-visible behavior, scope, acceptance
  criteria, business rules, and priority. Approved `REQ-*` are the product
  authority.
- **ADR / TDD** owns: technical choices, alternatives, trade-offs, and
  consequences needed to satisfy already-approved requirements.
- ADRs may cite `REQ-*`; they must **never** create or amend them.
- PE may propose technical options (and explain product consequences) before
  PM confirmation, but an ADR **cannot become Accepted** while it depends on
  an unapproved product-behavior change. Amend and re-approve the spec first.

## PE decision vs PM confirmation pattern

Many items have both a PE component and a PM component. The pattern:

1. **PE frames technical options first** — documents trade-offs against
   already-approved `REQ-*` constraints, recommends a default for the
   **internal** architecture.
2. **PM confirms only when product consequences change** — if the selected
   option would alter user-visible behavior not covered by an approved
   `REQ-*`, stop, amend the spec, and obtain approval before accepting the ADR.

Example (multi-schema) — correct ownership:

- Approved `REQ-07`: “One upload produces all four required outputs.”
  → Product behavior lives in the spec; not invented by the ADR.
- PE proposes internal options for satisfying `REQ-07` (e.g. single extraction
  pass vs four independent parsers) and drafts an ADR that selects
  `extract(file) → map<schema, rows>` as the **internal extraction boundary**.
- ADR fields: `product_constraints: [REQ-07]`,
  `changes_user_visible_behavior: false`, `spec_amendment_required: false`.
- PM is consulted **only if** a proposed option would change the approved
  product behavior (e.g. requiring four uploads). Until the spec is amended,
  that ADR must remain Draft / non-Accepted.

Never ask PM to choose between two engineering options without PE first
recommending one. Never accept an ADR that is the first source of product truth.

## Feasibility report PM questions — re-triage guide

When feasibility routes a question to PM, apply this filter:

1. Does answering it require knowing the engineering interface? → **PE first**
2. Does answering it require knowing business data sources? → **Domain SME**
3. Does answering it only require product priority or UX judgement? → **PM**
4. Can the agent resolve it from existing schema/spec documents? → **Auto-fix**
