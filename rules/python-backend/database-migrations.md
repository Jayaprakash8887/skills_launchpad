---
description: Alembic — agent runs create_postgres_migration.sh (autogenerate); human runs run_postgres_migration.sh. No DDL-NOTE substitutes.
alwaysApply: true
---

# Database migrations (Alembic)

Alembic requires a revision file under **`postgres_migrations/versions/`**.
That file is produced **only** by the consumer's create script (shipped by
**`python-fastapi-foundation`**), which runs Alembic **`revision --autogenerate`**.
Applying revisions to a live database is **human-owned**.

## Mandatory workflow (do not invent another)

1. **Create the revision file (agent / implementer):**

   After updating ORM schema and **`postgres_migrations/env.py`** imports:

   ```bash
   ./scripts/create_postgres_migration.sh "description"
   ```

   The script must call Alembic **`revision --autogenerate -m`**. It materializes
   a revision under **`postgres_migrations/versions/`** from registered
   **`postgres_metadata`**. Do **not** invent revision files by hand or call raw
   **`alembic`** outside this script.

   The script expects the target database to be at **head** (correct
   autogenerate diffs). If it refuses, the human must apply pending revisions
   first, then the agent re-runs create.

2. **Review (agent):** Read the generated **`upgrade`** / **`downgrade`**. Adjust
   only when autogenerate is wrong (ordering, destructive ops, missing
   constraints). Prefer intentional edits over blind acceptance.

3. **Apply (human):**

   ```bash
   ./scripts/run_postgres_migration.sh head   # or +1 / -1 per script help
   ```

Do **not** document raw `alembic` CLI as the default workflow in repo docs.
Scripts live in each service's **`scripts/`** (see the FastAPI chassis).

## Who does what (do not mix this up)

| Actor | Allowed | Forbidden |
|-------|---------|-----------|
| **Agent / automated work** | Update **`src/database/postgres/schema/`** and aligned repos/models; update **`postgres_migrations/env.py`** imports so new ORM modules register on **`postgres_metadata`**; **run** **`./scripts/create_postgres_migration.sh`** when schema/`env.py` changes require a new revision; review/adjust the generated revision | Run **`./scripts/run_postgres_migration.sh`** (or otherwise apply migrations) unless the human explicitly asked in that session; invent **`versions/`** files without the create script; invent **DDL-NOTE** / instruction-only substitutes instead of running create; call ad-hoc **`alembic revision`** / **`alembic upgrade`** outside the scripts |
| **Human** | Run **`run_postgres_migration.sh`** to apply (and to bring DB to head before a new create if needed) | Treating blank hand-written revisions or DDL notes as the default instead of the create script |

## Policy

- New files under **`versions/`** start **only** from
  **`./scripts/create_postgres_migration.sh`** (**`--autogenerate`**).
- Agents **must** run that script when a schema change needs a migration —
  not describe DDL in chat/PR notes as a substitute.
- Agents **must not** run **`run_postgres_migration.sh`**.
- Do **not** use blank **`revision -m`** (no autogenerate) as the chassis
  default.

## Schema registration vs revisions

- **`postgres_migrations/env.py`** is part of **schema registration** (import
  side effects on `postgres_metadata`); agents update it when adding tables,
  same as **`schema/`**.
- **`postgres_migrations/versions/`** files are **script-owned** (Alembic
  autogenerate via create). Agents commit the generated file after review;
  they do not hand-author a parallel instruction doc instead of running create.

## Practice

- Name revisions clearly; keep **`upgrade`** and **`downgrade`** symmetric and
  safe for shared environments.
- Coordinate **`schema/`**, **`env.py`**, and the generated revision so ORM
  metadata and the database stay aligned after the human applies.

## Related rules

- **Repositories & ORM:** `repository-pattern.md`
- **Chassis scripts:** `python-fastapi-foundation` (`scripts/create_postgres_migration.sh`, `scripts/run_postgres_migration.sh`)
