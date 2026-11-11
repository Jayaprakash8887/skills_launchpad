# Using EGM in this repo

This repo has the EGM add-on from `skills_launchpad`. EGM is Google's
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model) plugin for Claude
Code (Apache-2.0):

- **The Elephant** is the session that holds the context and writes a document.
- **The Goldfish** are fresh, read-only reviewer agents. Each sees only the document and the
  files it links to.

The harness lane already writes the documents: the PRD, the TDD and the implementation plan.
EGM adds independent review of them and a drift check of the code against them.

The rules below come from a trial that took a real PRD (the CCE v2 admin module) through EGM
to two working services.

## One-time setup on each machine

1. **Use Claude Code 2.1.271 or later.** Older versions silently break reviewer isolation.
   - The VS Code extension bundles its own Claude Code.
   - The `claude` on your PATH may be older; run `claude update`.
   - `harness status` reports both versions.
2. **Install the plugin.** Open the repo in Claude Code and trust the folder. Claude Code then
   offers to install the `egm` marketplace and plugin from `.claude/settings.json`. Accept, or
   run `claude plugin install egm@egm --scope project`.
3. **For headless runs only** (`claude -p`): project permission rules are ignored until the
   folder has been trusted in the terminal CLI. Trust it once in the CLI, or pass the four
   plugin-cache read rules from `.claude/settings.json` with `--allowedTools`.

## Running a gate

The gates and their anchors are in [gates.yaml](gates.yaml). The managed block in `CLAUDE.md`
lists the ones for this profile. A prompt for the design review looks like this:

```text
/egm:egm-review docs/specification/reports/Technical-Review-INIT-001.md
EGM artifact directory: docs/specification/reports/egm/INIT-001/design-review/
Use the preset "Feature spec only".
```

EGM asks questions one at a time. A person with context answers them; that is where EGM's
value comes from. If you delegate the answers, record them.

## Rules

1. **Give each gate its own artifact directory.** EGM overwrites `design_draft.md` and its
   reports, so two documents or two gates must never share a directory.
2. **Link every input from the target document.** Reviewers read nothing else: not
   `CLAUDE.md`, not `.claude/rules/`, not the code. A fact the reviewer needs must be in the
   document or in a file it links to, using a relative path.
3. **Keep one document to one repo or one pull request.** When two documents share an
   interface (an API, a table), name the document that owns it first. The other links it and
   does not redefine it.
4. **Review the design in depth, and the plan once.**
   - Run the design review on the TDD with the "Feature spec only" preset.
   - Run the plan review once, with "Implementation plan only".
   - In the trial, repeated rounds on a code-level plan did not converge: each round's fixes
     created new findings. The compiler and the tests check that level better.
5. **Triage before resolving.** A full review can return over 100 findings, and the stages can
   disagree. Prefer remedies that remove mechanisms over ones that add them.
6. **Mark gaps while implementing.**
   - Where the plan does not settle a point, the implementer leaves a `DESIGN-GAP:` comment
     and makes the smallest reasonable choice.
   - The drift gate then lists every marker next to the unmarked differences.
   - Run the drift gate after the wave. In the trial it found four real defects that every test
     had passed.
7. **Secrets.**
   - The add-on denies `Read(**/.env)`, because reviewers search the whole folder. This also
     stops Claude reading `.env`, so use `.env.example` for documented settings.
   - Add deny rules for any other local secret file, or keep such files outside the repo.
8. **Usage limits.**
   - A long review can be stopped mid-turn by the plan's usage limit. It can leave partial edits
     and a report that says "resolved".
   - After any interrupted turn, compare the report with the files before trusting it.
   - Commit through the forge skills after each completed gate, so an interruption shows up as
     a diff.
   - The trial spent about $190 at list price on two review-and-resolve rounds for two designs.
9. **Use the kit's skills to write documents.** Kit artifacts carry front matter, digests and
   handoffs that `/egm:egm-draft` does not produce. Use EGM to review, resolve and check drift.
   `/egm:egm-brainstorm` is fine for shaping an idea before `/prd-think`.

## Clean-up

`{reports_dir}/egm/<INIT>/` is walk-time material, like the other reports. Delete it when the
initiative closes. The purge skills do not know about it yet.

## Removing the add-on

1. Run `harness apply --repo . --profile <profile> --without egm --apply`. This removes
   `.harness/addons/egm/`, the CLAUDE.md section and the pin entry.
2. It leaves `.claude/settings.json` alone, because the team may rely on some entries (the
   `.env` deny rule, for example). It prints the EGM entries; remove the ones you no longer
   want.
