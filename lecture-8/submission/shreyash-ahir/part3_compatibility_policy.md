# Part 3.1 — Task Board API Compatibility Policy

*Version 1.0 — effective from initial v2 launch*

---

## 1. Rules for Additive vs. Breaking Changes

### What we guarantee never changes without a MAJOR version bump

- Field names in request and response JSON bodies
- HTTP method and path of any existing endpoint
- Required request headers or parameters
- The set of valid input values for any field (e.g. max length, enum values)
- The semantics of any error code (what triggers it)
- The HTTP status code for any documented outcome

### What we may change in a MINOR version (backward-compatible additions)

- Adding new optional response fields (existing clients must tolerate unknown fields)
- Adding new optional request fields or parameters (ignored if not sent)
- Adding new endpoints or methods to existing paths (e.g. `POST /tasks/bulk`)
- Adding new error codes for new conditions not previously reachable
- Relaxing a constraint on an existing field (e.g. increasing max length)

### What constitutes a PATCH (bug fix, no contract change)

- Fixing a documented behaviour that was broken (server returned wrong status code)
- Documentation corrections that match existing behaviour
- Performance or reliability improvements with no observable contract change

### The tolerance reader contract

All clients MUST be implemented as tolerant readers: they MUST ignore JSON fields they
do not recognise. This is the client's contractual obligation. The API provides
additive changes without notice; clients that break on unknown fields do so in violation
of this policy.

---

## 2. Deprecation Process

### Notice period

- **First-party clients** (Web SPA, Mobile App): minimum **6 months** from deprecation
  announcement to sunset date.
- **Partner integrations**: minimum **12 months** from deprecation announcement to
  sunset date.

These periods reflect the practical update cycles: first-party apps are released weekly;
partner integrations often have annual or quarterly release cycles.

### Communication channels

Deprecation is communicated through all three of the following simultaneously:

1. **HTTP response headers** on every request to the deprecated version:
   ```
   Deprecation: true
   Sunset: <RFC 7231 date of planned removal>
   Link: <https://docs.example.com/migration>; rel="deprecation"
   ```

2. **Developer portal** (`docs.example.com`): A migration guide is published on the
   same day as the deprecation announcement. The guide specifies every changed field
   with before/after examples.

3. **Direct notification** to registered partner API keys by email, with the migration
   guide link and the partner's current usage volume of the deprecated version.

### Sunset announcement

The sunset date is announced at the time of the MAJOR version launch — not later.
Partners and first-party teams must know the endpoint of the migration window from day
zero so they can plan accordingly. The sunset date is never moved earlier once
announced; it may be extended if partner adoption of the new version is below 80%.

### After sunset

On the sunset date, the deprecated version returns `410 Gone` with a machine-readable
body pointing to the migration guide:

```json
{
  "error": {
    "code": "API_VERSION_SUNSET",
    "message": "This API version has been retired. See https://docs.example.com/migration",
    "sunsetAt": "2026-03-01T00:00:00Z"
  }
}
```

The `error.code` value `API_VERSION_SUNSET` is itself stable and will never be reused
for a different meaning.

---

## 3. Error Format Stability

### What is stable

- The outer JSON shape `{ "error": { "code": "...", "message": "..." } }` is frozen
  for the lifetime of any major version. Clients may parse this shape safely.
- Error `code` values (e.g. `VALIDATION_ERROR`, `MISSING_CLIENT_ID`) are stable within
  a major version. A code value, once published, is never reassigned to a different
  meaning.

### What may change

- The `message` string is for human consumption only. Clients MUST NOT parse or
  branch on message text. It may be rephrased for clarity at any time without a semver
  bump.
- New error codes may be added in MINOR versions (for new conditions on new
  endpoints). Clients must handle unknown error codes gracefully (e.g. display a
  generic error message).

### When error codes may change

Error code changes require a MAJOR version bump if:

- An existing code is removed (clients that catch it by name would miss it)
- An existing code is reassigned to a different semantic meaning
- The HTTP status code for an existing documented scenario changes (e.g. from 400 to
  422 for the same validation failure)

---

## 4. Partner Integrations vs. First-Party Apps

### Partners receive longer notice

Partners are granted a longer sunset window (12 months vs. 6 months) and direct
personal notification when their registered API key is still sending requests to a
deprecated version. Partners with documented annual release cycles may request a
sunset extension in writing; extensions are evaluated on a case-by-case basis.

### Partners have stricter SLA on error format stability

Because partners may build automated pipelines that parse error codes, the error format
and existing error code values are treated as a **contractual guarantee for partner
integrations**, not merely a policy commitment. Changes to error codes affecting
partners require 6 months' advance notice even within a major version.

### First-party apps

The SPA and Mobile App are updated by the same product team. They may be migrated
on a faster timeline and may receive pre-release access to v2 before partners. However,
the same formal deprecation process applies — the team does not receive silent breaking
changes, even internally.

### What is identical for all clients

The JSON contract, HTTP semantics, and error format are identical between first-party
and partner calls. There are no undocumented or private endpoints for first-party use.
All behaviour is fully documented in the public developer portal.
