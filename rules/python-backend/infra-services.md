---
description: What belongs in infra_services — DB access stack, external APIs, LLMs, message buses.
alwaysApply: true
---

# Infrastructure services

## Definition

Put code here when it **integrates with the outside world** or **long-lived runtime resources**, not when it encodes **business rules**.

**Naming:** every infra module/class uses the **`*_service`** / **`*Service`**
suffix — including outbound HTTP clients (e.g. **`registry_client_service.py`** /
**`RegistryClientService`**, not **`registry_client.py`**). See
**`architecture.md`**.

Typical **infra** responsibilities:

- **Database**: connection pools, engine/session factory, transaction helpers used by repositories (not business logic itself).
- **Third-party HTTP APIs**: typed clients, auth, retries, base URLs.
- **Sibling service internal APIs**: typed HTTP clients to another platform service's **`/internal/v1/...`** (e.g. registry or identity clients). These are **outbound** callers — not **`api/internal/`** routes in *this* repo unless this service is an internal **provider** (see **`architecture.md`** service profiles).
- **LLMs / model providers**: SDK wrappers, chat completion clients, embedding clients.
- **Message buses / queues**: Kafka, Redis pub/sub, MQTT publishers/consumers as **clients**.
- **Object storage**, **email/SMS** gateways, **search** clients—same idea.

## What is not infra

- **Business services** orchestrate use cases (call repos + infra, enforce invariants).
- **Repositories** perform persistence against the DB using sessions provided by infra; they do not wrap unrelated HTTP APIs (those stay separate infra services).

## Lifecycle

- Use **`BaseInfraService`**: implement **`async initialize`**, **`async close`**, and **`health_check`** for **resource** open/close/probe (subclasses are `@abstractmethod`).
- Register every connection-backed client in **`InfraModule`** and include it in **`_INFRA_SERVICE_TYPES`** in **`dependency_container.py`** (keep in sync).
- **Business** services also expose `initialize()` / `close()` / `health_check()` on **`BaseBusinessService`**, but that is **not** resource lifecycle — see the infra vs business table in **`dependency-injection.md`**.

## Construction

- Use **`@inject`** on **`__init__`** — same as business services. `injector` with `scope=singleton` is the singleton contract; **do not** add a `get_instance()` class method on infra services.
- `__init__` is synchronous and cheap (settings assigned, no I/O). Actual resource opening (pool, client, connection) happens in **`async initialize()`** after the event loop is running.

## Settings

- Settings are **not** part of the DI graph — **do not** inject them as constructor parameters and **do not** bind them in `ConfigModule`.
- Call `FooSettings.get_instance()` **once** inside `__init__` and store on `self._settings`; do not call it again in methods or lifecycle hooks.

```python
class KafkaService(BaseInfraService):
    @inject
    def __init__(self) -> None:
        super().__init__()
        self._settings = KafkaSettings.get_instance()
```

## Session factory — Protocol, not abstract class

The session factory passed to repositories must be typed as a **`Protocol`**, not an abstract class or a concrete type. Decorating an abstract method with `@asynccontextmanager` causes pyright type errors because the decorator wraps the return type in a way that is incompatible with an abstract signature.

```python
# Correct — structural typing via Protocol
from typing import Protocol, AsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession

class PostgresSessionFactory(Protocol):
    def __call__(self) -> AsyncContextManager[AsyncSession]: ...
```

Benefits beyond pyright compliance:
- Any callable matching this signature is a valid session factory — no inheritance required
- Repositories and tests can be constructed with any mock that matches the shape
- The contract is structural ("what it does"), not hierarchical ("what it inherits")

Use this type in repository constructors:

```python
class DeviceRepository(BasePostgresRepository):
    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(session_factory)
```

## Related rules

- **Layout:** `architecture.md`
- **Repositories:** `repository-pattern.md`
- **DI:** `dependency-injection.md`
