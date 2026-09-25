# Greenfield walkthrough

How to start a brand-new project on this harness kit, from empty directories to
your first implemented initiative — using **Claude Code in VSCode**.

The kit runs a two-workspace model (same as upstream launchpad):

| Workspace | Profile | Who works here | Purpose |
|---|---|---|---|
| `<client>-meta` | `meta-pm` | PM lane | PRDs, validation reports, impact maps |
| service repo(s) | `python-backend` | Dev lane | Specs, ADRs, code, tests |

**Do not mix lanes.** PM skills run only in the meta repo; dev skills run only
in app repos. Running a skill in the wrong tree is the most common failure mode.

---

## Prerequisites

- Python 3.10+ with PyYAML (`python3 -c "import yaml"` must succeed)
- git
- VSCode with the **Claude Code** extension (skills appear as `/slash-commands`)
- This kit cloned somewhere, e.g. `~/Documents/workspace/skills_launchpad`

Throughout, `harness` means `<kit>/bin/harness`. Add it to your PATH if you like:

```bash
export PATH="$HOME/Documents/workspace/skills_launchpad/bin:$PATH"
```

---

## Day 0 — create the two workspaces

Pick a client/programme slug. We'll use `acme` and a first service `acme-orders`.

### 1. Meta repo (PM workspace)

```bash
mkdir -p ~/Workspace/acme/acme-meta && cd ~/Workspace/acme/acme-meta
git init -b main
mkdir -p prd/reports
echo "# acme-meta — programme PRDs and reports" > README.md

harness apply --repo . --profile meta-pm            # preview (dry-run)
harness apply --repo . --profile meta-pm --apply    # execute
harness status --repo .                             # ✔ harness OK

git add -A && git commit -m "Seed meta-pm harness"
```

The `layout` in `.harness/profile.yaml` tells the PM skills where things live:
PRDs in `prd/`, generated reports in `prd/reports/`.

### 2. Service repo (dev workspace)

Create the layout the `python-backend` profile expects
(see `layout:` in [profiles/python-backend.yaml](../profiles/python-backend.yaml)):

```bash
mkdir -p ~/Workspace/acme/acme-orders && cd ~/Workspace/acme/acme-orders
git init -b main
mkdir -p src \
         docs/specification/{product,adr,reports,as-built} \
         tests/{unit,verify,fixtures,debug}
echo "# acme-orders" > README.md
echo "# Testing harness — how to run unit and live-verify tests" > tests/README.md
echo "# Implementation status (as-built)" > docs/specification/as-built/implementation-status.md

harness apply --repo . --profile python-backend --apply
harness status --repo .

git add -A && git commit -m "Seed python-backend harness"
```

### 3. What `apply` installed

| Path | What it is |
|---|---|
| `CLAUDE.md` | Managed block between `<!-- harness:start/end -->`. Imports all 15 constitution rules. Anything you write *outside* the markers is yours and survives re-apply. |
| `.claude/rules/*.md` | The constitution (architecture, typing, DI, testing, …). **Read-only** — upgrades come from the kit. |
| `.claude/skills/<name>` | Symlinks that make skills callable as `/spec-draft`, `/loop-spec`, … |
| `.harness/skills/` | Skill sources (the hub the symlinks point into) |
| `.harness/references/` | `workflow.yaml`, `delivery-contract.yaml`, id conventions, handoff contracts |
| `.harness/profile.yaml` | Layout defaults every skill reads (spec dirs, test dirs) |
| `.harness-pin.yaml` | Pin: kit version + sha256 of every installed file |

### 4. Sanity check in VSCode

Open the repo in VSCode, start Claude Code, and:

- type `/` — you should see the profile's skills (`/spec-draft`, `/pre-implement`, …)
- ask *"what next?"* — Claude reads `.harness/references/workflow.yaml` plus any
  persisted handoff and tells you the current delivery stage.

---

## Day 1 — first initiative, PM lane (in `acme-meta`)

Work happens in initiative units with ids like `INIT-001`
(see `.harness/references/id-conventions.md`).

1. **Write the PRD** — draft `prd/INIT-001-<slug>.md` yourself, or use
   `/prd-think` to structure the problem before writing.
2. **`/prd-quality`** — quality pass on the draft.
3. **`/validate-requirements`** — audits PRD completeness; writes a findings
   report to `prd/reports/`.
