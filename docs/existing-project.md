# Adding the kit to an existing project

The kit works on a repo that already has code. There are three cautions:

- **Name clashes stop `apply`.** If one of your own rule files or skills has the same name as
  one of the kit's, `apply` stops before writing anything. Your other files in
  `.claude/rules/` and `.claude/skills/` are left alone.
- **The skills expect the profile's folder layout.**
- **Only Python services have a constitution today.**

Once seeded, each new use case is a new initiative and follows the
[greenfield walkthrough](greenfield.md) from Day 1. This page covers what to do before that,
and what changes when the code already exists.

## 1. Check the fit

| Question | If the answer is no |
|---|---|
| Is the service Python? `python-backend` is the only service profile with a constitution. | Add your stack to the kit first: `rules/<stack>/`, `profiles/<stack>.yaml`, and an entry in `CONSTITUTION_BY_PROFILE` in [harness.py](../harness.py) (see "Extending" in the [README](../README.md)). Don't apply Python rules to a Java or TypeScript repo. |
| Is there a PM workspace? | Create a `<client>-meta` repo with the `meta-pm` profile ([greenfield.md](greenfield.md), Day 0 step 1). It has no constitution, so it suits any stack. |
| Does the repo match the profile layout? (`src/`, `tests/{unit,verify,fixtures,debug}`, `tests/README.md`, `docs/specification/{product,adr,reports,as-built}`) | Create the missing folders. If the repo has a different layout, add a profile variant in the kit. Do not edit `.harness/profile.yaml` in the repo: `status` reports it as drift, and the next `apply` overwrites it. |

## 2. Check what `apply` touches

`apply` owns only the files it installed. It knows which files those are from the pin
manifest in `.harness-pin.yaml`.

| Path in your repo | What `apply` does |
|---|---|
| `.claude/rules/` | Adds the kit's rule files and keeps yours. A file of yours with the same name as a kit rule stops the run; rename it, or delete it if it is an old copy of the kit's rule. An identical copy is simply taken over. |
| `.claude/skills/<name>` | Adds a symlink per kit skill. A skill of yours with the same name stops the run; rename it. |
| `.harness/`, `.harness-pin.yaml` | Owned by the kit. Nothing should be there yet. |
| `CLAUDE.md` | Managed block appended. Your text is kept. |
| `.claude/settings.json` (only with `--with egm`) | EGM entries merged in. Your entries are kept. Invalid JSON stops the run. |

Run the dry-run first. It reports every name clash at once, and `apply` writes nothing until
they are resolved. The line `rules … N file(s) of yours kept` confirms your rule files stay.

Your rule files in `.claude/rules/` stay where they are, but the `CLAUDE.md` managed block
imports only the kit's rules. Keep importing yours from your own part of `CLAUDE.md`, outside
the markers.

## 3. Seed on a branch

```bash
cd ~/code/existing-service
git switch -c harness-seed
mkdir -p docs/specification/{product,adr,reports,as-built} tests/{unit,verify,fixtures,debug}

harness apply --repo . --profile python-backend                 # dry-run: read it
harness apply --repo . --profile python-backend --apply         # add --with egm for EGM
harness status --repo .

git add -A && git commit -m "Seed python-backend harness"
```

Open a pull request for the seed, so the team sees the new rules and the `CLAUDE.md` block.

## 4. Write down what already exists

The kit's rules tell Claude to read the as-built record and not to infer live behaviour from a
spec. A new repo starts with nothing to record, but an existing one does. Before the first
initiative, fill in two files:

- **`docs/specification/as-built/implementation-status.md`:** what the service does today. Cover
  its endpoints, tables, integrations, configuration and known gaps, with file paths.
  - Have Claude draft it from the code, then correct it yourself.
  - Tell it to cite file paths and to write "unclear" rather than guess.
  - In the CCE trial, docs written this way were accurate, and they surfaced defects that the
    tests had passed.
- **`tests/README.md`:** the exact commands to build, lint and run each test layer. The skills
  run these commands and must not invent others.

Leave existing design docs where they are, and link them from the as-built file.
`docs/specification/product/` holds the per-initiative specs that `/spec-draft` creates.

**With EGM:** run `/egm:egm-drift-report` on the existing design docs, with its own artifact
directory, before you build on them. It shows where those docs no longer match the code. Fix or
mark those places, so the first spec doesn't inherit stale facts.

## 5. The first initiative

Follow [greenfield.md](greenfield.md) from Day 1, with these changes:

- **The PRD links the existing system.** Link the as-built file and the documents for every
  system the change touches, such as another team's table definition, a gateway contract, or
  the identity provider's setup. These fixed constraints are where plans go wrong. In the CCE
  trial, a team plan written without them would have used the wrong database schema and the
  wrong table shape. It would also have locked out every existing user. EGM's reviewers found
  these problems only because the constraints were linked: reviewers read nothing else.
- **Scope the spec to the change.** `/spec-draft` should create REQs for what changes, not
  restate the whole system. The as-built file covers the rest.
- **Don't skip `/initiative-feasibility`.** On existing code it is where conflicts with what is
  already there come out.
- **Mark gaps while building.** During `/loop-spec`, a `DESIGN-GAP:` comment where the plan is
  silent keeps the as-built record and the spec honest. With EGM, the drift report lists every
  marker after the wave.
- **Update the as-built file at wave close.** That keeps it true for the next initiative.

## 6. One use case across several repos

When a feature spans repos, for example a service and its UI:

1. Write one PRD in the meta repo. `/prd-impact-map` maps its capabilities to each repo.
2. Each repo gets its own spec, TDD and plan, in its own lane.
3. **Name the owner of every shared contract** (an API, a table, an event) in the PRD. The
   owning repo's TDD defines it, and the other repo's TDD links to it instead of redefining it.
   Without this, the two designs drift apart, and each review sees only half the contract.
4. With EGM, review each repo's TDD separately, each with its own artifact directory. After
   both are resolved, check that the consuming TDD still matches the owner's contract.
