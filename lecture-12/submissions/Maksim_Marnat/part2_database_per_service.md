# Part 2.1 — Database per service (CityBite, paper design)

## Two contexts — logical schemas (names only)

| Context | Example tables / collections |
|---------|------------------------------|
| **Order & Checkout** | `orders`, `order_line_items`, `checkout_sessions`, `customer_order_timeline` |
| **Payment Settlement** | `payment_intents`, `psp_events`, `refunds`, `reconciliation_batches` |

No **foreign key** from `orders` rows to `payment_intents` across physical stores; link by **`order_id` UUID** carried in events/APIs only.

---

## Query you lose — replacement

**Lost:** `SELECT o.*, p.capture_status, SUM(li.subtotal) … FROM orders o JOIN payment_intents p ON … JOIN order_line_items li …` in **one** SQL round-trip.

**Replace:** **Order read API** loads `orders` + lines locally; calls **Payment internal API** `GET /internal/payments/by-order/{orderId}` (or consumes `PaymentCaptured` materialized into `customer_order_timeline` **read model**). For heavy dashboards: **precomputed view** fed by **change-data-capture** or domain events—not live cross-DB join.

---

## RPO / RTO intuition (Payment context, async replica)

If **Payment Settlement** uses **async read replica** for reporting and fraud dashboards (Lecture 11 link): **RPO** is **replication lag** (seconds typical)—a primary failure could **lose** not-yet-replicated commits unless we failover only after **lag ≈ 0** check. **RTO** is **promote standby + DNS/credentials swap** (minutes with automation). **Trade:** availability of analytics vs **strict freshness**; money-critical **primary** stays sync to SLA where regulator demands.
