# Part 2 — Task 2.2: Public API Evolution

---

## Endpoint Under Design

```
GET /orders/{id}
```

This is the highest-traffic read endpoint in CityBite's public surface. The mobile app polls it to display live order status. Third-party integrators (restaurant tablet apps, delivery-tracking widgets) also consume it. Any breaking change on this endpoint breaks every client that has not yet updated — the baseline explicitly names "mobile clients break on silent API changes" as a current pain point.

### Baseline v1 Response (current shape)

```json
{
  "orderId":    "ord_9f3a",
  "totalCents": 1850,
  "status":     "DISPATCHED"
}
```

This corresponds exactly to the `order_v1` shape in `example2_flexibility_api_evolution_citybite.py`. Old mobile clients read `orderId`, `totalCents`, and `status` — nothing else.

---

## Additive Change 1 — Add `estimatedDeliveryMinutes`

### Change

```json
{
  "orderId":                  "ord_9f3a",
  "totalCents":               1850,
  "status":                   "DISPATCHED",
  "estimatedDeliveryMinutes": 18
}
```

### Why it is safe for old clients

Old clients use a **tolerant reader** — they call `payload.get("orderId")`, `payload.get("totalCents")`, `payload.get("status")` and ignore every other key. The `simulate_old_client` function in `example2` demonstrates this directly: feeding it the additive payload returns `display order=ord_9f3a total=1850 status=DISPATCHED` — identical to the v1 result. The new field is invisible to old clients.

### New clients

New mobile builds read `estimatedDeliveryMinutes` when present and display the ETA banner. The field is **optional in the contract**: clients must not crash if it is absent (e.g. before dispatch assignment, the field is omitted or `null`). This mirrors the `order_v1_additive` pattern in `example2`.

### Contract rule applied

> Add optional fields freely. Never remove or rename existing fields. Clients that do not understand a field ignore it.

---

## Additive Change 2 — Add `courier` Object

### Change

```json
{
  "orderId":    "ord_9f3a",
  "totalCents": 1850,
  "status":     "DISPATCHED",
  "estimatedDeliveryMinutes": 18,
  "courier": {
    "displayName": "Amara T.",
    "avatarUrl":   "https://cdn.citybite.io/avatars/at29.jpg",
    "currentLat":  53.5511,
    "currentLng":  9.9937
  }
}
```

### Why it is safe for old clients

The entire `courier` object is a new top-level key. Old clients do not read it and their JSON parser discards it silently — the tolerant-reader guarantee still holds. Nesting the courier fields inside a sub-object (rather than flattening `courierName`, `courierLat`, etc. at the top level) has a secondary benefit: if courier tracking is later moved into a separate endpoint or made a separate resource, the nesting boundary makes the refactor clean. No existing field is touched.

### New clients

New app builds render a live courier map tile using `currentLat` and `currentLng`. The `courier` key is absent before dispatch assignment (status `PLACED` or `ACCEPTED`) — clients must handle the missing key gracefully rather than assuming it is always present.

### Contract rule applied

> Prefer grouped sub-objects for related new fields. Old clients ignore the entire object. New clients handle absence of the key at statuses where it does not yet exist.

---

## Breaking Change — Rename `totalCents` to `totalMinorUnits` and `orderId` to `id`

### Motivation

The engineering team wants to:
1. Support multi-currency orders where the smallest unit is not always a cent (e.g. Japanese Yen has no minor subdivision).
2. Align with internal domain language (`order_id` in the DB is already `id` in the new DDD model).

This is the `order_v2_breaking_rename` case from `example2`. The old client reads `payload.get("totalCents")` and `payload.get("orderId")` — both return `None` after the rename, breaking every client silently with no error raised.

### v2 Shape

```json
{
  "id":               "ord_9f3a",
  "totalMinorUnits":  1850,
  "currencyCode":     "EUR",
  "status":           "DISPATCHED",
  "estimatedDeliveryMinutes": 18,
  "courier": {
    "displayName": "Amara T.",
    "avatarUrl":   "https://cdn.citybite.io/avatars/at29.jpg",
    "currentLat":  53.5511,
    "currentLng":  9.9937
  }
}
```

