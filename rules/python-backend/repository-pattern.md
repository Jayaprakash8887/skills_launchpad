---
description: Repository pattern — strict layering: business → repository → ORM schema only.
alwaysApply: true
---

# Repository pattern

## Strict layering (team standard)

```
src.api  →  src.business_services  →  src.database.*.repository  →  src.database.*.schema
               ↓                               ↓
          Pydantic DTOs               map rows ↔ DTOs
```

- **Business services** call **repositories** only. They use **Pydantic models** / DTOs from **`models/`** — **never** import or accept **ORM schema** classes. Service **public** APIs default to **Pydantic**, not raw **`dict`** (see **`pydantic-schemas.md`** guardrail; dict-shaped exceptions need explicit product/user alignment).
- **Repositories** are the **only** layer that imports and uses **database schema** (ORM models / table definitions under **`database/.../schema/`** or equivalent). They execute queries and **map** ORM rows to/from **Pydantic** models (or primitives) for callers — structured payloads are **models**, not raw **`dict`** (see **`pydantic-schemas.md`**).
- **Postgres** repositories in this repo inherit **`BasePostgresRepository`** and accept **session** or **session_factory** as established in **`base_repository.py`**.
- **Nobody else** (API routers, business services, utils, infra except session factory) uses **ORM schema** types directly.

### Enforcement

These constraints are enforced by two tools — text rules alone are not sufficient:

| Constraint | Enforcer |
|------------|----------|
| `src.api` cannot import from `src.database.*` (any sub-package) | **`import-linter`** — hard CI failure |
| `src.business_services` cannot import from `src.database.*.schema` | **`import-linter`** — hard CI failure |
| Business service method signatures use Pydantic models, not `dict` | **pyright** — type error at call site |
| ORM type never appears in a business or API method signature | **pyright** — type error at call site |

See **`python-tooling.md`** for the canonical `.importlinter` contract. Adapt layer paths to match the service repo's actual package structure.

## Placement

- Repository classes under **`src/database/postgres/repository/`** (or equivalent store).
- ORM / table definitions under **`database/.../schema/`** (project naming may vary).
- One repository module (or cohesive group) per aggregate / table family.

## Responsibility

- Repositories: **data access only**—queries, mappings, pagination. **No** business rules or authorization policy.
- **No** SQL or ORM usage in route handlers, business services, or random utils.

## Async and sessions

- **Async** methods when using async SQLAlchemy (or async drivers).
- **Session** or **session factory** comes from **infra**; transaction boundaries live in the **service** layer unless the project uses a dedicated UoW.

## JSON / JSONB

- For **JSONB** (or JSON) columns, define a **Pydantic v2 model** for the payload shape. **Repository** validates with that model on read/write so the rest of the stack stays **strongly typed** (see **`pydantic-schemas.md`**).

## Base type

- Share patterns via **`BasePostgresRepository`** (this repo) / **`BaseRepository`** rather than duplicating session/query boilerplate.
- **`session_factory`** is **required** in the repository constructor (provided by **`RepositoryModule`** from **`PostgresService.get_session_factory()`**). Do not fall back to a global connection manager inside the base repository.

## ORM schema — `__tablename__` on concrete classes only

**Do not** define `__tablename__` on an abstract base ORM class using `@declared_attr`. When subclasses then set `__tablename__ = "table_name"` as a plain string, pyright flags a type mismatch because the base declared it as a descriptor type.

```python
# Wrong — @declared_attr on base causes pyright errors in subclasses
class BaseSchema(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()   # dead code — every subclass overrides this anyway

class DeviceSchema(BaseSchema):
    __tablename__ = "devices"         # pyright: type mismatch with declared_attr descriptor
```

```python
# Correct — no __tablename__ on the abstract base; every concrete class declares it explicitly
class BaseSchema(DeclarativeBase):
    pass                              # no __tablename__ here

class DeviceSchema(BaseSchema):
    __tablename__ = "devices"         # explicit, clear, pyright-clean
```

Requiring each concrete schema to declare `__tablename__` explicitly also makes the table name visible at a glance without tracing up an inheritance chain.

## Services without a database

- Tools / jobs may omit **`database/`**. Keep the same **separation idea**: persistence helpers + **business** orchestration; no ORM in the wrong layer.

## Related rules

- **Pydantic / JSONB / enums:** `pydantic-schemas.md`
- **DI:** `dependency-injection.md`
- **Infra (sessions):** `infra-services.md`
- **Typing:** `strong-typing.md`
