# Architecture

How the kit's components fit together, and what `harness apply` actually does.

## The model

Two kinds of trees exist:

1. **The kit** (this repo) — the single source of truth for rules, skills,
   references, and profiles. Versioned by [VERSION](../VERSION) and git.
2. **Consumer repos** — any repo the harness has been applied to. They hold
   *pinned copies* of kit content plus a manifest to detect drift. They never
   edit harness content; upgrades flow kit → repo via re-apply.

```
        the kit (SSOT)                        consumer repo (pinned copies)
┌──────────────────────────┐   harness    ┌──────────────────────────────────┐
│ rules/<stack>/*.md       │──── apply ──▶│ .claude/rules/*.md               │
│ skills/<lane>/<name>/    │──── apply ──▶│ .harness/skills/<name>/  (hub)   │
│                          │              │ .claude/skills/<name> ──symlink──┘
│ references/ (contracts)  │──── apply ──▶│ .harness/references/             │
│ profiles/<name>.yaml     │──── apply ──▶│ .harness/profile.yaml            │
│ templates/CLAUDE.*.md    │──── apply ──▶│ CLAUDE.md   (managed block)      │
│ harness.py  · VERSION    │              │ .harness-pin.yaml  (sha256 pin)  │
└──────────────────────────┘              └──────────────────────────────────┘
```

Claude Code in VSCode then consumes the right-hand side:

- `CLAUDE.md` loads automatically; its managed block `@`-imports every rule in
  `.claude/rules/`, so the constitution is always in context.
- `.claude/skills/<name>/SKILL.md` makes each skill callable as `/<name>`.
- Skills read `.harness/profile.yaml` (where do specs/tests live?) and
  `.harness/references/` (workflow, id conventions, handoff contracts) at run time.

## Why copies + symlinks instead of submodules

Upstream launchpad pins two git **submodules** into every repo (`.cursor/rules`,
`prayog-skills`) and symlinks skills into runtime dirs. This kit keeps the same
on-disk contract (`.harness/` hub, `.harness/profile.yaml`, `.harness-pin.yaml`,
runtime symlinks) but installs **real copies**:

- no submodule init/update friction for consumers — `git clone` is enough;
- the pin is a **sha256 manifest** of every installed file instead of a
  submodule SHA, so `harness status` detects edits to any single file;
- symlinks are only used *inside* the repo (`.claude/skills/x → ../../.harness/skills/x`),
  so they survive cloning on Linux/macOS.

## What `apply` does (in order)

For `harness apply --repo R --profile P` (see [harness.py](../harness.py)):

1. Load `profiles/P.yaml`; collect its `development_skills` +
   `requirements_skills` + `forge_skills`.
2. For each skill: copy `skills/<lane>/<name>/` → `R/.harness/skills/<name>/`,
   then ensure the relative symlink `R/.claude/skills/<name>`.
3. Copy `references/` → `R/.harness/references/`.
4. If the profile has a constitution (`CONSTITUTION_BY_PROFILE` in harness.py):
   copy `rules/<stack>/` → `R/.claude/rules/`.
5. Copy the profile → `R/.harness/profile.yaml`.
6. Upsert the managed block in `R/CLAUDE.md` between
   `<!-- harness:start -->` / `<!-- harness:end -->` (content outside the
   markers is never touched).
7. Hash everything installed and write `R/.harness-pin.yaml`.

Everything before step 7 is previewed by the default **dry-run**; only
`--apply` writes.

`harness status` re-hashes every file in the pin manifest and additionally
checks that each skill symlink resolves to a `SKILL.md` and that the CLAUDE.md
markers exist. Exit code is non-zero on any problem (CI-friendly).

## Mapping to upstream launchpad

| Upstream (Cursor-centric) | This kit |
|---|---|
| `.cursor/rules/*.mdc` submodule @ tag | `.claude/rules/*.md` copies, imported via CLAUDE.md |
| `prayog-skills` submodule → `.harness/skills` → `.agents/skills`, `.claude/skills` | kit `skills/` → `.harness/skills` → `.claude/skills` |
| `AGENTS.md` managed block | `CLAUDE.md` managed block |
| `.harness-pin.yaml` (refs) | `.harness-pin.yaml` (kit version + sha256 manifest) |
| `launchpad apply-harness / status` | `bin/harness apply / status` |
| `onboard interview`, `init-client`, `apply-scaffold`, `apply-gates` | *not ported* — no GitHub org automation |

## Component docs

- [rules.md](rules.md) — the constitution
- [skills.md](skills.md) — skill anatomy and lanes
- [profiles.md](profiles.md) — profile schema
- [references.md](references.md) — shared contracts
- [cli.md](cli.md) — harness CLI, pin file, managed block
- [greenfield.md](greenfield.md) — end-to-end walkthrough
