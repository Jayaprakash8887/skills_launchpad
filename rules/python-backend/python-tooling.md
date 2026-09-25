---
description: Black, Ruff, pyright, import-linter, pre-commit, pytest, pythonpath — standard Python repo hygiene.
alwaysApply: true
---

# Tooling

## Environment setup (Python 3.12 + Poetry + `.venv`)

**Python 3.12** is the interpreter. **Poetry** manages all Python packages via `pyproject.toml` and `poetry.lock`. A project-local **`.venv`** is created explicitly so the toolchain (pyright, ruff, pre-commit) is always self-contained.

### Standard setup

```bash
python3.12 -m venv .venv
poetry env use .venv/bin/python
poetry install --with dev
```

After this, `.venv` is the single environment for toolchain, tests, and running the app. No conda activation is required for standard FastAPI services.

### First-time setup: `make setup`

Every service repo provides a `scripts/setup_dev.sh` and a `make setup` target that runs it. This is the single onboarding command:

```bash
make setup   # run once after cloning
```

Canonical `scripts/setup_dev.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

command -v python3.12 >/dev/null || { echo "python3.12 required"; exit 1; }

python3.12 -m venv .venv
.venv/bin/pip install --upgrade pip poetry
POETRY_VIRTUALENVS_IN_PROJECT=1 .venv/bin/poetry env use .venv/bin/python
.venv/bin/poetry install --with dev

for tool in black ruff pyright pytest; do
  test -x ".venv/bin/$tool" || { echo "missing $tool"; exit 1; }
done

.venv/bin/pre-commit install
```

Make target:
```makefile
setup:
	@bash scripts/setup_dev.sh
```

`scripts/setup_dev.sh` is committed to the repo. README setup instructions point here — not to a sequence of manual commands.

### Tooling vs runtime

| Context | Env needed | How to run |
|---------|-----------|------------|
| `make check`, pyright, ruff, pre-commit | `.venv` only | `make check` from any shell |
| `pytest` (unit, no live infra) | `.venv` only | `make test` |
| `make run`, live verify | `.venv` only | `.venv/bin/python -m src.main` or documented verify command |

The toolchain and runtime both use `.venv`. Document service-specific verify commands in `tests/README.md` — not in the shared Makefile template.

---

## Format and lint

- **Black** + **Ruff**; line length **100**; target **Python 3.12** (match **`pyproject.toml`**).
- Run on **`src/`** and **`tests/`** (or project convention) in CI and locally before push.

---

## Static type checking (pyright)

Use **pyright** as the static type checker. Cursor / Pylance already runs pyright in the editor — CI gates on the same tool so editor squiggles and CI failures are identical.

