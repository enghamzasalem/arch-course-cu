# Part 1.1 — Workload dimensions and bottlenecks (CityBite at peak)

**Baseline:** K8s Order API, optional notification workers, managed **PostgreSQL**, **object storage** (or PVC) for menu images, mobile + restaurant tablets + dispatch. Evening dinner spikes; occasional marketing pushes.

## Workload dimensions and first-saturating resources

| # | Workload dimension | How we measure it | First resource that typically saturates |
|---|--------------------|-------------------|----------------------------------------|
| 1 | **Concurrent browsing / checkout sessions** | Simultaneous mobile sessions, cart updates, `POST /orders` attempts | **App CPU** (serialization, JSON) and **DB connection pool**; under extreme load also **app instances / threads** if pool too small. |
| 2 | **Orders per minute (write throughput)** | Inserts/updates to `orders`, inventory locks, outbox | **OLTP primary CPU and WAL I/O**; also **row-level locks** on hot SKUs. |
| 3 | **Kitchen dashboard reads** (active orders per restaurant) | QPS to “active orders for `restaurant_id`” (see `example1`: partition by tenant) | **DB CPU and buffer cache** if queries miss a proper **index / partition key**; else **replica I/O** if we offload reads. |
| 4 | **Outbound notifications** (push, email after checkout) | Events/sec to notify pipeline | **Outbound network** and **third-party API rate limits**; without a queue, **Order API thread time** (see `example2`). |
| 5 | **Per-restaurant menu and image traffic** | Bytes of JPEG/WebP, CDN/cache hits, menu `GET` | **Object storage / CDN egress**; origin hit rate if **cache** is cold. |
| 6 | **Onboarded restaurants and historical orders** | Table and index size, report queries | **Primary disk and backup window**; **p95** on ad-hoc reports without **replica** or time windowing. |

## “Hero scenario”: Friday 19:00–21:00, one city

**If scaled well (architecture matches growth):** Customers see **stable p95** on browse and “place order”; kitchen tablets refresh **active orders in seconds** without the global order table scanning every restaurant. Dispatch stays usable. Marketing coupons may add queue depth for notifications, but **checkout returns quickly** after the DB commit because **notify work is async** (queue + workers). Operations sees **HPA** adding API pods, **queue consumers** keeping up, DB **CPU below alarm** on the primary with reads shifted to a replica and hot paths **indexed by `restaurant_id`**.

**If scaled poorly:** p95 and error rates **climb** together: **connection pool exhaustion** produces spurious 5xx; **one expensive query pattern** (e.g. scanning all open orders) makes kitchen boards **stutter** as global order volume grows; **synchronous** SMS/email in the request path **lengthens** checkout. **Primary DB** goes red; adding **only** stateless pods **does not** fix TPS. Product sees “peak = outage,” not “peak = slower but honest limits.”
