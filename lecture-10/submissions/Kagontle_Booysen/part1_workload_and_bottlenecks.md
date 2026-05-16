# Part 1 — Workload Model and Bottlenecks
**CityBite Scalability Architecture | Lecture 10 Assignment**

---

## 1.1 Workload Dimensions

The table below identifies the five primary dimensions that grow as CityBite expands, the resource that saturates first under that growth, and the observable symptom that signals saturation.

| # | Workload Dimension | How It Is Measured | Resource That Saturates First | Saturation Symptom |
|---|---|---|---|---|
| 1 | **Concurrent active customers** (browsing menus, checking out) | Active HTTP sessions / WebSocket connections per second | **DB connection pool** — each request acquires a Postgres connection; the pool cap is hit before CPU | `connection pool exhaustion` errors; requests queue or fail at the API gateway |
| 2 | **Orders per minute (OPM)** — the transactional write rate | Checkout events/min; tracked by the Order API and SQS queue depth | **Database write IOPS / WAL throughput** — every order is a multi-row ACID write (orders, order_items, payment_log) | p95 write latency climbs; Postgres `wal_buffers` pressure; replication lag on any replica |
| 3 | **Restaurants onboarded** — the read fan-out multiplier | Count of active restaurant profiles; menu query rate from dashboards | **Application-level CPU + DB read IOPS** — each restaurant tablet polls for new orders every few seconds; N restaurants = N×polling queries | DB CPU spikes on `SELECT … WHERE restaurant_id = ?`; duplicate queries per restaurant (identified in the baseline pain points) |
| 4 | **Menu image bytes** — binary asset volume | Total GB stored in object storage / PVC; egress GB/month | **Network egress bandwidth + storage IOPS** — images are large (50–500 KB each), served on every menu page load | High CDN origin-fetch cost; slow first-byte time for customers on mobile; PVC disk saturation if stored locally |
| 5 | **Dispatch dashboard query load** — analytical read pressure | Dashboard page loads/min; slow-query count on reporting queries | **DB CPU + I/O for sequential scans** — dashboard queries (order history, revenue summaries, heatmaps) compete with OLTP writes on the same Postgres instance | p95 latency rise on the Order API during heavy dashboard usage; long-running SELECT transactions cause lock contention |

### Additional dimension (honourable mention)
| 6 | **Notification fan-out** — outbound I/O per order | SMS/push/email events emitted per order | **External API rate limits + worker thread count** | Notification worker backs up; customers receive delayed "order confirmed" messages |

---

## 1.2 Resource Saturation Mapping

The diagram below summarises which layer of the Lecture 9 Kubernetes baseline each dimension stresses.

```
┌────────────────────────────────────────────────────────────────────────┐
│  DIMENSION                    FIRST BOTTLENECK                         │
│                                                                         │
│  1. Concurrent customers ──►  Postgres connection pool cap              │
│  2. Orders per minute    ──►  DB write IOPS / WAL buffer               │
│  3. Restaurant polling   ──►  DB CPU (hot read path, no cache)         │
│  4. Menu image bytes     ──►  Network egress / PVC disk                │
│  5. Dashboard queries    ──►  DB CPU / lock contention with OLTP       │
│  6. Notifications        ──►  Notification worker thread pool          │
└────────────────────────────────────────────────────────────────────────┘
```

Dimensions 1, 2, 3, and 5 all converge on a **single Postgres instance** — this is the primary serial bottleneck in the current baseline. Dimensions 4 and 6 are I/O-bound but can be addressed independently.

---

## 1.3 Hero Scenario — Friday 19:00–21:00, Bremen City Centre

### Scenario description

**Trigger:** A marketing team launches a "free delivery" campaign at 18:55, valid only during the dinner window. Within minutes, every mobile customer in the city sees the push notification simultaneously and opens the app. Three hundred restaurants go into peak service. The dispatch dashboard is open on tablets across the city. The notification worker must confirm every order.

This is the worst-case overlap of **all five dimensions at once**: customer concurrency peaks, OPM peaks, restaurant polling doubles, dashboards are open everywhere, and notifications fan out at maximum rate.

### If scaled well — what users feel

| User type | Experience |
|---|---|
| **Mobile customer** | Menu images load in under 1 s (CDN cache hit). Checkout completes in under 2 s. "Order confirmed" push arrives within 5 s. No spinner timeouts. |
| **Restaurant tablet** | New orders appear within 3 s of placement. The polling endpoint returns instantly from a read replica / Redis cache; the tablet never shows a loading state. |
| **Dispatch operator** | Dashboard refreshes smoothly. Revenue and heatmap queries run against a dedicated read replica and return in under 3 s without affecting checkout latency. |

The system achieves this because:
- The **hot path** (menu read + checkout write) is protected by Redis caching and connection pooling with PgBouncer, aligned with `example1_scalability_hot_path_citybite.py`.
- Checkout is decoupled: the Order API writes the order row and enqueues an SQS event; fulfilment and notifications are processed asynchronously by autoscaled workers, aligned with `example2_scalability_queue_workers_citybite.py`.
- Read replicas absorb dashboard and restaurant-polling queries, leaving the primary for writes only.
- Menu images are served from object storage behind a CDN; zero origin hits per returning customer.

### If scaled poorly — what users feel

| User type | Experience |
|---|---|
| **Mobile customer** | Checkout spinner runs for 15–30 s. Intermittent `503 Service Unavailable` as Postgres connection pool exhausts. "Order confirmed" SMS arrives 4 minutes late or not at all. Some customers abandon and resubmit, causing **duplicate orders** (a data-integrity risk on top of the latency risk). |
| **Restaurant tablet** | Order list freezes. The tablet's polling query competes with write transactions; `p95 latency rises under load` (baseline pain point). Restaurant staff call customers to re-confirm, damaging brand trust. |
| **Dispatch operator** | Dashboard query triggers a full sequential scan on the orders table. This holds a shared lock that blocks write transactions. OPM drops chain-reaction style as the DB becomes the bottleneck for every subsystem simultaneously. |

The contrast illustrates why the remainder of this assignment focuses on **breaking the single-DB serial bottleneck** as the highest-priority architectural risk.

---

## Summary: Bottleneck Priority Stack

| Priority | Bottleneck | Root cause | Section that addresses it |
|---|---|---|---|
| P0 | Postgres connection pool exhaustion | All requests open a connection; no pooler in front of DB | Part 2 (PgBouncer / read replicas) |
| P1 | DB CPU from restaurant polling | No cache; N restaurants = N redundant queries | Part 2 (Redis hot-path cache) |
| P2 | DB CPU from dashboard queries on primary | OLTP and OLAP share one instance | Part 2 (read replica routing) |
| P3 | Notification fan-out blocking checkout | Synchronous outbound I/O in request thread | Part 2 (SQS + autoscaled worker) |
| P4 | Menu image egress cost and latency | Origin fetch on every request; no CDN | Part 3 (object storage + CDN) |

---

*Terminology aligned with `example1_scalability_hot_path_citybite.py` (hot path, indexing, partition key) and `example2_scalability_queue_workers_citybite.py` (decouple checkout from outbound I/O).*
