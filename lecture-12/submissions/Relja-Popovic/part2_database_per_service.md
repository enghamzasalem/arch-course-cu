## Task 2.1

### Logical Schemas

**Ordering DB**
- `orders` (order_id, customer_id, status, total_cents, created_at)
- `order_lines` (line_id, order_id, item_id, quantity, unit_cents)
- `payment_attempts` (attempt_id, order_id, gateway_ref, result, attempted_at)

**Restaurant DB**
- `restaurants` (restaurant_id, name, address, is_open)
- `menu_items` (item_id, restaurant_id, name, price_cents, is_available)
- `menu_categories` (category_id, restaurant_id, label)

### Query Lost and How to Replace It

**Lost query:** `SELECT o.order_id, r.name FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id` - a joined view used by the dispatch dashboard to show order + restaurant name in one row.

**Replacement:** The Dispatch dashboard calls the Ordering API for open orders, extracts the `restaurant_id` from each, then calls the Restaurant API to resolve names.

### RPO / RTO for Ordering with Async Replication

If the Ordering DB uses an async read replica, the RPO at the moment of a primary failure is the current replication lag, typically a few seconds, meaning a small number of recently placed orders could be lost. The RTO depends on how quickly the replica is promoted. With a managed Postgres service this is usually under 60 seconds. For a payment-critical context like Ordering, a sync replica raises RPO to zero at the cost of slightly higher write latency on every checkout.