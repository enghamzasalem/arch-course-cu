# Assignment: Task Board API — Compatibility and Coupling

## Overview

You **analyze and design** (not fully implement) how a **Task Board REST API** and its clients stay **maintainable** under change. You apply **Chapter 8: Compatibility and Coupling**: identify coupling, classify API changes, plan **version coexistence**, and write a short **compatibility policy**.

**Scenario:** A product exposes `GET/POST/PATCH /tasks` for web, mobile, and partner integrations. Teams want new fields, stricter validation, and internal service splits without breaking everyone at once.

## Learning Objectives

By completing this assignment, you will:

- Identify **coupling** between components and clients
- Classify **breaking vs non-breaking** API and contract changes
- Relate changes to **semantic versioning** (MAJOR / MINOR / PATCH)
- Propose **v1/v2 coexistence** (routing, headers, gateways)
- Document **deprecation** and **migration** expectations

---

## Baseline system (given)

Assume this logical structure (you may refine names):

- **Web SPA** and **mobile app** call the public API
- **API gateway** (optional in your diagram) routes to **Task API service**
- **Task API** uses **Task store** (database) and **Notification** service for reminders
- **Partner integrations** call the same public API with long-lived clients

You will **not** implement code; you document architecture decisions.

---

## `/tasks` API: example JSON (baseline vs after changes)

Use the examples below as a **shared reference** for Part 2 (and in your write-up if you quote payloads). Paths are relative to your chosen base (e.g. `https://api.example.com`); assume **`Content-Type: application/json`** on bodies unless noted.

### Baseline **v1** (before changes A–E)

**Assumptions for v1**

- No `X-Client-Id` header required.
- Task field `title` may be up to **500** characters.
- Each task has: `id` (string), `title` (string), `done` (boolean).

---

**`GET /tasks`** — list tasks (200 OK)

```http
GET /tasks HTTP/1.1
Host: api.example.com
Accept: application/json
```

```json
{
  "tasks": [
    {
      "id": "tsk_7a2c",
      "title": "Review compatibility notes",
      "done": false
    },
    {
      "id": "tsk_91fe",
      "title": "Deploy hotfix to gateway",
      "done": true
    }
  ]
}
```

---

**`GET /tasks/{id}`** — one task (200 OK)

```http
GET /tasks/tsk_7a2c HTTP/1.1
Host: api.example.com
Accept: application/json
```

```json
{
  "id": "tsk_7a2c",
  "title": "Review compatibility notes",
  "done": false
}
```

---

**`POST /tasks`** — create task (201 Created)

```http
POST /tasks HTTP/1.1
Host: api.example.com
Content-Type: application/json
```

```json
{
  "title": "File expense report"
}
```

```json
{
  "id": "tsk_new_01",
  "title": "File expense report",
  "done": false
}
```

---

**`PATCH /tasks/{id}`** — partial update (200 OK)

```http
PATCH /tasks/tsk_7a2c HTTP/1.1
Host: api.example.com
Content-Type: application/json
```

```json
{
  "done": true
}
```

```json
{
  "id": "tsk_7a2c",
  "title": "Review compatibility notes",
  "done": true
}
```

---

