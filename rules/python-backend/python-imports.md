---
description: Module imports — all at file top; no local/function-scope imports (team standard).
alwaysApply: true
---

# Imports (module scope only)

## Rule

- Place **all** `import` and `from … import` statements at the **top of the file** after the module docstring (PEP 8 order: stdlib, third party, local).
- **Do not** use **local imports** inside functions, methods, or class bodies for normal dependencies.

## Why

- Easier review of dependencies, cycles, and unused imports.
- Consistent with a **strong-typed**, explicit codebase.

## No `TYPE_CHECKING`-only imports

- **Do not** use **`if TYPE_CHECKING: ... import`** for dependencies that are part of the module's real contract (e.g. settings types on public function signatures). Prefer a **normal top-level import** so the dependency graph is visible at runtime and **import cycles surface as design issues** to fix (split modules, invert dependency), not hidden.
- **Do not** use **string annotations** or **`TYPE_CHECKING`** to postpone names for real dependencies—use **direct imports** and fix cycles with structure (see **`strong-typing.md`**).

## Service modules

- Module and class names under **`business_services/`** and **`infra_services/`**
  must use the **`*_service`** / **`*Service`** suffix (see **`architecture.md`**).
- Import **service classes** and **`get_*_service`** getters from their **service files** (e.g. **`device_service.py`**), **not** from package **`__init__.py`** re-exports.

## Narrow exception

- **DI bootstrap only**: `dependency_container.py` (or equivalent) may use **lazy imports inside** `configure_container()`, `initialize_all_services()`, or similar **factory functions** strictly to break **circular import** cycles. Do not spread this pattern elsewhere—fix cycles with layering or smaller modules first.

## Related rules

- **Layout:** `architecture.md`
- **DI:** `dependency-injection.md`
