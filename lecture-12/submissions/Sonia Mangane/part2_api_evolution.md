# Task 2.2: Public API evolution

## Chosen Endpoint: `GET /orders/{id}`

This is the most widely consumed endpoint in CityBite — called by the customer mobile app, the restaurant portal, and the courier app to display order details. Any breaking change here directly impacts all three clients.

### Current v1 Response Shape

```json
{
  "orderId": "ord_abc123",
  "totalCents": 1850,
  "status": "CONFIRMED"
}
```

Old mobile clients depend on exactly these three keys.

---

## Two Additive Changes Safe for Old Clients

Both changes follow the `order_v1_additive` pattern from `example2`: new optional fields are appended to the existing response. Old clients using tolerant JSON parsers (standard in iOS/Android) simply ignore unknown keys — their existing reads of `orderId`, `totalCents`, and `status` continue to work without any code change.

### Additive Change 1: Add `estimatedDeliveryMinutes`

```json
{
  "orderId": "ord_abc123",
  "totalCents": 1850,
  "status": "CONFIRMED",
  "estimatedDeliveryMinutes": 28
}
```

**Why it is safe:** The field is optional and new. Old clients that do not know about `estimatedDeliveryMinutes` ignore it. New clients (app version 2.x+) can display the ETA. No coordination with old client versions is required before deploying this change.

### Additive Change 2: Add `restaurantName` and `items[]`

```json
{
  "orderId": "ord_abc123",
  "totalCents": 1850,
  "status": "CONFIRMED",
  "estimatedDeliveryMinutes": 28,
  "restaurantName": "Bella Napoli",
  "items": [
    { "name": "Margherita Pizza", "quantity": 1, "unitCents": 1250 },
    { "name": "Sparkling Water", "quantity": 2, "unitCents": 300 }
  ]
}
```

**Why it is safe:** Again, purely additive. Old clients continue reading the three original keys. New clients can render a richer order detail screen without a separate `GET /orders/{id}/items` call, reducing round trips.

---

## One Breaking Change — Versioning and Deprecation

### Breaking Change: Rename `orderId` → `id` and `totalCents` → `totalAmount` (object)

The mobile team wants to align with a new internal naming convention and express the total as a structured money object rather than a raw integer:

```json
{
  "id": "ord_abc123",
  "total": { "amount": 18, "currency": "USD" },
  "state": "confirmed"
}
```

As demonstrated by `order_v2_breaking_rename` in `example2`, old clients calling `payload.get("orderId")` will receive `None` — the field is gone. This is a **breaking change** that cannot be deployed without a versioning strategy.

**Versioning approach — URL versioning:**

- The new shape is served at `/v2/orders/{id}`.
- The original shape continues to be served at `/v1/orders/{id}` (or the unversioned `/orders/{id}` which is treated as v1).
- Both versions run simultaneously during the deprecation window.

**Deprecation window:**

| Milestone | Action |
|-----------|--------|
| Day 0 | `/v2/orders/{id}` goes live; `/v1` response gains `Deprecation: true` header and `Sunset: <date>` header (RFC 8594) |
| Day 0–60 | New client versions adopt `/v2`; analytics track what % of traffic is still on `/v1` |
| Day 60 | `/v1` returns HTTP 410 Gone if traffic has dropped below 1%; otherwise window is extended |
| Day 90 (hard sunset) | `/v1` is removed; any remaining old clients must upgrade |

A 60–90 day window gives the mobile team time to ship an app update through the App Store / Play Store review process, which can take 1–2 weeks on its own.

---

## Consumer-Driven Contract Tests

The Ordering team uses **Pact** to generate contract tests: each consumer (mobile app, restaurant portal, courier app) publishes a "pact" file describing the exact fields it reads from `GET /orders/{id}`, and the Ordering service's CI pipeline verifies that every proposed API change satisfies all published pacts before merging, catching breaking changes automatically, before they reach production.
