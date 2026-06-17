# Part 2.1 – Writes, Reads, Caches, Queues

## Write Path – New Order (Strong Consistency)

1. API gets POST /order with cart + customer ID
2. Validate restaurant open, menu items exist
3. **Atomic write** to PostgreSQL: insert order, update inventory
4. API returns order confirmation

**Strong consistency required:** Inventory double-selling must be prevented.

## Eventually Consistent

- Order confirmation email/push (customer can wait 1–2 seconds)
- Analytics for restaurant dashboard (can be delayed minutes)
- Dispatch queue assignment

## Read Path – Kitchen Active Orders (Partition Key Thinking)

**Query:** "Show all pending orders for restaurant XYZ"

**Index:** `restaurant_id` + `status` + `created_at DESC`

**Why:** Each restaurant only sees its own orders. Partitioning (`restaurant_id`) keeps scans small regardless of total orders count.

## Cache Design

**What:** Restaurant menu items (read-heavy, infrequent updates)

**Key:** `menu:{restaurant_id}`

**TTL:** 5 minutes

**Invalidation:** When restaurant updates menu, write-through invalidates cache

**Stale read:** Customer sees old menu item for up to 5 minutes. Acceptable for price/description changes.

**CityBite screen:** Customer browsing menu before ordering.

## Queue – Where to Not Block HTTP Response

**Do not block:** Sending order confirmation email/push, updating analytics, dispatching to delivery partner.

**Example from Lecture 10:** API publishes `OrderCreated` event to SQS; workers send notifications asynchronously.

**Why:** Email provider slow or down should not stop the customer from seeing order confirmation.

## Summary

| Concern | Solution |
|---------|----------|
| Write consistency | PostgreSQL primary + atomic transactions |
| Read scalability | Read replica + restaurant_id partition index |
| Hot menu reads | Redis cache with 5-minute TTL |
| Async notifications | SQS queue + worker pods |