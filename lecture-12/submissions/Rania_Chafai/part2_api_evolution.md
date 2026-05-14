# Part 2.2 — Public API Evolution

## Selected Endpoint

GET /orders/{id}

Example response:

```json
{
  "id": 145,
  "status": "confirmed",
  "total_price": 42.5
}
```

---

## Safe Additive Changes

### Additive Change 1

Add a new optional field:

```json
"estimated_delivery_time": "20 minutes"
```

Old clients continue working because they ignore unknown fields.

---

### Additive Change 2

Add a loyalty_points field:

```json
"loyalty_points": 120
```

This change is backward compatible and does not affect older mobile applications.

---

## Breaking Change

### Breaking Change Example

Rename:

```json
"total_price"
```

to:

```json
"price_total"
```

Older clients would fail because they still expect the original field name.

---

## Versioning Strategy

CityBite introduces a new API version:

```text
/api/v2/orders/{id}
```

The old API version remains available during a deprecation period to give mobile clients enough time to migrate.

---

## Consumer-Driven Contract

Mobile application teams generate contract tests to verify that API responses remain compatible with client expectations.