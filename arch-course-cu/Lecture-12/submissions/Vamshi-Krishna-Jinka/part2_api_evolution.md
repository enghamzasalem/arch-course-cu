# Part 2: Data, APIs, Sagas
## Task 2.2: Public API Evolution

## 1. Endpoint Chosen
### `GET /orders/{id}`

This endpoint returns the current order summary to mobile customers and restaurant users. It is a public surface, so changes must be made carefully to avoid breaking older app versions that are still in the field.

Example response shape:
```json
{
  "orderId": "o1",
  "totalCents": 1299,
  "status": "PLACED"
}
```

---

## 2. Additive Changes Safe for Old Clients

Following the lecture theme of additive JSON evolution, old clients should ignore unknown fields and continue working normally. fileciteturn5file0

### Additive change 1: Add an optional ETA field
Add:
```json
{
  "estimatedDeliveryMinutes": 42
}
```
Old clients that only read `orderId`, `totalCents`, and `status` still work. New clients can display a delivery estimate.

### Additive change 2: Add a nested metadata object
Add:
```json
{
  "metadata": {
    "restaurantName": "Pizza Corner",
    "canCancel": true
  }
}
```
This is safe because it adds information without changing existing field names or meanings. Older apps ignore it, while newer apps can use it for richer UI.

---

## 3. Breaking Change and Versioning Rule

### Breaking change
Rename or remove existing keys, for example:
- `orderId` → `id`
- `totalCents` → `total_cents`
- `status` → `state`

This is breaking because old mobile clients expect the original keys and will fail to display the order correctly. The lecture example shows this exact risk: additive fields are safe, but renaming keys breaks old client code. fileciteturn5file0

### Versioning strategy
CityBite should expose the breaking change as:
- `GET /v2/orders/{id}`

Alternatively, a version header could be used, but URL versioning is easier to understand and debug for a public mobile API.

### Deprecation window
- Keep `v1` available for at least **90 days**
- Announce the change early in release notes
- Log `v1` usage and warn client teams
- Remove `v1` only after usage drops below an agreed threshold

---

## 4. Consumer-Driven Contract Testing

The consumer team, usually the mobile app or restaurant dashboard team, should generate the contract tests that the API provider must satisfy. That way, the provider knows what each client actually depends on before making a change.

---

## 5. Summary
For `GET /orders/{id}`, CityBite should prefer additive JSON changes and reserve versioning for real breaking changes. Old mobile clients stay stable when new fields are added, but renamed or removed fields need a new version and a deprecation plan. Consumer-driven contracts help ensure the API evolves safely across teams.
