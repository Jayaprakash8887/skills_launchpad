# Persistent handoff envelope

Every Prayog stage ends with a handoff block in its durable output artifact.
Chat summaries may repeat it, but chat is not workflow state.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-001.md
    # digest omitted — this stage does not mint/cite a durable identity;
    # artifact.path existing is the walk-time proof-of-write
  blockers:
    - FF-02
  signals:
    new_adr: true
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
```

Blockers MUST use stable ids from
[id-conventions.md](id-conventions.md) (`VF-*`, `FF-*`, `OQ-*`, `TASK-*`, …).
Never bare check numbers (`F-12`, `1`) or free-text sentences.

Canonical artifact paths and revision rules:
[artifact-write-contract.md](artifact-write-contract.md).

## Required fields

| Field | Meaning |
|-------|---------|
| `contract` | Delivery contract implemented by the producer |
| `stage` | Node id from `workflow.yaml` |
| `outcome` | One of the contract outcomes |
| `artifact.path` | Stage output (canonical path while the file exists); `null` when the stage has no workspace artifact (e.g. forge skills that only mutate GitHub) |
| `artifact.digest` | **Required only** on stages that mint or cite a durable identity — `prd-impact-map` (H1/H2), `spec-implementation-plan` §10 (`plan_digest`), `spec-technical-review` ADR Lint evidence. **Optional/omit elsewhere** — `artifact.path` existing at the canonical location is sufficient walk-time proof-of-write; do not fabricate a digest to fill this field on stages where it isn't required |
| `blockers` | Stable process/delivery ids that prevent progress |
| `signals` | Stage-specific routing facts; never implicit prose |
| `next_candidates` | Must match the pinned `workflow.yaml` transition for `(stage, outcome)`; never an authorization to execute |
| `human_checkpoint` | `true` **iff** the resolved next node’s `type` is `human-checkpoint`; **not** “this artifact deserves review” |
| `external_action` | `true` **iff** the resolved next node’s `type` is `external-action` — not “agent must run `gh`” |
| `forge` | Optional. Instance payload for forge executors when the pin expects mutation readiness (see below) |

Optional future field (not required in v1): `executed_by: manual | orchestrated`
records who ran a skill; it does not change navigation or eligibility.

### Durable identity vs mid-lane digests

On feas / TDD / plan / wave reports, `artifact.path` existing at the canonical
location is the walk-time proof that **this hop's file** was written.
`artifact.digest` is **optional** on these stages — omit it rather than
fabricate one; nothing in this contract or its validators reads it back, and
these paths are PURGE at initiative-closure anyway (see
[artifact-write-contract.md](artifact-write-contract.md)). Front-matter fields
that merely restate an upstream file's digest for a "source freshness" table
(e.g. a feasibility report citing its own spec's digest) are the same kind of
non-authoritative value — informational at best, never attested by a human
reviewer, safe to omit.

Long-term / mid-lane **`stale`** authority is **H1–H4 + G1–G3** (PRD digest,
scope digest, map revision, product-spec citations, gate/merge SHAs) plus
**`plan_digest`** (the Gate 2 `spec-implementation-plan` §10 attestation
identity) and the ADR **Lint evidence** digest (`spec-technical-review`,
independently re-verifiable via `scripts/adr_boundary_lint.py
--verify-lint-evidence`) — not recomputing or requiring purged-file digests.

Purge-stage handoffs list `deleted` / `refused` / `missing_ok` under `signals`
(or the purge artifact body); they do not invent extra digest gates.

## `handoff.forge` (instance readiness)

When the next node is `type: external-action` with `forge.requires`, or the
stage recommends a forge action, producers **fill** `handoff.forge` so human
forge skills and the orchestrator ForgeClient share one package. Policy
(action, draft, labels) comes from the pin; the skill fills instance slots.
See [`forge-side-effects.md`](forge-side-effects.md) (**Content producers**).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-001.md
    digest: sha256:{hex}
  blockers: []
  signals:
    pr_ready: true
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "Spec: INIT-001 — …"
    body_path: docs/specification/product/INIT-001.md
```

Rules:

- Pin wins on `action`, `draft`, `apply_labels`, `remove_labels`.
- Skill must supply every name listed in the pin’s `forge.requires`.
- Missing required slots on an outcome that routes to that external-action →
  **incomplete** handoff (fail closed for automate).
