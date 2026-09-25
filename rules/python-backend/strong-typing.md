---
description: Strong typing — Python 3.12+, annotations, validated boundaries, JSONB → Pydantic.
alwaysApply: true
---

# Strong typing

## Baseline

- Target **Python 3.12+**.
- Annotate **public** functions and methods, including **`-> None`**.
- Prefer concrete types over **`Any`** at API, file, settings, and **persistence** boundaries.

## Persistence and JSONB

- **JSONB** (and structured JSON) columns must have a **Pydantic v2 model**; repositories validate into that model before business logic sees the data (see **`pydantic-schemas.md`** and **`repository-pattern.md`**).

## Boundaries

- **Validate at the edges**: env → **`AppSettings`**; HTTP → Pydantic; files → **`model_validate`**; DB JSON → Pydantic in the **repository**.
- **`business_services`** public methods default to **Pydantic** in/out—not untyped **`dict`**; exceptions need explicit alignment (see **`pydantic-schemas.md`**).
- **Closed vocabularies** (statuses, profiles, kinds): use **`str, Enum`** with a **`Type` suffix** on the class; do not use untyped **`str`** for those domains (see **Domain enums** in **`pydantic-schemas.md`**).
- Inner logic works with already-validated types.

## Collections and generics

- Prefer **`list[Foo]`**, **`dict[str, Bar]`** over bare **`list`** / **`dict`**.
- Prefer **`TypedDict`** or a Pydantic model over untyped **`dict`** when shape is stable.

## Forward references and imports

- **No forward-reference workarounds** for real dependencies: do **not** rely on **`TYPE_CHECKING`-only imports** or **string-quoted** type names to hide imports. Use **direct imports** and fix design (smaller modules, invert dependencies) when cycles appear (see **`python-imports.md`**). **`isinstance()`** is preferred over **`hasattr()`** for type/shape checks at boundaries.

## Quality bar

- Do not silence checkers by widening to **`Any`** or untyped **`dict`**; fix the model or narrow the type.
- **pyright** is the enforcer — see **`python-tooling.md`** for configuration. Editor squiggles (Cursor / Pylance) and CI failures are the same tool; a clean pyright run is the definition of "passes type checking".

## Related rules

- **Fail fast vs defensive coding:** `fail-fast.md`
- **Pydantic / enums / metadata fields:** `pydantic-schemas.md`
- **Repos:** `repository-pattern.md`
