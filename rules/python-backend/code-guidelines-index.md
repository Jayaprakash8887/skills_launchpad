---
description: Index of Python backend guideline rules (modular MDC topics).
alwaysApply: true
---

# Code guideline modules (index)

These **`.md`** files govern **architectural patterns** for Python microservices. They live in the **`python-services-rules`** repository and are consumed via a **git submodule** at each service repo's **`.claude/rules/`** (this directory when mounted).

**Product-specific** requirements, ADRs, route catalogs, and env URLs belong in each service repo under **`docs/specification/`** and **README** — not in this package.

## Architectural rules (this package)

| File | Topic |
|------|--------|
| **`architecture.md`** | Layered **`src/`** layout, **`*_service` naming**, service profiles, JWT verification, **`main.py`** vs **`app.create_app()`** |
| **`fail-fast.md`** | **Fail fast**; avoid defensive / silent recovery without approval |
| **`python-imports.md`** | **All imports at top of file**; DI bootstrap exception |
| **`dependency-injection.md`** | **`injector`**, unified **`@inject`** for all services, init/shutdown lifecycle |
| **`infra-services.md`** | DB stack, third-party APIs, sibling internal HTTP clients, buses |
| **`repository-pattern.md`** | **Business → repo → ORM only**; JSONB + Pydantic at repo boundary |
| **`pydantic-schemas.md`** | **Pydantic not Dict**; **`_metadata`**; domain enums |
| **`strong-typing.md`** | Annotations, boundaries, JSONB typing |
| **`database-migrations.md`** | **Alembic**: agent runs **`create_postgres_migration.sh`** (**`--autogenerate`**); human runs **`run_postgres_migration.sh`**; no DDL-NOTE substitutes |
| **`spec-driven-development.md`** | SDD truth hierarchy, as-built discipline, PR traceability |
| **`testing-verify-flows.md`** | verify / debug / pytest methodology |
| **`logging-loguru.md`** | **`get_logger`**, **`setup_logging`**, structured JSON, correlation |
| **`python-tooling.md`** | Black, Ruff, **pyright**, **import-linter**, **Makefile**, pytest, **`pythonpath`** |
| **`http-api-conventions.md`** | REST/FastAPI body/query/path conventions |

## Per-repository product documentation

Each service repo should provide (not in this package):

| Path | Purpose |
|------|---------|
| **`docs/specification/product/`** | Requirements, capabilities, features |
| **`docs/specification/adr/`** | Architecture decision records |
| **`docs/specification/as-built/`** | What is live today |
| **`tests/README.md`** | Verify/debug commands, feature map |
| **`README.md`** | Setup, env vars, run commands |

## Cross-project conventions

- **Do not** add product features or service names to shared **`.md`** files — extend **`docs/specification/`** in the consumer repo.
- **Do not** edit **`.claude/rules/`** in consumer repos — propose changes via PR on the upstream `python-services-rules` repository.
- **No emojis** in code or logs; use tags such as **[OK]**, **[ERROR]**, **[WARNING]**, **[INFO]** when needed.
- **Service naming:** every module/class under **`business_services/`** and **`infra_services/`** uses the **`*_service`** / **`*Service`** suffix (see **`architecture.md`**).
- **Service imports:** import service classes and **`get_*_service`** getters from **service modules**, not from package **`__init__.py`**.

## Where to start

1. **`architecture.md`** and **`dependency-injection.md`** for structure and lifecycle.
2. Consumer repo **`docs/specification/`** when the task changes behavior, APIs, or integrations.
