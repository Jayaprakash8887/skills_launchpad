# Skills — procedural workflows

`skills/<lane>/<name>/` are **agent skills**: step-by-step procedures the agent
runs when you type `/<name>` in Claude Code. Adapted from
[prayog-skills](https://github.com/drivestream-lab/prayog-skills).

Rules say **how code must look**; skills say **what steps a delivery stage
runs**. A skill never overrides the constitution.

## Three lanes

| Lane | Directory | Runs in | Skills |
|---|---|---|---|
| **Requirements (PM)** | [skills/requirements/](../skills/requirements/) | `<client>-meta` repo | `prd-think`, `prd-quality`, `validate-requirements`, `review-findings`, `update-documents`, `prd-impact-map`, `purge-initiative-artifacts-meta` |
| **Development** | [skills/development/](../skills/development/) | app/service repos | `spec-draft`, `initiative-feasibility`, `spec-technical-review`, `spec-implementation-plan`, `pre-implement`, `loop-spec`, `ground-spec`, `learning-extract`, `purge-initiative-artifacts-app` |
| **Forge** | [skills/forge/](../skills/forge/) | both | `commit-workspace`, `open-draft-pr`, `create-board-tickets` |

The hard boundary: **content skills (requirements + development) only change
the local workspace**. Anything that mutates git or GitHub — branch, commit,
push, PR, labels, board — belongs exclusively to forge skills or the human.
This is what makes agent runs auditable: you can always diff what a content
skill did before anything is published.

## Anatomy of a skill

```
skills/development/loop-spec/
├── SKILL.md                      # the procedure (frontmatter + steps)
├── prompts/                      # versioned invocation brief
│   ├── schema.yaml               #   inputs the skill expects
│   ├── template.md               #   canonical invocation prompt
│   └── fixtures/                 #   example inputs + expected outputs
│       ├── happy_path.inputs.yaml
│       └── happy_path.expected.md
└── references/                   # (optional) skill-local reference docs,
                                  #   e.g. layout-defaults.md, templates
```

### SKILL.md frontmatter

```yaml
---
name: spec-draft
description: >-            # when to use it — Claude reads this to offer/route
disable-model-invocation: true   # only a human /command triggers it (most skills)
paths: CLAUDE.md, docs/specification/**, .claude/rules/**   # files it touches
background_eligible: true        # (some) safe for orchestrated dispatch
background_trigger: "..."        # condition an orchestrator would key on
---
```

`disable-model-invocation: true` on nearly every skill is deliberate: delivery
stages are **human-initiated**; the agent must not decide on its own to, say,
start implementing.

## How a skill knows where things live

Skills never hardcode repo paths. At run time they read:

- **`.harness/profile.yaml`** — layout defaults for this repo (spec dirs,
  report prefixes, test dirs). See [profiles.md](profiles.md).
- **`.harness/references/`** — cross-skill contracts: id formats, the handoff
  envelope, artifact write paths. See [references.md](references.md).

## Handoffs — how "what next?" works

Every skill ends by **persisting a handoff** (format:
[references/handoff-envelope.md](../references/handoff-envelope.md)) recording
the stage it completed, its outcome, and forge-readiness. The pinned
[references/workflow.yaml](../references/workflow.yaml) is a graph of nodes
(`type: skill | external-action | human-checkpoint`) whose `outcomes:` map
results to next nodes. Ask Claude *"what next?"* and it resolves: latest
handoff × workflow graph → current stage, blockers, next candidate.

This is why skills stay portable across runtimes (Claude Code, Cursor, Codex):
navigation lives in data (workflow + handoff), not in the skill text.

## Adding a skill

1. Create `skills/<lane>/<name>/SKILL.md` (+ `prompts/`, `references/` as
   needed). Follow
   [references/prompt-package-contract.md](../references/prompt-package-contract.md).
2. Add the name to the relevant profile list (`development_skills`,
   `requirements_skills`, or `forge_skills`).
3. If it's a workflow stage (not a utility), add its node and outcome edges to
   `references/workflow.yaml`.
4. Bump [VERSION](../VERSION) and re-apply to consuming repos.
