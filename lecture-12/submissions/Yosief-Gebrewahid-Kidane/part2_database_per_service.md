# Part 2 — Database per Service (CityBite)

## 1. Overview

As CityBite grows, sharing a single database across all features becomes a major source of coupling. Teams cannot evolve schemas independently, and one poorly optimized query can affect the entire platform.

To improve flexibility, each bounded context should gradually own its own datastore or logical schema. This approach reduces hidden dependencies and allows services to scale and evolve independently.

---

# 2. Ordering Context Database

## Purpose

The Ordering context handles customer checkout, order lifecycle management, and payment coordination.

---

## Example Logical Schema

### Tables

- `orders`
- `order_items`
- `customer_addresses`
- `payment_attempts`
- `checkout_sessions`

---

## Responsibilities

This datastore owns:
- Order creation
- Checkout state
- Customer order history
- Payment status tracking

The Ordering context is responsible for transactional consistency because failed or duplicated orders directly impact customer trust and revenue.

---

# 3. Restaurant Operations Database

## Purpose

The Restaurant Operations context manages restaurant workflows and kitchen activity.

---

## Example Logical Schema

### Tables

- `restaurants`
- `menus`
- `menu_items`
- `kitchen_active_orders`
- `restaurant_settings`

---

## Responsibilities

This datastore owns:
- Menu management
- Restaurant dashboards
- Kitchen queues
- Restaurant-specific operational data

This context is read-heavy and optimized for fast restaurant dashboard queries.

---

# 4. Query We Lose After Database Separation

## Problem

In the monolith, teams could run large SQL joins across every table.

Example:
```sql
SELECT *
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.id
JOIN payments p ON o.id = p.order_id;
```

After splitting databases, these joins are no longer possible directly because each service owns its own data.

---

# 5. Replacement Strategy

Instead of cross-database joins, CityBite can use:

- API aggregation
- Event-driven read models
- Reporting pipelines
- Materialized views for analytics

---

## Example

A reporting service may:
1. Consume events from Ordering and Payments
2. Build a separate analytics datastore
3. Generate dashboards independently from transactional systems

This keeps operational systems isolated while still supporting business reporting needs.

---

# 6. Why This Trade-off Is Worth It

Losing direct SQL joins increases architectural complexity, but it improves:

- Team independence
- Deployment flexibility
- Fault isolation
- Schema ownership
- Scalability

The system becomes easier to evolve over time, especially as engineering teams grow.

---

# 7. Replication and Availability (RPO/RTO Intuition)

CityBite may use asynchronous replication for read replicas or disaster recovery.

### Example: Restaurant Operations Context

- **RPO (Recovery Point Objective):** a few seconds of recent updates may be lost during a catastrophic failure
- **RTO (Recovery Time Objective):** recovery should happen within minutes

This trade-off is acceptable because:
- Restaurant dashboards can tolerate slightly stale data
- Availability is prioritized during incidents
- Core checkout transactions still rely on the primary transactional database

For critical payment and order creation workflows, stronger consistency guarantees remain necessary.