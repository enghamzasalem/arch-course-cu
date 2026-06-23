## Task 2.1: Change Classification

---

### A - Add optional `priority` field to `GET /tasks` response

- **Breaking or non-breaking:** Non-breaking for clients that ignore unknown fields. Breaking for strict clients that reject unexpected fields or validate responses against a fixed schema.
- **Semver bump:** MINOR - new functionality is added in a backward-compatible way.
- **Semantic risk:** Clients that silently ignore `priority` may display or process tasks without it, leading to incorrect sorting or filtering behaviour even though the response parses without error.

---

### B - Rename `done` → `completed` in all task responses

- **Breaking or non-breaking:** Breaking - any client reading `done` to check task status will receive `undefined` or `null` after the change, without any error being raised.
- **Semver bump:** MAJOR - an existing field is removed from the public contract.
- **Semantic risk:** A client that falls back to a falsy `done` value may treat all tasks as incomplete, corrupting task lists silently rather than failing visibly.

---

### C - Require `X-Client-Id` header on all requests

- **Breaking or non-breaking:** Breaking - all existing clients that do not send this header will immediately start receiving errors, with no grace period.
- **Semver bump:** MAJOR - a new obligation is placed on callers that did not exist before.
- **Semantic risk:** Even clients that add the header may send an incorrect or placeholder value, which could pass validation but produce misleading analytics or audit logs on the server side.

---

### D - Reduce `title` max length from 500 to 100 characters

- **Breaking or non-breaking:** Breaking - requests with titles between 101 and 500 characters were valid before and will now be rejected, even though the field name and type are unchanged.
- **Semver bump:** MAJOR - existing valid inputs are no longer accepted.
- **Semantic risk:** Clients may not discover the breakage until a user submits a longer title at runtime, since the JSON field looks identical and no schema change is visible to static analysis tools.

---

### E - Add `POST /tasks/bulk` endpoint

- **Breaking or non-breaking:** Non-breaking - no existing endpoint or response is changed; this is purely additive.
- **Semver bump:** MINOR - a new capability is introduced without affecting existing behaviour.
- **Semantic risk:** Clients that independently implement bulk creation by looping `POST /tasks` may produce inconsistent results compared to the new endpoint if the bulk endpoint applies different validation or partial-failure handling (e.g. a 207 multi-status response).