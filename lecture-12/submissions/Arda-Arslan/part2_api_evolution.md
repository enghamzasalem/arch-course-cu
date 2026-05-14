# Task 2.2 - Public API evolution

## Endpoint

`GET /orders/{id}` - returned to the mobile app when a customer opens an order detail screen. This is a public surface: many app versions in the wild, we cannot force everyone to upgrade.

### v1 response (today)

```json
{
  "orderId": "o_123",
  "totalCents": 1299,
  "status": "PLACED"
}
```

Old mobile clients read exactly these three keys.

## Two additive changes (safe for old clients)

Additive means we only add new optional fields. Old clients ignore unknown keys (standard JSON parser behaviour), so they keep working.

### Additive 1 - `estimatedDeliveryMinutes`

```json
{
  "orderId": "o_123",
  "totalCents": 1299,
  "status": "PLACED",
  "estimatedDeliveryMinutes": 35
}
```

New field, optional, used by newer app versions to show "arrives in ~35 min". Old clients do not see it and behave exactly as before.

### Additive 2 - `paymentStatus`

```json
{
  "orderId": "o_123",
  "totalCents": 1299,
  "status": "PLACED",
  "estimatedDeliveryMinutes": 35,
  "paymentStatus": "AUTHORIZED"
}
```

New optional field reflecting the payment state for this order (authorized / captured / refunded / failed). Old clients still only read `status` and ignore `paymentStatus`. No deploy coordination with the mobile team needed.

**Rules we follow for additive:**
- never rename an existing key
- never change the type of an existing key
- never make an existing optional field required
- new fields are optional and have a documented default meaning when absent

## One breaking change

Say we decide the v1 names are inconsistent (camelCase vs snake_case mixed across the API) and we want to clean them up:

- `orderId` -> `id`
- `totalCents` -> `total_cents`
- `status` -> `state`

This is a **breaking change** - any old client looking for `orderId` will get `null` and crash or show empty data.

### How we ship it - URL versioning

We do not change `/orders/{id}`. We add a new path:

- `GET /v1/orders/{id}` - old shape, unchanged
- `GET /v2/orders/{id}` - new shape

Both run side by side. The mobile team picks when to move each app version to v2.

### Deprecation window

- **Month 0:** v2 goes live. v1 still default. Announce in the developer docs.
- **Month 0-6:** both versions supported. v1 responses include a `Deprecation` header so monitoring can see who is still on v1.
- **Month 6:** v1 returns a clear error explaining v1 is retired and pointing to v2.

6 months is enough time for app store rollouts and for users who do not auto-update to upgrade.

## Consumer-driven contract

The mobile team (the consumer) writes contract tests describing what they expect from `GET /orders/{id}`, and the Orders service (the provider) runs those tests in its CI so that any change in Orders that would break the mobile app fails the build before deploy.