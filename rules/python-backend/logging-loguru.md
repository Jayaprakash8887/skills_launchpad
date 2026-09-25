---
description: Logging with loguru — get_logger, setup_logging, structured JSON output, correlation context.
alwaysApply: true
---

# Logging (loguru)

## Central API

- Implement **`get_logger()`** and **`setup_logging(settings)`** in **`src/logging/`** (or one module re-exporting them).
- Configure sinks, levels, and format from **settings** (`AppSettings` or equivalent), not scattered literals.
- **`APP_LOG_LEVEL`** (or equivalent on settings) drives both loguru sinks and the stdlib **root** logger level in **`setup_logging`**.

## Output format — structured JSON in production

- **Production deployments must emit structured JSON** (one JSON object per log line) so logs are queryable by field in aggregators (Datadog, Loki, ELK, etc.).
- **Local development** uses human-readable text output for readability.
- Drive the choice from a settings value (e.g. **`LOG_FORMAT=json`** in prod, **`LOG_FORMAT=text`** locally). The implementation lives in `setup_logging()` — call sites (`logger.info(...)`) are identical regardless of format.
- All structured logs must include at minimum: **`service`**, **`environment`**, **`correlation_id`**, **`level`**, **`message`**, **`timestamp`**. Bind `service` and `environment` once at app startup; bind `correlation_id` per request / job / batch run.

## Loguru vs stdlib (two paths)

| Path | Used for | Configuration |
|------|----------|----------------|
| **loguru** (`get_logger()`) | All **`src/`** application and service code | Console + JSON/text sink in **`setup_logging`**; level from settings |
| **stdlib `logging`** | Third-party libs (boto3, uvicorn, SQLAlchemy, etc.) | **Root level only** — set from the same app log level; **no** catch-all root handler |

### Stdlib rules (in `setup_logging`)

- **Do** set **`logging.getLogger().setLevel(...)`** from app log level so child loggers inherit unless they override.
- **Do** clear **root handlers** after setup so stdlib does not duplicate loguru output to stderr.
- **Do not** use **`logging.basicConfig(level=0, ...)`** or attach a root **`StreamHandler`** that prints every library DEBUG line.
- **Do not** maintain a hardcoded "noisy loggers" list in shared rules; if one dependency still spams after root-level fix, cap **that** logger in repo setup or env — case by case.

### Uvicorn / HTTP server

- Pass **`log_level=`** into **`uvicorn.run`** (aligned with app settings). Uvicorn configures **`uvicorn`**, **`uvicorn.error`**, **`uvicorn.access`** on its own; do not rely on **`basicConfig`** for server access logs.

## Usage

- After startup **`setup_logging`**, at module scope: **`logger = get_logger()`**.
- In service base classes, set **`self.logger = get_logger()`** in **`__init__`** (or use inherited **`self.logger`**) so instance methods log consistently.

## Message style

- Prefer loguru **placeholders**: **`logger.info("User {} logged in", user_id)`** instead of f-strings for high-volume paths (defer formatting when the level is disabled).
- Pass structured fields as **keyword arguments** to log calls so they appear as **discrete queryable JSON fields** in production output. IDs, status values, and domain identifiers must always be kwargs — not embedded in the message string.

### `{}` placeholders vs kwargs — critical distinction for structured logging

`{}` placeholders are convenient for human-readable text mode. In JSON mode they **defeat structured logging** — the value is interpolated into the `message` string and is no longer a queryable field:

```python
# Wrong for structured logging — campaign_id disappears into message text
logger.info("Created campaign {} for tenant {}", campaign.id, tenant_id)
# JSON output: {"message": "Created campaign abc-123 for tenant xyz-456"}
# Cannot filter by campaign_id or tenant_id in Datadog / Loki

# Correct — discrete queryable fields
logger.info("Created campaign", campaign_id=str(campaign.id), tenant_id=str(tenant_id))
# JSON output: {"message": "Created campaign", "campaign_id": "abc-123", "tenant_id": "xyz-456"}
# Can filter: @campaign_id:abc-123 AND @tenant_id:xyz-456
```

**Rule:** keep the message string a static human-readable label. Put every variable value — IDs, counts, statuses, resource names — as a **named kwarg**. Both text and JSON modes render correctly; only JSON mode makes the values queryable.

## Correlation / tracing

- Use **`LoggingContext(correlation_id)`** (or `logger.contextualize(...)`) around a **request**, **job**, or **batch run** so all nested logs share the ID as a structured field.
- Set correlation ID in **middleware**, **main**, or **lifespan** as early as practical.
- In structured output, `correlation_id` must appear as a **top-level field**, not embedded in the message string.

## Errors

- In top-level handlers / **`main`**, use **`logger.exception("...")`** to capture stack traces.
- In deeper library-style code, **`logger.error("...", exc_info=True)`** when you intentionally handle and re-raise or wrap.

## Related rules

- **Layout:** `architecture.md` (`logging/` package)
- **Imports:** `python-imports.md`
