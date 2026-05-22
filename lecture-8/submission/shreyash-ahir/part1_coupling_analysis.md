# Part 1.1 — Coupling Inventory

## System Elements

The system has seven identifiable elements: Web SPA, Mobile App, Partner Integration,
API Gateway, Task API, Task Store (database), and Notification Service.

Coupling is analyzed using the facets from Chapter 8: interface, data, timing, discovery,
interaction, platform, and session.

---

## Dependency Pairs

### 1. Web SPA → API Gateway / Task API

**Direction:** Web SPA depends on Task API (via Gateway)

**Coupling types:**

- **Interface coupling** (high): The SPA encodes field names (`id`, `title`, `done`),
  endpoint paths (`/tasks`, `/tasks/{id}`), and HTTP methods into its JavaScript.
  Any rename of a field or path breaks the SPA at runtime.

- **Data coupling** (medium): The SPA parses the task JSON DTO. It only uses the
  fields it knows about — but if the DTO shrinks (a field is removed), the SPA's
  rendering logic breaks silently or throws.

- **Timing coupling** (medium): The SPA makes synchronous HTTP calls and blocks the
  UI thread while waiting. If the API is slow or unavailable, the user sees a loading
  spinner or an error.

**Ripple risk:** A field rename (like `done` → `completed`) in the API response breaks
every SPA component that reads `task.done`. No compile-time check catches this.

---

### 2. Mobile App → API Gateway / Task API

**Direction:** Mobile App depends on Task API (via Gateway)

**Coupling types:**

- **Interface coupling** (high): Same as SPA, but worse: mobile apps are compiled and
  shipped through app stores. A breaking change to the API means clients in the field
  run the old code against a changed interface for weeks until users update.

- **Platform coupling** (low-medium): iOS and Android SDKs may hardcode the base URL.
  Changing the API's host or certificate anchor breaks the mobile app at the
  discovery/binding level.

- **Session coupling** (low): The API is currently stateless (no session); each request
  carries all context. This is a coupling-reducing design choice.

**Ripple risk:** Adding a required header (change C: `X-Client-Id`) breaks all installed
mobile app versions that do not send it. The provider cannot force an upgrade.

---

### 3. Partner Integration → API Gateway / Task API

**Direction:** Partner depends on Task API

**Coupling types:**

- **Interface coupling** (high): Partners generate code from a shared API schema or
  manually write clients. Long-lived partner integrations may run unchanged for years,
  making them the most brittle consumers of any interface change.

- **Data coupling** (high): Partners often store and transform the full task DTO in their
  own systems. If the response schema changes shape (field rename, type change), their
  internal data pipeline breaks.

- **Temporal coupling** (medium): Partner batch jobs may call the API in fixed time
  windows. If API availability drops during that window, their batch fails entirely.

**Ripple risk:** Semantic changes (change D: title max length reduction) invalidate data
that partners have already stored and may try to re-submit. The partner's existing records
become unsubmittable without migration on their side.

---

### 4. API Gateway → Task API

**Direction:** Gateway depends on Task API (routes requests to it)

**Coupling types:**

- **Discovery coupling** (medium): The Gateway must know the address of the Task API
  service. If the Task API moves to a different host or port, the Gateway routing rules
  must be updated.

- **Interface coupling** (low): The Gateway typically passes requests through without
  inspecting the body. However, if it enforces request validation (e.g. the
  `X-Client-Id` header in change C), it becomes coupled to the header schema.

- **Deployment coupling** (medium): For v1/v2 coexistence, the Gateway must route
  `/v1/tasks` and `/v2/tasks` to different service instances. This means the Gateway
  configuration must be updated whenever a new API version is introduced.

**Ripple risk:** A split of Task API into separate v1 and v2 services requires Gateway
routing rule changes. Misconfigured routing silently sends v2 clients to the v1 service.

---

### 5. Task API → Task Store (database)

**Direction:** Task API depends on Task Store

**Coupling types:**

- **Data coupling** (high): The Task API's data model maps directly to the Task Store
  schema. If the `tasks` table gains a `priority` column (change A), the API must
  be deployed together with the schema migration, or queries fail.

- **Deployment coupling** (high): Schema migrations and API deployments must be
  sequenced carefully. Running the new API against the old schema (before migration)
  or the old API against the new schema (after migration) causes runtime errors.

- **Temporal coupling** (high): The Task API makes synchronous database queries on
  every request. If the database is unavailable, every API request fails.

**Ripple risk:** A schema change (adding `NOT NULL` column without default) breaks the
running API immediately on deployment of the migration, before the API code is updated.

---

### 6. Task API → Notification Service

**Direction:** Task API depends on Notification Service (for reminders)

**Coupling types:**

- **Timing coupling** (medium-high if synchronous): If the Task API waits for the
  Notification Service to confirm delivery before returning a response, a slow or
  unavailable Notification Service degrades API response times.

- **Interface coupling** (low-medium): Task API sends a notification request; the
  Notification Service defines the message format. Changes to the notification schema
  require coordinated updates on both sides.

**Ripple risk:** A synchronous coupling here means a Notification Service outage causes
cascading failures visible to Task API clients. An asynchronous queue connector would
isolate the failure.

---

### 7. Task API (v1) → Task API (v2) [during coexistence]

**Direction:** The migration period introduces a relationship between versions

**Coupling types:**

- **Data coupling** (high): Both versions share the same Task Store. A schema migration
  that v2 requires must not break v1's queries that run concurrently.

- **Deployment coupling** (medium): Both versions must be deployed and scaled
  independently during the migration window.

**Ripple risk:** A v2 schema migration that adds a `NOT NULL` column with no default
breaks v1's `INSERT` statements immediately.

---

## Two Places Where Coupling Is Intentionally Tight (Acceptable)

**1. Task API ↔ Task Store**  
The data coupling between the API and the database is tight by design. The database is
a private implementation detail of the Task API — no external client depends on the
schema directly. Tight coupling here is acceptable because both sides are owned and
deployed by the same team. The coupling is managed through disciplined migration
sequencing (expand-contract pattern) rather than abstracted away.

**2. Web SPA ↔ Task API (field names)**  
The SPA is a first-party client under the same product team. Tight interface coupling
here is a controlled trade-off: the team can update both the SPA and the API in
coordinated releases. For a partner integration this would be unacceptable; for a
same-team client it is a reasonable pragmatic choice.

---

## Two Places Where Coupling Should Be Reduced

**1. Task API → Notification Service (timing coupling)**  
Currently the API calls the Notification Service synchronously, making every API
response dependent on the Notification Service's availability. This should be reduced
by introducing an **asynchronous connector** (message queue): the Task API publishes
a `task.reminder_requested` event and returns immediately. The Notification Service
consumes the event independently. A failure in the Notification Service no longer
degrades the Task API.

**2. Partner Integration ↔ Task API (data coupling on full DTO)**  
Partners couple tightly to the full task DTO, including fields they do not use. This
should be reduced by offering **field projection** (`GET /tasks?fields=id,title`) or
**separate partner-specific endpoints** that expose a minimal, stable subset of fields.
Partners then depend only on the fields they actually use, reducing the blast radius of
any field change.
