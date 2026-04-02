# Part 3.1: Compatibility Policy
### Task Board API — Public Governance Document

---

## 1. Rules for Additive vs Breaking Changes

### Additive changes (permitted without a new major version)

The following changes may be shipped to an existing version without incrementing the major version number. They must be backwards-compatible for all clients that follow the robustness principle.

- Adding a new **optional** field to a response body
- Adding a new **optional** request field or query parameter
- Adding a new endpoint or HTTP method
- Adding a new value to an enum that clients are expected to ignore if unrecognised
- Relaxing a validation rule (e.g. increasing a max length, making a required field optional)
- Adding a new non-breaking error code to the existing error format

Any additive change that ships to a live version must be announced in the changelog with a note on strict-client risk where applicable (see Change A precedent — optional response fields can break strict deserialisation).

### Breaking changes (require a new major version)

The following changes must never be applied to a live versioned API path. They require a new major version (`/v2/`, `/v3/`) with a coexistence and sunset plan in place before release.

- Removing or renaming a request or response field
- Changing the type of an existing field (e.g. string → integer)
- Adding a new **required** request field, header, or parameter
- Tightening a validation rule (e.g. reducing max length, making an optional field required)
- Changing the semantics of an existing field without renaming it
- Changing or removing a stable error code (see Section 3)
- Removing an endpoint or HTTP method

### Decision rule

When uncertain, apply the following test: *can an existing client that has not been updated continue to call this API and receive a meaningful, correct response?* If the answer is no for any production client, the change is breaking.

---

## 2. Deprecation Process

### Notice period

| Client type | Minimum notice period |
|-------------|----------------------|
| Partner integrations | 12 months from deprecation announcement |
| Mobile app (public) | 12 months (accounts for app store release cycles and user update lag) |
| First-party web SPA | 3 months (team controls deployment; coordinated release possible) |

The notice period begins on the day the new major version is released and the `Deprecation` and `Sunset` headers are added to the old version's responses — not on the day the decision to deprecate is made internally.

### Communication channels

1. **Response headers** — every response from a deprecated version carries:
   ```
   Deprecation: true
   Sunset: Sat, 01 Jan 2027 00:00:00 GMT
   Link: <https://api.example.com/v2/tasks>; rel="successor-version"
   ```
   These headers are present from the first day of the deprecation window and must not be removed before sunset.

2. **Developer changelog** — a dated entry is published at the API documentation site on the day of the v2 release, listing every breaking change, the sunset date, and a migration guide link.

3. **Partner direct notification** — all registered partner integrations receive an email to their technical contact on the day of the deprecation announcement and again at the 6-month and 1-month marks before sunset.

4. **In-product dashboard notice** — first-party teams are notified via the internal engineering channel on the day of release.

### Sunset announcement

On the sunset date the deprecated version returns `410 Gone` for all requests, with a response body pointing to the successor version:

```json
{
  "error": {
    "code": "VERSION_SUNSET",
    "message": "API v1 was retired on 2027-01-01. Migrate to /v2/tasks. See https://api.example.com/docs/migration."
  }
}
```

The `410` response is maintained for a minimum of 6 months after sunset to give clients a clear signal rather than a connection failure.

---

## 3. Error Format Stability

### Stable contract

The error envelope shape is part of the public API contract and is subject to the same versioning rules as the data contract. The following structure is frozen for the lifetime of a major version:

```json
{
  "error": {
    "code": "STRING_CONSTANT",
    "message": "Human-readable description"
  }
}
```

- The `error.code` field is a **stable string constant**. Client code may branch on it programmatically. It must not be renamed, removed, or have its meaning changed within a major version.
- The `error.message` field is **informational only**. Its wording may change between patch releases for clarity. Clients must not parse or branch on `message` content.

### When error codes may change

Error codes may only change under the following conditions:

| Situation | Action required |
|-----------|----------------|
| New error condition introduced | Add a new code — additive, no version bump required |
| Existing code renamed or removed | Treat as breaking change — requires new major version |
| Error code meaning changes (same code, different semantics) | Treat as breaking change — requires new major version |
| HTTP status code for an existing error changes | Treat as breaking change — requires new major version |

### Example — stable codes across v1 and v2

| Code | HTTP status | Stable in v1 | Stable in v2 |
|------|-------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Yes | Yes |
| `MISSING_CLIENT_ID` | 400 | Not present | Yes (introduced in v2 with change C) |
| `VERSION_SUNSET` | 410 | Yes (at sunset) | N/A |

---

## 4. Partner Integrations vs First-Party Apps

Partners and first-party apps are treated differently in two areas: notice period and migration support obligations.

### Notice period

As stated in Section 2, partners receive a minimum 12-month notice period. First-party apps (Web SPA, internal tooling) receive a minimum 3-month notice period. This reflects the reality that the team controls first-party deployments and can coordinate a release, whereas partners operate on their own release cycles and may have contractual or procurement processes that prevent rapid updates.

### Migration support obligations

| Obligation | Partners | First-party apps |
|------------|----------|-----------------|
| Migration guide published | Required — before or on v2 release day | Required |
| Direct notification at 6 months before sunset | Required | Not required (internal comms sufficient) |
| Alias period (serve both old and new field names) | Recommended during the v1 sunset window to ease migration | Not required |
| Request for extension beyond sunset date | May be granted for up to 3 months in exceptional cases, by written agreement | Not granted — internal teams must migrate on schedule |

### Alias period for partners (change B precedent)

For the `done` → `completed` rename (change B), the v1 contract continues to return `done` throughout the sunset window. Additionally, during the first 6 months of the window, the v2 contract may optionally return **both** `done` and `completed` in the same response to allow partners to update their read logic before their write logic. This dual-field alias must be explicitly documented and has a defined end date — it is not a permanent fixture of v2.

### What partners may not do

Partners may not treat the alias period as a permanent solution. The sunset date is a hard commitment. Extensions beyond 3 months will not be granted, as maintaining v1 handler code and the associated database schema columns (e.g. the legacy `done` field) carries an ongoing cost that grows with time.

---

