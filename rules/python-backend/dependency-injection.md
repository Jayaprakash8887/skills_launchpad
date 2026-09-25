---
description: Injector-based DI — unified @inject pattern for all services, modules, container, singletons, lifespan (reusable across Python services).
alwaysApply: true
---

# Dependency injection (`injector`)

## Design principle

**One DI style for all services.** Both infra and business services use **`@inject`** on `__init__`. The `injector` container owns singleton creation for every service type — there is no `get_instance()` singleton pattern on service classes. This keeps the dependency graph readable, testable, and consistent across HTTP, worker, CLI, and batch entry points.

The `BaseInfraService` async lifecycle (`initialize` / `close` / `health_check`) is a **separate concern** from DI construction — it handles external resource open/close after the event loop is running, not object creation.

## Container

- Expose **`configure_container() -> Injector`** and **`provide_service(Type[T]) -> T`** from **`src/di/dependency_container.py`** (or equivalent single module).
- **`get_container()`** should fail fast if used before **`configure_container()`**.

## Modules

- Split bindings by concern under **`src/di/modules/`**, for example:
  - **`ConfigModule`** — `AppSettings` and other settings singletons
  - **`InfraModule`** — Postgres pool, Redis, Kafka, HTTP clients, LLM clients, etc.
  - **`RepositoryModule`** — repository classes (when using the repository pattern)
  - **`BusinessServicesModule`** — business service bindings
- Register **`@singleton`** (or `binder.bind(..., scope=singleton)`) for long-lived services created once per process.

## Construction rules

### All services — unified `@inject` pattern

**Always** use **`@inject`** on **`__init__`** for every service — infra, business, and stateless helpers. Collaborators (repos, other infra services) are injected as constructor parameters. Settings are **not** injected — see the Settings section below.

**Business service:**
```python
from injector import inject

class DeviceService(BaseBusinessService):
    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        repository: DeviceRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._repository = repository
```

**Infra service:**
```python
from injector import inject

class PostgresService(BaseInfraService):
    @inject
    def __init__(self) -> None:
        super().__init__()
        self._settings = AppSettings.get_instance()  # settings fetched directly, not injected

    async def initialize(self) -> None:
        self._pool = await asyncpg.create_pool(self._settings.database_url)

    async def close(self) -> None:
        await self._pool.close()

    async def health_check(self) -> bool:
        return self._pool is not None
```

**Never** use a `get_instance()` class method as a singleton guard on service classes — `injector` with `scope=singleton` is the singleton contract.

### Why `@inject` on infra services

`injector.get(PostgresService)` calls `__init__` synchronously (cheap: Python object created, settings assigned). The async resource opening (`await pool.open()`) happens in `initialize_all_services()` after the event loop is running. These are two separate phases — DI handles the first, the startup loop handles the second. There is no conflict.

### Repository Bindings

Use **`@provider`** and **`@singleton`** for repositories that need session factories:
```python
@provider
@singleton
def provide_device_repository(
    self, postgres_service: PostgresService
) -> DeviceRepository:
    return DeviceRepository(
        session_factory=postgres_service.get_session_factory()
    )
```

### DI Module Bindings

All services — infra and business alike — bind the same way:
```python
def configure(self, binder: Binder) -> None:
    binder.bind(PostgresService, scope=singleton)   # infra
    binder.bind(RedisService, scope=singleton)      # infra
    binder.bind(DeviceService, scope=singleton)     # business
```

No `to=SomeService.get_instance()` — the container constructs the instance.

### FastAPI Integration

**`get_*_service()`** functions delegate to **`provide_service(...)`** (lazy-import inside the getter if needed to avoid import cycles):
```python
def get_device_service() -> DeviceService:
    from src.di.dependency_container import provide_service
    return provide_service(DeviceService)
```

Do not construct heavy singletons (pools, clients) inside arbitrary business methods — resolve them once via DI.

### Settings (env-backed singletons)

Settings classes (`AppSettings`, `KafkaSettings`, `S3Settings`, `CrateDBSettings`, etc.) are **configuration bags**, not lifecycle-managed services. They follow a **completely separate singleton pattern** from DI:

- **Always** access them via `FooSettings.get_instance()` — directly, without going through the injector.
- **Never** bind settings classes in `ConfigModule` or any DI module — they are not part of the injector graph.
- **Never** add a `@provider` or `binder.bind()` entry for a settings class — doing so is the wrong pattern even if it works.
- **Never** declare a settings type as an `@inject` constructor parameter on a service — receive the instance directly in `__init__` instead.

```python
class KafkaService(BaseInfraService):
    @inject
    def __init__(self) -> None:
        super().__init__()
        self._settings = KafkaSettings.get_instance()   # correct
```

The `@inject` decorator is still required on `__init__` (so the injector owns construction), but settings are fetched via `get_instance()` inside the constructor body — **not injected as parameters**.