- Never put approval labels (`*-lgtm`) in `apply_labels`.
- `forge` does **not** authorize invoke and does not replace `next_candidates`.
- Chat may repeat the recommendation; handoff is the durable SSOT.

Also set `external_action` from the pin:

```text
external_action = (next.type == "external-action")
```

Whether the orchestrator **STOPs** for interactive authorize is **not** this
flag — it is pin `authorization` on that external-action node (`explicit` |
`automated`). See [`forge-side-effects.md`](forge-side-effects.md).
`external_action: true` only means the next node is an external-action.

## Outcome vocabulary (examples)

Outcomes are stage-local and must be edges that exist on the pin for that
stage. Same word, different next node — always read `workflow.yaml`.

| Outcome | Typical meaning (content skills) |
|---------|----------------------------------|
| `pass` | Stage contract satisfied; advance on the happy path |
| `findings` | Blocking engineering findings need an owning stage (e.g. PE review) |
| `needs-input` | Required answer or source is missing/unreadable; human clarification |
| `blocked` | Authoritative source exists and shows an unsatisfied gate |
| `stale` | Authority drift (H1–H3 / G1 / head / tip) vs canonical inputs — not missing mid-lane report digests |
| `failed` | Execution/validation failure on otherwise valid inputs |
| `skipped` | Only where the pin defines a skip edge (e.g. `wave-complete`) |

Illustrations (live edges always come from the pin):

| stage | outcome | next (example) |
|-------|---------|----------------|
| `initiative-feasibility` | `pass` / `findings` | `spec-technical-review` |
| `initiative-feasibility` | `needs-input` | `spec-human-decision` |
| `spec-technical-review` | `stale` | `initiative-feasibility` |
| `spec-implementation-plan` | `blocked` | `spec-human-decision` |

No branch, commit, PR, label, issue, or cleanup operation is added by choosing
an outcome — Forge mutations stay on `external-action` nodes / forge skills.

Human-checkpoint **`wave-acceptance`** is the only **human approved** signal for
the wave tip (smoke or P15 N/A). Ingress is GitHub label `wave-accepted`
(phase-1); content skills never apply it. Human-checkpoint **`wave-signoff`**
is **merge/publish only** — record **reviewed head SHA** and **merge commit
SHA** after the human merges manually. That is checkpoint state, **not** a
second approval, **not** `handoff.forge` authorization, and never a Forge merge
action.

## Derive from pinned `workflow.yaml`

After choosing `outcome`, producers **must** fill navigation fields from the
pinned root `workflow.yaml` (same rules for every skill and every invoke mode):

```text
next_id = nodes[stage].outcomes[outcome]
next    = nodes[next_id]

next_candidates  = [next_id]    # match the pin transition; do not invent
human_checkpoint = (next.type == "human-checkpoint")
external_action  = (next.type == "external-action")
```

Rules:

- Durable artifacts are always reviewable; that does **not** set
  `human_checkpoint: true`.
- An envelope that nominates a `type: skill` next node with
  `human_checkpoint: true` is **invalid** (contradicts the pin).
- `next_candidates` never authorize invoke and never bypass a resolved
  `type: human-checkpoint` node.
- Illustrations only (live edges always come from the pin):

| stage | outcome | next (example) | `human_checkpoint` |
|-------|---------|----------------|--------------------|
| `validate-requirements` | `findings` | `review-findings` (`skill`) | `false` |
| `pre-implement` | `pass` | `loop-spec` (`skill`) | `false` |
| `loop-spec` | `pass` | `wave-pr-action` (`external-action`) | `false` (`external_action: true`) |
| `wave-pr-action` | `pass` | `wave-acceptance` (`human-checkpoint`) | `true` |

> At `wave-acceptance`, the human runs the wave's planned live prove
> (`verify_command` under `live_verify_dir` with fixture packs under
> `fixtures_dir` for declared `CAP-*` / `J-*`) or accepts P15 N/A, completes
> any `human_observations` look-ats, then signals accept (`wave-accepted` on tip).
> That `pass` is **human approved** — including look-ats — not unit/`make test`
> alone. There is **no** `/verify` content skill.
| `learning-extract` | `pass` | `ground-spec` (`skill`) | `false` |
| `ground-spec` | `pass` | `wave-done-action` (`external-action`) | `false` (`external_action: true`) |
| `wave-done-action` | `pass` | `wave-signoff` (`human-checkpoint`) | `true` |

