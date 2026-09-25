---
description: Layered src/ layout, *_service naming for business/infra, entrypoints, import paths — reusable Python service pattern.
alwaysApply: true
---

# Architecture & package layout

Use a **layered `src/` tree** so entry, composition, domain, and IO stay separated. HTTP APIs, workers, lab tools, and CLIs can **omit** packages they do not need (`api/`, `database/`, etc.).

## Entrypoints

- **`src/main.py`** — Process entry only: load `.env`, construct **`AppSettings`**, **`setup_logging`**, then either start **uvicorn** (with a factory target) or run an **async lifecycle** (`initialize_all_services` → work → `close_all_services`). Keep this file thin.
- **`src/app.py`** — **`create_app()`** is the **single composition root**: build the FastAPI app **or** return the lab/batch runnable after wiring **DI** and logging. Avoid business logic here beyond wiring.

## Standard packages (enable what you use)

| Package | Responsibility |
|--------|----------------|
| **`configs/`** | Settings hierarchy, `get_settings` / `load_dotenv`, env-backed `AppSettings` |
| **`logging/`** | `get_logger`, `setup_logging`, `LoggingContext` / correlation |
| **`di/`** | `injector` container, `dependency_container`, `modules/*` |
| **`infra_services/`** | DB pool/session factory, external HTTP, LLMs, buses, storage—see **`infra-services.md`** |
| **`business_services/`** | Use cases: call **repositories** + **infra**; **no** ORM; subclass **`BaseBusinessService`**; **default** API is **Pydantic**, not **`dict`** (see **`pydantic-schemas.md`**) |
| **`database/`** | Connection managers, **repositories**, **ORM schema** (tables)—**only repos** use ORM types upward |
| **`models/`** | **All** Pydantic DTOs: request/response bodies, persistence DTOs, JSONB payloads, repo boundary types. Named by domain (e.g. `device_models.py`, `owner_models.py`). **Never define Pydantic models inside `api/`.** |
| **`exceptions/`** | `BaseAppException` and typed errors |
| **`api/`** | Routers, dependencies, health endpoints (when HTTP). Domain routers as **`*_routes.py`** (or domain-named modules per repo convention); import models from **`src.models.*`**. **No `models.py` inside `api/`** — not under **`api/v1/`**, **`api/internal/`**, or anywhere under **`api/`**. |
| **`utils/`** | Generic helpers (not domain "engine" or repo logic) |
| **`engine/`** | Optional: deterministic domain logic without HTTP/DB |
| **`observability/`** | Optional: metrics, tracing helpers (when the product requires them) |

## Naming — explicit `*_service` suffix

Every module and class under **`business_services/`** and **`infra_services/`**
uses an explicit **`_service`** / **`Service`** suffix for readability and
grep-ability. Bases (`base_business_service.py`, `base_infra_service.py`) already
follow this.

| Layer | Module file | Class |
|-------|-------------|-------|
| Business | `device_service.py` | `DeviceService` |
| Business | `job_worker_service.py` | `JobWorkerService` |
| Infra | `postgres_service.py` | `PostgresService` |
| Infra | `redis_service.py` | `RedisService` |
| Infra | `telemetry_service.py` | `TelemetryService` |
| Infra | `registry_client_service.py` | `RegistryClientService` |
| Infra | `kafka_service.py` | `KafkaService` |

**Do not** use truncated role nouns for service modules — e.g. `forge_client.py`,
`policy_engine.py`, `run_orchestrator.py`, `notifier.py`. Prefer
`forge_client_service.py`, `policy_engine_service.py`, `run_orchestrator_service.py`,
`notifier_service.py` (class names end in **`Service`**).

Protocols / small helper types may live in the same module as the service or a
sibling non-service module when they are not DI-registered services.

Import services from **service modules**, not package `__init__.py` re-exports
(see **`python-imports.md`**). The reference chassis is
**`python-fastapi-foundation`**.

## Service profiles (apply rules with repo requirements)

Not every HTTP service needs every package. Classify the service before copying a sibling repo:

| Profile | Inbound **`api/internal/`** | Outbound sibling **internal** clients |
|---------|----------------------------|--------------------------------------|
| **Internal provider** | **Yes** — mount **`/internal/v1`** | Often yes |
| **Internal consumer only** | **No** — callers use your **public** API | **Yes** — typed clients in **`infra_services/`** |

**Rule:** Missing **`api/internal/`** is **not** a gap when the service only **consumes** other services' internal APIs. Document outbound clients in **`infra_services/`** and the repo **README**.

