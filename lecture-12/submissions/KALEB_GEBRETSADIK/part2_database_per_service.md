# Part 2.1: Database Per Service (Paper Design)

## Context 1: Ordering Service Schema

| Table | Key Columns |
|---|---|
| `orders` | `order_id`, `customer_id`, `status`, `placed_at`, `total_cents` |
| `order_items` | `item_id`, `order_id`, `menu_item_ref`, `quantity`, `unit_price_cents` |
| `order_events` | `event_id`, `order_id`, `event_type`, `occurred_at`, `payload` |

## Context 2: Payment Service Schema

| Table | Key Columns |
|---|---|
| `charges` | `charge_id`, `order_ref`, `customer_ref`, `amount_cents`, `status`, `gateway_txn_id`, `created_at` |
| `refunds` | `refund_id`, `charge_id`, `amount_cents`, `reason`, `issued_at` |
| `payment_methods` | `method_id`, `customer_ref`, `type`, `last_four`, `token` |

---

## Lost Query & Replacement

**Lost query:** `SELECT o.order_id, o.total_cents, c.gateway_txn_id FROM orders o JOIN charges c ON c.order_ref = o.order_id WHERE o.customer_id = ?`

This cross-service JOIN is impossible when Ordering and Payment own separate databases.

**Replacement:** The Order API calls `GET /payments/charges?order_ref={order_id}` to enrich a response before returning it to the client (**API aggregation**). Alternatively, the Payment service publishes a `ChargeCompleted` event that the Ordering service consumes to store a `payment_status` denormalized in its own `orders` table as a **read model**.

---

## RPO/RTO Intuition — Ordering Context with Async Replication

If the Ordering service's primary Postgres node fails and we rely on **async replication**, the replica may be a few seconds behind. This means:
- **RPO (Recovery Point Objective):** Up to ~5–10 seconds of orders could be lost if the primary crashes before replication catches up.
- **RTO (Recovery Time Objective):** Failover to the async replica is fast (seconds), but we must accept that orders placed in the replication lag window may need manual reconciliation.

**Trade-off:** For lower RPO, switch to synchronous replication (as discussed in Lecture 11), accepting slightly higher write latency per checkout.
