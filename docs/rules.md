# Rules — the constitution

`rules/<stack>/*.md` is the **coding constitution** for a stack: the
architectural and hygiene rules every agent session must follow in repos of
that stack. Adapted from
[python-services-rules](https://github.com/drivestream-lab/python-services-rules)
(`.mdc` → `.md`).

## How rules reach the agent

1. `harness apply` copies `rules/<stack>/` → `<repo>/.claude/rules/`.
2. The managed block in `CLAUDE.md` contains one `@.claude/rules/<file>.md`
   import line per rule.
3. Claude Code resolves `@` imports when it loads `CLAUDE.md`, so **every rule
   is always in context** — the equivalent of upstream's `alwaysApply: true`
   (all 15 Python rules carry that flag upstream).

Rules keep their original frontmatter (`description`, `alwaysApply`). Claude
Code ignores it; it documents intent and eases diffing against upstream.

## The python-backend constitution (15 rules)

| Rule | Governs |
|---|---|
| [code-guidelines-index.md](../rules/python-backend/code-guidelines-index.md) | Index/map of all rules — read this first |
| [architecture.md](../rules/python-backend/architecture.md) | Layered `src/` layout, `*_service` naming, thin entrypoints, composition root |
| [dependency-injection.md](../rules/python-backend/dependency-injection.md) | Injector-based DI: `@inject`, modules, container, singletons, lifespan |
| [repository-pattern.md](../rules/python-backend/repository-pattern.md) | Strict layering: business → repository → ORM schema only |
| [infra-services.md](../rules/python-backend/infra-services.md) | What belongs in `infra_services` — DB stack, external APIs, LLMs, buses |
| [http-api-conventions.md](../rules/python-backend/http-api-conventions.md) | REST/FastAPI: JSON body for writes, query for GET filters, path for IDs |
| [pydantic-schemas.md](../rules/python-backend/pydantic-schemas.md) | Pydantic v2 models over dicts, settings, JSONB, enums |
| [strong-typing.md](../rules/python-backend/strong-typing.md) | Python 3.12+ annotations, validated boundaries |
| [fail-fast.md](../rules/python-backend/fail-fast.md) | Fail-fast over defensive coding; no silent recovery |
| [python-imports.md](../rules/python-backend/python-imports.md) | All imports at file top; no function-scope imports |
| [logging-loguru.md](../rules/python-backend/logging-loguru.md) | loguru: `get_logger`, structured JSON, correlation context |
| [database-migrations.md](../rules/python-backend/database-migrations.md) | Alembic flow: agent autogenerates, human runs migrations |
| [python-tooling.md](../rules/python-backend/python-tooling.md) | Black, Ruff, pyright, import-linter, pre-commit, pytest |
| [testing-verify-flows.md](../rules/python-backend/testing-verify-flows.md) | Integration testing methodology: debug → verify → pytest |
| [spec-driven-development.md](../rules/python-backend/spec-driven-development.md) | Truth hierarchy (spec > code) and same-PR discipline |

`meta-pm` has **no constitution** — the PM workspace holds PRDs, not code.

## Ownership and change flow

- In consumer repos, `.claude/rules/` is **read-only by convention**; the pin
  manifest makes any local edit visible as `drift:` in `harness status`.
- To change a rule: edit it **in the kit**, bump [VERSION](../VERSION),
  re-run `harness apply --apply` in each consuming repo, and commit the diff
  there. That is the whole upgrade protocol.

## Adding a stack's constitution

1. Create `rules/<stack>/` with your `.md` rules (an index file mirroring
   `code-guidelines-index.md` is strongly recommended).
2. Map the profile in `CONSTITUTION_BY_PROFILE` in [harness.py](../harness.py).
3. Reference the glob in the new profile's `layout.rules_glob`
   (see [profiles.md](profiles.md)).
