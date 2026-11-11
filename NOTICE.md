# Attribution

This kit adapts MIT-licensed content from the
[drivestream-lab](https://github.com/drivestream-lab) organisation:

- `skills/` and `references/` — adapted from
  [prayog-skills](https://github.com/drivestream-lab/prayog-skills) (MIT),
  with paths rewritten from Cursor conventions (`.cursor/rules/`,
  `prayog-skills/references/`) to Claude Code conventions
  (`.claude/rules/`, `.harness/references/`).
- `rules/python-backend/` — adapted from
  [python-services-rules](https://github.com/drivestream-lab/python-services-rules)
  (MIT), converted from `.mdc` to `.md`.
- `harness.py` and the on-disk contract (`.harness/`, `.harness-pin.yaml`,
  managed constitution block) — re-implementation of the `apply-harness` /
  `status` ideas from
  [launchpad](https://github.com/drivestream-lab/launchpad) (MIT).

Copies of the upstream MIT license terms apply to the adapted content.

## Add-ons

- `addons/egm/` enables Google's
  [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model)
  plugin (Apache-2.0). No EGM code or content is copied into this kit. The
  add-on only points Claude Code at the upstream marketplace, at a pinned tag,
  and Claude Code installs the plugin from there under its own license. The
  gate definitions and usage guidance in `addons/egm/` are original to this kit.
