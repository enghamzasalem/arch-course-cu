# Part 3.1 - Compatibility Policy (Task Board API)

## Scope

This policy governs the public Task Board API consumed by:
- first-party clients (Web SPA, Mobile App),
- third-party partner integrations.

It defines rules to ensure backward compatibility and controlled API evolution.

---

## 1) Rules for additive vs breaking changes

### Additive changes (normally allowed in MINOR releases)

Examples:
- adding optional response fields (`priority`),
- adding optional request fields,
- adding new endpoints (`POST /tasks/bulk`),
- adding new error codes without removing old stable codes.

Rules:
1. New fields must be optional by default.
2. Existing required fields and endpoint behavior must remain unchanged.
3. Additive changes must be documented before production rollout.
4. SDKs and examples should be updated in the same release window.

### Breaking changes (MAJOR releases only)

Examples:
- renaming/removing fields (`done` -> `completed`),
- requiring new headers (`X-Client-Id`) where previously absent,
- stricter validation that rejects previously valid inputs (`title <= 100` instead of 500),
- changing endpoint semantics or status code behavior for existing flows.

Rules:
1. Breaking changes require new API version (`/v2`).
2. No silent in-place breaking change on `/v1`.
3. Breaking changes must include migration docs and compatibility timeline.

---

## 2) Deprecation process
During the deprecation period, both old and new API versions are supported in parallel.

### Notice period

- Minimum deprecation notice: **90 days** for public endpoints/fields.
- Critical security exceptions may have shorter windows with explicit incident notice.

### Communication channels

1. Changelog/release notes.
2. Developer portal / API docs.
3. Partner email notices (for registered integrations).
4. Runtime warning headers in deprecated version responses.

### Sunset announcement

Deprecated version responses include:
- `Deprecation: true`
- `Sunset: <RFC date>`
- `Link: <migration guide>; rel="deprecation"`

At sunset date:
- endpoints return a structured error (`API_VERSION_SUNSET`) or are disabled according to announced plan.

---

## 3) Error format stability

We keep a stable error envelope:

```json
{
  "error": {
    "code": "SOME_STABLE_CODE",
    "message": "Human-readable message"
  }
}
```

Policy:
1. `error.code` is stable within a major version.
2. `message` text may improve for clarity but should not be machine-parsed.
3. New codes may be added in minor releases.
4. Existing codes are not removed/repurposed in the same major version.
5. If code taxonomy changes significantly, it must happen in next major version with migration map.

---

## 4) Partner integrations vs first-party apps

### First-party apps (web/mobile)
- Can migrate earlier and receive pre-release builds.
- May adopt feature flags to validate v2 before public launch.

### Partner clients
- Receive longer communication lead time and explicit migration checklist.
- Contract tests/sandbox recommended before production cutover.
- No partner is forced onto breaking changes without the declared deprecation window (except severe security emergencies).

This difference is operational, not contractual fairness: all clients still get versioned APIs and documented timelines.

---

## Governance checklist (release gate)

Before any API release:
1. Classify change as additive/breaking.
2. Confirm semver impact and version path.
3. Update docs/examples and SDK notes.
4. Validate error codes and backward compatibility tests.
5. If deprecation: set notice date, sunset date, and communications plan.

This policy keeps change predictable, minimizes unexpected integration failures, and enables safe, incremental API evolution.
