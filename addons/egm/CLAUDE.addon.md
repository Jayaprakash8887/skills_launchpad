### Add-on: EGM (Elephant-Goldfish Model)

- Plugin `{{PLUGIN}}` {{PLUGIN_VERSION}}, marketplace pinned to `{{MARKETPLACE_REF}}`, enabled in
  `.claude/settings.json`. Needs Claude Code {{MIN_CLAUDE_CODE}} or later.
- Commands: {{COMMANDS}}.
- Only a person can start an EGM command, by typing it. Skills cannot start one.

EGM gates are optional and manual. They do not change `workflow.yaml`: when the workflow
reaches a gate's anchor, a person may run the gate, act on its outcome, then continue the
pinned workflow. Gates for this profile (`.harness/addons/egm/gates.yaml`):

{{GATES}}

Every EGM prompt names its own artifact directory, one per document and gate, with a line
`EGM artifact directory: <dir>`. EGM overwrites its reports, so never share a directory
between gates. Reviewers see only the target file and the files it links to. Rules and
lessons learned: `.harness/addons/egm/integration.md`.
