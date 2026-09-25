# Prompt package contract

Versioned **invocation briefs** for skills under `skills/requirements/`,
`skills/development/`, and `skills/forge/`. Procedure remains in each skill’s
`SKILL.md`. Prompt packages do **not** replace procedure and are **independent
of** workflow `dispatch` (see INIT-PRAYOG-SKILLS-002).

Contract id remains `sdd-delivery/v2` (CHANGELOG documents additive semantics;
no `v2.x` label).

## Coverage

| In scope | Out of scope |
|----------|--------------|
| Every skill under `skills/requirements/*` | `skills/engg-reviews/*` |
| Every skill under `skills/development/*` | Gateflow runtime bind/render (BOUNDINPUT later) |
| Every skill under `skills/forge/*` | |
| Directory inventory (see `prompt_inventory.json`) | Using `dispatch` to select coverage |

Inventory SSOT for CI: `tests/fixtures/prompt_inventory.json`.

## Layout (normative)

```text
skills/<area>/<skill-id>/     # area ∈ {requirements, development, forge}
  SKILL.md
  prompts/
    template.md
    schema.yaml
    fixtures/
      happy_path.inputs.yaml
      happy_path.expected.md
```

### `schema.yaml`

| Field | Rule |
|-------|------|
| `prompt_id` | Equals skill node id |
| `revision` | Semver `MAJOR.MINOR.PATCH` |
| `variables` | Shared dictionary names only (v1) |

**Semver bumps**

| Bump | When |
|------|------|
| MAJOR | Required variable added/removed/renamed; breaking binding change |
| MINOR | New optional variable; additive non-breaking guidance |
| PATCH | Wording / formatting only |

### Shared variables (v1 — normative `required`)

| Name | Type | Required |
|------|------|----------|
| `ticket` | string | true |
| `initiative` | string | false |
| `handoff_path` | string | true |
| `workspace` | string | true |
| `meta_workspace` | string | false |
| `skill_id` | string | true |

Missing optional → empty string at render. Per-skill deviation needs an explicit
Decision and MAJOR revision rationale.

**`workspace` vs `meta_workspace`:** `workspace` is the app coding root (product
spec / plan / code artifacts). `meta_workspace` is the prayog-meta (or
client-meta) checkout when Gateflow dual-binds on spec start. Spec-lane
orchestrated skills (`spec-draft`, `initiative-feasibility`,
`spec-technical-review`) and human `spec-implementation-plan` must surface both
in Bound context; implement-only packages may omit `{{meta_workspace}}` from
the template when Gateflow does not bind it (empty string).

**Required vs optional (intentional):** the shared dictionary keeps
`meta_workspace.required: false`. That is **not** “meta is optional on Spec
Pass-1.” Gateflow **fail-closes** when `POST /waves/spec/start` lacks a usable
meta checkout / bind. Skills CI cannot mark the var `required: true` only on
orchestrated packages without a PE Decision to allow **per-skill required
overrides** (today every package must match `SHARED_VARIABLES` exactly,
including `required`). Do not set `required: true` globally — implement-lane
binds do not send meta today.

### `template.md`

Simple `{{var}}` substitution only. No filters, conditionals, or partials.
Every `{{var}}` must be declared in `schema.yaml`.

### `handoff_path` (orchestrator baton)

`handoff_path` is **not** a read-only preference. For packaged / automated
invoke it is the **orchestrator ingest target**:

1. Persist the usual durable workspace artifact and append the `handoff:`
   envelope there (see [`handoff-envelope.md`](handoff-envelope.md)).
2. **Overwrite** `{{handoff_path}}` with the same envelope before considering
   the skill complete.
3. Do not leave `{{handoff_path}}` empty. Do not rely on docs-only or chat-only
   handoff for orchestrator continuation.
4. Prior envelope at that path may be read for context; final write replaces it.

Templates must instruct this dual-write explicitly. Golden fixtures must match.

### Envelope navigation (all packaged skills)

Templates must instruct producers to derive `next_candidates` and
`human_checkpoint` from pinned `workflow.yaml` for `(stage, outcome)` — see
[`handoff-envelope.md`](handoff-envelope.md) (**Derive from pinned workflow**).
`human_checkpoint` is `true` only when the resolved next node’s `type` is
`human-checkpoint` (never because the artifact “should be reviewed”).

## Consumer resolution (automated runs)

```text
skill = packaged skill selected for automated run
pkg   = resolve_prompt_package(pin, skill)

if pkg missing OR schema invalid:
    FAIL CLOSED

validate bound_inputs against pkg.schema.variables
message = render(pkg.template, bound_inputs)   # simple {{var}} only
outcome.prompt_id = pkg.prompt_id
outcome.prompt_revision = pkg.revision
hand_off_rendered_message(message)   # invoke skill — NOT workflow dispatch
# orchestrator persists outcome — out of this contract surface
```

**Humans** executing a skill may freeform and are **not** required to use the
package.

**Invoke ≠ `dispatch`:** “Hand off / invoke” means run the skill with the
rendered brief. Workflow `dispatch` (`manual` | `orchestrated`) only answers
orchestrator **eligibility**.

## Eval before promote

Before bumping a pin/tag that carries prompt revisions:

1. Checklist: procedure in `SKILL.md` still matches the brief intent.
2. Golden fixtures green (`happy_path` normalized match).
3. CHANGELOG lists `prompt_id@revision` for changed packages.
4. Contract tests + `scripts/check_consistency.py` pass.

## Tooling

| Path | Role |
|------|------|
| `scripts/prompt_contract.py` | Load/validate/render/compare |
| `scripts/check_consistency.py` | `check_prompt_package_surface()` |
| `tests/test_prompt_contract.py` | Unit + inventory + golden suite |
| `tests/fixtures/prompt_inventory.json` | Coverage SSOT |

## Related

- [`handoff-envelope.md`](handoff-envelope.md) — persistent handoff (post-run)
- [`delivery-contract.yaml`](../delivery-contract.yaml) — `dispatch` vs prompts
- [`workflow.yaml`](../workflow.yaml) — node graph and eligibility