Configure via **`pyrightconfig.json`** at the repo root (pyright's native format, takes precedence over `[tool.pyright]` in `pyproject.toml`):

```json
{
  "pythonVersion": "3.12",
  "venvPath": ".",
  "venv": ".venv",
  "typeCheckingMode": "basic",
  "exclude": [".venv", "postgres_migrations"]
}
```

**Notes:**
- `venvPath` + `venv` point pyright at the project `.venv` — it sees all installed packages. Without these, pyright falls back to the system Python and reports `reportMissingImports` for every dependency.
- `exclude` is mandatory. Without it, pyright scans every file inside `.venv` as project source — turning a 5-second check into a 2+ minute one.
- Do **not** set `pythonPlatform` in local config — let pyright auto-detect the current OS. Set `"pythonPlatform": "Linux"` only in a CI-specific override (`pyrightconfig.ci.json` or via env var) where the container is genuinely Linux.
- **Existing services**: use `"typeCheckingMode": "basic"` and tighten incrementally.
- **New services**: start at `"strict"` from the first commit.
- **Do not** widen types to `Any` or add `# type: ignore` to silence pyright — fix the model or narrow the type (see **`strong-typing.md`**).

### What pyright enforces for this codebase

- **Pydantic boundary**: catches returning `dict` where a Pydantic model is declared, missing field access after `model_validate`, `None`-safety on `Optional` fields.
- **Enum exhaustiveness**: flags non-exhaustive `match` on `StrEnum` types — adding a new enum value immediately shows every handler that needs updating.
- **ORM isolation**: if ORM types are typed as internal-only (not re-exported from `database/`), pyright flags accidental use in business or API layers.
- **Refactoring safety**: renaming a Pydantic field produces an instant list of every broken call site.
- **DI constructor mismatches**: `@inject` constructor type mismatches caught at write time, not at `injector.get()` runtime.

---

## Architectural layer enforcement (import-linter)

**`import-linter`** enforces that no layer imports from a layer it should not know about. This is the mechanical enforcement for the constraints stated in **`repository-pattern.md`** and **`architecture.md`** — text rules alone are not enough.

Configure at the repo root as **`.importlinter`**:

```ini
[importlinter]
root_packages =
    src

[importlinter:contract:layer-architecture]
name = Layered architecture — no cross-layer imports
type = layers
layers =
    src.api
    src.business_services
    src.database.postgres.repository
    src.database.postgres.schema
```

**What this contract makes a hard CI failure:**

| Violation | Why it is wrong |
|-----------|-----------------|
| `src.api` imports from `src.database.postgres.repository` | Routes must go through business services |
| `src.api` imports from `src.database.postgres.schema` | ORM must never reach the API layer |
| `src.business_services` imports from `src.database.postgres.schema` | ORM is confined to repositories only |
| Any lower layer imports from a higher layer | No upward / circular dependencies |

**What pyright enforces on top** (types at call sites, not imports):

| Violation | Enforcer |
|-----------|----------|
| Business service method returns `dict` instead of declared Pydantic model | pyright |
| Route handler uses ORM type in a type-annotated parameter or return | pyright |
| `None`-safety on `Optional` Pydantic fields not handled | pyright |

Together, `import-linter` closes the **import boundary** gap and pyright closes the **type signature** gap. Neither alone is sufficient.

Adapt the `.importlinter` layers to match each service repo's actual package paths (e.g. `src.database.redis.repository` when Redis repos exist).

---

## Pre-commit hooks

Every repo must have a **`.pre-commit-config.yaml`** at the root. Hooks run at commit time — format, lint, type, and layer errors are caught before they reach CI.

**Critical:** pyright and import-linter must be **`local` hooks** that call tools from the project's own `.venv`. Remote hooks (e.g. `RobertCraigie/pyright-python`) install into an isolated sandbox with no visibility of the project's installed packages — every import produces `reportMissingImports`. `language: system` with a bare tool name also fails in non-interactive shells where `.venv` is not on PATH.

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: "24.x.x"          # pin to latest stable
    hooks:
      - id: black
        args: ["--line-length=100"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: "v0.x.x"
    hooks:
      - id: ruff
        args: ["--fix"]

  - repo: local
    hooks:
      - id: pyright
        name: pyright
        entry: .venv/bin/pyright
        language: system
        types: [python]
        pass_filenames: false

      - id: import-linter
        name: import-linter
        entry: .venv/bin/lint-imports
        language: system
        pass_filenames: false
```

- **`pre-commit` must be in dev dependencies** so `poetry install` makes it available in `.venv`:
  ```toml
  [tool.poetry.group.dev.dependencies]
  pre-commit = "^4.0"
  ```
- Pre-commit install is handled by **`make setup`** / `scripts/setup_dev.sh` — no manual `pre-commit install` step needed.
- No conda activation required to run hooks — `.venv` is self-contained.
- CI runs **`.venv/bin/pre-commit run --all-files`** as a separate check step.

---

## Local developer workflow (Makefile)

Every service repo must provide a **`Makefile`** at the root. The canonical targets:

```makefile
.PHONY: setup check format lint types layers test

setup:
	@bash scripts/setup_dev.sh

# Run everything — use this before committing
check: format lint types layers

format:
	.venv/bin/black --line-length 100 src/ tests/

lint:
	.venv/bin/ruff check --fix src/ tests/

types:
	.venv/bin/pyright

layers:
	.venv/bin/lint-imports

test:
	.venv/bin/pytest tests/ -v --ignore=tests/debug/ --ignore=tests/verify/ --ignore=tests/e2e/
```

**Workflow:**
1. Clone repo → `make setup` (once).
2. Write code in Cursor — pyright catches **type violations in real-time** (red squiggles).
3. Run **`make check`** before committing — catches layer violations, lint, and type errors.
4. **`git commit`** — pre-commit hooks run automatically as the safety net.
5. **CI** — final gate; same tools, same `.venv`.

`make check` must pass cleanly before a PR is opened.

---

## Tests

### Current layout (as-built)

- **pytest** with **`testpaths = ["tests"]`** in **`pyproject.toml`**.
- Set **`pythonpath = ["."]`** (or equivalent) so **`from src....`** imports work without an editable install.
- **`make test`** runs pytest on **`tests/`** but **ignores** **`tests/debug/`**, **`tests/verify/`**, and **`tests/e2e/`** — live and exploratory scripts are not collected.
- Shared helpers live under **`tests/_helpers/`** (not collected as tests).
- In-process modules may sit at **`tests/test_*.py`** until a service adopts **`tests/unit/`**.

### Target layout (service quality epic — deferred)

When a service runs a test-quality program:

- Create **`tests/unit/`** for logic and edge-case pytest.
- Move in-process tests there; set **`testpaths = ["tests/unit"]`**.
- Update **`Makefile`**, **`tests/README.md`**, and **as-built** (`testing-and-verification.md` + `implementation-status.md`) together.

Do **not** require **`tests/unit/`** in new services until that epic is explicitly scheduled.

## Business-flow verification

- Use **`tests/verify/`** for smoke / end-to-end business flows (see **`testing-verify-flows.md`**), separate from fast unit tests.
- Document the exact invocation command in `tests/README.md` for each service repo — not in the shared Makefile template.

---

## Dependencies

- **Python 3.12** is the interpreter (enforced in `scripts/setup_dev.sh` and `pyproject.toml`).
- **Poetry** owns all Python packages via `pyproject.toml` and `poetry.lock`.
- Commit **`poetry.lock`** in the repo so `poetry install` is reproducible.
- Prefer **pinned ranges** in Poetry aligned with your stack (e.g. pydantic v2, pydantic-settings, loguru, injector when using DI).

### conda — optional, only for native dependencies

Standard FastAPI services do **not** need conda. Use **Python 3.12 + `.venv` + Poetry** only.

**`environment.yml` / conda is required only when** the service has native dependencies: CUDA, system libraries, compiled C extensions, or packages not available on PyPI. Document the conda workflow in that service's `tests/README.md` — not in the shared scaffold.

---

## Related rules

- **SDD workflow:** `spec-driven-development.md`
- **Strong typing:** `strong-typing.md`
- **Verify flows:** `testing-verify-flows.md`
- **Import style:** `architecture.md`
