# Task 2.1 - Database per service

## Two contexts, two separate stores

Picking the two contexts that talk to each other the most: Orders and Payments. Today they share one Postgres. The proposal is to split them into two logical schemas (could be two databases later, or two schemas in the same Postgres instance to start with).

### Orders schema (owned by Orders)

- `orders` - id, customer_id, restaurant_id, status, total_cents, created_at
- `order_items` - id, order_id, name, qty, price_cents
- `order_status_history` - id, order_id, from_status, to_status, changed_at
- `payment_status_cache` - order_id, status (authorized / captured / refunded / failed), payment_ref, updated_at

The last table is not Payments data - it is a local read-only copy, kept up to date from Payments events. Orders never writes payment logic into it, only reflects what Payments has told it.

### Payments schema (owned by Payments)

- `charges` - id, order_ref, customer_ref, amount_cents, status, gateway_id, created_at
- `refunds` - id, charge_id, amount_cents, status, reason, created_at
- `payment_methods` - id, customer_ref, type, gateway_token, last_used_at
- `gateway_events` - id, charge_id, raw_payload, received_at (audit / idempotency)

No table is shared. If Orders wants payment info it does not own, it asks the Payments API or reads its local cache.

## One query you lose

**Today (single DB):** "list this customer's last 10 orders with their payment status" is one SQL join between `orders` and `charges`.

**After split:** that join is gone. There is no `charges` table on the Orders side.

**Replacement (event-driven local cache):** Payments publishes events like `payment_authorized`, `payment_captured`, `payment_refunded`. Orders subscribes and updates its `payment_status_cache` table. The "last 10 orders with payment status" query then runs locally inside Orders, against `orders` joined to `payment_status_cache`. No cross-context call, no API aggregation at read time.

The cost: this is eventually consistent. A refund just processed in Payments might take a second or two to show up in Orders. For a customer-facing list this is fine; for actual money decisions, Orders must still call the Payments API and not trust the cache.

## RPO / RTO intuition for Orders with async replication

If the Orders database uses async replication to a standby (writes go to the primary, the standby catches up after a short delay):

- **RPO (data loss tolerance):** a few seconds. If the primary dies before the last writes have replicated, those orders are lost or have to be replayed. The business impact is smaller than in Payments because the customer can retry the order flow, although there is still a reconciliation cost if a charge was already authorized for the lost order.
- **RTO (time to recover):** minutes, not hours. Promote the standby, point Orders pods at it, restart. With async we accept a small window of lost writes in exchange for fast failover and lower cost compared to sync replication.

This trade-off is acceptable for Orders. It would not be acceptable for Payments, where a lost write means a charge that customers were told succeeded but never landed - so Payments would need stricter replication.