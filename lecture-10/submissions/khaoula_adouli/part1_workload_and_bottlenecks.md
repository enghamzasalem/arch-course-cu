# Part 1.1 - Workload Model and Bottlenecks (CityBite)

## Baseline context used

CityBite has dinner spikes (especially 19:00-21:00), marketing campaigns, PostgreSQL for orders/accounts, and image storage in object storage. Main pain today: p95 latency rise, DB CPU pressure, connection pool exhaustion, duplicate heavy restaurant queries.

---

## 1) Workload dimensions and first saturated resource

| Workload dimension (grows with demand) | Example measure | First resource likely to saturate | Why |
|---|---|---|---|
| Concurrent customer checkout requests | Active in-flight requests per second | API CPU + DB connections | Checkout touches auth, pricing, write path, and transactions. |
| Orders per minute (OPM) | New orders/minute at peak | Postgres write IOPS / WAL throughput | Order creation is write-heavy and transaction-bound. |
| Restaurant kitchen dashboard polling | Queries/sec per restaurant tablet | DB CPU + cache miss pressure | Repeated active-order reads create hot read path fan-out. |
| Menu image traffic | MB/s image egress + requests/sec | Network egress / CDN origin bandwidth | Burst browsing drives image delivery cost/latency. |
| Notification fan-out (push/SMS/email) | Messages/sec after checkout | Worker throughput + outbound provider rate limits | Side effects spike with orders and can block if synchronous. |
| Partner integration sync jobs | Batch calls/min + payload size | Gateway rate limits + API thread pool | Long-running partner pulls can starve interactive user traffic. |
| Onboarded restaurants and active menus | Tenants and catalog rows | DB index size + cache memory | Larger working set increases cache misses and query cost. |

---

## 2) Hero scenario

### Friday 19:00-21:00 in one city (campaign + free delivery)

**If scaled well:**
- Customer app remains responsive; checkout p95 stays near target (for example under 500-700ms).
- Kitchen tablet shows fresh active orders with small lag.
- Notifications may arrive a little later but order confirmation is immediate.
- System degrades gracefully (e.g., slower analytics, not order placement).

**If scaled poorly:**
- Checkout stalls or times out, duplicate order attempts increase.
- DB connection pool is exhausted, causing cascading 5xx errors.
- Kitchen dashboard lags, dispatch quality drops, and support tickets spike.
- One viral restaurant can starve other restaurants (tenant unfairness).

---

## 3) Bottlenecks to prioritize

1. **Postgres primary write bottleneck** on order placement and status transitions.
2. **Hot read path** for kitchen active orders (repetitive heavy queries).
3. **Synchronous outbound I/O** (notifications) in request path.
4. **Connection pool and query fan-out** under tablet/dashboard polling.
5. **Image delivery burst traffic** if CDN/cache is weak.

These align with lecture examples: optimize hot path/indexing and decouple slow outbound work through queues/workers.
