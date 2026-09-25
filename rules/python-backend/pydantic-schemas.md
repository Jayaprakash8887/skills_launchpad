---
description: Pydantic v2 — business layer uses models not Dict (default), settings, JSONB, Type* enums.
alwaysApply: true
---

# Schema pattern (Pydantic v2)

## Architecture guardrail — business services

- **`business_services`** method signatures (**arguments and return values**) use **Pydantic v2 models** for structured data. Use **plain primitives** (`str`, `UUID`, `bool`, `int`, …) only where a model is unnecessary (e.g. a single id).
- **Do not** use untyped **`dict`**, **`Dict[str, Any]`**, or loose **`Mapping`** as the **default** service API. That is **not** the standard Python project architecture.
- **Exceptions** (legacy bridge, rare adapter, product-specific constraint) are **opt-in**: they require **explicit alignment with the user / tech lead** and documentation (PR, ticket, or ADR)—never silent defaults.
- **Repositories** and **routers** exchange **Pydantic** with business services; map HTTP/ORM ↔ models at those edges.

## Where to use models

- **HTTP** request/response bodies and query shapes
- **Persistence DTOs** exchanged with repositories (not ORM classes in business code)
- **JSONB / JSON columns**: **always** define a matching **Pydantic v2 model** for the document shape—**strong typing** end-to-end; repository validates on load/store
- **Files**: YAML, JSON manifests, config at startup
- **Internal** boundaries where a structured object beats a loose `dict`
- **JWT auth context** at the API edge: validate **`request.state.auth`** into a model (e.g. **`AuthContext`**) — see **`architecture.md`** (JWT verification)

## Where models live — `src/models/` only

- **All** Pydantic models (request bodies, response shapes, domain DTOs, repo payloads) belong in **`src/models/`**, named by domain: `device_models.py`, `owner_models.py`, `tenant_security_config_models.py`, etc.
- **Never** define Pydantic models inside `src/api/` — not as `api/v1/models.py`, not as `api/internal/models.py`, not inline in router files.
- Router files (`api/v1/policy_routes.py`, `api/internal/router.py`, …) **import** from `src.models.*`; they contain only routing logic.

**Enforcement:** `import-linter`'s layers contract (see **`python-tooling.md`**) makes it a CI failure for `src.api` to import from anything other than `src.models`, `src.business_services`, and `src.common`. Since models are defined only in `src.models`, a route file with a locally-defined `BaseModel` subclass would have no valid import path for it — pyright will surface the inconsistency. Additionally, any `BaseModel` subclass found under `src/api/` during code review or agent sessions is an immediate reject with no exceptions.

## Metadata field naming

- **Do not** use a bare field name **`metadata`** on schemas when it collides with frameworks or reserved semantics.
- Use a **prefixed name** such as **`device_metadata`**, **`owner_metadata`**, or team-agreed **`_metadata`** for auxiliary / extensible bag fields so models stay explicit and tooling-friendly.

## Domain enums (strong typing — no magic strings)

Use **`enum.Enum`** for any **closed vocabulary** shared across API, services, and persistence (status values, artifact profiles, parse profiles, lifecycle states). **Do not** type these as bare **`str`** or scatter string literals across call sites when a single enum exists or should exist.

### Class shape

- Subclass **`str, Enum`** (or **`StrEnum`** on 3.11+) so values are **strings** at runtime, JSON/OpenAPI stay readable, and **`model_dump(mode="json")`** emits plain strings for DB columns.
- Name the **class** with a **`Type` suffix** (e.g. **`ReleaseLifecycleStatusType`**, **`ReleaseArtifactTypeType`**, **`DefinitionParseProfileType`**) so enums are grep-friendly and distinct from Pydantic models.
- **Member names** are **`SCREAMING_SNAKE`**; **values** are the **stable wire/DB strings** (often lowercase_snake), e.g. **`CAN_DBC = "can_dbc"`**.

### Pydantic fields

