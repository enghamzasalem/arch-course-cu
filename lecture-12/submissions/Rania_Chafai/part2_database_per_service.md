# Part 2.1 — Database per Service

## Separate Datastores by Context

### Order Context Database

Tables:
- orders
- order_items
- carts
- checkout_sessions

Purpose:
This database stores all information related to customer orders and checkout operations.

---

### Payment Context Database

Tables:
- payments
- refunds
- transactions
- invoices

Purpose:
This database handles payment processing and financial records independently from the Order context.

---

## Query Lost After Database Split

### Lost Query

Before splitting databases, CityBite could execute queries such as:

```sql
SELECT *
FROM orders
JOIN payments
ON orders.payment_id = payments.id;
```

This type of cross-context SQL join is no longer possible because each service owns its own datastore.

---

## Replacement Strategy

CityBite can replace this query using:

- API aggregation
- Read models
- Asynchronous events

Example:
- Order Service publishes an event after checkout
- Payment Service processes payment
- Reporting service builds a combined read model

This reduces coupling between services.

---

## Async Replication — RPO / RTO

For the Payment Context:

### RPO (Recovery Point Objective)

A small amount of recent payment data may be lost during failure if asynchronous replication is used.

Estimated RPO:
- Few seconds

---

### RTO (Recovery Time Objective)

Time required to restore payment service availability.

Estimated RTO:
- Few minutes

---

## Trade-offs

Benefits:
- Independent scaling
- Better service isolation
- Clear ownership boundaries

Trade-offs:
- Increased operational complexity
- Eventual consistency
- More complex reporting queries