**Product documentation** (requirements, ADRs, frozen routes) belongs in each consumer repo under **`docs/specification/`** (see that repo's **README**), not in this shared rules package.

## API layering

- **Routers** depend on **business services** only (**`Depends(get_*_service)`**), not repositories directly.
- **Business services** depend on **repositories** (and infra as needed); **repositories** return **Pydantic** models — schema ↔ model mapping stays inside the repository.
- **HTTP contract shape** (body vs query vs path): follow **`http-api-conventions.md`** so OpenAPI and BFFs stay predictable.
- **Published routes:** refactoring composition (e.g. **`tenant_router`**) is allowed only if **external URLs and methods stay unchanged** (document frozen paths in the repo **README** or **`docs/specification/`**).

These layering constraints are mechanically enforced — not just documented:

| Layer boundary | Tool |
|----------------|------|
| `src.api` → must not import from `src.database.*` | **`import-linter`** |
| `src.business_services` → must not import from `src.database.*.schema` | **`import-linter`** |
| Method signatures at each boundary use correct Pydantic types | **pyright** |

See **`python-tooling.md`** for the canonical `.importlinter` contract and pre-commit setup. See **`repository-pattern.md`** for the full enforcement table.

## `api/` structure convention

- **`api/v1/`** — one module per domain resource, composed in **`api/v1/__init__.py`**. Prefer either:
  - **Nested tenant router:** `tenant_router = APIRouter(prefix="/tenants/{tenant_id}")` plus resource-relative paths (`/devices`, …), or
  - **Full paths** on each router (`/tenants/{tenant_id}/devices`, …).
  Both are valid if **mounted URLs** match the product contract. All models come from **`src.models.*`**.
- **`api/internal/`** — **optional**; only when this service **exposes** S2S endpoints (no end-user JWT). Models from **`src.models.*`**, no local **`models.py`**. Mount at **`/internal/v1`** (or org standard).
- **`api/health/`** — health router only.
- **`api/auth/`** — **optional**; JWT route helpers and/or identity login proxy for verify-only services. Paths must match **`public_paths`** in **`app.py`**.
- Dependencies shared across v1 routes live in **`api/v1/dependencies.py`**; auth helpers live under **`api/auth/`** when present.

## Service plumbing parity

Keep the **non-domain shell** aligned across all Python HTTP services in the platform so feature work stays in **`business_services`**, **`models`**, and route modules — not in one-off **`app.py`** wiring.

- **`src/common/auth/`** — **Verify** platform-issued JWTs on protected routes (see **JWT verification** below). **`issuance.py`** belongs only on the **issuer service** (your identity service). **Not** outbound HTTP — identity clients live in **`infra_services/`**.
- **`src/app.py`** — Thin composition: **lifespan** (`configure_container` → **`initialize_all_services`** → **`close_all_services`**), **AuthMiddleware** with **`public_paths`** for **actually mounted** paths, **CORS**, request-id / correlation middleware, **`BaseAppException`** handler, then routers in stable order: **health** → **internal** (if present) → **ops/auth routers as documented in that repo** → **`api_router`** at **`/api/v1`**.
- **`src/api/v1/`** — Bearer-protected product API.

Exact copy-paste across repos is optional; **same layout, names, and responsibilities** reduces cognitive load when switching services.

## JWT verification (non-issuer services)

The **identity service** (issuer) issues platform/tenant JWTs. All other HTTP services **verify** only — they are not issuers.

| Layer | Responsibility |
|-------|----------------|
| **`common/auth/`** | **`AuthConfig`**, **`AuthMiddleware`**, RS256 public PEM from **`JWT_PUBLIC_KEY_PATH`** |
| **`infra_services/`** | Outbound HTTP to the identity service (login proxy, etc.) — never inside middleware |
| **`api/auth/`** (optional) | Route deps + optional login proxy; models in **`src/models/`** |
| **`exceptions/`** | **`UnauthorizedError`** (401/403) for consistent API envelope |

**Middleware contract:** set **`request.state.auth`** with **`user_id`**, **`tenant_id`**, **`role`**; add **`owner_id`** when the token role is owner-style (per your identity service's claim shapes). Use structured **401** JSON with **`UNAUTHORIZED`**.

**`app.py` when auth is on:** fail fast if RS256 / public key path is misconfigured; **`public_paths`** must list **this repo's mounted paths only** (exact or prefix). Include **`/internal`** only if this service exposes **`api/internal/`**.

**API edge:** validate **`request.state.auth`** into a Pydantic model (e.g. **`AuthContext`** in **`src/models/`**), not a raw **`dict`**. Product-specific authorization stays in that repo's **`api/.../dependencies.py`**.

## Import paths

- Use **`from src.<package>.<module> import ...`** from the repo root.
- Set **`pythonpath = ["."]`** in **pytest** (and Poetry) so `src.*` resolves.
- **All imports at top of file**—see **`python-imports.md`** (narrow exception for DI bootstrap only).

## Related rules

- **HTTP body/query/path conventions:** `http-api-conventions.md`
- **Fail fast / no silent defensive coding:** `fail-fast.md`
- **Imports policy:** `python-imports.md`
- **Infra scope:** `infra-services.md`
- **DI:** `dependency-injection.md`
- **Repos & ORM isolation:** `repository-pattern.md`
- **Pydantic / JSONB / enums:** `pydantic-schemas.md`
- **Types:** `strong-typing.md`
- **Logs:** `logging-loguru.md`
- **Migrations:** `database-migrations.md`
- **Verify flows:** `testing-verify-flows.md`
- **Format / test:** `python-tooling.md`