## Orchestrator baton (`handoff_path`)

When an orchestrator / AgentRunner binds `handoff_path` (absolute path to the
run baton file), the producer **must** dual-write:

1. Persist the usual durable skill artifact under the workspace and append the
   `handoff:` envelope to that artifact (as today).
2. **Overwrite** the file at exactly `handoff_path` with the **same** envelope
   (plain YAML starting with `handoff:` **or** a single fenced `yaml` block
   containing it). Prefer a minimal baton file (envelope ± fence).

Rules:

- Do **not** leave `handoff_path` empty after an automated/packaged run.
- Chat-only handoff is **not** durable for orchestrator continuation.
- Envelope fields are unchanged. `artifact.path` remains the **workspace-relative**
  skill output (checklist/report/etc.), **not** the baton path.
- If `handoff_path` already holds a prior envelope, read it for context if
  useful; the final write **replaces** it with this stage’s envelope.
- Manual freeform `/skill` without a bound baton path keeps artifact-only
  behavior (no invented path).

## Navigation rules

1. Read the latest handoff and the pinned `workflow.yaml`.
2. Verify the handoff contract matches the installed contract.
3. Resolve the transition for the recorded outcome from `workflow.yaml` (SSOT).
4. Explain the next action before executing it.
5. Never auto-transition a `type: human-checkpoint` node. Mechanism is human
   review; `purpose` on the node is intent for display/ops only — not a
   separate node kind (`type: gate` is forbidden).
6. Never perform an external action unless the pin authorizes it.
   `authorization: explicit` → interactive / API authorize then Forge;
   `authorization: automated` → ForgeClient when `handoff.forge` requires are
   complete (no interactive STOP). `external_action: true` only means the next
   node is an external-action — not that the content skill must run `gh`.
7. A stale artifact routes to the workflow's stale transition, not the nominal
   next skill.
8. `next_candidates` never authorize invoke and never bypass
   `human_checkpoint: true` or a resolved `type: human-checkpoint` node.
9. **Invocation mode is not an exemption.** Human `/skill` and AgentRunner
   both obey the same pinned workflow + delivery contract + latest handoff.
10. For a resolved `type: skill` node: a human or ad-hoc agent may run the
    skill when preconditions allow. An orchestrator may **auto-dispatch** only
    when `dispatch: orchestrated` (missing `dispatch` → schema default
    `manual`). Read `dispatch` from the pin — do not hardcode skill-id lists.
    Forge skills under `skills/forge/` are never auto-dispatched (not on
    `outcomes`).
11. Technical review reports `ready_for_pe_review: true` and
    `ready_for_plan: false` until Accepted TDD/ADR files exist on the spec
    branch. Mid-lane PE acceptance updates files only — not `spec-lgtm`.
12. `/spec-implementation-plan` may run when TDD/ADR files are **Accepted**;
    **`spec-lgtm`** is set only after the plan is on head (Gate 2 unlock).
13. `/pre-implement` and `/loop-spec` require spec PR **merged** with
    `spec-lgtm` on merge head and board tickets seeded — not an open Draft spec
    PR branch.
14. ADR signals contain actual file paths/digests; target paths or future
    promotion tasks are not artifacts.
15. When the pin expects forge readiness, fill `handoff.forge` per
    [`forge-side-effects.md`](forge-side-effects.md). Executors are human
    forge skills or ForgeClient — not the content skill’s success path.

## Outcome vocabulary

- `pass` — stage criteria are satisfied.
- `findings` — durable findings require a workflow-defined resolution path.
- `needs-input` — required information is unavailable.
- `blocked` — an explicit gate prevents progress.
- `stale` — durable authority (H1–H3 / G* / head / tip) no longer matches.
- `failed` — execution or verification failed.
- `skipped` — stage is legitimately inapplicable with a recorded reason.

Stage-specific statuses such as `PR READY`, `approved`, or `partial` belong
under `signals`; they map to one of the standard outcomes.
