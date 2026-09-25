# The harness CLI

[harness.py](../harness.py) (launcher: [bin/harness](../bin/harness)) is the
whole factory: ~300 lines, three commands, PyYAML as the only dependency.

```
harness list                                    profiles + their skills
harness apply  --repo PATH --profile NAME       preview (dry-run is the default)
harness apply  --repo PATH --profile NAME --apply
harness status --repo PATH                      verify repo against its pin
```

Design rules inherited from upstream launchpad: **dry-run by default** (nothing
writes without `--apply`), **one repo per invocation** (no `--all`), and the
**kit is the SSOT** (no CLI flag overrides profile content).

## `apply`

Installs or refreshes the harness in a target repo — idempotent, so re-running
after a kit upgrade is the upgrade mechanism. Step-by-step behavior is
documented in [architecture.md](architecture.md#what-apply-does-in-order).

Refresh semantics: installed trees (`.harness/skills/<name>`, `.claude/rules`,
`.harness/references`) are **replaced wholesale** (`rm -rf` + copy), so local
edits do not survive — intentionally. `CLAUDE.md` is the exception: only the
text between the markers is replaced.

## `status`

Read-only verification, non-zero exit on any problem — suitable for CI or a
pre-commit hook:

- re-hashes every file listed in the pin `manifest` → reports `missing:` or `drift:`;
- checks each pinned skill resolves through `.claude/skills/<name>/SKILL.md`
  (catches broken/deleted symlinks);
- checks `CLAUDE.md` still contains the managed-block markers.

Fix for any finding is the same: re-run `apply --apply` (heals drift by
re-copying from the kit), or if the drift was a deliberate improvement, port
the edit into the kit first.

## `.harness-pin.yaml`

Written only on a real `--apply`, after files land:

```yaml
kit: skills_launchpad
kit_version: 0.1.0            # from VERSION at apply time
profile: python-backend
delivery_contract: sdd-delivery/v2
skills: [spec-draft, initiative-feasibility, ...]
manifest:                     # repo-relative path -> sha256
  .harness/profile.yaml: 3f6c…
  .harness/references/workflow.yaml: 91d2…
  .claude/rules/architecture.md: c04a…
  # … every installed file
```

The manifest is what makes "pinned" real without submodules: any byte change
in any installed file is detected. Symlinks themselves are not hashed — their
resolution is checked structurally by `status`.

## The CLAUDE.md managed block

Rendered from [templates/CLAUDE.harness.md](../templates/CLAUDE.harness.md)
with `{{PROFILE}}`, `{{KIT_VERSION}}`, `{{RULES_SECTION}}` (one
`@.claude/rules/<file>` import per rule), and `{{SKILLS_SLASH_LIST}}` filled in.

Upsert rules:

- markers present → only the text between `<!-- harness:start -->` and
  `<!-- harness:end -->` is replaced;
- no markers → the block is appended to the existing file;
- no `CLAUDE.md` → a minimal one is seeded.

Everything **outside the markers belongs to the repo team** — project notes,
run commands, product context all survive every re-apply.

## Extension points in harness.py

| Symbol | Change it to… |
|---|---|
| `CONSTITUTION_BY_PROFILE` | map a new profile to its `rules/<stack>/` dir (or `None`) |
| `SKILL_LANES` | add a new skill lane directory under `skills/` |
| `MARK_START` / `MARK_END` | (don't) — changing markers orphans existing blocks |
| `render_block()` | add template variables to the managed block |
| `cmd_status()` | add repo-health checks (e.g. required scaffold dirs) |
