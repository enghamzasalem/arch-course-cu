# Part 2 — Public API Evolution (CityBite)

## 1. Overview

CityBite’s mobile applications and restaurant tablets depend heavily on stable APIs. If backend teams introduce breaking changes without coordination, older clients may fail in production even when the server itself is healthy.

To avoid this, CityBite follows API evolution rules that prioritize backward compatibility whenever possible.

---

# 2. Example Endpoint

## Endpoint

```http
GET /orders/{id}
```

---

## Original Response (v1)

```json
{
  "orderId": "ORD-1001",
  "totalCents": 2499,
  "status": "PLACED"
}
```

Older mobile clients rely on these exact fields.

---

# 3. Safe Additive Changes

Additive changes are preferred because older clients usually ignore unknown JSON fields.

---

## Additive Change #1 — Estimated Delivery Time

```json
{
  "orderId": "ORD-1001",
  "totalCents": 2499,
  "status": "PLACED",
  "estimatedDeliveryMinutes": 35
}
```

### Why This Is Safe

Older clients continue reading:
- `orderId`
- `totalCents`
- `status`

and simply ignore the new field.

This allows newer apps to display richer delivery information without breaking existing versions.

---

## Additive Change #2 — Courier Tracking Status

```json
{
  "orderId": "ORD-1001",
  "totalCents": 2499,
  "status": "PLACED",
  "courierStatus": "ARRIVING_AT_RESTAURANT"
}
```

### Why This Is Safe

The new field enhances real-time delivery tracking while remaining optional for older clients.

This supports gradual feature rollout across different app versions.

---

# 4. Breaking Change Example

## Problematic Change

```json
{
  "id": "ORD-1001",
  "amount": 2499,
  "state": "PLACED"
}
```

---

## Why This Breaks Clients

Older clients expect:
- `orderId`
- `totalCents`
- `status`

Renaming fields causes older applications to fail because they cannot find the expected keys.

This is considered a breaking API change.

---

# 5. Versioning Strategy

For breaking changes, CityBite introduces a new API version instead of silently changing the existing response.

---

## Example

### Existing Endpoint

```http
GET /v1/orders/{id}
```

### New Endpoint

```http
GET /v2/orders/{id}
```

---

## Deprecation Policy

CityBite maintains older API versions during a transition window.

Example policy:
- Support `/v1` for 6–12 months
- Notify mobile teams before removal
- Track usage metrics before shutdown

This gives customers time to upgrade their applications safely.

---

# 6. Consumer-Driven Contracts

CityBite uses consumer-driven contract testing so client teams can verify that backend API changes remain compatible with their expectations.

In practice:
- Mobile or frontend teams define expected request/response contracts
- Backend CI pipelines run these tests before deployment

This reduces accidental breaking changes and improves confidence during releases.