- Prefer a field name with an **`_type` suffix** when the field holds an enum (**`status_type`**, **`artifact_type`**, **`definition_profile`** as enum type where the name fits). If the domain word is already unambiguous, a short name is acceptable; stay consistent within a bounded context.
- **HTTP**: declare **`Query(...)` / body fields** using the **enum type**, not **`str`**, so OpenAPI lists allowed values and the stack validates at the edge. **`PUT`** and multi-field writes **must** use **body models**, not query — see **`http-api-conventions.md`**.
- **Services**: accept and return the **enum type** (or Pydantic models containing enums); use **`.value`** only at the last step when the ORM or a third-party API requires a plain string.

### Placement

- Group **related** enums in one module when they evolve together (e.g. **`src/models/release_artifact_types.py`** for artifact profile + parse profile). Split when domains are unrelated to avoid giant "god" enum modules.

### Database

- Persist as **`VARCHAR`** (string values). No opaque integer codes unless product explicitly standardizes them.
- **Repository** (or ORM adapter) is the usual place to ensure **string column ↔ enum** on read/write; **business** and **routers** see **Pydantic** models with **enum** fields, not raw strings for those columns.

### Verify / scripts

- Import the shared enum and use **`SomeEnumType.MEMBER.value`** (or the enum in APIs that accept it) instead of duplicating string literals in **`tests/verify/`** or **`tests/debug/`**.

## Model strictness

- Prefer **`model_config = ConfigDict(extra="forbid")`** for **internal** DTOs and strict APIs.
- Use **`extra="ignore"`** for **external** or versioned payloads where unknown keys must be tolerated.

## Loading data

- After **`yaml.safe_load`**, **`json.loads`**, or DB JSON extraction, validate with **`Model.model_validate(...)`** (or **`model_validate_json`**).
- Avoid ad-hoc **`dict["key"]`** chains at module boundaries.

## Fields and invariants

- Use **`Field(..., description="...")`** for non-obvious fields.
- Use **`field_validator`** / **`model_validator`** for invariants.

### `Field()` — always use keyword form for defaults (pyright requirement)

Always pass the default as a **keyword argument** to `Field()`. The positional form `Field(None, ...)` is not recognised as a default by pyright's Pydantic v2 stubs — pyright will treat the field as required and raise type errors at every call site.

```python
# Wrong — pyright treats this field as required (no recognised default)
name: Optional[str] = Field(None, description="Display name")

# Correct — pyright recognises the default and treats the field as optional
name: Optional[str] = Field(default=None, description="Display name")
```

This applies to any default value, not just `None`:

```python
# Wrong
status: str = Field("active", description="Current status")

# Correct
status: str = Field(default="active", description="Current status")
```

### `extra="allow"` models — use `model_validate` at construction sites

When a model has `extra="allow"` (typically for variable-shape JSONB documents), pyright correctly rejects passing undeclared fields as `__init__` keyword arguments — the typed `__init__` signature only includes declared fields even when extra fields are allowed at runtime.

Always use **`model_validate({...})`** to construct `extra="allow"` models with dynamic fields:

```python
class JobEventPayloadDocument(BaseModel):
    model_config = ConfigDict(extra="allow")
    event_type: str

# Wrong — pyright error: unexpected keyword argument
doc = JobEventPayloadDocument(event_type="upload", vin_count=5, source="csv")

# Correct — model_validate accepts arbitrary dict keys
doc = JobEventPayloadDocument.model_validate({
    "event_type": "upload",
    "vin_count": 5,
    "source": "csv",
})
```

This applies at every call site that constructs such a model with dynamic keys. Static construction (only declared fields) can still use keyword arguments.

## Settings (`pydantic-settings`)

- Shared **`BaseSettings`** with **`PREFIX`**, **`SettingsConfigDict(env_file=".env", ...)`**, and documented **`get_instance()`** when standardized.

## Related rules

- **Repository-only ORM:** `repository-pattern.md`
- **Typing:** `strong-typing.md`
- **Imports:** `python-imports.md`
- **Layout:** `architecture.md`
