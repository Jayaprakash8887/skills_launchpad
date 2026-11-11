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

**Optional EGM review.** Every step below works without it. With the `egm`
add-on (Google's Elephant-Goldfish Model), you can also have fresh reviewer
agents check the PRD, the TDD and the plan before the human checkpoints, and
check the code against the spec after each wave. Steps marked **EGM** are only
for repos seeded `--with egm`; see [addons.md](addons.md).

Adding the kit to a project that already has code? Read
[existing-project.md](existing-project.md) first.

---

## Prerequisites

- Python 3.10+ with PyYAML (`python3 -c "import yaml"` must succeed)
- git
- VSCode with the **Claude Code** extension (skills appear as `/slash-commands`)
- This kit cloned somewhere, e.g. `~/Documents/workspace/skills_launchpad`
- **EGM only:** Claude Code **2.1.271 or later**. Older versions silently
  break the reviewers' isolation.
  - The VS Code extension bundles its own Claude Code, which is usually current.
  - The `claude` on your PATH can be much older; check with `claude --version`
    and run `claude update`. That matters for headless (`claude -p`) runs.
  - `harness status` reports both versions.

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
# EGM: harness apply --repo . --profile meta-pm --with egm --apply
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
# EGM: harness apply --repo . --profile python-backend --with egm --apply
harness status --repo .

git add -A && git commit -m "Seed python-backend harness"
```

With `--with egm`, commit `.claude/settings.json` too, so everyone who clones
the repo gets the same pinned plugin and permission rules.

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
| `.claude/settings.json` | **EGM only.** Enables the EGM plugin pinned to a release tag, lets its reviewers read their rubric files, and denies reads of `.env`. Your own entries in this file are kept. |
| `.harness/addons/egm/` | **EGM only.** `gates.yaml` (where each review fits in the workflow) and `integration.md` (rules for using EGM well). The `CLAUDE.md` block gains an EGM section listing this repo's gates. |

### 4. Sanity check in VSCode

Open the repo in VSCode, start Claude Code, and:

- type `/` — you should see the profile's skills (`/spec-draft`, `/pre-implement`, …)
- ask *"what next?"* — Claude reads `.harness/references/workflow.yaml` plus any
  persisted handoff and tells you the current delivery stage.

**EGM only:**

1. The first time you open the repo, Claude Code asks whether you trust the
   folder. It then offers to install the `egm` marketplace and plugin listed in
   `.claude/settings.json`. Accept both.
2. Start a new Claude Code session. Plugin commands and agents load only when a
   session starts.
3. Type `/egm`. You should see `/egm:egm-review`, `/egm:egm-resolve`,
   `/egm:egm-drift-report` and the others.
4. Run `harness status --repo .`. Its `·` lines confirm the Claude Code version
   and the installed plugin, and `⚠` lines say what to fix.

---

## Day 1 — first initiative, PM lane (in `acme-meta`)

Work happens in initiative units with ids like `INIT-001`
(see `.harness/references/id-conventions.md`).

1. **Write the PRD** — draft `prd/INIT-001.md` yourself, or use
   `/prd-think` to structure the problem before writing. Keep the file name
   exactly `prd/INIT-<id>.md`: `/prd-impact-map` and the purge skill look for
   that name.
2. **`/prd-quality`** — quality pass on the draft.
   - **EGM (optional): `prd-review`.** Have fresh reviewers check the PRD, then
     apply what you accept with `/egm:egm-resolve` (prompts below). Questions
     only the product owner can answer go to the usual requirements decision.
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

**EGM prompts for `prd-review`** (in Claude Code, in `acme-meta`):

```text
/egm:egm-review prd/INIT-001.md
EGM artifact directory: prd/reports/egm/INIT-001/prd-review/
Use the preset "Feature spec only".
```

When the report is written, resolve it in the same session, preferably the one
that wrote the PRD:

```text
/egm:egm-resolve
EGM artifact directory: prd/reports/egm/INIT-001/prd-review/
```

EGM asks one question at a time. Answer them yourself; that is where the
review's value comes from. Reviewers see only the PRD and the files it links
to, so link anything they need, such as an existing system's docs, with a
relative path.

---

## Day 1 — same initiative, dev lane (in `acme-orders`)

Run these in order; each skill persists a handoff so *"what next?"* always works:

| Step | Skill | Output |
|---|---|---|
| 1 | `/spec-draft` | `docs/specification/product/INIT-001.md` — PRD translated into repo-scoped `REQ-*` rows. **Review and edit it yourself** — it's a starting point, not truth. |
| 2 | `/initiative-feasibility` | Read-only buildability triage → `docs/specification/reports/Initiative-Feasibility-Report-*.md` |
| 3 | `/spec-technical-review` | TDD → `docs/specification/reports/Technical-Review-INIT-001.md`, plus Draft ADRs in `docs/specification/adr/`, bound to approved REQs |
| 3a | **EGM `design-review`** (optional) | Fresh reviewers check the TDD → `docs/specification/reports/egm/INIT-001/design-review/`. Resolve with `/egm:egm-resolve` **before** the PE accepts the TDD and ADRs. |
| 4 | `/spec-implementation-plan` | Wave plan + WorkManifest → `docs/specification/reports/Implementation-Plan-INIT-001.md` |
| 4a | **EGM `plan-review`** (optional, **one round**) | Implementation-readiness check of the plan → `…/egm/INIT-001/plan-review/`. Resolve before coding readiness. |
| 5 | `/pre-implement` | Gate-only preflight before each wave (no code) |
| 6 | `/loop-spec` | The build loop: implement → check/unit-test → fix, wave by wave |
| 7 | `/ground-spec` | Grounds each implemented REQ against reality; sign-off package |
| 7a | **EGM `drift-report`** (optional, each wave) | Code vs spec differences → `…/egm/INIT-001/drift-W<N>/`. Link it from the Ground Report. |
| 8 | `/learning-extract` | Structured `L-*` learnings at closeout |

**EGM prompts for the dev lane** (in `acme-orders`). Each gate gets its own
artifact directory, because EGM overwrites its reports:

```text
/egm:egm-review docs/specification/reports/Technical-Review-INIT-001.md
EGM artifact directory: docs/specification/reports/egm/INIT-001/design-review/
Use the preset "Feature spec only".
```

```text
/egm:egm-review docs/specification/reports/Implementation-Plan-INIT-001.md
EGM artifact directory: docs/specification/reports/egm/INIT-001/plan-review/
Use the preset "Implementation plan only". The detailed plan starts at the
heading "## 2. Implementation phases".
```

```text
/egm:egm-drift-report docs/specification/
EGM artifact directory: docs/specification/reports/egm/INIT-001/drift-W0/
The code is in src/ and tests/. List every DESIGN-GAP comment as a divergence.
Do not change any file other than the report.
```

After each review, run `/egm:egm-resolve` with the same artifact-directory line.
Three habits make the gates pay off:

- **The TDD must link its inputs:** the product spec, the feasibility report and
  the Draft ADRs, as relative paths. The reviewers read nothing else.
- **Review the plan once.** A second round on a code-level plan tends to produce
  new findings from the first round's fixes. The wave's tests check that level
  better.
- **During `/loop-spec`, leave a `DESIGN-GAP:` comment** wherever the plan does
  not settle a point, and make the smallest reasonable choice. The drift report
  lists every marker, so the spec can be corrected after the wave.

More rules, including secrets and usage limits:
`.harness/addons/egm/integration.md` in the seeded repo.

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

**Solo with EGM.** Fresh reviewers are most useful when nobody else reviews
your work. Keep two things:

1. **One review of the design before planning.** With no TDD, run
   `/egm:egm-review` on `docs/specification/product/INIT-001.md` with the
   "Feature spec only" preset. That is where the expensive mistakes surface:
   wrong assumptions about systems you integrate with, missing failure cases,
   access rules that lock users out.
2. **The drift report after each wave.**

Skip the plan review until plans get large.

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

Add-ons recorded in the pin (such as `egm`) are kept on re-apply; you don't
need to repeat `--with`. To add EGM to an already-seeded repo later, re-apply
with `--with egm`. To remove it, re-apply with `--without egm`.

**Add a second service**: repeat Day 0 step 2 with a new repo name.
**Add a new stack** (e.g. Next.js): add `rules/<stack>/`, a
`profiles/<stack>.yaml`, and register it in `CONSTITUTION_BY_PROFILE` in
[harness.py](../harness.py) — see "Extending" in the [README](../README.md).

**Close an initiative**: after all waves are accepted,
`/purge-initiative-artifacts-app` (app repos) and
`/purge-initiative-artifacts-meta` (meta repo) delete the working papers that
were only needed during delivery. The purge skills do not know about EGM's
folders yet, so also delete `docs/specification/reports/egm/INIT-<id>/` and
`prd/reports/egm/INIT-<id>/` by hand.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Skill isn't offered as `/command` | `.claude/skills/<name>` symlink broken — `harness status` reports it; re-run `apply --apply`. |
| `status` reports `drift:` | Someone edited an installed file in the repo. Harness files are read-only by convention — change them in the kit, then re-apply. Re-apply also heals the drift. |
| Skill writes to wrong paths | Wrong profile for this repo, or you edited `.harness/profile.yaml` locally — fix the profile in the kit. |
| PM skill run in an app repo (or vice versa) | Lanes are workspace-bound. Move to the right repo; the skills read `.harness/profile.yaml` to know which lane they're in. |
| Claude ignores a rule | Check the rule is imported in the `CLAUDE.md` managed block (`@.claude/rules/...`) and the block markers are intact. |
| **EGM:** `/egm:` commands don't appear | Run `harness status`. The usual causes: the plugin isn't installed (accept the prompt, or run `claude plugin install egm@egm --scope project`), Claude Code is older than 2.1.271, or the session started before the install. Start a new session. |
| **EGM:** permission prompts for files under `~/.claude/plugins/cache/egm/` | The four plugin read rules are missing from `.claude/settings.json`. `harness status` names them; re-apply to restore them. |
| **EGM:** a headless `claude -p` run ignores the rules | Project permission rules apply only after the folder is trusted. Open the repo once in the terminal CLI and trust it, or pass the rules with `--allowedTools`. |
| **EGM:** a reviewer says it cannot see something | Reviewers read only the target file and the files it links to. Add a relative link in the target document. |
| **EGM:** two reviews overwrote each other's reports | They shared an artifact directory. Give every document and gate its own `…/egm/<INIT>/<gate>/`. |
| **EGM:** a report says "resolved" but the document hasn't changed | The turn was cut off, often by a usage limit. Compare the report with the document, then resume the session and ask it to apply what is missing. |
| Claude refuses to read `.env` | Intended: the `egm` add-on denies it because reviewers search the whole folder. Put documented settings in `.env.example`. |