**Error example (v1)** — validation failure (400 Bad Request)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "title is required"
  }
}
```

---

### After each proposed change (illustrative)

Treat these as **what the wire format looks like** after that single change is deployed. In your answers you may still recommend v2 paths or headers— these samples show **payload/header shape** only.

---

#### After **A** — optional `priority` on list (and typically on single-task responses)

`GET /tasks` **200** — same as v1, but tasks may include `priority` when set:

```json
{
  "tasks": [
    {
      "id": "tsk_7a2c",
      "title": "Review compatibility notes",
      "done": false,
      "priority": "high"
    },
    {
      "id": "tsk_91fe",
      "title": "Deploy hotfix to gateway",
      "done": true
    }
  ]
}
```

Older clients that **ignore unknown fields** keep working; clients that **reject** unknown keys may break (state your assumption in Part 2).

---

#### After **B** — rename `done` → `completed` in **all** task JSON representations

`GET /tasks/tsk_7a2c` **200**:

```json
{
  "id": "tsk_7a2c",
  "title": "Review compatibility notes",
  "completed": false
}
```

`PATCH /tasks/tsk_7a2c` — client might send:

```json
{
  "completed": true
}
```

Any client or SDK still sending or expecting **`done`** is **broken** unless you define an alias period (your coexistence plan may keep `done` on v1 only).

---

#### After **C** — required header `X-Client-Id` on **all** requests

Example **`GET /tasks`**:

```http
GET /tasks HTTP/1.1
Host: api.example.com
Accept: application/json
X-Client-Id: mobile-ios-3.2.1
```

Example **`POST /tasks`**:

```http
POST /tasks HTTP/1.1
Host: api.example.com
Content-Type: application/json
X-Client-Id: partner-acme-integration
```

```json
{
  "title": "Sync invoices"
}
```

Requests **without** `X-Client-Id` → e.g. **400** or **401** (you decide in policy; show consistency):

```json
{
  "error": {
    "code": "MISSING_CLIENT_ID",
    "message": "X-Client-Id header is required"
  }
}
```

---

#### After **D** — `title` max length **100** characters (was 500)

**Valid** `POST /tasks`:

```json
{
  "title": "Short title under 100 chars"
}
```

**Invalid** if `title` length > 100 (example 400):

```json
{
  "title": "This string is intentionally longer than one hundred characters so that the server rejects it under the new maximum title length rule."
}
```

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "title exceeds maximum length of 100"
  }
}
```

Titles that were **valid in v1** (101–500 chars) become **errors** after D — a **semantic** break even though the JSON field name is unchanged.

---

#### After **E** — new endpoint `POST /tasks/bulk`

Does not alter existing `POST /tasks`; adds a **new** request/response shape.

```http
POST /tasks/bulk HTTP/1.1
Host: api.example.com
Content-Type: application/json
X-Client-Id: partner-acme-integration
```

```json
{
  "tasks": [
    { "title": "First bulk item" },
    { "title": "Second bulk item" }
  ]
}
```

Example **200** or **207** (you may define multi-status; be explicit in your doc):

```json
{
  "results": [
    { "index": 0, "status": "created", "task": { "id": "tsk_b1", "title": "First bulk item", "done": false } },
    { "index": 1, "status": "created", "task": { "id": "tsk_b2", "title": "Second bulk item", "done": false } }
  ]
}
```

If you require **`X-Client-Id` only after C**, you can show bulk **with** that header when discussing E+C together; in Part 2 treat **E alone** as “new endpoint + new body schema” unless the prompt says otherwise.

---

## Part 1: Coupling analysis

### Task 1.1: Coupling inventory

**Objective:** Map dependencies and characterize coupling.

**Requirements:**

1. List **at least 5 elements** (e.g. Web SPA, Mobile, Partner client, Gateway, Task API, Task store, Notification). For each pair that depends on another, describe:
   - Direction of dependency
   - **Type of coupling** (e.g. data, control, temporal, deployment — use the terminology from the chapter / lecture)
   - **Why** a change on the provider side might **ripple** to the consumer

2. Identify **two** places where coupling is **intentionally tight** (acceptable trade-off) and **two** where you would **reduce** coupling (how: abstraction, boundary, async, versioning, etc.).

**Deliverable:** `part1_coupling_analysis.md`

**Grading:** 30 points

---

### Task 1.2: Coupling / dependency diagram

**Objective:** Visualize dependencies and coupling hotspots.

**Requirements:**

1. Create a **diagram** (draw.io): boxes for components/clients, **arrows** for dependencies.
2. **Label** arrows or regions with coupling type or strength (e.g. “data: shared DTO”, “temporal: sync REST”).
3. Include a **legend**.

**Deliverables:**

- `part1_coupling_diagram.drawio`
- `part1_coupling_diagram.png`

**Grading:** 20 points

---

## Part 2: Compatibility and versioning

### Task 2.1: Change classification

**Objective:** Practice **syntactic** vs **semantic** compatibility and semver.

**Requirements:**

Consider these **proposed changes** (treat each independently):

