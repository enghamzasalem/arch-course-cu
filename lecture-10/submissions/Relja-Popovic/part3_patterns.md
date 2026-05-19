## Task 3.1: Scalability Patterns Applied to CityBite

**Load balancing:** The Kubernetes Ingress distributes requests across Order API pods in round-robin. This is already in place and handles dinner-rush spikes well. To protect multi-tenant fairness, rate limiting per `restaurant_id` at the Ingress prevents one viral restaurant from starving others of pod capacity.

**Sharding / partitioning:** Full DB sharding is not the first choice at current scale - the operational cost outweighs the benefit. Instead, an index on `(restaurant_id, status)` achieves the same access-pattern isolation cheaply, as shown by `IndexedOrderBoard` in `example1`. Sharding becomes worth revisiting only if WAL throughput on a single primary becomes the ceiling.

**Scatter / gather:** Not a natural fit yet. CityBite's hot paths (checkout, kitchen dashboard) are scoped to one restaurant at a time, so there is nothing to fan out across. If CityBite later shards by city, scatter/gather would aggregate cross-shard reports - but adding it before sharding exists adds latency for no benefit.

**Master / worker:** Already in use for notifications. The Order API enqueues an event after each commit; a pool of `notification-worker` pods drains it in parallel - the `checkout_with_worker_pool` pattern from `example2`. Workers process messages in arrival order regardless of source, so a high-volume restaurant deepens the queue but cannot block other restaurants' notifications.