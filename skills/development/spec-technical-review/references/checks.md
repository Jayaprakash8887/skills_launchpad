# Technical review checks (T1–T12)

Run every check. PASS = zero **blocking** findings for that check.
SKIPPED = missing input (state reason).

Governance and routing detail: [governance.md](governance.md).

| ID | Check | Evidence required |
|----|-------|-------------------|
| T1 | **Module / package boundaries** | Each affected module named; inputs and outputs of each boundary stated; no ambiguity about which layer owns what. **Codebase grounding evidence** (codegraph query or `source_roots` read, per SKILL.md NON-NEGOTIABLE 11) confirms these modules actually exist, their declared relationships are real, and no unexpected existing module is relevant |
| T2 | **Public interface contracts** | For each module boundary, the method names, argument shapes (types described in engineering terms, not language syntax), return shapes, and invariants are specified |
| T3 | **NEW-ADR dispositions** | Every `NEW-ADR` maps to exactly one `ADR_REQUIRED` Draft file, `TDD_ONLY` rationale, or `DEFERRED_WITH_DEFAULT` risk/default/revisit trigger. **Codebase grounding evidence** supports the qualification (a named, real behavioral difference between options — see the ADR qualification rubric in `SKILL.md`), not just the feasibility finding's prose |
| T4 | **Test policy** | Unit / integration / live-verify (smoke/sandbox) boundary documented per module; golden test strategy named (exact match vs fuzzy vs snapshot); AI-output determinism policy stated where applicable |
| T5 | **Error handling strategy** | Failure modes named for each module; propagation path to caller stated; which failures are recoverable vs terminal; how errors surface at the CLI/API boundary |
| T6 | **Observability contract** | What is logged at which level for each module; which fields appear in structured output (correlation IDs, domain IDs); no silent swallowing of errors |
| T7 | **Data contract ownership** | Schema ownership named (who defines, who validates, which layer); validation points stated (edge vs internal); versioning policy if schema evolves |
| T8 | **Dependency graph integrity** | No circular dependencies introduced; no ADR violations; import layer order consistent with `rules_glob` layering constraints |
| T9 | **Engineering questions — zero PE-lane items unresolved** | All items routed to PE lane are resolved or deferred with defaults; PM/domain items explicitly listed as out-of-scope for this review |
| T10 | **PE review readiness** | Package explicitly requires PE review, lists the exact TDD + ADR files to review, reports `ready_for_pe_review`, and does not claim approval or planning readiness |
| T11 | **ADR artifact integrity** | Every `ADR_REQUIRED` file exists under `{adr_dir}`, is Draft, links the feasibility finding/TDD, contains context/options/recommendation/consequences/revisit triggers, product constraint fields, and is linked with digest from TDD/handoff |
| T12 | **Product-boundary integrity** | Every user-visible normative statement in the TDD or ADR cites an approved `REQ-*`. ADRs/TDD may constrain implementation but must **not** create scope, UX, acceptance criteria, priority, or business rules absent from approved REQs. **FAIL** when an ADR would invent or amend product behavior (`changes_user_visible_behavior` / `spec_amendment_required` true without an approved amended REQ), when an ADR quotes/paraphrases REQ prose instead of citing the id, when an ADR resolves more than one decision or exceeds the record-body length discipline (see [adr-template.md](adr-template.md) Scope discipline), or **when the independent re-read below (a genuinely separate pass — fresh subagent/task where the runtime supports it, a deliberate context-reset otherwise) flags product leakage or invented behavior the mechanical lint did not catch** |

## T4 vocabulary — do not leave "integration" undefined

"Integration test" is an overloaded term (Fowler). Define per module:
**unit** = single component, no I/O, test doubles for every collaborator;
**integration** = exactly one named boundary/dependency exercised for real
(or a contract test run against both a fake and the real implementation) —
never "the whole stack"; **smoke** / **sandbox** = human-run live verify
under `live_verify_dir` against the CLI/API surface. Name the boundary under
test for every "integration" row — the word alone is not sufficient evidence.

