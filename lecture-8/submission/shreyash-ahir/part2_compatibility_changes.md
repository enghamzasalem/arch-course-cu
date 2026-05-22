# Part 2.1 — Change Classification

## Assumption for All Changes

Clients are assumed to be **tolerant readers** unless stated otherwise: they ignore
unknown JSON fields.  This is the standard posture for well-written HTTP clients.
Partner integrations are treated as potentially strict and are called out explicitly.

---

## Change A — Add optional `priority` field to GET /tasks response

**Breaking or non-breaking?**

Non-breaking for tolerant-reader clients. A client that ignores unknown fields
continues to work correctly — it simply never sees `priority`. A client with strict
JSON parsing (e.g. deserialising into a class that rejects unknown fields) will break.

*Assumption: We treat strict parsers as a client configuration issue, not a server
contract issue. The API contract does not promise to send only known fields.*

**Semver bump:** `MINOR` (new capability added in a backward-compatible way: `1.1.0`)

**Semantic risk:** Even though the JSON shape is compatible, clients that display
all task fields to users will now unexpectedly surface `priority` in their UI without
any product decision on their side. A non-breaking structural change can be a
breaking product change.

---

## Change B — Rename field `done` → `completed` in all task representations

**Breaking or non-breaking?**

**Breaking** for all clients. Every client that reads `task.done` from the response
receives `undefined` or null after this change. Every client that writes `{ "done": true }`
in a PATCH body sends an unrecognised field — the server either ignores it or rejects it,
neither of which gives the client the result it expects.

This is a **syntactic breaking change**: the field name is part of the interface contract,
and renaming it removes a feature that clients depend on.

**Semver bump:** `MAJOR` (`2.0.0`) — existing clients break without code changes.

**Semantic risk:** Even if you run a 6-month alias period where the API accepts both
`done` and `completed`, clients that rely on reading the field by name are silently broken
the moment the alias expires. The alias period reduces migration urgency but does not
eliminate the breaking nature of the eventual removal.

---

## Change C — Require new header `X-Client-Id` on all requests

**Breaking or non-breaking?**

**Breaking** for all existing clients. No current client sends `X-Client-Id`. After this
change, every request without the header receives a 400/401 error. This is a
**protocol-level breaking change**: the request format (headers) is part of the
interface contract, and adding a required field to the request breaks all callers.

This is especially severe for partner integrations and installed mobile app versions
that cannot be updated quickly.

**Semver bump:** `MAJOR` (`2.0.0`)

**Semantic risk:** Even if you provide a grace period where the header is optional and
logged but not enforced, the eventual enforcement date is a hard breaking change for
any client that misses the migration window. Partner integrations with annual release
cycles will be broken if the enforcement date is less than 12 months from announcement.

---

## Change D — Reduce `title` max length from 500 to 100 characters

**Breaking or non-breaking?**

**Breaking** — semantically, even though the JSON field name is unchanged.

A client sending a title of 150 characters received `201 Created` before this change
and receives `400 Bad Request` after it. The interface contract (the set of valid inputs
the server accepts) has shrunk. This is a **semantic breaking change**: the wire format
is identical but the set of accepted values has changed.

Data already stored in partner systems with titles of 101–500 characters cannot be
re-submitted after this change without modification.

**Semver bump:** `MAJOR` (`2.0.0`)

**Semantic risk:** This is the hardest kind of breaking change to detect with contract
tests — the JSON schema for `title` (type: string) remains valid; only the allowed range
changes. Partners who test with short titles will not catch this in their test suite.

---

## Change E — Add new endpoint `POST /tasks/bulk`

**Breaking or non-breaking?**

Non-breaking. Existing endpoints (`POST /tasks`, `GET /tasks`, `PATCH /tasks/{id}`)
are unchanged. Adding a new endpoint adds capability without modifying existing
contracts. No existing client calls `POST /tasks/bulk` — they simply do not have access
to a feature that now exists.

**Semver bump:** `MINOR` (`1.1.0`) — new capability, backward-compatible.

**Semantic risk:** If `POST /tasks/bulk` uses `done` (the v1 field name) in its response
while the team is planning to rename it to `completed` in a future release, partners who
adopt the bulk endpoint immediately couple themselves to a field name that is about to
be renamed. Introducing new endpoints during a planned migration increases the number
of places where `done` must be aliased or eventually removed.

---

## Summary Table

| Change | Breaking? | Semver | Reason |
|---|---|---|---|
| A — add optional `priority` | Non-breaking (tolerant readers) | `MINOR` | Additive to response; clients ignore unknown fields |
| B — rename `done` → `completed` | **Breaking** | `MAJOR` | Removes a response field clients depend on |
| C — require `X-Client-Id` header | **Breaking** | `MAJOR` | Adds required request field; existing clients send nothing |
| D — reduce title max length | **Breaking** (semantic) | `MAJOR` | Shrinks accepted input set; existing valid data becomes invalid |
| E — add `POST /tasks/bulk` | Non-breaking | `MINOR` | New endpoint only; existing endpoints unchanged |
