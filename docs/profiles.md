# Profiles — stack key → skills + layout

`profiles/<name>.yaml` binds a **stack key** to (a) the skill set installed in
repos of that stack and (b) the **layout defaults** those skills read at run
time. `harness apply` copies the profile verbatim to the consumer repo as
`.harness/profile.yaml`.

The profile name, the filename, and the `profile:` key inside must all match
(no aliases) — [harness.py](../harness.py) rejects mismatches.

## Schema

```yaml
profile: python-backend          # == filename == stack key

layout:                          # where skills read/write in this repo
  constitution: CLAUDE.md        # constitution entry point
  rules_glob: .claude/rules/*.md # where the rules live
  spec_root: docs/specification
  product_spec_dir: docs/specification/product     # /spec-draft writes here
  as_built: docs/specification/as-built/implementation-status.md
  adr_dir: docs/specification/adr                  # /spec-technical-review
  reports_dir: docs/specification/reports          # feasibility + plan reports
  tests_readme: tests/README.md
  source_roots: [src/]
  unit_tests_dir: tests/unit
  live_verify_dir: tests/verify                    # smoke/live verification
  fixtures_dir: tests/fixtures
  debug_tests_dir: tests/debug

reports:                         # canonical report filename prefixes
  feasibility_prefix: Initiative-Feasibility-Report
  plan_prefix: Implementation-Plan

as_built:
  harness_section: "## Testing harness"

development_skills: [...]        # dev-lane skills to install
requirements_skills: [...]       # PM-lane skills to install (meta-pm only)
forge_skills: [...]              # forge skills to install
```

The union of the three `*_skills` lists is exactly what `apply` installs and
what the pin records. A skill name must exist under `skills/<lane>/<name>/`.

## Shipped profiles

| Profile | Constitution | Layout highlights | Skills |
|---|---|---|---|
| [python-backend](../profiles/python-backend.yaml) | `rules/python-backend/` | specs under `docs/specification/`, code in `src/`, tests split unit/verify/fixtures/debug | 9 dev + 3 forge |
| [meta-pm](../profiles/meta-pm.yaml) | none | PRDs in `prd/`, reports in `prd/reports/` | 7 requirements + 3 forge |

## Why layout lives in the profile

Skills are shared across stacks; repo layouts differ. By resolving every path
through `.harness/profile.yaml`, the same `/spec-draft` skill can write to
`docs/specification/product/` in a Python service and somewhere else in a
future Next.js profile — without editing the skill. If you change the layout
keys, you change where *all* skills read/write in that stack's repos.

## Adding a profile

1. Copy [python-backend.yaml](../profiles/python-backend.yaml) to
   `profiles/<stack>.yaml`; set `profile:` and adjust `layout` to the stack's
   conventions.
2. Choose the skill lists (dev stacks usually keep all development + forge
   skills).
3. If the stack has a constitution, add `rules/<stack>/` and map it in
   `CONSTITUTION_BY_PROFILE` in [harness.py](../harness.py); otherwise map it
   to `None`.
4. `harness list` to verify, then apply to a repo.
