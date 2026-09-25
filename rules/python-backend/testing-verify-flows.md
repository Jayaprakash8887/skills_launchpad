---
description: Methodology for integration testing—debug, verify, pytest; config and HTTP client patterns.
alwaysApply: true
---

# Integration testing methodology

Each repository documents **concrete paths, config file names, auth providers, and run commands** in **`tests/README.md`**. Maintain **`docs/specification/as-built/`** as the SSOT for layout, CI vs live boundaries, and feature-map alignment.

This file defines **approach and structure** reusable across Python service repos. Derive service-specific detail from **as-built testing docs** and **`tests/README.md`** in the consumer repo.

Product documentation tree: **`docs/specification/product/`**, **`docs/specification/adr/`**, **`docs/specification/as-built/`**.

## Objectives

- Run **integration-style** checks against a **live API** without folding everything into pytest.
- Keep **secrets and machine-specific URLs** out of version control while staying easy to run locally.
- Separate **fast in-process pytest** from **live verify** — and avoid duplicating full HTTP journeys in both.

## Standard folder layout

```text
tests/
  test_*.py               # pytest — in-process (may move to tests/unit/ in a later quality epic)
  verify/                 # live API — one module per product area
    verify_all.py         # optional aggregator
    verify_<feature>.py
  debug/                  # exploration — not gating
  _helpers/               # shared — not collected by pytest
  config.yaml.example     # committed example
  config.yaml             # local only (gitignored)
```

**`tests/unit/`** is the **target** layout for logic-focused pytest (see **Pytest scope**). Services may adopt it in a dedicated quality epic — do not require it in constitution until that epic lands.

Each repo maintains a **feature map** in **`tests/README.md`**: capability → verify script → pytest coverage (honest as-is).

## Categories (separate concerns)

| Category | Role | Typical invocation | Assertions |
|----------|------|--------------------|------------|
| **Debug** | Explore flows; print responses | `python -m tests.debug.<script>` | Optional or informal |
| **Verify** | Contract and smoke on a **running** server | `python -m tests.verify.<script>` + optional `verify_all` | Exit code, status, response shape |
| **Pytest** | Fast in-process | `make test` | **`TestClient`**, mocks — no live-server requirement |

