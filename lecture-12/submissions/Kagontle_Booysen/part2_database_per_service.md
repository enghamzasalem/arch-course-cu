# Part 2 — Task 2.1: Database per Service (Paper Design)

---

## Overview

The database-per-service principle states that each bounded context owns its persistence layer exclusively — no other context may connect to that database, read its tables, or write to its schema. Integration happens at the service boundary (API call or event), never at the storage boundary. This section designs separate logical schemas for two contexts, confronts the query that disappears when the shared schema is split, and reasons about RPO/RTO for one context under async replication.

---

## Section 1 — Logical Schema: Ordering Context

**Datastore:** PostgreSQL — `ordering` schema (separate DB instance at extraction time)

### Tables

```
orders
  order_id          PK
  customer_ref      (opaque foreign reference — NOT a FK to customers.id)
  restaurant_ref    (opaque reference — NOT a FK to catalogue.restaurants.id)
  status            ENUM(PLACED, ACCEPTED, READY, DISPATCHED, DELIVERED, CANCELLED)
  currency_code
  total_minor_units (authoritative total at time of placement; NOT joined to catalogue live)
  placed_at
  updated_at

order_lines
  line_id           PK
  order_id          FK → orders.order_id
  item_ref          (opaque reference to Catalogue item at time of placement)
  item_name_snapshot  (denormalised — captured at placement, insulates against menu edits)
  unit_price_snapshot
  quantity
  line_total_minor_units

order_status_events
  event_id          PK
  order_id          FK → orders.order_id
  from_status
  to_status
  actor             (customer | restaurant | system | courier)
  occurred_at
  reason_code

cart_sessions
  session_id        PK
  customer_ref
  restaurant_ref
  items             JSONB  (ephemeral; cleared on order placement or TTL expiry)
  created_at
  expires_at

outbox_events
  event_id          PK
  aggregate_type    (e.g. 'order')
  aggregate_id
  event_type        (e.g. 'OrderPlaced', 'OrderStatusChanged', 'OrderCancelled')
  payload           JSONB
  published         BOOLEAN DEFAULT false
  created_at
```

**Design notes:**
- `customer_ref` and `restaurant_ref` are opaque string handles (UUIDs). No foreign-key constraint crosses context boundaries. The Ordering context does not join to any other schema to resolve these references.
- `item_name_snapshot` and `unit_price_snapshot` on `order_lines` are deliberate denormalisation: the order record is a historical document of what the customer paid, immune to future menu edits in the Catalogue context.
- `outbox_events` implements the transactional outbox pattern (Lecture 9 baseline). Status changes write to both `order_status_events` and `outbox_events` in the same local transaction, guaranteeing at-least-once event delivery to downstream consumers without a two-phase commit.

---

## Section 2 — Logical Schema: Payment Context

**Datastore:** PostgreSQL — `payment` schema (separate DB instance, hardened network perimeter)

### Tables

```
payment_intents
  intent_id         PK
  order_ref         (opaque reference to Ordering — NOT a FK)
  customer_ref
  amount_minor_units
  currency_code
  status            ENUM(PENDING, AUTHORISED, CAPTURED, VOIDED, REFUND_PENDING, REFUNDED, FAILED)
  gateway_name      (e.g. 'stripe', 'adyen')
  created_at
  updated_at

authorisations
  auth_id           PK
  intent_id         FK → payment_intents.intent_id
  gateway_auth_token  (e.g. Stripe charge ID — opaque to domain logic)
  authorised_at
  expires_at
  amount_minor_units

captures
  capture_id        PK
  auth_id           FK → authorisations.auth_id
  captured_amount_minor_units
  captured_at
  gateway_capture_ref

refunds
  refund_id         PK
  intent_id         FK → payment_intents.intent_id
  amount_minor_units
  reason_code       ENUM(CUSTOMER_REQUEST, FRAUD, ITEM_UNAVAILABLE, SYSTEM)
  status            ENUM(PENDING, PROCESSED, FAILED)
  initiated_by      (customer | ops | system)
  initiated_at
  processed_at

settlement_batches
  batch_id          PK
  gateway_name
  settlement_date
  total_captured_minor_units
  total_refunded_minor_units
  net_minor_units
  status            ENUM(PENDING, RECONCILED, DISPUTED)

gateway_webhooks
  webhook_id        PK
  gateway_name
  event_type        (raw gateway event name)
  payload           JSONB
  processed         BOOLEAN DEFAULT false
  received_at

outbox_events
  event_id          PK
  aggregate_type
  aggregate_id
  event_type        (e.g. 'PaymentAuthorised', 'PaymentCaptured', 'RefundProcessed')
  payload           JSONB
  published         BOOLEAN DEFAULT false
  created_at
```

