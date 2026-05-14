# Part 2.1 — Database Per Service (Paper Design)

## Principle

Each bounded context owns its data exclusively. No other service may connect directly to another context's database. Cross-context data needs are satisfied through published APIs or event-driven read models. This eliminates the shared-schema coupling that currently slows CityBite's teams.

---

## Context 1: Ordering Context — Logical Schema

```
orders
  order_id          UUID  PK
  customer_id       UUID
  restaurant_id     UUID
  status            TEXT   -- PLACED | CONFIRMED | READY | DELIVERED | CANCELLED
  total_cents       INT
  placed_at         TIMESTAMPTZ
  confirmed_at      TIMESTAMPTZ
  cancelled_at      TIMESTAMPTZ

order_items
  item_id           UUID  PK
  order_id          UUID  FK → orders.order_id
  menu_item_ref     UUID  -- opaque reference; no FK into Restaurant DB
  name_snapshot     TEXT  -- denormalised at order time
  unit_price_cents  INT
  quantity          INT

order_events
  event_id          UUID  PK
  order_id          UUID
  event_type        TEXT  -- OrderPlaced | PaymentSucceeded | OrderCancelled …
  payload           JSONB
  occurred_at       TIMESTAMPTZ
```

**Key design decisions:**
- `menu_item_ref` is an opaque UUID — Ordering does not join into the Restaurant schema. The item name and price are **snapshotted** at order time so the order record is self-contained even if the restaurant later changes its menu.
- `order_events` is an append-only log used for the event sourcing pattern (Lecture 11 bonus) and for publishing domain events to the message bus.

---

## Context 2: Dispatch Context — Logical Schema

```
deliveries
  delivery_id       UUID  PK
  order_ref         UUID  -- opaque reference to Ordering context
  restaurant_ref    UUID  -- opaque reference to Restaurant context
  courier_id        UUID  FK → couriers.courier_id
  status            TEXT  -- PENDING | ASSIGNED | PICKED_UP | DELIVERED
  pickup_address    TEXT
  dropoff_address   TEXT
  assigned_at       TIMESTAMPTZ
  picked_up_at      TIMESTAMPTZ
  delivered_at      TIMESTAMPTZ

couriers
  courier_id        UUID  PK
  name              TEXT
  phone             TEXT
  current_zone      TEXT
  is_available      BOOLEAN

delivery_eta
  delivery_id       UUID  FK → deliveries.delivery_id
  estimated_minutes INT
  calculated_at     TIMESTAMPTZ
  source            TEXT  -- 'maps_api' | 'cached' | 'manual'
```

**Key design decisions:**
- `order_ref` is an opaque reference — Dispatch does not join into the Orders table. It receives the delivery address and restaurant location via the `OrderConfirmed` event payload, which it stores locally in `pickup_address` / `dropoff_address`.
- `delivery_eta` is a separate table because ETAs are recalculated frequently and the history is useful for analytics.

---

## Query Lost With Split Databases — and How to Replace It

**Lost query:**
```sql
-- Previously possible with a shared schema:
SELECT o.order_id, o.customer_id, o.total_cents,
       d.courier_id, d.estimated_minutes
FROM   orders o
JOIN   deliveries d ON d.order_ref = o.order_id
WHERE  o.status = 'CONFIRMED'
  AND  d.status = 'ASSIGNED';
```
This query powered the operations dashboard showing "active orders with assigned couriers".

**Replacement — Event-driven read model:**

1. Both Ordering and Dispatch publish domain events to a shared message bus (e.g. Kafka or SQS).
2. A dedicated **Operations Read Model** service (or a simple worker) subscribes to `OrderConfirmed` and `CourierAssigned` events and maintains a denormalised `active_orders_view` table in its own read-only store.
3. The operations dashboard queries this read model instead of joining across two databases.

```
active_orders_view  (read model — owned by Operations context)
  order_id          UUID
  customer_id       UUID
  total_cents       INT
  order_status      TEXT
  courier_id        UUID
  estimated_minutes INT
  last_updated_at   TIMESTAMPTZ
```

This is eventually consistent (the view lags by the event processing time, typically < 1 second), which is acceptable for an operations dashboard. The trade-off is that the view can be slightly stale, but the two source-of-truth databases remain fully decoupled.

---

## RPO / RTO Intuition for the Dispatch Context with Async Replication

The Dispatch context uses an **async read replica** for ETA queries and courier availability lookups (high-read, low-write workload). Linking back to Lecture 11:

- **RPO (Recovery Point Objective):** If the primary Dispatch DB fails and the async replica is promoted, the replica may be lagging by up to ~30 seconds. This means up to 30 seconds of courier assignment updates and ETA recalculations could be lost. For Dispatch, this is acceptable — a courier can be re-assigned and ETAs recalculated from the current state. It would not be acceptable for the Ordering context's payment ledger, which uses synchronous replication (RPO ≈ 0).
- **RTO (Recovery Time Objective):** Managed failover (e.g. RDS Multi-AZ) promotes the standby in ~30–60 seconds. During this window, new courier assignments are queued in the message bus and processed once the new primary is available. Customers see a slightly delayed ETA update — a graceful degradation rather than a hard failure.
