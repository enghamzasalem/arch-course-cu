# Part 2: Compatibility and Versioning
## Task 2.1: Change Classification

---

### Assumptions (baseline)

All analysis treats existing clients as **strict JSON clients** — meaning they may reject unknown fields, break on renamed keys, or fail silently on unexpected validation errors. This is the conservative assumption stated in the assignment. Where a lenient client would behave differently, this is noted explicitly.

Semver rules applied:
- **PATCH** — backwards-compatible bug fixes only; no contract change
- **MINOR** — backwards-compatible additions (new optional fields, new endpoints)
- **MAJOR** — any breaking change: removal, rename, stricter validation, new required input

---

### Change A — Add optional `priority` field to `GET /tasks` response

**Example (after change A):**
```json
{
  "tasks": [
    { "id": "tsk_7a2c", "title": "Review compatibility notes", "done": false, "priority": "high" },
    { "id": "tsk_91fe", "title": "Deploy hotfix to gateway", "done": true }
  ]
}
```

#### 1. Breaking or non-breaking?

**Non-breaking for lenient clients. Potentially breaking for strict clients.**

For clients that follow the robustness principle (ignore unknown fields), adding an optional field to a response is safe — they simply discard `priority`. However, strict clients that deserialise into a fixed schema and reject unknown keys (e.g. a TypeScript interface with `additionalProperties: false`, or a generated SDK with exhaustive field validation) will throw a deserialisation error on any task that includes `priority`. Since `priority` only appears when set, this failure is intermittent and environment-dependent — making it harder to detect in testing.

**Assumption stated:** This analysis treats clients as strict. Therefore change A is classified as **potentially breaking**.

#### 2. Semver bump

**MINOR** — under strict semver, adding an optional response field is a backwards-compatible addition. A MAJOR bump would only be warranted if the field were required on input. Since `priority` is output-only and optional, MINOR is correct — but teams must communicate the strict-client risk in the changelog.

#### 3. Semantic risk

Even though the JSON shape gains only one optional field, a client that renders task lists without a priority column will silently discard business-critical urgency data that users expect to see reflected in the UI.

---

### Change B — Rename `done` → `completed` in all task representations

**Example (after change B):**
```json
{ "id": "tsk_7a2c", "title": "Review compatibility notes", "completed": false }
```

#### 1. Breaking or non-breaking?

**Breaking for all existing clients.**

This is a hard breaking change. Every client that reads `done` from a response will now receive `undefined` / `null` for the field it relies on — task completion state disappears silently. Every client that sends `done: true` in a `PATCH` request body will have its update ignored by the server (the server now only recognises `completed`). There is no alias period defined in the baseline, so the rename breaks both the read and write paths simultaneously. Mobile clients on old builds and partner integrations with no planned update cycle are broken with no migration window.

#### 2. Semver bump

**MAJOR** — removing a field from a response and renaming the field expected on input are both breaking changes under strict semver. A MAJOR version increment is required, and the old `done` field must continue to be served on v1 until the v1 deprecation window closes.

#### 3. Semantic risk

Even if an alias period is introduced (serving both `done` and `completed` on v1), a client that writes `done: true` and a separate client that writes `completed: true` can produce inconsistent state in the task store if the server applies them to different columns during the transition period.

---

### Change C — Require new header `X-Client-Id` on all requests

**Example (after change C):**
```http
GET /tasks HTTP/1.1
X-Client-Id: mobile-ios-3.2.1
```
**Missing header response:**
```json
{ "error": { "code": "MISSING_CLIENT_ID", "message": "X-Client-Id header is required" } }
```

#### 1. Breaking or non-breaking?

**Breaking for all existing clients.**

Every client that does not send `X-Client-Id` will receive a `400` or `401` error on every single request — a total loss of service. This is the most immediately visible breaking change in the set because it affects every endpoint simultaneously. Partners and old mobile builds that cannot be patched quickly will be locked out entirely. The change is also operationally risky: if the header is enforced at the gateway before the Task API, even health checks and monitoring probes will start failing unless they are updated.

#### 2. Semver bump

**MAJOR** — introducing a required input (a header that, if absent, causes a request to be rejected) is a breaking change for all callers. No existing client can continue to function without modification.