**Design notes:**
- `order_ref` is again an opaque reference. Payment knows what order it is paying for as a label; it does not query order details cross-schema.
- `gateway_webhooks` captures raw inbound gateway events before processing, enabling idempotent replay if the handler crashes after receiving but before writing. The `PaymentPort` adapter in `example1_flexibility_coupling_citybite.py` sits between this schema and the gateway SDK — the schema never encodes Stripe-specific field names.
- A separate `outbox_events` table ensures `PaymentCaptured` and `RefundProcessed` are published reliably to Ordering and Notifications consumers without distributed transactions.

---

## Section 3 — The Query You Lose and How to Replace It

### The Lost Query

In the shared-schema monolith, the support dashboard runs:

```sql
SELECT
  o.order_id,
  o.status          AS order_status,
  o.total_minor_units,
  pi.status         AS payment_status,
  pi.gateway_name,
  r.refund_id,
  r.amount_minor_units AS refund_amount
FROM ordering.orders o
JOIN payment.payment_intents pi ON pi.order_ref = o.order_id
LEFT JOIN payment.refunds r     ON r.intent_id  = pi.intent_id
WHERE o.customer_ref = $1
ORDER BY o.placed_at DESC;
```

This cross-schema join is the canonical distributed monolith smell: two ownership domains fused in SQL. Once Ordering and Payment own separate databases, this query is physically impossible.

### Replacement Strategy: Event-Sourced Read Model (CQRS Projection)

The replacement is a **dedicated read model** maintained by a separate, lightweight projection service (or a background worker within an operations/support context). This is the CQRS (Command Query Responsibility Segregation) pattern — writes go through the owning context, reads are served from a purpose-built projection.

**How it works:**

1. The Ordering context publishes `OrderPlaced`, `OrderStatusChanged` events via its outbox.
2. The Payment context publishes `PaymentAuthorised`, `PaymentCaptured`, `RefundProcessed` events via its outbox.
3. A `support_read_model` consumer (running as a K8s Deployment in the same cluster) subscribes to both event streams and maintains a denormalised projection table:

```
order_payment_summary  (in support_db schema — owned by support/ops context)
  order_id              PK
  customer_ref
  order_status
  order_total_minor_units
  placed_at
  payment_status
  gateway_name
  refund_amount_minor_units
  last_updated_at
```

4. The support dashboard queries `order_payment_summary` directly — a single-table read, no joins across ownership boundaries.

**Trade-off acknowledged:** The read model is **eventually consistent**. There is a window (typically sub-second at low event lag, potentially seconds under backpressure) where `order_payment_summary` lags behind the authoritative states in Ordering and Payment. For a support dashboard this is acceptable. For a real-time checkout confirmation it would not be — which is why the checkout flow uses the synchronous Ordering → Payment API call, not this read model.

**Alternative for simpler cases:** An **API aggregation** approach — where the support API calls both the Ordering API (`GET /orders?customer={id}`) and the Payment API (`GET /payment-intents?order_ref={id}`) and merges the results in-process — is lower infrastructure cost but introduces runtime coupling: if Payment is slow, the support dashboard is slow. For a background reporting query, the read model is preferable. For a low-traffic internal tool, API aggregation is a reasonable first step.

