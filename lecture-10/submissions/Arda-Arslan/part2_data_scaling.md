# Task 2.1 - Data Plane: Reads, Writes, Caches

## Write path - new order

When a customer places a new order, the request goes to the Order API and is written to the PostgreSQL database. This part must be strongly consistent, because the order must be stored correctly and not duplicated.

After the order is saved, some actions do not need to be strongly consistent. For example, sending notifications or updating analytics can be done later. These can be handled asynchronously, so the HTTP response does not wait for them.

## Read path - kitchen active orders

The kitchen dashboard needs to show active orders for one restaurant. This should be based on restaurant_id, so each query only reads relevant data.

If the system scans all orders for every request, the cost grows with total system size and does not scale well. Using a filter or index on restaurant_id keeps the query efficient and focused on one restaurant.

This follows the idea from example1_scalability_hot_path_citybite.py, where queries are scoped by restaurant_id instead of scanning all orders.

Dispatch dashboard queries can use a read replica, because they are read-heavy and do not need to add more load to the primary database.

## Cache

One useful cache is for restaurant menus. The key can be restaurant_id, and the cache stores menu data for that restaurant.

A simple strategy is to use a short TTL, for example a few minutes. If the menu changes, the cache can expire or be refreshed.

If the cache is slightly stale, it is usually acceptable for users browsing menus. However, critical operations like placing orders should always use fresh data from the database.

## Queue or async processing

A queue can be used after the order is written to the database. For example, sending notifications or emails should not block the HTTP response.

The API can return success after saving the order and adding a task for background processing. Workers then process these tasks separately.

This follows example2_scalability_queue_workers_citybite.py, where notifications are handled asynchronously instead of blocking the request.