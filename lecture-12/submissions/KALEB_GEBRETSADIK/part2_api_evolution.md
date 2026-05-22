# Part 2.2: Public API Evolution

## Chosen Endpoint: `GET /orders/{id}`

**Current v1 Response:**
```json
{
  "orderId": "o1",
  "totalCents": 1299,
  "status": "PLACED"
}
```

---

## Two Additive Changes (Safe for Old Clients)

Based on `example2_flexibility_api_evolution_citybite.py`, adding optional fields is safe because old clients use tolerant JSON parsers and simply ignore unknown keys.

**Additive Change 1 — Add `estimatedDeliveryMinutes`:**
```json
{
  "orderId": "o1",
  "totalCents": 1299,
  "status": "PLACED",
  "estimatedDeliveryMinutes": 35
}
```
Old clients ignore this field entirely; new mobile clients display the ETA.

**Additive Change 2 — Add `restaurantName`:**
```json
{
  "orderId": "o1",
  "totalCents": 1299,
  "status": "PLACED",
  "estimatedDeliveryMinutes": 35,
  "restaurantName": "Sakura Kitchen"
}
```
Old clients remain unaffected; new clients show the restaurant name on the order detail screen.

---

## One Breaking Change & Versioning Strategy

**Breaking Change:** Renaming `orderId` → `id` and `totalCents` → `totalAmount` (with currency object) to align with a new payment API standard.

```json
{
  "id": "o1",
  "totalAmount": { "value": 1299, "currency": "USD" },
  "state": "PLACED"
}
```

Any old client reading `payload.get("orderId")` will get `None` — this is a hard break, as shown in `example2`.

**Versioning approach:** Ship the new shape at **`/v2/orders/{id}`** (URL versioning). Maintain `/v1/orders/{id}` for a **6-month deprecation window**, returning a `Deprecation` response header pointing to the migration guide. After the window, v1 returns HTTP 410 Gone.

---

## Consumer-Driven Contract Idea

The **mobile client team** generates contract tests (using Pact or similar) that describe exactly which fields they read from `GET /orders/{id}`; the backend runs these tests in CI on every deploy to guarantee the contract is never silently broken.
