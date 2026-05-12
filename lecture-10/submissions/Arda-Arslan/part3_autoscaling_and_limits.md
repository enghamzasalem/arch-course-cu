# Task 3.2 - Autoscaling and Backpressure

## HPA rule for the Order API

Assumption: the Order API is stateless and the main traffic spike happens during Friday dinner rush or a marketing campaign. A simple HPA rule is to scale on average CPU utilization. The target can be 70 percent CPU, with a minimum of 2 replicas and a maximum of 8 replicas. This is a reasonable Year 1 setup because CPU is easy to measure and the API already scales horizontally in Kubernetes. If traffic grows and average CPU stays above the target, Kubernetes adds more API pods automatically. 

## Backpressure or degradation policy

A practical backpressure policy is to protect the system when the notification queue grows too much. If the queue depth passes a fixed limit, CityBite should still save the order, but delay non-critical work such as notifications or analytics updates. This keeps the checkout path available even when downstream systems are slow. If the overload continues, the system can temporarily disable non-critical features instead of slowing down the whole API. This matches the lecture idea of degrading less critical work during peak load. 

## Failure lesson

If CityBite only scales stateless API pods and forgets the database, the first result is usually higher p95 latency, slower checkouts, and more time spent waiting on the database. Adding more pods can even make the situation worse, because each new pod creates more database traffic and more connection pressure. Users may then see timeouts, failed requests, or delayed dashboard updates even though Kubernetes shows many healthy API pods. The problem can be detected by looking at database CPU, connection pool usage, slow queries, and replication lag if a read replica exists. The main lesson is that autoscaling the API does not remove a serial bottleneck in the primary database. To mitigate this, CityBite should optimize hot queries, use indexes such as restaurant_id where needed, move read-heavy traffic like dispatch dashboards to a read replica, and scale up the database when the primary becomes the real limit. 