4. **`/review-findings`** — you (PM) decide on each finding.
5. **`/update-documents`** — applies the accepted decisions to the PRD.
6. **`/prd-impact-map`** — maps PRD capabilities to target repos
   (`acme-orders`) and produces the handoff the dev lane starts from.
7. **Commit** via `/commit-workspace` (or plain git). If you use GitHub PRs for
   PRD review, `/open-draft-pr` opens the draft PR.

Gate: the PRD is reviewed/approved (in a greenfield solo setup, that's you
deciding it's ready). Only then does the dev lane start.

---

## Day 1 — same initiative, dev lane (in `acme-orders`)

Run these in order; each skill persists a handoff so *"what next?"* always works:

| Step | Skill | Output |
|---|---|---|
| 1 | `/spec-draft` | `docs/specification/product/INIT-001.md` — PRD translated into repo-scoped `REQ-*` rows. **Review and edit it yourself** — it's a starting point, not truth. |
| 2 | `/initiative-feasibility` | Read-only buildability triage → `docs/specification/reports/Initiative-Feasibility-Report-*.md` |
| 3 | `/spec-technical-review` | Design options + ADRs in `docs/specification/adr/`, bound to approved REQs |
| 4 | `/spec-implementation-plan` | Wave plan + WorkManifest → `docs/specification/reports/Implementation-Plan-*.md` |
| 5 | `/pre-implement` | Gate-only preflight before each wave (no code) |
| 6 | `/loop-spec` | The build loop: implement → check/unit-test → fix, wave by wave |
| 7 | `/ground-spec` | Grounds each implemented REQ against reality; sign-off package |
| 8 | `/learning-extract` | Structured `L-*` learnings at closeout |

Two hard rules the harness enforces by convention:

- **Content skills never touch git/GitHub.** Commits, pushes, PRs, labels go
  through the forge skills (`/commit-workspace`, `/open-draft-pr`,
  `/create-board-tickets`) or through you.
- **Specs before code.** `/loop-spec` implements only what the approved spec
  slice and plan cover. New scope → back to the PRD/spec, not into the diff.

### Trimming ceremony for a small/solo greenfield

The full pipeline assumes a team with review gates. Solo, a sensible minimum is:

```
/spec-draft → edit spec → /spec-implementation-plan → /loop-spec → /ground-spec
```

Skip `/initiative-feasibility` (trivial builds) and `/spec-technical-review`
(no competing design options yet); keep them from the second initiative on.
`/create-board-tickets` and label-driven gates assume a GitHub project board —
ignore them until you have one.

---

## Day N — maintenance

**Verify a repo** (CI-friendly; exits non-zero on drift):

```bash
harness status --repo ~/Workspace/acme/acme-orders
```

**Upgrade the kit** (rules or skills changed): bump `VERSION` in the kit, then
re-apply and commit the diff in each consuming repo:

```bash
harness apply --repo ~/Workspace/acme/acme-orders --profile python-backend --apply
git -C ~/Workspace/acme/acme-orders add -A && git -C ~/Workspace/acme/acme-orders commit -m "Harness → v$(cat <kit>/VERSION)"
```

**Add a second service**: repeat Day 0 step 2 with a new repo name.
**Add a new stack** (e.g. Next.js): add `rules/<stack>/`, a
`profiles/<stack>.yaml`, and register it in `CONSTITUTION_BY_PROFILE` in
[harness.py](../harness.py) — see "Extending" in the [README](../README.md).

**Close an initiative**: after all waves are accepted,
`/purge-initiative-artifacts-app` (app repos) and
`/purge-initiative-artifacts-meta` (meta repo) delete the working papers that
were only needed during delivery.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Skill isn't offered as `/command` | `.claude/skills/<name>` symlink broken — `harness status` reports it; re-run `apply --apply`. |
| `status` reports `drift:` | Someone edited an installed file in the repo. Harness files are read-only by convention — change them in the kit, then re-apply. Re-apply also heals the drift. |
| Skill writes to wrong paths | Wrong profile for this repo, or you edited `.harness/profile.yaml` locally — fix the profile in the kit. |
| PM skill run in an app repo (or vice versa) | Lanes are workspace-bound. Move to the right repo; the skills read `.harness/profile.yaml` to know which lane they're in. |
| Claude ignores a rule | Check the rule is imported in the `CLAUDE.md` managed block (`@.claude/rules/...`) and the block markers are intact. |