### Versioning Strategy — URL Path Prefix

CityBite uses **URL path versioning** (`/v1/` and `/v2/`):

```
GET /v1/orders/{id}   →  returns old shape (orderId, totalCents)
GET /v2/orders/{id}   →  returns new shape (id, totalMinorUnits, currencyCode)
```

**Why URL versioning over header or content negotiation:**

- URL versioning is visible, cacheable by CDN and reverse proxy without custom `Vary` headers, and unambiguous in logs and dashboards. A support engineer reading an access log can immediately see which version a client called.
- Header versioning (`Accept: application/vnd.citybite.v2+json`) is less discoverable and breaks HTTP caching unless `Vary: Accept` is configured on every edge node — an ops burden at CityBite's scale.
- Content negotiation has the same caching problem and requires client SDK changes that are no simpler than a URL change.

The `/v1/` prefix is also applied retroactively to all existing endpoints at the same deployment that ships `/v2/`. Old clients calling the un-prefixed path `/orders/{id}` are redirected `301 → /v1/orders/{id}` during the migration window to avoid a hard cutover.

### Deprecation Window

| Phase | Duration | Action |
|---|---|---|
| **Announce** | Sprint 0 (release day) | `/v1/` response gains `Deprecation: true` header and `Sunset: <date>` header (RFC 8594). Release notes published. Mobile team notified. |
| **Parallel run** | 90 days | Both `/v1/` and `/v2/` are fully supported. Monitoring dashboards track `/v1/` call volume per client by reading `User-Agent` and API key. |
| **Reminder** | Day 60 | Automated email to all registered API key holders still calling `/v1/`. In-app banner for mobile builds below minimum supported version. |
| **Sunset** | Day 90 | `/v1/` returns `410 Gone` with a body pointing to the migration guide. Clients that have not migrated break with an explicit, debuggable error rather than silent data corruption. |

**90 days** is chosen because the mobile app release cycle (App Store / Play Store review + user adoption) typically takes 2–4 weeks per release, and CityBite must allow time for the slowest users to update their app before the old app build calls a gone endpoint.

### During the window — dual-write bridge

While both versions are live, the Ordering service maintains a **response mapping layer** that takes the canonical internal model and projects it into either shape:

```
canonical model  →  v1_serialiser  →  { orderId, totalCents, status }
canonical model  →  v2_serialiser  →  { id, totalMinorUnits, currencyCode, status, … }
```

The canonical model is never `orderId`/`totalCents` internally — those are v1-only presentation artefacts. This prevents the deprecated naming from bleeding back into domain logic, which is the exact lesson of `OrderServiceTight` in `example1`: coupling to a vendor (or version) shape inside core logic makes it impossible to evolve.

---

## Consumer-Driven Contract Tests

The **mobile client team** (and each third-party integrator) generates the contract tests: they define, in code (e.g. using Pact), exactly which fields they read from `GET /orders/{id}`, and the Ordering service's CI pipeline runs these consumer contracts against every candidate build — failing the build before production if a proposed change would remove `orderId` or `totalCents` while `/v1/` consumers are still registered.

---

## Summary

| Change | Type | Safe for old clients? | Mechanism |
|---|---|---|---|
| Add `estimatedDeliveryMinutes` | Additive | Yes — tolerant reader ignores new fields | Optional field, omitted before dispatch |
| Add `courier` sub-object | Additive | Yes — entire key ignored by old clients | Absent at pre-dispatch statuses |
| Rename `orderId`→`id`, `totalCents`→`totalMinorUnits` | Breaking | No — old clients read None for both keys | URL `/v2/` + 90-day deprecation window + `Sunset` header |

---

*Vocabulary and patterns aligned with `example2_flexibility_api_evolution_citybite.py` (`order_v1`, `order_v1_additive`, `order_v2_breaking_rename`, `simulate_old_client`), Lecture 12 (additive JSON evolution, versioning strategy, tolerant reader), and Lecture 11 (availability — circuit breaker implied at API gateway layer).*
