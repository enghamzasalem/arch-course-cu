# Part 2.1: Change Classification and Compatibility

---

### A) Add optional JSON field `priority` to `GET /tasks` response

1. **Classification:** **Non-breaking (Syntactically)**
   Adding an optional field to a JSON response is generally a backwards-compatible change. Standard HTTP clients and most modern JSON unmarshallers simply ignore unmapped or unknown fields. *(Note: If a stubborn client implements strict validation configured to throw fatal errors on unexpected fields, it will break, but standard API design assumes permissive consumption).*
2. **Semver Bump:** **MINOR** (e.g., `v1.1.0`)
   This constitutes new, backward-compatibly integrated functionality.
3. **Semantic Risk:** Even if the JSON shape parses successfully, if `priority` dictates standard business rules (like tasks with "High" priority absolutely must be shown first), older clients ignoring the field will display tasks in an incorrect semantic order.

---

### B) Rename JSON field `done` → `completed` in responses

1. **Classification:** **Breaking**
   Any existing client looking for the `done` property will now receive `undefined` or `null`. A strongly-typed frontend checking `task.done === true` will fail silently or throw a type exception.
2. **Semver Bump:** **MAJOR** (e.g., `v2.0.0`)
   Modifying or renaming an existing contract field is an incompatible API change.
3. **Semantic Risk:** Even if the legacy application doesn't crash from missing fields, it will incorrectly interpret all historically finished tasks as incomplete simply because the mapped boolean fell back to a default `false`.

---

### C) Require new header `X-Client-Id` on all requests

1. **Classification:** **Breaking**
   Tightening operational requirements by introducing mandatory inputs means that existing legacy payloads, which were perfectly valid yesterday, will immediately be rejected by the server with a `400 Bad Request` or `401 Unauthorized`.
2. **Semver Bump:** **MAJOR** (e.g., `v3.0.0`)
   An incompatible API change due to stricter ingress constraints.
3. **Semantic Risk:** The JSON payload shape itself remains perfectly compatible, yet the operational wrapper (HTTP headers) fundamentally completely breaks integration workflows, masking the break as an infrastructure issue rather than a data issue.

---

### D) Change `title` max length from 500 to 100 characters

1. **Classification:** **Breaking**
   Stricter input validation logic is always a breaking change. Workflows or users that submit perfectly valid 350-character task titles via the legacy API will instantly hit validation error walls (`HTTP 400/422`).
2. **Semver Bump:** **MAJOR** (e.g., `v4.0.0`)
   This alters existing API guarantees in a non-backwards-compatible manner.
3. **Semantic Risk:** Partner bots dynamically generating 200-character titles will construct syntactically flawless JSON matching the exact DTO shape, but will semantically fail business rule execution resulting in silent data ingestion losses.

---

### E) Add `POST /tasks/bulk` with new request shape

1. **Classification:** **Non-breaking**
   Deploying a completely isolated, standalone endpoint does not alter the routing, parameters, or payloads of existing endpoints like `POST /tasks` or `GET /tasks`. Existing clients remain entirely unaffected unless they actively choose to consume it.
2. **Semver Bump:** **MINOR** (e.g., `v4.1.0`)
   New, additive functionality built alongside existing code perfectly aligns with a Minor semantic version bump.
3. **Semantic Risk:** While syntactically isolated, the backend might process bulk arrays asynchronously. If a client simultaneously sends a bulk deletion and a single creation, the network race condition could result in semantic consistency issues across the datastore.
