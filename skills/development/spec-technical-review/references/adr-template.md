# ADR-{NNN} — {title}

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | {INITIATIVE} |
| Feasibility finding | {FINDING_ID} (`FF-*`) |
| Technical review | `{TDD_PATH}` |
| Source spec | `{SPEC_PATH}` |
| Source spec digest | `sha256:{hex}` |
| product_constraints | `[REQ-…, …]` — approved REQs this decision binds |
| changes_user_visible_behavior | `false` / `true` |
| spec_amendment_required | `false` / `true` |
| supersedes | `{ADR-… or none}` |
| superseded_by | `{ADR-… or none}` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

List, **by `REQ-*` id only**, the product choices this ADR deliberately does
not make (owned by the approved requirement / PM). Do not restate what the
REQ says — a reader who wants that opens the spec.

- {e.g. "See REQ-07." — not "See REQ-07 (whether one upload yields four outputs)"}

## Scope discipline (read before writing Context)

- **One decision per ADR.** If you are resolving more than one independent
  question, split the file — an ADR covering three decisions is a design doc
  in disguise. The design doc is the TDD; this file is the terse record.
- **Reference `REQ-*` by id only** (e.g. `REQ-07`). Never quote or paraphrase
  a REQ's behavioral sentence in Context, Recommendation, or Consequences —
  that is the feature restated, not the engineering decision.
- **Smell test:** delete every `REQ-*` id from Context/Recommendation and
  re-read what remains. If it still reads like something a PM would write
  (a feature, a UX flow, an acceptance outcome), rewrite it in engineering
  vocabulary (data flow, module boundary, protocol, storage, concurrency) or
  delete it and link to the spec/TDD instead of inlining it.
- **Keep it short — and don't hollow it out either.** The record body
  (Product decisions excluded → Revisit triggers, excluding the metadata
  table and the Lifecycle/Acceptance boilerplate) should read in well under
  a minute — target roughly 150–400 words. If it needs a code example, a
  restated acceptance criterion, or a "why the user needs this" paragraph to
  make its point, that content belongs in the TDD or the spec, not here.
  A body under ~60 words is mechanically rejected as too thin to show real
  reasoning — trimming content to dodge phrase/overlap detection while still
  satisfying T11's structural checklist is itself a T12 failure, not a way
  to pass it.
- **Run `python scripts/adr_boundary_lint.py {this file} --source-text ...
  --approved-req-id ... --require-sources --finding-text-file ...`**
  (vendored inside this skill, present in a standalone install) **before
  marking T12 PASS** — see `checks.md` T12 for the full flag set. This is
  required, not optional; `SKIPPED` only when no Python runtime is
  available, with the reason stated. It is a mechanical check, independent
  of the drafting agent's own judgment — and still only a heuristic floor,
  not a semantic guarantee (see the lint's own module docstring for the two
  gaps it cannot see).

## Context

{State the engineering problem and constraints in engineering vocabulary —
not a restatement of product behavior. Reference `REQ-*` ids only; cite
existing Accepted ADRs that bound the design space. Do not introduce new
user-visible behavior.}

## Options considered

**Before listing an Option here, independently ground it in the codebase**
(codegraph query when available, `source_roots` read otherwise, per
`SKILL.md` NON-NEGOTIABLE 11) to verify it is a real, technically viable
alternative — not one already foreclosed by existing code (e.g. a dormant
mechanism already does this) or by spec exclusions (e.g. REQ-14). Remove a
foreclosed option, or explicitly annotate why it is listed despite the
exclusion. If grounding shows every remaining option produces identical
system behavior, this finding does not qualify as `ADR_REQUIRED` — see the
qualification rubric in `SKILL.md`.

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A | | |
| B | | |

> **Product consequences do not get narrated here either.** If a technical
> option would change something a user could notice, that is a PM
> confirmation trigger (see `governance.md` "PE decision vs PM confirmation
> pattern"), not commentary for this table. Record it as a routed question
> in TDD §10 and reference the id (`PM-{n}`) in one clause — do not describe
> the product impact in prose in this ADR. If describing it requires more
> than an id reference, the ADR is not ready to recommend an option yet:
> stop and route the PM question first.

## Recommendation

{Selected option and the *technical* rationale — stated in engineering
terms, not by restating acceptance criteria. Must satisfy `product_constraints`
without amending product behavior.}

## Consequences

- {Positive and negative consequences — technical, not user-facing outcomes
  already owned by the REQ.}

## Revisit triggers

- {Observable condition that would justify superseding this ADR.}

## Lifecycle — Accepted immutability and supersession

Once `Status: Accepted`, do **not** rewrite the accepted body in place.
To change the decision:

1. create a new ADR that `supersedes` this one,
2. set this ADR's `superseded_by` to the new id and status `Superseded`,
3. record owner, date, and review evidence on both files.

## Acceptance finalization

After PE review comments are resolved and PE explicitly states the decision is
ready for acceptance — **and** product-boundary fields remain `false` —
update the file before final GitHub approval:

```text
Status: Accepted
Decision owner: @{pe-name}
Approval evidence: {review/comment URL}
Approved head: {full SHA to be approved}
product_constraints: [REQ-…]
changes_user_visible_behavior: false
spec_amendment_required: false
Lint evidence: adr_boundary_lint.py {sources_checked}/{N expected}, PASS,
  sha256:{hex}
```

`Lint evidence` must match this exact shape — `adr_boundary_lint.py N/M,
PASS|FAIL, sha256:<hex>` — presence alone (`yes`, `TBD`, `-`) fails the
shape check and is rejected. Generate the line with:

```bash
python scripts/adr_boundary_lint.py {this file} --strict \
  --source-text <req_text_file> --source-text <feasibility_evidence_file> \
  --approved-req-id <every approved REQ-* in the spec> \
  --finding-text-file <feasibility_finding_file> \
  --print-evidence
```

and paste the printed line verbatim — do not hand-write the hash.
`--strict` bundles `--require-sources` with `--approved-req-id` and
`--finding-text-file` so this is the one recommended production invocation,
not four independently-optional flags.

A **shape match is not a genuine-hash guarantee** — anyone could type a
correctly-shaped but fabricated hex string. At any later point (PE review,
P13 re-check), re-verify the recorded digest against the current file and
sources with:

```bash
python scripts/adr_boundary_lint.py {this file} \
  --source-text <same sources> --verify-lint-evidence
```

A mismatch means the file changed since the digest was recorded, or the
digest was never genuinely computed — either way, the acceptance is not
trustworthy as recorded and must be redone. Even a verified match only
proves internal consistency with the sources supplied at verification time,
not that those sources were the correct/complete ones — that judgment call
remains PE's, not the script's.

The formal PE GitHub Approve must be on the final commit containing this
Accepted metadata. No file changes occur after that approval (publish via
Forge `/commit-workspace` — not inside content skills).