#### 3. Semantic risk

Even after clients add the header, the `X-Client-Id` value becomes an implicit trust input — if the server uses it for rate limiting, logging, or access control without validating its format, a malicious client can spoof any identity string and attribute abusive requests to a legitimate partner's client ID.

---

### Change D — Reduce `title` max length from 500 to 100 characters

**Example — now invalid (after change D):**
```json
{ "title": "This string is intentionally longer than one hundred characters so that the server rejects it under the new maximum title length rule." }
```
**Error response:**
```json
{ "error": { "code": "VALIDATION_ERROR", "message": "title exceeds maximum length of 100" } }
```

#### 1. Breaking or non-breaking?

**Breaking — a silent semantic break.**

The JSON field name (`title`) and its type (string) are unchanged, so the wire format looks identical. However, any client that was previously allowed to submit titles between 101 and 500 characters will now receive a `400 VALIDATION_ERROR` for requests that were valid under v1. This is particularly dangerous for partner integrations: a partner system may have been creating tasks with 200-character titles for months, and after this change those same API calls begin failing with no change on the partner's side. The break is **semantic, not syntactic** — the schema looks the same but the contract has narrowed.

#### 2. Semver bump

**MAJOR** — tightening an input constraint is a breaking change even when the field name and type are unchanged. Existing callers with valid v1 data can no longer successfully call the API without modifying their data or their clients.

#### 3. Semantic risk

Tasks already stored in the database with titles of 101–500 characters become unreachable via `PATCH` if the server validates title length on updates too — a client trying to mark such a task `done` while echoing the full title in the body will receive a `400` error on a record that already exists and was previously valid.

---

### Change E — Add `POST /tasks/bulk` endpoint

**Example request:**
```http
POST /tasks/bulk HTTP/1.1
Content-Type: application/json

{ "tasks": [ { "title": "First bulk item" }, { "title": "Second bulk item" } ] }
```
**Example response (207 Multi-Status):**
```json
{
  "results": [
    { "index": 0, "status": "created", "task": { "id": "tsk_b1", "title": "First bulk item", "done": false } },
    { "index": 1, "status": "created", "task": { "id": "tsk_b2", "title": "Second bulk item", "done": false } }
  ]
}
```

#### 1. Breaking or non-breaking?

**Non-breaking for all existing clients.**

Adding a new endpoint does not alter any existing endpoint's request shape, response shape, or validation rules. Clients that never call `POST /tasks/bulk` are entirely unaffected. Clients that discover and adopt the new endpoint are opting into new behaviour. The existing `POST /tasks` endpoint is unchanged — there is no collision.

One caveat: if change C (required `X-Client-Id`) is also in effect, then `POST /tasks/bulk` must also require the header, which is consistent and non-additive. Treat E alone as non-breaking.

#### 2. Semver bump

**MINOR** — adding a new endpoint with a new request/response shape is a backwards-compatible addition. Existing clients continue to function identically; new clients can optionally adopt the endpoint.

#### 3. Semantic risk

`POST /tasks/bulk` returns a `207 Multi-Status` where individual items can fail while the overall HTTP status is `200/207` — a client that checks only the top-level HTTP status code will incorrectly assume all tasks were created successfully, silently losing some records without any error surfacing.

---

## Summary Table

| Change | Description | Breaking? | Semver | Semantic risk |
|--------|-------------|-----------|--------|---------------|
| A | Add optional `priority` to response | Non-breaking (lenient) / **Breaking (strict)** | MINOR | Silent data loss if UI ignores the new field |
| B | Rename `done` → `completed` | **Breaking** | **MAJOR** | Alias period risks split-brain state between old and new writers |
| C | Require `X-Client-Id` header | **Breaking** | **MAJOR** | Header value can be spoofed; becomes implicit trust input |
| D | Shrink `title` max length 500 → 100 | **Breaking** (semantic) | **MAJOR** | Existing stored records with long titles become un-patchable |
| E | Add `POST /tasks/bulk` endpoint | Non-breaking | MINOR | `207` partial failure invisible to clients checking only HTTP status |

---