---

## Section 4 — RPO / RTO Intuition: Payment Context under Async Replication

### Context (Lecture 11 Link)

Lecture 11 covers availability patterns including replication lag, failover, and the distinction between synchronous replication (zero RPO, higher write latency) and asynchronous replication (non-zero RPO, lower write latency). The Payment context is the highest-criticality context in CityBite — a loss of payment data has direct financial and regulatory consequences — so it warrants explicit RPO/RTO reasoning.

### Setup Assumption

The Payment context Postgres instance runs with **async streaming replication** to a hot standby (same-region, separate availability zone) as deployed in the Lecture 9 K8s baseline. This mirrors a typical managed Postgres configuration (e.g. AWS RDS Multi-AZ in async mode, or a self-managed Postgres with `synchronous_commit = off`).

### RPO (Recovery Point Objective)

**Definition:** Maximum acceptable data loss measured in time — how far back the recovered state can be.

With async replication, the standby continuously applies WAL segments shipped from the primary, but there is always a **replication lag** — typically 100 ms to a few seconds under normal load, potentially higher under write spikes. If the primary fails at moment T, the standby has applied WAL up to moment T − Δ, where Δ is the lag at the instant of failure.

**RPO intuition for Payment:** Under normal conditions, replication lag is sub-second, so RPO ≈ 1–2 seconds of payment events (a handful of `payment_intents` rows). In the worst case (primary under heavy write load at peak order time), lag could reach 10–30 seconds, meaning up to 30 seconds of payment records — authorisations, captures, webhook receipts — may not be replicated before failover.

**Implication:** Those lost transactions are not in the database, but they *may* still exist as gateway webhooks in `gateway_webhooks` (if received before the crash) or as gateway-side records retrievable via the payment gateway's reconciliation API. The `gateway_webhooks` table's design specifically supports this recovery path: a post-failover reconciliation job can replay unprocessed webhook events to reconstruct the missing authorisations.

**If RPO must be zero:** Switch to `synchronous_commit = on` with `synchronous_standby_names` set. Every `COMMIT` blocks until the standby acknowledges WAL receipt. Write latency increases by one network round-trip (typically +1–5 ms intra-AZ). For payment captures, this latency cost is acceptable and the trade-off favours RPO = 0.

### RTO (Recovery Time Objective)

**Definition:** Maximum acceptable downtime — how long before the service is serving traffic again after a failure.

With a hot standby already running and receiving WAL, promotion is fast: a managed Postgres (RDS, Cloud SQL) failover completes in **30–60 seconds** including DNS propagation. A self-managed Patroni cluster on the K8s baseline can achieve **10–20 seconds** with pre-configured automatic failover.

**RTO intuition for Payment:** The Ordering context's checkout flow calls Payment synchronously. With the circuit breaker from Lecture 11 configured with a 10-second open-circuit timeout, a 30-second Payment DB failover means:

- Seconds 0–10: circuit breaker trips after timeout threshold; checkout calls fail fast rather than blocking.
- Seconds 10–30: Payment service is unavailable (circuit open); Ordering returns a graceful "payment temporarily unavailable" error to the customer.
- Second ~30: Payment DB standby is promoted; Payment service reconnects; circuit breaker half-opens and probes.
- Second ~60: Full traffic restored.

**Implication:** RTO of ~60 seconds end-to-end is acceptable for most food-delivery SLAs (orders are not safety-critical infrastructure). During the window, in-flight orders that have already been authorised are unaffected — their state lives in the authorisations table which was replicated up to T − Δ. Only new checkout attempts are blocked.

---

*Vocabulary aligned with Lecture 9 (K8s + Postgres baseline, outbox pattern), Lecture 10 (scalability), Lecture 11 (async replication, RPO/RTO, circuit breaker), and Lecture 12 (database-per-service, CQRS read model).*
