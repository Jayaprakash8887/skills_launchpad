---
description: REST/FastAPI — PUT/POST/PATCH use JSON body only for writes; query for GET filters; path for IDs; OpenAPI-friendly.
alwaysApply: true
---

# HTTP API conventions (FastAPI)

These rules keep **`src/api/`** contracts **uniform**, **documentable**, and consistent across sibling services in the platform (creates/updates use **Pydantic JSON bodies** from **`src/models/`**; **query** is for list/filter/pagination on **GET**).

## PUT — full writes use **body only**

- **`PUT` must not** carry the resource payload as **query parameters**. Business fields belong in a **single JSON request body** as one **Pydantic model** from **`src/models/`**.
- **Path** identifies the resource (e.g. `/tenants/{tenant_id}/…`); **body** carries the replaceable state. OpenAPI then documents one obvious contract for clients and BFFs.

## Mutations (POST, PATCH, and POST-as-action)

- **Default:** any multi-field or domain payload is a **JSON request body** declared as a **single Pydantic model** from **`src/models/`** (see **`pydantic-schemas.md`** — never define request bodies inline in routers).
- **`PATCH`** uses a **body model** (optional fields or **`model_dump(exclude_unset=True)`** downstream). Do not put the "shape of the change" on the query string.
- **`POST`** actions that take parameters (e.g. enable feature + one flag) use a **small JSON body model**, not query strings, so OpenAPI stays consistent with **`PUT`**.

## When query parameters are appropriate

- **GET:** filters, pagination (`skip` / `limit` or team standard), sort keys, **`detailed=true`**-style toggles — use explicit **`Query(..., description=...)`** where helpful.
- **Rare POST** with no payload: document that the body is empty; avoid adding business fields only as query params.

## Path parameters

- **Resource identifiers** (`tenant_id`, `device_id`, etc.) belong in the **path** when they identify the resource being read or mutated.
- Avoid **required** identifiers only in **query** on routes that otherwise use tenant/device in the path (confusing for clients and security reviews).

## Validate vs apply

- When you expose **"validate this payload"** and **"apply this payload"** for the same concern (e.g. policy), use the **same field names and types** in both body models; **`tenant_id`** may appear in the path only — use a shared model or a base model and document whether path wins over body when both exist.

## FastAPI pitfall (why this rule exists)

- A handler parameter such as `mode: SomeEnumType` **without** `Path` / `Query` / `Body` on a POST/PUT/PATCH is treated as **query** by default, not body. **Structured writes must use an explicit Pydantic body parameter** — especially for **`PUT`**, where accidental query binding is easy and wrong.

## Internal (`/internal/...`) vs authenticated API

- **Inbound** **`/internal/v1`** on *this* service is optional (see **`architecture.md`** service profiles). When present, trust model = network / mesh / keys (document in README).
- **Outbound** calls to another service's internal API belong in **`infra_services/`**, not in route handlers.
- Auth and "who may call what" on **public** routes are product concerns — document in **`docs/specification/`** and README. This rule does not relax **model placement** (`src/models/` only).

## Contract changes

- Prefer a **single wire shape** (body-only for writes). If you must change a published contract, treat it as a **breaking change**: document in **README** / **CHANGELOG** and update **verify** scripts — avoid **dual** query + body support unless explicitly approved.

## Related rules

- **Models location & enums:** `pydantic-schemas.md`
- **Router layout:** `architecture.md`
- **Verify clients:** `testing-verify-flows.md`