## T12 — run as an independent re-read, not a self-grade

Writing the ADR and certifying it are different acts. Do not tick T12 in the
same breath you drafted the file.

**Run, on every Draft ADR, before claiming T12 PASS:**

```bash
python scripts/adr_boundary_lint.py <adr_file> --strict \
  --source-text <req_text_file> --source-text <feasibility_evidence_file> \
  --approved-req-id <REQ-01> --approved-req-id <REQ-02> ... \
  --finding-text-file <feasibility_finding_file> \
  --print-evidence
```

`--strict` **is the recommended invocation** — it bundles `--require-sources`
with a hard requirement that `--approved-req-id` and `--finding-text-file`
are also supplied, so these are not four independently-optional flags where
omitting one silently narrows what got checked:

- `--source-text` for **both** the cited REQ's spec sentence and the
  feasibility "Spec quote" collected during T1 — feeding both in is
  required whenever they exist; a lint run that omits an available source
  has not actually checked the one thing most likely to have leaked.
- `--approved-req-id` for **every** REQ-* id approved in the current spec
  (not just the ones this ADR cites) — this is what lets the lint catch a
  citation to a fabricated or unapproved REQ id, which a bare REQ-id-present
  check cannot.
- `--finding-text-file` — the feasibility `Finding` cell text for this
  `NEW-ADR`, so the `ALTERNATIVE:` marker (and the substance/register of the
  text after it) is validated mechanically, not just documented. **A
  malformed `Finding` here is a `blocked` outcome routed back to
  `/initiative-feasibility` — do not proceed to draft this ADR, and do not
  re-derive the alternative yourself** (see `SKILL.md` T1 and Outcome
  selection).
- `--print-evidence` prints the exact `Lint evidence` line to paste into
  the ADR's Acceptance finalization block — do not hand-write the hash.

**Also run, once per TDD, before claiming T12 PASS** — T12's own check row
says "Every user-visible normative statement in the TDD **or ADR**"; the TDD
is not exempt just because it isn't the ADR:

```bash
python scripts/adr_boundary_lint.py --tdd <tdd_file> \
  --source-text <req_text_file>... --require-sources
```

This scans the TDD's engineering free-text sections (§1 Problem statement,
§5 Test policy, §9 Resolved engineering decisions) for the same forbidden
phrasing and source overlap as an ADR — the TDD template inviting "1-3
sentences from spec" was itself a prior leak vector (see §1 wording in
`references/output-template.md`); this closes the gap where only ADRs had a
mechanical check and the TDD was manual-only. §10/§11 (routed PM/domain
questions) are **deliberately not scanned** — flagging them would be a
permanent false positive, since they exist specifically to carry genuine
product-scope language for PM/domain routing.

The path is relative to this skill's own directory — the script ships
vendored at `scripts/adr_boundary_lint.py` inside this skill, so it is
present in a standalone install, not only in this monorepo.

