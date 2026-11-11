# skills_launchpad

**Harness kit for spec-driven development with Claude Code in VSCode** — pinned
rules (constitution) + agent skills, seeded into any repo with one command.

A VSCode/Claude Code adaptation of
[drivestream-lab/launchpad](https://github.com/drivestream-lab/launchpad)'s
`apply-harness`, reusing content from
[prayog-skills](https://github.com/drivestream-lab/prayog-skills) and
[python-services-rules](https://github.com/drivestream-lab/python-services-rules)
(see [NOTICE.md](NOTICE.md)). No GitHub org automation — just the harness.

**Starting a new project?** Follow the [greenfield walkthrough](docs/greenfield.md).
**Understanding the pieces?** See the [documentation index](docs/README.md) —
[architecture](docs/architecture.md) · [rules](docs/rules.md) · [skills](docs/skills.md) ·
[profiles](docs/profiles.md) · [references](docs/references.md) · [CLI](docs/cli.md) ·
[add-ons](docs/addons.md).

## What it does

```bash
bin/harness list                                        # profiles + skills + add-ons
bin/harness apply  --repo ~/code/my-service --profile python-backend   # dry-run
bin/harness apply  --repo ~/code/my-service --profile python-backend --apply
bin/harness apply  --repo ~/code/my-service --profile python-backend --with egm --apply
bin/harness status --repo ~/code/my-service             # verify against pin
```

`apply` writes into the target repo (all committed, no submodules):

| Path | Purpose |
|---|---|
| `.claude/rules/*.md` | Constitution — coding rules, always loaded via `CLAUDE.md` imports |
| `.claude/skills/<name>` | Claude Code skills (`/spec-draft`, `/loop-spec`, …) — symlinks into the hub |
| `.harness/skills/<name>/` | Skill sources (hub — real copies) |
| `.harness/references/` | Shared contracts: `workflow.yaml`, id conventions, handoff envelope, … |
| `.harness/profile.yaml` | Repo layout defaults the skills read (spec dirs, test dirs) |
| `.harness-pin.yaml` | Pin record: kit version + sha256 manifest of every installed file |
| `CLAUDE.md` | Managed block between `<!-- harness:start/end -->` markers (team content outside the markers is kept) |
| `.harness/addons/<name>/` | Only with `--with <name>`: add-on sources, such as EGM's review gates and usage rules |
| `.claude/settings.json` | Only with an add-on: its entries are merged in (team entries are kept) |

`status` re-hashes every pinned file and reports **drift**, missing files,
broken skill symlinks, a missing managed block, or missing add-on settings.

## Add-ons

| Add-on | What it adds |
|---|---|
| `egm` | Google's [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model) plugin, pinned to `v0.1.1`. It adds optional fresh-context review gates on the PRD, the TDD and the implementation plan, plus a drift check of the code after each wave. The gates are anchored to the existing workflow without changing it. See [docs/addons.md](docs/addons.md). |

## Profiles

| Profile | Workspace | Constitution | Skills |
|---|---|---|---|
| `python-backend` | App/service repo | `rules/python-backend/` (15 rules) | dev lane: `/spec-draft` → `/initiative-feasibility` → `/spec-technical-review` → `/spec-implementation-plan` → `/pre-implement` → `/loop-spec` → `/ground-spec` → `/learning-extract` + forge skills |
| `meta-pm` | `<client>-meta` PM repo | none | requirements lane: `/prd-think`, `/prd-quality`, `/validate-requirements`, `/review-findings`, `/update-documents`, `/prd-impact-map` + forge skills |

Two lanes — do not mix. PM skills run in the meta repo; dev skills run in app
repos. Forge skills (`/commit-workspace`, `/open-draft-pr`,
`/create-board-tickets`) are the only ones allowed to touch git/GitHub.

## Using it in VSCode

Open the seeded repo in VSCode with the Claude Code extension. The constitution
loads automatically through `CLAUDE.md`; skills appear as `/slash-commands`.
Typical dev flow after a PRD is approved:

```
/spec-draft → review/edit spec → /initiative-feasibility → /spec-technical-review
→ /spec-implementation-plan → /pre-implement → /loop-spec → /ground-spec
```

## Extending

- **New stack**: add `rules/<stack>/*.md`, a `profiles/<stack>.yaml`, and map it
  in `CONSTITUTION_BY_PROFILE` in [harness.py](harness.py).
- **New skill**: add `skills/<lane>/<name>/SKILL.md` (+ optional `prompts/`,
  `references/`) and list it in the relevant profile.
- **New add-on**: add `addons/<name>/addon.yaml` (+ optional `gates.yaml`,
  `CLAUDE.addon.md`). See [docs/addons.md](docs/addons.md#writing-a-new-add-on).
- **Upgrade a repo**: edit the kit, bump [VERSION](VERSION), re-run
  `apply --apply`, commit the diff in the target repo. Pinned add-ons are kept.
- **Tests**: `python3 -m unittest discover -s tests`.

## Layout

```
harness.py            CLI (list / apply / status)
bin/harness           launcher
profiles/             stack-key → skills + repo layout defaults
rules/<stack>/        constitution rules per stack
skills/<lane>/<name>/ SKILL.md + prompts + references
references/           shared contracts incl. workflow.yaml, delivery-contract.yaml
addons/<name>/        optional add-ons (addon.yaml, gates.yaml, CLAUDE.addon.md, docs)
templates/            CLAUDE.md managed-block template
tests/                unittest suite for harness.py
```