- **Do not** call `FooSettings.get_instance()` inside service **methods** or after `__init__` — fetch once in the constructor, store in `self._settings`.

### Settings and optional dependencies — `is_configured()` anti-pattern

**Do not** make a required service dependency optional at the settings level using `is_configured()` guards. This violates **`fail-fast.md`** — the service silently degrades at runtime instead of failing at startup.

```python
# Anti-pattern — do not do this
class ExternalApiSettings(BaseSettings):
    base_url: Optional[str] = Field(default=None)   # silently optional

    def is_configured(self) -> bool:
        return bool(self.base_url)

# Then in a business service:
if self._external_client.is_configured():   # silent skip if not configured
    await self._external_client.do_work(...)
```

**If the dependency is required for correct operation:** declare the setting as required (`base_url: str`, no default). The process will fail at settings load if the env var is missing — that is the correct behaviour.

**If the dependency is genuinely optional by product design** (the feature works correctly without it): `is_configured()` is acceptable, but it must be:
1. Documented in a PR or ADR explaining *why* the dependency is optional
2. Logged at `WARNING` level when the skip path is taken so it is observable in production
3. Tested — the "not configured" path must have a verify/test case

## Lifecycle and startup

`initialize_all_services()` runs **two phases** (see `dependency_container.py`). Same method names on infra and business; **different purpose** — do not open external resources in business `initialize()`.

| | **Infra** (`BaseInfraService`) | **Business** (`BaseBusinessService`) |
|---|-------------------------------|--------------------------------------|
| **Purpose** | Own **long-lived resources** (pools, clients) | **Orchestration**; collaborators injected in `__init__` |
| **`initialize()`** | **Required** real setup (e.g. open Postgres pool). Subclasses implement `@abstractmethod`. | Called at app startup after infra. Sets `_initialized`; default is logging only. Override on a specific service only for rare async setup (caches, file loads) — **not** for DB pools or HTTP clients. |
| **`close()`** | Release resources | Clear startup flag; no resource teardown in the usual case |
| **`health_check()`** | Probe the **external dependency** (pool, client, etc.) | Indicates startup **`initialize()`** completed (`_initialized`). **Not** a substitute for infra health or `/health` routes. |
| **Fail-fast** | `await initialize()` fails if resources cannot start | `injector.get(Service)` fails if DI / `__init__` breaks; `await initialize()` fails if override raises |

**Startup order:** (1) all `_INFRA_SERVICE_TYPES` → `injector.get()` then `await initialize()`; (2) all `_BUSINESS_SERVICE_TYPES` → `injector.get()` then `await initialize()`. Postgres must be first in the infra tuple.

Both phases **must** call `await service.initialize()` — `injector.get()` (or `provide_service()`) only constructs the object; it does not call `initialize()`. Omitting the `await` silently skips all async startup work:

```python
# Correct — both phases follow the same two-step pattern
async def initialize_all_services() -> None:
    for cls in _INFRA_SERVICE_TYPES:
        service = injector.get(cls)
        await service.initialize()          # required — opens pools, connects clients

    for cls in _BUSINESS_SERVICE_TYPES:
        service = provide_service(cls)
        await service.initialize()          # required — even if default impl only logs

# Wrong — construction only, initialize() never called
for cls in _BUSINESS_SERVICE_TYPES:
    provide_service(cls)                    # DI construction only; initialize() skipped
```

**Shutdown:** business `close()` then infra `close()` (reverse order of infra list).

- **`dependency_container.py`** keeps **`_INFRA_SERVICE_TYPES`** and **`_BUSINESS_SERVICE_TYPES`** in sync with **`InfraModule`** / **`BusinessServicesModule`**.
- Break import cycles with **lazy imports** inside **`configure_container`**, **`initialize_all_services`**, or provider factories — this is the **main allowed exception** to top-of-file imports (see **`python-imports.md`**).
- For **tests**, expose **`reset_container()`** (or similar) to clear the global `Injector` between cases.

## Entry points (HTTP, worker, CLI)

The same `configure_container()` call works across all entry points. Infra modules and bindings are identical regardless of whether the process is an HTTP server or a background worker:

```python
# HTTP entry (main.py)
container = configure_container()
await initialize_all_services()
uvicorn.run("src.app:create_app", factory=True, ...)

# Worker / CLI entry (worker_main.py)
container = configure_container()
await initialize_all_services()
worker = provide_service(WorkerService)
await worker.run()
```

No separate wiring for workers — the DI container is the single composition root for all process types.

## Related rules

- **Where DI is wired:** `architecture.md`
- **Infra scope:** `infra-services.md`
- **Repos / schemas:** `repository-pattern.md`, `pydantic-schemas.md`
- **Imports:** `python-imports.md`
