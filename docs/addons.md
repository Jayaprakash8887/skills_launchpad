# Add-ons

An add-on is an optional piece applied on top of a profile with `--with NAME`. It can enable a
Claude Code plugin, ship guidance into the repo, and add review gates to the lanes. The kit has
one add-on today: **`egm`**.

```bash
harness apply --repo ~/code/my-service --profile python-backend --with egm          # preview
harness apply --repo ~/code/my-service --profile python-backend --with egm --apply
harness status --repo ~/code/my-service
```

## The `egm` add-on

[EGM](https://github.com/google/elephant-goldfish-model) (Elephant-Goldfish Model, Google,
Apache-2.0) is a Claude Code plugin for design review:

- **The Elephant** is the session that holds the context and writes a document.
- **The Goldfish** are fresh, read-only reviewer agents. Each sees only the document and the
  files it links to.

The kit's lanes already write the documents. EGM adds what they lack:

- independent review of those documents before the human checkpoints;
- a check of the code against them after each wave.

The add-on comes from a trial that took the CCE v2 admin-module PRD through EGM to two working
services. In that trial:

- **The review caught integration-breaking errors before any code.** These included a wrong
  database schema, a table shape that didn't match the gateway's, and every existing user
  locked out.
- **It also showed EGM's limits.** Review rounds on a code-level plan did not converge, and
  usage limits stopped long sessions mid-turn.

The gates and rules below encode both.

### What `--with egm` does

| Step | Result in the target repo |
|---|---|
| Copy [addons/egm/](../addons/egm/) | `.harness/addons/egm/` with `addon.yaml`, `gates.yaml`, `integration.md` (pinned in the manifest like everything under `.harness/`) |
| Merge settings | `.claude/settings.json` gains the EGM marketplace pinned to tag `v0.1.1`, `enabledPlugins` `egm@egm`, four read rules for the plugin cache (the reviewers read their rubrics from there), and a `Read(**/.env)` deny rule (the reviewers search the whole folder). Team entries are kept: objects merge key by key, lists are unioned. |
| Render CLAUDE.md | The managed block gains an "Add-on: EGM" section listing the commands and the gates for this profile, with paths from `.harness/profile.yaml` |
| Pin | `.harness-pin.yaml` gains `addons: {egm: {plugin, plugin_version, marketplace_ref}}` |

The plugin itself is not bundled. When someone opens the repo in Claude Code and trusts the
folder, Claude Code offers to install the pinned marketplace and plugin.

### Gates

The gates are defined in [addons/egm/gates.yaml](../addons/egm/gates.yaml). They are optional
and run by hand, because only a person can start an EGM command. They **do not change**
`references/workflow.yaml`: skills still compute their next step from the pinned
`sdd-delivery/v2` graph. Each gate is anchored to existing nodes, and its outcomes route to
existing checkpoints.

| Gate | Profile | Anchor | Command and preset | Findings go to |
|---|---|---|---|---|
| `prd-review` | meta-pm | before `validate-requirements` | `/egm:egm-review` on `prd/<INIT>.md`, *Feature spec only* | `/egm:egm-resolve`, then `validate-requirements`; open product questions → `requirements-human-decision` |
| `design-review` | python-backend | after `spec-technical-review`, before `technical-review-approval` | `/egm:egm-review` on `Technical-Review-<INIT>.md`, *Feature spec only* | `/egm:egm-resolve`, then the PE accepts the resolved TDD; open questions → `spec-human-decision` |
| `plan-review` | python-backend | after `spec-implementation-plan`, before `coding-readiness` | `/egm:egm-review` on `Implementation-Plan-<INIT>.md`, *Implementation plan only*, **one round** | `/egm:egm-resolve`, then `coding-readiness` |
| `drift-report` | python-backend | after `ground-spec`, before `wave-done-action` | `/egm:egm-drift-report` on the spec root | Linked from the Ground Report; spec changes → `spec-human-decision`, code fixes → next wave's `/pre-implement` |

Each gate writes to its own folder, `{reports_dir}/egm/<INIT>/<gate>/`, because EGM overwrites
its reports.

The rules for using EGM inside a repo ship as
[addons/egm/integration.md](../addons/egm/integration.md). They cover linking inputs, contract
ownership, one plan round, `DESIGN-GAP` markers, secrets and usage limits.

### What `status` checks

- **Fails** (non-zero exit) if any settings entry from `addon.yaml` is missing from
  `.claude/settings.json`, or if the installed `addon.yaml` is missing or has drifted.
- **Warns** (never fails) about this machine:
  - a Claude Code older than 2.1.271, checked both on PATH and in the VS Code extension
    (older versions silently break reviewer isolation);
  - the plugin not being installed yet.

### Re-apply, upgrade, remove

- **Re-apply.** Add-ons recorded in the pin are kept when you re-apply without `--with`, so
  the usual kit upgrade (`apply --apply`) does not drop EGM.
- **Upgrade EGM:**
  1. In [addons/egm/addon.yaml](../addons/egm/addon.yaml), change `ref` under
     `extraKnownMarketplaces` and `plugin_version`. Change `min_claude_code` too if upstream
     changed it.
  2. Bump [VERSION](../VERSION) and re-apply.
  3. A test checks that `ref` is `v<plugin_version>`.
- **Remove:** `apply --without egm --apply` removes `.harness/addons/egm/`, the CLAUDE.md
  section and the pin entry. It prints the settings entries but leaves `.claude/settings.json`
  alone, because the team may rely on some of them.

## Writing a new add-on

Create `addons/<name>/` with:

| File | Required | Purpose |
|---|---|---|
| `addon.yaml` | yes | `addon` (= directory name), `title`, `profiles` it supports, and optionally `plugin` (`name@marketplace`), `plugin_version`, `min_claude_code`, `commands`, and `settings` (a fragment merged into `.claude/settings.json`) |
| `CLAUDE.addon.md` | no | Section added to the managed block. Placeholders: `{{PLUGIN}}`, `{{PLUGIN_VERSION}}`, `{{MARKETPLACE_REF}}`, `{{MIN_CLAUDE_CODE}}`, `{{COMMANDS}}`, `{{GATES}}` |
| `gates.yaml` | no | Gates with `id`, `profiles`, `after`/`before` (workflow node ids), `command`, `preset`, `rounds`, `target`, `artifact_dir` (`{reports_dir}`-style placeholders from the profile layout), `on_findings`, `on_needs_input`, `note` |
| anything else | no | Copied to `.harness/addons/<name>/` |

Then run `python3 -m unittest discover -s tests`. The tests check that every gate anchor is a
real workflow node and every gate profile exists.
