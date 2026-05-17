# Part 2.1 - Change Classification (A-E)

Assumption used for strict analysis: some clients are strict and may break on unknown fields or required header additions unless versioning/tolerance is explicitly introduced.

## Summary table

| Change | Breaking? | Semver bump | Reason (short) |
|---|---|---|---|
| A: Add optional `priority` | Non-breaking under tolerant clients; breaking for strict schema clients | MINOR | Additive field; tolerant clients ignore unknown keys |
| B: Rename `done` -> `completed` | Breaking | MAJOR | Removes/renames existing contract key |
| C: Require `X-Client-Id` header | Breaking | MAJOR | Previously valid requests become rejected |
| D: `title` max length 500 -> 100 | Breaking (semantic) | MAJOR | Old valid inputs become invalid |
| E: Add `POST /tasks/bulk` | Non-breaking | MINOR | New endpoint, existing endpoints unchanged |

---

## Detailed classification

### A) Add optional JSON field `priority` to `GET /tasks`
- **Breaking or non-breaking:** Non-breaking for tolerant clients; potentially breaking for strict schema clients that reject unknown fields.
- **Semver bump:** **MINOR** under strict semver for public API features.
- **Semantic risk sentence:** Even additive fields can trigger hidden breakage when clients use strict JSON schema validation or generated DTOs that disallow unknown properties.

### B) Rename JSON field `done` -> `completed`
- **Breaking or non-breaking:** **Breaking**.
- **Semver bump:** **MAJOR**.
- **Semantic risk sentence:** The payload still "means task completion", but consumer code keyed on `done` fails at runtime or silently misbehaves.

### C) Require header `X-Client-Id` on all requests
- **Breaking or non-breaking:** **Breaking**.
- **Semver bump:** **MAJOR**.
- **Semantic risk sentence:** The resource model is unchanged, but protocol-level requirements invalidate previously valid requests.

### D) Change `title` max length from 500 to 100
- **Breaking or non-breaking:** **Breaking** (primarily semantic compatibility break).
- **Semver bump:** **MAJOR**.
- **Semantic risk sentence:** JSON shape is unchanged, yet business validation rejects data that v1 accepted, which is a behavioral break for clients.

### E) Add `POST /tasks/bulk` endpoint
- **Breaking or non-breaking:** **Non-breaking**.
- **Semver bump:** **MINOR**.
- **Semantic risk sentence:** New endpoint can still create operational risk if rate limits, idempotency, or partial-failure semantics are unclear for clients.

---

## Notes on strict compatibility practice

1. Additive changes should still be rolled out with:
   - tolerant-read guidance,
   - schema examples,
   - SDK updates.
2. Contract renames and stricter required inputs should be treated as major changes and isolated in v2.
3. Semantic compatibility is as important as syntax; unchanged JSON keys do not guarantee backward compatibility.