| # | Proposed change |
|---|-----------------|
| A | Add optional JSON field `priority` to `GET /tasks` response |
| B | Rename JSON field `done` → `completed` in responses |
| C | Require new header `X-Client-Id` on all requests |
| D | Change `title` max length from 500 to 100 characters |
| E | Add `POST /tasks/bulk` with new request shape |

For **each A–E**:

1. **Breaking or non-breaking** for existing clients (justify)
2. Recommended **semver bump** for the **public API** if you follow strict semver rules (MAJOR / MINOR / PATCH)
3. One sentence on **semantic** risk even when JSON shape looks compatible

**Deliverable:** `part2_compatibility_changes.md`

**Grading:** 25 points

---

### Task 2.2: Version coexistence

**Objective:** Plan how **v1 and v2** run together during migration.

**Requirements:**

1. Choose **one** strategy (or hybrid): e.g. path prefix (`/v1`, `/v2`), `Accept-Version` / custom header, separate gateway routes, or subdomain.
2. Describe how **new** clients use v2 while **legacy** clients stay on v1 for a **sunset period**.
3. State **one operational cost** (e.g. dual deployment, routing rules, documentation burden).

**Deliverable:** `part2_version_coexistence.md`

**Grading:** 15 points

---

## Part 3: Policy and migration story

### Task 3.1: Compatibility policy

**Objective:** Short **governance** text for teams and integrators.

**Requirements:** Address in **≤2 pages** (markdown):

1. Rules for **additive** vs **breaking** changes
2. **Deprecation** process: notice period, communication channel, how sunset is announced
3. **Error format** stability (e.g. keep error `code` stable; when codes may change)
4. How **partner** integrations are treated vs first-party apps (if different)

**Deliverable:** `part3_compatibility_policy.md`

**Grading:** 20 points

---

### Task 3.2: Migration sequence diagram

**Objective:** Show one **migration** or **dual-version** flow.

**Requirements:**

1. **Sequence diagram** (draw.io): e.g. client discovers v1 sunset → updates to v2 → or gateway routes by version.
2. **≥5 participants** (e.g. Client, Gateway, Task API v1, Task API v2, Store), labeled messages.

**Deliverables:**

- `part3_migration_sequence.drawio`
- `part3_migration_sequence.png`

**Grading:** 10 points

---

## Submission Requirements

### Submission Method

GitHub Pull Request. See `../lecture-3/SUBMISSION_GUIDE.md` if needed.

### File Structure

```
submissions/YOUR_NAME/
├── part1_coupling_analysis.md
├── part1_coupling_diagram.drawio
├── part1_coupling_diagram.png
├── part2_compatibility_changes.md
├── part2_version_coexistence.md
├── part3_compatibility_policy.md
├── part3_migration_sequence.drawio
├── part3_migration_sequence.png
└── README.md
```

### Diagrams

Provide **both** `.drawio` and `.png` for every diagram.

---

## Grading Rubric

| Part | Task | Points |
|------|------|--------|
| Part 1 | Coupling analysis | 30 |
| Part 1 | Coupling diagram | 20 |
| Part 2 | Change classification & semver | 25 |
| Part 2 | Version coexistence | 15 |
| Part 3 | Compatibility policy | 20 |
| Part 3 | Migration sequence diagram | 10 |
| **Total** | | **120** |

### Quality Criteria

- **Coupling:** Precise vocabulary; plausible ripple effects
- **Diagrams:** Match the narrative; readable labels and legend
- **Compatibility:** Clear breaking vs non-breaking reasoning; semver aligned with rules you state
- **Policy:** Actionable, consistent with Part 2

---

## Getting Started

1. Read **`/tasks` API: example JSON (baseline vs after changes)** above before writing Part 2.
2. Run **`example1_compatibility_and_api_evolution.py`** and **`example2_coupling_and_dependencies.py`**.
3. Sketch clients → API → backend on paper; mark **who knows what** about payloads and deployment.
4. For Part 2, assume **strict** JSON clients that break on unknown required fields or renamed keys unless you explicitly design tolerance.

---

## Deadline

**Due date:** [To be announced by instructor]

**Submission:** GitHub Pull Request to `arch-course-cu/lecture-8/submissions/YOUR_NAME/`

Good luck.
