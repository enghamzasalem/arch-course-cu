## Task 2.2

**Endpoint:** `GET /orders/{id}`

**Current response:**
```json
{ "orderId": "o1", "totalCents": 1299, "status": "PLACED" }
```

### Two Additive Changes

As shown in `example2`, old clients using tolerant JSON parsers simply ignore unknown fields, so new optional fields are safe to ship without a version bump.

1. Add `"estimatedDeliveryMinutes": 35` - new clients can display the ETA.
2. Add `"restaurantName": "Pizza Palace"` - removes a second API call for clients that want to display the restaurant name inline.

### One Breaking Change

Renaming `orderId` to `id` and `totalCents` to `total_cents` breaks old clients that read those keys by name, as `simulate_old_client` in `example2` demonstrates - it returns `None` for every field.

**Versioning approach:** Ship the new shape under `/v2/orders/{id}`. Both endpoints run in parallel. After announcing the deprecation, old clients have a **90-day window** to migrate. The v1 endpoint returns a `Deprecation` response header pointing to the migration guide. After 90 days, v1 stops working and returns a 400 response code.

### Consumer-Driven Contract

The mobile client team owns and generates the contract tests, running them against the Order API on every pull request so a breaking change is caught before it is merged.