# Part 3: Pattern Checklist
## Task 3.1: Pattern Checklist

## 1. Load Balancing
CityBite should use load balancing at the entry point so traffic is spread across multiple Order API pods instead of one instance taking all the traffic. This is especially important during dinner rush and marketing campaigns, when many users may place orders at the same time. Load balancing helps keep latency stable and supports horizontal scaling. It also helps with multi-tenant fairness because one viral restaurant or one busy campaign should not overwhelm a single API pod and starve requests from other restaurants.

## 2. Sharding / Partitioning
CityBite would use sharding or partitioning for data that grows with restaurant activity, especially order data and dashboard queries. A practical partition key could be `restaurant_id`, so the kitchen screen and order history queries touch only the data for that restaurant. This reduces hot-path work and keeps queries smaller as the system grows. It is a strong choice for active-order and reporting workloads, but it must be designed carefully so one high-traffic restaurant does not create an unfair hotspot that hurts the rest of the system.

## 3. Scatter / Gather
CityBite can use scatter/gather for some read-heavy reporting tasks, such as collecting order counts or delivery stats across several partitions or replicas. In this pattern, the system sends smaller queries to multiple nodes and then combines the results into one response. This is useful for analytics or dashboard summaries, but it is not the first choice for the main checkout path because it can add complexity and delay. For fairness, scatter/gather should be limited and controlled so one restaurant’s heavy reporting request does not consume all capacity from shared resources.

## 4. Master / Worker (Worker Pool)
CityBite should use a master/worker or worker-pool pattern for non-critical background work such as notifications, receipts, analytics events, and dispatch updates. The API can place jobs into a queue, and workers can process them in parallel at a controlled rate. This decouples checkout from slow outbound I/O and makes the system much more resilient under spikes. It also supports multi-tenant fairness because the queue and worker limits can be managed so one high-volume restaurant cannot block notification processing for others.

## 5. Summary
These patterns fit different parts of CityBite. Load balancing protects the API layer, partitioning protects hot data paths, scatter/gather helps with distributed reads, and worker pools handle background jobs. The system should use each pattern only where it improves scalability without making the main checkout flow too complex. Multi-tenant fairness should be enforced through queue limits, per-restaurant partitioning, and controlled resource allocation so a single viral restaurant does not dominate the platform.
