# References — shared delivery contracts

[references/](../references/) holds the **cross-skill contracts**: the data
formats and conventions every skill obeys, so lanes and runtimes interoperate.
`harness apply` copies the whole directory to `<repo>/.harness/references/`,
and skills cite these files by that path at run time.

Rules govern *code*; skills govern *procedure*; references govern the
**interfaces between skills** — ids, handoffs, artifacts, workflow navigation.

## The two YAML anchors

### [workflow.yaml](../references/workflow.yaml) — the delivery graph

`kind: SkillWorkflow` (`id: sdd-delivery`). A graph of nodes, each one of:

- `type: skill` — a stage a skill executes (with `profile:` naming its lane,
  `dispatch: manual | orchestrated`, and a `forge:` mutation policy);
- `type: external-action` — a git/GitHub mutation (PR open, labels, merge);
- `type: human-checkpoint` — a human decision; agents stop here.

Each node's `outcomes:` map (`pass`, `findings`, `needs-input`, `failed`, …)
points to the next node. `entrypoints:` name where each lane starts
(`meta-pm: validate-requirements`, `development: spec-draft`). Combined with
the latest persisted handoff, this graph is how the agent answers
*"what next?"* — navigation lives here, never hardcoded in skill text.

### [delivery-contract.yaml](../references/delivery-contract.yaml) — the meta-contract

`kind: DeliveryContract` (`sdd-delivery/v2`, recorded in `.harness-pin.yaml`).
Declares which workflow file applies and which spec governs each interface
(handoff, forge, prompt packages, WorkManifest), the legal outcome vocabulary,
and the WorkManifest identity/validator. If workflow.yaml is the map,
this file is the legend.

## Contracts (markdown, each an SSOT)

| File | Governs |
|---|---|
| [id-conventions.md](../references/id-conventions.md) | The id vocabulary every skill must use: initiative (`INIT-*`), product (`CAP-*`, `J-*`, `REQ-*`), process/report, and delivery ids. |
| [handoff-envelope.md](../references/handoff-envelope.md) | The YAML handoff block every stage persists in its output artifact — durable workflow state (chat is not state). |
| [artifact-write-contract.md](../references/artifact-write-contract.md) | Canonical paths for files skills create; git history is the archive — no `*-revN` sibling files in `reports/`. |
| [forge-side-effects.md](../references/forge-side-effects.md) | The mutation policy: which git/GitHub side effects each workflow node may perform, and why content skills perform none. |
| [workmanifest-contract.md](../references/workmanifest-contract.md) | The WorkManifest: immutable, approved execution intent (epic/waves/tasks/deps/exit proof) seeded by `/spec-implementation-plan` §9. |
| [prompt-package-contract.md](../references/prompt-package-contract.md) | The `prompts/` package every skill ships: `schema.yaml` (inputs), `template.md` (invocation brief), `fixtures/` (examples). |
| [quality-confidence-ladder.md](../references/quality-confidence-ladder.md) | Stack-agnostic rungs of product confidence as the environment gets more real (unit → live verify → …). |
| [live-fixture-contract.md](../references/live-fixture-contract.md) | What a fixture pack must contain so live verification is stimulus + observe, not a bare health curl. |
| [live-verify-coverage-contract.md](../references/live-verify-coverage-contract.md) | How `tests/verify` artifacts self-declare their `CAP-*`/`J-*`/`REQ-*` coverage so it survives artifact purges. |
| [codegraph-tool-contract.md](../references/codegraph-tool-contract.md) | Optional interface for a code-graph/knowledge-graph tool a skill may use during a hop (a Tool, not Forge). |

## Change discipline

These files are single sources of truth: change a contract **in the kit**, and
treat it like an interface change — check every skill that cites it (grep the
filename under `skills/`), bump [VERSION](../VERSION), re-apply to consumer
repos. Contracts referenced from `.harness-pin.yaml` (`delivery_contract:
sdd-delivery/v2`) version explicitly; bump the version id on breaking changes.

Some contracts mention upstream orchestration (Gateflow, board labels,
`dispatch: orchestrated`). Those parts are inert in this kit — everything here
runs `dispatch: manual` via a human in Claude Code — but they are kept so the
content stays merge-able with upstream prayog-skills.
