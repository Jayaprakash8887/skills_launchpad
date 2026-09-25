---
name: spec-technical-review
description: >-
  After feasibility, produce a principal-engineer design document: resolve all
  engineering decisions (ADRs, interface contracts, test policy, module
  boundaries), draft any required ADRs, and route only true product questions
  back to PM on the meta PRD PR. Runs after /initiative-feasibility on both
  pass and findings (pin always enters this stage before plan). Writes TDD and
  Draft ADRs locally (or records N/A / light confirmation when feasibility was
  clean) and emits Forge readiness for the Draft spec PR; PE accepts
  architecture in files before planning. Final Gate 2 unlock (spec-lgtm)
  happens only after the implementation plan exists.
disable-model-invocation: true
paths: CLAUDE.md, docs/specification/**, .claude/rules/**
metadata:
  background_eligible: true
  background_trigger: "spec PR branch: spec slice committed + initiative-feasibility report produced"
---

# Spec technical review

Resolve all **engineering decisions** that block the implementation plan.
**Do not implement.** Produce a Technical Design Document (TDD) and draft ADRs.

Runs **while the Draft spec PR is open** — write TDD and ADR files locally and
emit Forge readiness for the spec branch. Gate 2 label remains **`spec-pending`**.
PE architecture acceptance is recorded in **artifact metadata**
(`Draft` → `Accepted`); **`spec-lgtm`** is set only after the full spec package
(including plan) is on head.

Benchmarked against: Stripe/Cloudflare/Oxide RFC process, Sentry design-first
gate, `agentic_development_workflow` multi-role review, GitHub Spec Kit
`/speckit.plan` architectural artifact pattern.

## NON-NEGOTIABLE

1. Never skip a check in [references/checks.md](references/checks.md). Mark SKIPPED with reason.
2. Every engineering decision in the output must be **resolved** (recommendation
   recorded) or **explicitly deferred** with a named risk and default assumption.
3. Do not ask PM to choose architecture. Route only product-scope and
   user-visible behaviour questions to the **meta PRD PR**. See
   [references/governance.md](references/governance.md) for the routing rubric.
4. Every `NEW-ADR` from feasibility maps to exactly one disposition:
   `ADR_REQUIRED` with a Draft file under `adr_dir`, `TDD_ONLY` with rationale,
   or `DEFERRED_WITH_DEFAULT` with risk and revisit trigger.
5. Dual output: chat summary + saved TDD file (local persistence + Forge readiness).
6. Run T0–T5 control loop (Gather → Understand → Analyze → Design → Execute → Verify).
7. Human PE acceptance is **required** before the implementation plan runs.
   Technical review creates Draft ADR files first; planning consumes only
   **Accepted** files in `{adr_dir}`. Mid-lane PE work updates files on the
   spec branch — it does **not** set `spec-lgtm`.
8. Verify **light freshness**: product-spec **H1–H3** citations, tip continuity,
   and **G1** when applicable agree with live handoff. Stop on authority drift.
   Do **not** fail closed solely on feasibility `artifact.digest` mismatch —
   feas/TDD digests are walk-time (PURGE at initiative closure).
9. **Product/architecture boundary.** PE may frame options and draft ADRs
   against approved `REQ-*` constraints. An ADR **must not** become `Accepted`
   when it depends on user-visible behavior not already represented by an
   approved `REQ-*` — amend and re-approve the spec first. Reference `REQ-*`
   by id only in Context/Recommendation/Consequences — never quote or
   paraphrase the REQ's behavioral sentence; that restates the feature
   instead of stating the engineering decision. T12 enforces this as an
   independent re-read pass, not a same-pass self-grade (see
   `references/checks.md`).
10. **No forge mutations.** Do not commit, push, branch, open PRs, apply labels,
    create issues, or merge. Fill `handoff.forge` / recommend `/commit-workspace`.
11. **Ground every `NEW-ADR` finding in the actual codebase before classifying
    or drafting it — never draft from feasibility's `ALTERNATIVE:` text
    alone.** Feasibility's F1/F2 baseline already inspected the repo once;
    this stage re-verifies and extends that evidence, because a finding's
    prose can itself encode a wrong question (see the ADR qualification
    rubric below). Use a codegraph provider when available
    (`.harness/references/codegraph-tool-contract.md`), otherwise read
    `source_roots` directly — **the tool is optional, the grounding activity
    is not.** Record what was found (or "none found — new capability") in
    the row's **Code evidence** — extend feasibility's column, don't just
    trust it blank or stale.
12. If a codegraph provider is available, prefer it for the grounding pass in
    NON-NEGOTIABLE 11 and for other architecture/impact questions. Always
    fall back to direct `source_roots` reads when unavailable — never block
    or change outcome selection on its absence.

## Inputs

Resolve paths from `.harness/profile.yaml` or
[references/layout-defaults.md](references/layout-defaults.md).

**Dual workspace (orchestrated / Gateflow):** `workspace` = app coding root
(TDD/ADR drafts). `meta_workspace` when bound = meta checkout for PRD /
product-scope context. Do not invent a meta path when empty.

1. **Feasibility report** — primary input (REQUIRED); source of NEW-ADR
   findings, Critical/Should-fix items, open engineering questions
2. **Initiative spec** — (REQUIRED)
3. **ADR directory** — existing accepted ADRs from `adr_dir` (REQUIRED)
4. **`rules_glob`** — workspace MDC rules (REQUIRED). Read before T2 Analyze.
5. **As-built** — `implementation-status.md` (REQUIRED)
6. **`.harness/profile.yaml`** or layout defaults (REQUIRED)
7. **Canonical handoff references** — product-spec H1–H3 citations, approved
   meta PR head / tech-lead review when Gate 1 still applies (REQUIRED; resolve
   under `meta_workspace` when bound). Feasibility report is an input artifact,
   not long-term digest SSOT.
8. **Codegraph provider** — OPTIONAL — see `.harness/references/codegraph-tool-contract.md`

## When to use

- Feasibility report contains one or more `NEW-ADR` findings
- Feasibility has Critical findings involving module design, interface shape,
  or test policy
- Implementation plan is blocked by engineering questions (not PM questions)
- PE wants to document interface contracts before planning

## Process

1. **T0 Gather and freshness gate** — feasibility report, spec, H1–H3 / G1
   references, ADRs, rules_glob, as-built; stop if durable authority or tip is
   stale (not solely on feas file digest)
2. **T1 Understand** — list all NEW-ADR items, Critical/Should-fix engineering
   findings, and open engineering questions from feasibility. Every `NEW-ADR`
   `Finding` cell must start with the literal `ALTERNATIVE:` marker (see
   `initiative-feasibility/references/output-template.md`); run
   `validate_finding_marker` (in the vendored `scripts/adr_boundary_lint.py`)
   against each `Finding` cell.
   **On a malformed `Finding` (missing marker): do not infer, guess, or
   re-derive the alternative yourself — that reconstructs architecture from
   product prose, the exact failure this stage exists to prevent.** Stop
   drafting that ADR, select outcome `blocked`, cite the malformed finding,
   and route it back to a re-run of `/initiative-feasibility` to correct the
   phrasing (via `spec-human-decision` → `pass` → `initiative-feasibility`,
   the same existing edge `stale` uses). Only well-formed `Finding` cells may
   proceed to T3 Design. For each well-formed finding, extract only the
   **technical alternative it names** and the `REQ-*` id(s) it cites. Collect
   the feasibility report's "Spec quote" evidence text for each finding into
   a source-text file — it proves the ambiguity exists, it is not draftable
   Context; do not carry that quote (verbatim or paraphrased) into any
   TDD/ADR field.
3. **T2 Analyze** — read relevant Accepted ADRs; read rules_glob; **ground
   every well-formed finding in the actual codebase** (NON-NEGOTIABLE 11):
   verify and extend the row's Code evidence via codegraph query or
   `source_roots` read before mapping anything — a dormant/existing
   mechanism found here can change what the real engineering question is,
   not just how it's answered (this is what separates a genuine trade-off
   from a bookkeeping question — see the qualification rubric). Then map
   each grounded finding to an engineering decision, a PM question, or a
   domain clarification (routing rubric in
   [references/governance.md](references/governance.md))
4. **T3 Design** — classify every NEW-ADR using the rubric below, now that it
   is grounded in code, not just in the finding's prose; for each
   `ADR_REQUIRED`, allocate a stable file path. Before listing any Option in
   the ADR, check it against the grounding evidence *and* the spec's scope/
   exclusions — drop or explicitly annotate an option the code or the
   approved spec already forecloses (never present a foreclosed option as a
   live peer choice). Render
   [references/adr-template.md](references/adr-template.md) using the REQ
   id(s), the technical alternative from T1, and the T2 grounding evidence —
   not the feasibility evidence text; produce module boundaries and public
   interface contracts
5. **T4 Execute** — write TDD + every Draft ADR file; make TDD §4 an ADR
   index; run T1–T12 checks. Run **T12 as a separate re-read pass** after the
   files are written, not while still drafting them (see
   [references/checks.md](references/checks.md) "T12 — run as an independent
   re-read"): run `scripts/adr_boundary_lint.py` (vendored in this skill)
   against every Draft ADR **first** — it is required, not optional, `SKIPPED`
   only when no Python runtime is available. Then perform the manual re-read
   as a **fresh, independent pass, not a same-session self-grade**: when the
   runtime supports spawning a sub-task/subagent with no access to this
   session's drafting turns, do the re-read there; otherwise, the honest
   fallback is a deliberate context-reset — re-open each file as if it were
   someone else's submission, not "the file I just wrote a moment ago." Strip
   `REQ-*` references from Context/Recommendation/Consequences and confirm
   what remains reads as an engineering decision grounded in the T2 code
   evidence, not a feature description; confirm one-decision-per-ADR and the
   word-count discipline in
   [references/adr-template.md](references/adr-template.md). Fix violations
   in the artifact itself before proceeding to T5 — a lint PASS alone is not
   sufficient, the manual re-read still applies, and it is a weaker check
   when it is not genuinely independent of the drafting reasoning.
6. **T5 Verify** — all required ADR files exist and are linked; all engineering
   blockers are resolved/deferred; only genuine PM/domain questions remain;
   T12 product-boundary integrity passes; select workflow outcome; emit
   `ready_for_pe_review: true` and `ready_for_plan: false`

## Outcome selection (workflow edges)

Map evidence to exactly one outcome declared for `spec-technical-review` in
pinned `workflow.yaml`:

| Outcome | When | Next (from workflow) |
|---------|------|----------------------|
| `pass` | T1–T12 PASS; engineering decisions resolved/deferred; T12 clean; ready for PE review; no blocking PM/domain that prevents PE package readiness | `technical-review-approval` |
| `findings` | Unresolved engineering quality gaps that need human clarification before PE can accept (not product input) — includes a T12 FAIL caused by **citation/quality** leakage (REQ prose quoted instead of cited, multi-decision or oversized ADR) where the underlying behavior is already covered by an approved REQ | `spec-human-decision` |
| `needs-input` | Blocking PM or domain input required; product behavior missing from approved REQs — includes a T12 FAIL caused by an ADR that **depends on user-visible behavior not represented by any approved REQ** (`changes_user_visible_behavior` / `spec_amendment_required` true). This is a missing product-input gap, not an engineering-quality gap — do not emit `findings` for it. Amend and re-approve the spec first | `spec-human-decision` |
| `blocked` | Explicit gate prevents progress — includes a malformed `NEW-ADR` `Finding` (missing the `ALTERNATIVE:` marker). Cite the malformed finding; do not re-derive the alternative yourself | `spec-human-decision` |
| `stale` | Product-spec H1–H3 / G1 / tip authority drift | `initiative-feasibility` |
| `failed` | Execution/render failure on valid inputs | `workflow-stop` |

Product/domain input must prevent `pass`. Stale inputs must emit `stale`.
Unresolved engineering decisions must not claim PE-review readiness.

## Output

Save to `{reports_dir}/Technical-Review-{initiative}.md` (from profile).

Use [references/output-template.md](references/output-template.md).

## PE acceptance (artifact gate — not Gate 2 unlock)

Persist TDD + Draft ADR files locally and publish via Forge
(`/commit-workspace`) to the Draft spec PR. PE reviews on the **same PR**:
- Discuss engineering decisions in spec PR comments
- Request changes until decisions and artifacts are correct
- CODEOWNERS on `Technical-Review-*` may request PE review when the TDD file is present

When PE explicitly states decisions are ready for acceptance:

1. update required ADR files `Draft` → `Accepted` with PE/date/review evidence
   **only if** each ADR binds approved `REQ-*` and `changes_user_visible_behavior: false`,
2. update the TDD `Status` field to **Accepted** and TDD §4 ADR index rows,
3. publish the acceptance package via Forge to the spec branch,
4. record the approved head SHA in TDD/ADR metadata when helpful.

**Do not set `spec-lgtm` at this stage.** `/spec-implementation-plan` reads
Accepted files (P12/P13). The GitHub Gate 2 unlock (`spec-lgtm` + Approve +
attestation) happens only after the plan is published to the same PR head.

## Routing rubric

See [references/governance.md](references/governance.md) for the full table.

Quick rule:
- **Engineering** — module boundaries, interface contracts, ADR gaps, test
  policy, error propagation, observability, data contract ownership → PE resolves on spec PR
- **Product** — user-visible behaviour choices, scope cuts, priority → meta PRD PR
- **Domain** — business source-of-truth (tab names, BU process, data ownership)
  → named domain SME
- **Auto-fixable** — naming drift, enum value mismatches with spec → agent fixes
  without human, note in TDD

## ADR qualification rubric

Use `ADR_REQUIRED` when **all three** hold: (1) independent implementers could
choose incompatibly, (2) the answer is not obvious from compliant code/current
rules, and (3) a real trade-off exists — **and** the decision is cross-module/
service, security/privacy relevant, chooses data/storage authority or deployment
architecture, is hard to reverse, constrains later initiatives, or deliberately
departs from the constitution.

**Criterion (3) requires naming the system-behavior difference between
options, grounded in the T2 codebase inspection — not a checkbox.** "We could
write this as one ADR or three" is not a trade-off; neither is any choice
where every option produces identical runtime behavior. If grounding reveals
no behavioral difference can be named, the finding is not `ADR_REQUIRED` —
either reclassify as `TDD_ONLY`, or the grounding has surfaced a *different*,
real question underneath the one feasibility posed (e.g. "does this need new
verification machinery, or does an existing dormant mechanism already cover
it") — draft against that question instead, don't force the original one.

Use `TDD_ONLY` for a local, easily reversible implementation choice already
bounded by rules. Use `DEFERRED_WITH_DEFAULT` only with a named risk, safe
default, and observable revisit trigger.

Every disposition remains traceable to its feasibility finding. Never satisfy
T11 with a future promotion task or a target path alone. Never invent product
behavior in an ADR (T12).

## Workflow handoff

1. Append/emit the envelope from `.harness/references/handoff-envelope.md` to the TDD. Use stage `spec-technical-review`.
2. When the invocation binds `handoff_path` (orchestrator / AgentRunner baton), also **overwrite** that path with the same `handoff:` envelope before exit. Leaving the baton empty is a failed stage for automated consumers. `artifact.path` remains the workspace skill output, not the baton path. See `.harness/references/handoff-envelope.md` (Orchestrator baton).
3. Derive `next_candidates` and `human_checkpoint` from pinned root `workflow.yaml` for `(stage: spec-technical-review, outcome)` per `.harness/references/handoff-envelope.md` (**Derive from pinned workflow**). Set `human_checkpoint: true` only when the resolved next node's `type` is `human-checkpoint` — never because the artifact "should be reviewed."
4. Follow `.harness/references/forge-side-effects.md#content-producers` when this stage's pin has `forge.commit_workspace` other than `disabled` or next is an `external-action` with `forge.requires` — fill `handoff.forge` / recommend `/commit-workspace`; do not treat local CLI as skill success.


**Transitions:** pinned root `workflow.yaml` for this stage (SSOT). Human or
agent may run this skill; legality and auto-dispatch follow `dispatch` +
delivery contract + latest handoff. `pass` resolves to human-checkpoint
`technical-review-approval` (`purpose: tdd-adr-acceptance`).

Before final approval, signals must include actual Draft ADR paths/digests,
`ready_for_pe_review: true`, and `ready_for_plan: false`. After the final
exact-head approval, the approval node—not this skill—enables planning.
`next_candidates` never authorize invoke.
