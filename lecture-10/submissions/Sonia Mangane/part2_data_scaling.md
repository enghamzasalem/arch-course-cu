# Task 2.1: Data plane — reads, writes, caches


### 1. Write Path: New Order Flow
When a customer checks out, we make sure the order is saved safely and correctly.

* **API to Database:**  The Order API writes the order directly to the Postgres Primary. This is a normal ACID write.
* **After the Write:** Once the order is saved, we drop an event into a queue (like SQS or RabbitMQ). 
* **Consistency Rules:** * **Strong Consistency:** For payments and order status, we must always know the exact state.
    * **Eventual Consistency:** For things like notifications or analytics, a few seconds of delay is fine.

### 2. Read Path: Kitchen Active Orders
Kitchens need fast reads without slowing down the main database.

* **Indexes:** We index orders by `restaurant_id` and `status` so the kitchen only reads the orders it cares about.
* **Read Replica:** The kitchen dashboard reads from a replica, not the primary. This keeps checkout fast even if many kitchens refresh at once.

### 3. Caching Strategy: The Restaurant Menu
Menus get requested a lot, so we cache them in Redis.

* **Key:** `menu:v1:{restaurant_id}`
* **TTL / Invalidation:**30 minutes.
* **Invalidation:** If a restaurant updates a menu item, we delete the Redis key so the next request pulls fresh data.
* **Stale Reads:** A user might briefly see an old price which is acceptable during peak load.

### 4. Queueing: Decoupling the Hot Path
Some tasks shouldn’t slow down the customer’s checkout.

* **After Saving the Order:** The API returns `202 Accepted` right away.
* **Background Workers Handle:** 
    * Push notifications to the Driver.
    * SMS receipts to the Customer.
    * Sending order details to the Restaurant's printer.
* **Benefit:** If an SMS provider or restaurant Wi‑Fi is slow, it won’t freeze the customer’s app.