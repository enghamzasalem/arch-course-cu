# Part 3.1 — Scalability Pattern Checklist

## Load Balancing

CityBite's Kubernetes Ingress (nginx or Envoy) acts as the load balancer in front of
the Order API Deployment. Requests from mobile customers are stateless — each HTTP
request carries a JWT for authentication and carries all context needed to serve it —
so any API pod can handle any request. The load balancer distributes requests across
pods using round-robin or least-connections. HPA adds pods when CPU crosses the
target threshold, and the load balancer automatically includes new pods in the pool
as they pass readiness checks. The load balancer itself is a single entry point and can
become a bottleneck at very high RPS, but at CityBite's Year 1 scale the Ingress
controller running on dedicated nodes is not the first constraint — the database is.

---

## Sharding / Partitioning

Sharding is not the first choice for Year 1 CityBite, but horizontal table partitioning
is already valuable. The `orders` table should be range-partitioned by `created_at`
(monthly partitions), so that the active-orders query for the kitchen dashboard only
scans the current month's partition rather than all historical data. This is application-
transparent partitioning within a single Postgres instance — no routing logic changes.
Full horizontal sharding (separate Postgres clusters per `city_id`) would be introduced
when write TPS on the primary consistently exceeds 60% capacity and read replicas no
longer relieve enough pressure. Sharding introduces routing complexity and cross-shard
query difficulties that are not justified until the single-writer ceiling is genuinely close.

---

## Scatter / Gather

CityBite does not currently use scatter/gather in its hot path, but it is the natural
architecture for the dispatch dashboard's city-wide view: "show me all active orders
across all restaurants in Amsterdam." At scale, if orders are sharded by `city_id`,
this query must be scattered to all city shards and the results gathered and sorted
before returning. In Year 1 with a single Postgres instance, a single indexed query
suffices. The scatter/gather pattern becomes necessary if the city-wide view needs to
span multiple shards — at that point, an Aggregator service fans out the query to each
city's shard in parallel (to minimize latency) and merges the sorted results. The key
engineering constraint is that the aggregator's response latency equals the slowest
shard response, so shard count and size must be kept balanced.

---

## Master / Worker (Worker Pool)

This is the pattern CityBite already uses for notifications (example2) and should
expand to other background work: receipt generation, analytics event ingestion,
restaurant onboarding verification. The Order API (master) places messages on an
SQS queue; a pool of notification workers subscribes and processes them. The pool
scales independently of the API: during a campaign push, the queue depth grows and
KEDA or a custom HPA metric triggers more worker pods. Workers are stateless — they
read a job, call an external API, ack the message — so any worker can handle any job.
This is the correct pattern for input-size scaling: when one "client" (the API) generates
a large burst of work, you add workers to drain it rather than scaling the API itself.

---

## Multi-Tenant Fairness

A single viral restaurant (e.g. one that is featured on a popular food blog and gets
10x its normal order volume) must not exhaust the DB connection pool, cache write
bandwidth, or notification queue worker capacity at the expense of all other restaurants.

Three mechanisms enforce fairness:

1. **Per-restaurant Redis rate limiting** on `POST /orders`: a sliding-window counter
   keyed on `restaurant_id` caps inbound order rate at, say, 50 orders/minute per
   restaurant. Requests beyond the cap receive `429 Too Many Requests` with a
   `Retry-After` header. This prevents one restaurant from monopolising DB write
   capacity.

2. **Notification queue priority lanes**: a separate low-priority queue for non-critical
   notifications (promotional messages) ensures that order confirmation messages for
   all restaurants are not delayed behind a bulk notification campaign.

3. **Partition key discipline**: the `(restaurant_id, status, created_at)` composite
   index ensures that a restaurant with 10x the normal order volume only affects
   its own index pages, not those of other restaurants. The hot partition for a viral
   restaurant does not cause lock contention on rows belonging to other restaurants.
