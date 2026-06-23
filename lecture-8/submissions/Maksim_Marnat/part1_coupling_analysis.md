# Part 1.1 — Coupling inventory

**System slice:** Web SPA, Mobile app, Partner integrations → (optional) **API Gateway** → **Task API** → **Task store** (DB); Task API → **Notification** (reminders).

## Dependencies (representative pairs)

| Consumer | Provider | Coupling | Why changes ripple |
|----------|----------|----------|-------------------|
| Web SPA | Gateway / Task API | **Data** (shared JSON task DTO), **temporal** (sync HTTPS, timeouts) | Response shape or status codes change → UI parsing and flows break. |
| Mobile app | Gateway / Task API | **Data**, **temporal**, **deployment** (app store releases lag server) | Same as web; older binaries stay in the wild → server cannot assume instant client upgrades. |
| Partner client | Gateway / Task API | **Data**, **control** (error codes, rate limits), **deployment** (long-lived integrations) | Partners bind to documented contracts; undocumented behavior or stricter validation breaks batch jobs. |
| API Gateway | Task API | **Data** (routing keys, paths), **control** (auth, headers) | New required headers or path changes need gateway config updates. |
| Task API | Task store | **Data** (ORM/schema, SQL), **temporal** (transaction boundaries) | Column/constraints change → API must map errors and fields consistently. |
| Task API | Notification | **Temporal** (call latency, failure handling), **data** (task id, schedule payload) | Notification contract or availability affects user-visible “reminder” behavior. |

*(Elements counted: Web SPA, Mobile, Partner client, Gateway, Task API, Task store, Notification — seven.)*

## Intentionally tighter coupling (acceptable)

1. **Task API ↔ Task store** — **Data + temporal**: transactional create/update of tasks with reminders needs consistent schema and commit order; loosening this (e.g. duplicate writes) would harm correctness. Acceptable because it is **inside** the service boundary.
2. **First-party Web/Mobile ↔ release process** — **Deployment**: internal apps ship with known API builds; tight coordination with backend releases is a deliberate trade-off for faster iteration vs partners.

## Where to reduce coupling

1. **Partner ↔ public API** — **Data/control**: publish **OpenAPI + explicit versioning** and **compatibility policy**; avoid partner reliance on incidental error text. Reduces surprise when fields or validation evolve.
2. **Task API ↔ Notification** — **Temporal**: replace direct synchronous calls with **async messaging** (queue/event) and a **stable integration DTO** so Notification outages or schema tweaks do not block task writes.