This is a required step, not optional tooling — treat a missing Python
runtime the same way `checks.md`'s own header treats any missing input:
`SKIPPED` with a stated reason, not silently omitted. It is a deterministic
check, not a model self-assessment: it validates structure (every required
section present **exactly once, matched case-insensitively** — a missing,
empty, or duplicated section is a `FAIL`; an unrecognized heading like
`## Customer outcome` is flagged **and** still scanned; scaffolding
sections are exempt from the shape rules but still scanned for leakage),
the ADR title (a **numeric** id and non-empty title, plus content), and
metadata consistency (matched case-insensitively on the field name — an
`Accepted` status with a `true` product-boundary flag, a conflicting
duplicate metadata row, an invalid `Status` value, a placeholder
`Approval evidence`/`Approved head` (`TBD`, `-`, `N/A`, not just literally
`Pending`), or a malformed `Lint evidence` shape are all `FAIL`), on top of
phrase/lexical checks. **A lint PASS is still necessary but not
sufficient** — three gaps remain that only the manual re-read (or a human/
independent-model reviewer) can catch, and the lint says so honestly in its
own docstring: (1) a loose paraphrase using vocabulary entirely outside the
lint's synonym map, (2) invented behavior under a correctly-cited real REQ
with the metadata flags left (falsely) `false`, and (3) multiple decisions
narrated in prose inside one **un-duplicated** Recommendation section (no
repeated heading for the structural check to catch). Do not treat a lint
PASS as proof none of these occurred — and do not treat a shape-valid
`Lint evidence` field as a genuine-hash guarantee either; `--verify-lint-evidence`
narrows that gap but cannot force anyone to actually run it (see the
script's own module docstring on this boundary).

After T4 Execute writes all ADR/TDD files, re-open each one as a **genuinely
separate pass** — a fresh sub-task/subagent with no visibility into this
session's drafting turns where the runtime supports it, or a deliberate
context-reset (read the file cold, as someone else's submission) when it
does not — and audit it:

1. For every Context / Recommendation / Consequences paragraph, mentally (or
   literally) strike every `REQ-*` id reference and re-read what remains. If
   it still reads like a feature description, a UX flow, or an acceptance
   outcome a PM would write, it **fails** T12 — rewrite in engineering
   vocabulary, or delete it and link to the spec/TDD instead of restating it.
   Also check for verbatim or near-verbatim (6+ consecutive words) overlap
   with the REQ's own sentence **or** the feasibility report's "spec quote" /
   evidence text — either source ending up in the ADR body is the same
   failure, since the evidence text is proof the ambiguity exists, not
   pre-written Context.
2. Confirm each ADR resolves exactly **one** decision and its record body is
   within the ~150–400 word discipline (the lint enforces the structural
   floor/ceiling and duplicate-section signal mechanically — this step is
   about judgment on borderline cases the lint's numeric thresholds miss,
   e.g. one decision written twice in different words without a duplicated
   heading).
3. Confirm no "product consequence" note from Options-considered has migrated
   into Context or Recommendation as if it were the decision itself.
4. **The two gaps the lint cannot see are your job here**: (a) does any
   sentence, reworded in unfamiliar vocabulary, actually restate something
   the cited REQ or feasibility evidence already says — even with zero
   shared words? (b) does any sentence introduce a capability, side effect,
   or user-facing outcome that is not implied by the REQ it's filed under,
   regardless of what the `changes_user_visible_behavior` field claims? A
   `false` in that field is the drafter's assertion, not proof — read the
   sentence and judge it independently.
5. Fix violations in the artifact before proceeding to T5 — do not just note
   them as a finding and move on.

**Outcome routing for a T12 FAIL is not uniform** (see `SKILL.md` Outcome
selection): if the ADR depends on behavior absent from any approved `REQ-*`
(`changes_user_visible_behavior` / `spec_amendment_required` true), that is a
missing-product-input gap → `needs-input`, never `findings`. If the behavior
is already covered by an approved REQ and the failure is citation/quality
only (REQ prose quoted instead of cited, multi-decision or oversized ADR),
that is an engineering-quality gap PE can resolve → `findings`.

Severity: **Blocking** (PE cannot sign off until resolved), **Should fix**, **Verify**.

**Blocking** when: T3 has an unresolved NEW-ADR with no disposition/default; T9
has PE-lane items pending; T2 is missing for a crossed boundary; T11 finds a
missing/broken/duplicate ADR file or embedded ADR content without its required
canonical file; or **T12** finds uncited user-visible behavior, product
leakage (verbatim/paraphrased REQ prose in Context or Recommendation), or an
ADR violating the one-decision/length discipline.

Findings discovered natively in this stage (e.g. a T12 audit result) use the
**`TF-*`** namespace, never the feasibility-owned `FF-*` (see
`.harness/references/id-conventions.md`) — cite the originating `FF-*`
separately for lineage when the finding traces back to a `NEW-ADR` (e.g.
"`TF-01`, from `FF-02`"), do not conflate the two ids.
