# ID conventions (SSOT)

Stable identifiers across PM and development skills. Every skill that assigns
or cites an id MUST follow this vocabulary. Check ids (rule numbers) are
**not** entity primary keys.

See also: [artifact-write-contract.md](artifact-write-contract.md),
[quality-confidence-ladder.md](quality-confidence-ladder.md).

## Mint-only-if-consumed

**Do not mint an id with no named downstream consumer.** For every namespace
below, the “Must be consumed by” column is normative. If nothing fails closed
when the id is missing, stop generating it.

---

## Namespaces

| Namespace | Purpose | Stable across revisions? |
|-----------|---------|--------------------------|
| **Product** | What we want (PRD / spec) | Yes — never recycle |
| **Process** | What an audit/review produced | Yes within a report revision chain |
| **Delivery** | How we execute (plan / board) | Yes for the initiative |
| **Checks** | Which rule fired | Stage-local documentation only |

---

## Product ids

| Kind | Shape | Lives in | Meaning | Must be consumed by |
|------|-------|----------|---------|---------------------|
| Capability | `CAP-{nn}` | PRD (+ carried in spec) | Product ability — **own prove rung** | Every CAP → ≥1 `REQ-*`; capability live prove / `covers` when live applies |
| Journey | `J-{nn}` | PRD § Journeys (+ carried in spec) | Multi-step actor path — **own prove rung** | spec-draft → plan → WM `covers` → pre-implement → wave-acceptance |
| Requirement | `REQ-{nn}` | PRD + spec | Testable requirement (**canonical**) | TASK `implements`, unit and/or live evidence, ground |
| Contract | `CTR-{nn}` | PRD / impact / spec | Cross-repo seam (mint only when seam exists) | Spec contracts; feas F9; plan when touched |
| Open question (product) | `OQ-{nn}` | PRD | Unresolved **product** decision in the PRD | quality, validate, review→CHG |
| Impact question | `IM-{nn}` | Impact-Map § Open questions | Unresolved **repo / programme / Gate-1** question | Gate 1 / coding-readiness **fail closed** when `Blocking: yes` and open |

**Journey / capability shape:** `J-01`, `CAP-01`, … — **exactly two digits**
(`{nn}`). Reject `J1`, `J-1`, `J-001`, `CAP-1` for new artifacts.

**`REQ-*` is canonical.** Spec tables may show `FR-{nn}` only as a **display
alias** (`FR-05` ≡ `REQ-05`). Never mint new `FR-*`.

**Capability ≠ journey.** CAP is not “grouping only” for prove — capability
live uses `CAP-*` on `covers`; journey live uses `J-*`. Both may list related
`REQ-*`.

Trace:

```text
CAP-03 ──▶ REQ-07, REQ-08
CAP-03 ──▶ (optional) journeys J-02, J-10 that exercise it
J-02   ──▶ live covers / fixtures
REQ-07 ──▶ TASK implements / unit and/or live
```

---

## Process ids

| Kind | Shape | Producer | Meaning | Must be consumed by |
|------|-------|----------|---------|---------------------|
| Validation finding | `VF-{nn}` | `validate-requirements` | One finding instance | review-findings → `CHG-*` |
| Feasibility finding | `FF-{nn}` | `initiative-feasibility` | One feasibility finding | technical-review / plan / blockers |
| Technical review finding | `TF-{nn}` | `spec-technical-review` | TDD/ADR-stage finding | handoff blockers / ADR lineage |
| Ground finding | `GF-{nn}` | `ground-spec` | Grounding discrepancy | wave closeout blockers |
| Change to apply | `CHG-{nn}` | `review-findings` / `update-documents` | Approved edit unit | `update-documents` applies |
| Product question (PE→PM) | `PQ-{nn}` | engg-reviews | Product/UX/scope question after code evidence | PM answer → PRD update |
| Spec question (engineering) | `Q-{n}` | `spec-draft` | Engineering open question **in app spec** | feas / plan / TDD |
| Learning | `L-{nn}` | `learning-extract` | Structured learning | ground-spec cite / handoff |

Rules:

- Validation tables use **`VF-01`**, never bare `# 1` as the primary key.
- Incremental re-validation: surviving findings **keep the same `VF-*`**.
- Resolution and `update-documents` link **`VF-*` → `CHG-*`**.
- Feasibility blockers use **`FF-*`**, never bare `F-12`.
- Grounding uses **`GF-*`**. Do **not** reuse `FF-*` for ground findings.
- Technical-review-native findings use **`TF-*`**. Cite originating `FF-*`
  for lineage when applicable — do not conflate ids.
- **engg-reviews mints `PQ-*` only** (not `Q-NN`). Spec engineering questions
  stay **`Q-*`**. PRD product opens stay **`OQ-*`**. Impact opens stay
  **`IM-*`**. Do not mix registries.
- Open `IM-*` with **Blocking: yes** closes Gate 1 / coding-readiness until
  resolved or deferred with an explicit default.

---

## Delivery ids

| Kind | Shape | Meaning |
|------|-------|---------|
| Initiative | `INIT-…` | Programme initiative |
| Epic / parent | `EPIC` (WorkManifest) / board parent | Board root |
| Wave | `W{n}` | Sign-off / merge boundary (`W0`, `W1`, …) |
| Task | `TASK-W{n}-{nn}` | Executable unit |
| File / Test | `FILE-…` / `TEST-…` | Plan-only helpers |

```text
TASK-W0-01 ──implements──▶ REQ-07, REQ-08
```

Do **not** invent shadow `REQ-W{n}`.

Durable digests **H1–H4** / gate identities live in
[artifact-write-contract.md](artifact-write-contract.md) — not a second
product-id registry here.

---

## Check ids (not entities)

| Stage | Examples |
|-------|----------|
| validate-requirements | `1`…`11`, `S1`…`S4` |
| initiative-feasibility | `F1`…`F14` |
| spec-technical-review | `T1`…`T12` |
| spec-implementation-plan | `P1`…`P16` |
| ground-spec | `G1`…`G10` |
| create-board-tickets (forge) | `B1`…`B8` |
| learning-extract | `L-01`…`L-{nn}` |
| engg-reviews | `C0`…`C12` |

Cite the check on a finding (`VF-04`, Check `7`) — never use the check number
alone as a handoff blocker.

---

## Handoff blockers

`handoff.blockers` MUST use stable process or delivery ids, for example:

- `VF-03`, `FF-02`, `GF-01`, `TF-01`, `L-01`
- `OQ-04`, `IM-02`, `PQ-03`, `Q-06`
- `TASK-W0-03`

Not: `1`, `F-12`, `Critical #2`, free-text sentences.

---

## Coherence bar

1. Product ids (`CAP`, `J`, `REQ`, `CTR`, `OQ`, `IM`) are assigned once and never recycled.
2. Process ids (`VF`, `FF`, `TF`, `GF`, `CHG`, `PQ`, `L`) are stable within a report revision chain.
3. Delivery ids (`W`, `TASK`) never rename product ids.
4. Check ids document which rule fired — not primary keys.
5. Mint only if consumed (see top rule).