**Convention:** Do not make debug or verify scripts **depend on** pytest discovery. Prefer **`verify/`** (including multi-step journeys) over a duplicate **e2e/** tree unless a second layer is clearly scoped (e.g. cross-service only).

## Toolchain vs runtime

| Task | Environment | Command pattern |
|------|-------------|-----------------|
| Format, lint, types, layers | `.venv` only | `make check` |
| Pytest | `.venv` only | `make test` |
| Verify / debug | `.venv` only | Document in **`tests/README.md`** (e.g. `.venv/bin/python -m tests.verify.<script>`) |

- **Toolchain** (pyright, ruff, pytest, pre-commit) and **verify/debug** run from **`.venv`** — no conda for standard FastAPI services.
- **Verify/debug** use the same Python env as the running API (`src.*` on **`pythonpath`**). Follow **`tests/README.md`** for the canonical command — not a shared Makefile target.

## Configuration pattern

- **Committed example** (`tests/config.yaml.example`) + **local file** (`tests/config.yaml`, gitignored) for URLs, credentials, and structured test inputs.
- **Verify and debug read the tests config file** for URLs, credentials, and flow inputs — not **`.env`** (application env vars stay separate).
- **Environment variables** may override file values for CI or disambiguation when documented — but the tests config file is the primary local contract.
- **Structured inputs** (IDs, metadata, sequences) live in config or central defaults with getters — avoid scattering literals across scripts.

## Pytest scope

- Set **`testpaths`** in **`pyproject.toml`** (current convention: **`["tests"]`**).
- Set **`pythonpath = ["."]`** so **`from src....`** imports work without an editable install.
- **`make test`** must **exclude** **`tests/debug/`**, **`tests/verify/`**, and **`tests/e2e/`** from pytest collection.
- **`_helpers/`** must not be collected (package naming or explicit ignore).
- **Target (deferred):** `tests/unit/` as the sole pytest home with **`testpaths = ["tests/unit"]`** — adopt per service quality epic, not by default.

## Tenant and identity from APIs

- When protected routes use Bearer tokens from an identity provider, **derive tenant (or user) context from token claims** (or from the provider's selection response) for downstream request bodies instead of hardcoding tenant UUIDs in config.
- Keep **optional config/env overrides** only for **disambiguation** (multi-tenant selection) or when tokens omit a claim.

## Shared helpers layout

- Place shared code under a path pytest does **not** collect (e.g. **`tests/_helpers/`**).
- **Config loader:** merge defaults, file, and env; one place for precedence rules.
- **HTTP client:** base URL, timeouts, optional **`Authorization`** header construction.
- **API paths helper:** maintain **`tests/_helpers/api_paths.py`** with functions for **this repo's mounted routes** — do not copy path prefixes from a sibling service.
- **Token acquisition:** isolate login or token exchange; parse third-party JSON with **Pydantic v2** and **`extra="ignore"`** where responses evolve.
- **Policy:** When an identity service is **configured** for tests, obtain tokens through that path for protected routes; reserve static token env vars for documented exceptions (e.g. narrow CI or `skip_*` flags), not as the default hidden bypass.
- **Enums:** closed vocabulary strings in verify code must come from shared **enums** in **`src/models/`** — use **`.value`** in JSON payloads and assertions.

## Verify script practices

- Exit **`0`** on success, **non-zero** on failure.
- Prefer a **`verify_all`** aggregator for full smoke with one command — document order and any in-process session reuse in **`tests/README.md`** and **as-built testing doc**.
- **In-process provision:** when multiple verify scripts share one tenant or credentials, use a shared session helper (e.g. `ensure_*_provisioned()`) rather than requiring manual setup between scripts. Standalone provision scripts may exist outside the aggregator.
- Scripts **not** in **`verify_all`** (internal-only, standalone provision) must be documented in the feature map.
- Failures should print **clear, grep-friendly** messages.

## CI vs live verify

| Layer | Typical CI | Local / board Verify column |
|-------|------------|----------------------------|
| `make check` | yes | yes |
| `make test` (in-process pytest) | yes | yes |
| `tests/verify/*` | **no** (needs running stack) | yes — document command in **`tests/README.md`** |

Document per-repo skips (e.g. telemetry needing local Alloy) in **as-built testing doc** and **`tests/README.md`**.

## Unit vs verify — no overlap

| Concern | Owner |
|---------|--------|
| Full HTTP journey on a **running** API | **verify** |
| Service **logic**, branches, edges (mocked repos) | **pytest** (target: **`tests/unit/`**) |
| Thin liveness (e.g. `/health` 200) | **both** acceptable until quality epic trims verify to one representative assertion |

**Rule for new work:** do not duplicate full HTTP journeys in pytest when a verify script already proves the live path. Add pytest for **logic** pytest can own cheaply.

## Pytest practices (in-process)

- When the app **always** enables auth middleware, in-process tests should either supply a **test verification key** fixture or document how they satisfy startup — avoid disabling auth in tests unless the repo explicitly allows it.
- Tests that only hit **public** routes should not require tokens.

## Public vs authenticated routes

- **Align scripts with the product:** use no **`Authorization`** only where the API contract says the route is public; use real tokens for protected routes the same way production clients do.
- **Health and ops:** keep the simplest liveness check cheap; if detailed diagnostics are sensitive, protect them consistently — document behavior in the repo README, not only in code.

## Related rules

- **SDD workflow:** `spec-driven-development.md`
- **Tooling:** `python-tooling.md`
- **Architecture:** `architecture.md`
- **Product paths (per repo):** consumer **`docs/specification/`**
