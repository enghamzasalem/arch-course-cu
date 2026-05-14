# Part 2.2: Public API Evolution — Mobile-Safe Rules

**Chosen endpoint:** `GET /orders/{id}`  
**Baseline JSON (v1):**

```json
{
  "orderId": "o_123",
  "totalCents": 1299,
  "status": "PLACED"
}
```

This matches the **additive vs breaking** themes in `example2_flexibility_api_evolution_citybite.py` (tolerant clients ignore unknown keys; renames break old parsers).

---

## 1. Two additive changes (safe for old clients)

**Assumption:** Mobile clients use tolerant JSON parsing and only read documented keys (`orderId`, `totalCents`, `status`).

### Additive change 1 — optional ETA field

Same spirit as `estimatedDeliveryMinutes` in example2:

```json
{
  "orderId": "o_123",
  "totalCents": 1299,
  "status": "PLACED",
  "estimatedDeliveryMinutes": 42
}
```

Old app: unchanged display. New app: can show ETA when present.

### Additive change 2 — optional nested `restaurant` summary

```json
{
  "orderId": "o_123",
  "totalCents": 1299,
  "status": "PLACED",
  "restaurant": {
    "id": "r_9",
    "displayName": "CityBite Kitchen"
  }
}
```

Old app: ignores `restaurant`. New app: avoids extra round-trip.

---

## 2. One breaking change — versioning and deprecation

### Breaking change — rename fields (example2 `order_v2_breaking_rename`)

```json
{
  "id": "o_123",
  "total_cents": 1299,
  "state": "PLACED"
}
```

Old mobile clients looking for `orderId` / `totalCents` / `status` **break**.

**Versioning approach:** **URL prefix** — ship `GET /v2/orders/{id}` with the new shape; keep `GET /v1/orders/{id}` (or unversioned alias to v1) during sunset.

**Deprecation window:**

- Announce sunset date in docs + `Deprecation` / `Sunset` HTTP headers on v1 responses.
- Minimum **90 days** for first-party apps; **180 days** for partners (align with course policy patterns).

---

## 3. Consumer-driven contract tests (one sentence)

**Consumer-driven contracts:** Mobile team publishes **expected fixtures** for `GET /orders/{id}` (Pact or similar), and the Task API CI **verifies** the provider cannot merge a change that breaks those contracts without an explicit major version bump.
