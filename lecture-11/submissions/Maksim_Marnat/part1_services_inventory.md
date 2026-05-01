# Part 1.1 — Components vs services inventory (CityBite)

## Inventory table

| Name | Component or external service | Who operates | Connector | Main risk if unavailable |
|------|-------------------------------|--------------|-----------|---------------------------|
| Order API & checkout orchestration | **Component** (Deployment in our K8s cluster) | CityBite platform team | HTTPS from ingress / mobile app | Customers cannot place or pay for orders; revenue stops; incident volume spikes. |
| Managed PostgreSQL (orders, payments state) | **Component** (we configure HA; vendor runs metal) | Cloud DB vendor + CityBite SRE | TCP/TLS, JDBC/async driver from Order API & workers | No durable orders; **readiness** should fail if pool cannot talk to DB (`example2_availability_monitoring_citybite.py`). |
| Dispatch / routing worker | **Component** | CityBite platform team | Queue (e.g. Kafka/Rabbit) + internal gRPC/HTTP | Delayed or stuck deliveries; SLA for “order handed to courier” slips. |
| Payment gateway (PSP) | **External service** | Third-party PSP | HTTPS REST + webhooks | **Paid checkout path blocked**; blind retries multiply load on sick partner (`example1_availability_circuit_breaker_citybite.py`). |
| Maps & ETA / routing API | **External service** | Maps SaaS vendor | HTTPS | Wrong or missing ETA; dispatch degradation; **product trust** drops even if orders technically complete. |
| SMS / push notification provider | **External service** | CPaaS vendor | HTTPS APIs | Couriers and restaurants miss time-critical alerts; operational chaos, higher support load. |

## Formal SLA or exit plan (two dependencies)

1. **Payment gateway (PSP)** — We would insist on a **written SLA** (availability, latency percentiles, incident comms) and a contractual **exit plan**: migration window, tokenization/portability of payment methods, webhook compatibility, and test environments for cutover drills. A PSP outage is direct revenue loss and chargeback risk.

2. **Maps & routing API** — Same bar: **SLA** on quota, latency, and incident notice; **exit plan** with a second routing provider behind a feature flag, cached static fallbacks for coarse ETA, and documented degradation (e.g. “ETA unavailable”) so we are not locked into one vendor’s roadmap or bankruptcy.

## Why external API availability is a product risk, not “only IT”

When a maps or payments API degrades, customers experience **failed checkouts, wrong ETAs, or silent notification gaps**—that is churn, bad reviews, and lost GMV, not a ticket closed in the ops queue. Product commitments (“food arrives in X minutes”, “pay now”) are implemented **through** those APIs; their failure modes surface as **brand and regulatory risk** (failed payments, misleading ETAs), so availability trade-offs must be owned jointly by product, legal/compliance, and engineering—not treated as invisible infrastructure.

## At least four distinct availability risks (named mechanisms)

| Risk | Mechanism / pattern |
|------|---------------------|
| **Partner PSP slow or failing** — checkout pile-up | **Circuit breaker**, bounded retries, **timeouts**, **bulkhead** pools per dependency (`example1_availability_circuit_breaker_citybite.py` themes). |
| **Pods “green” but cannot serve** — DB pool exhausted | **Readiness** probe with **deep** dependency check vs shallow `/healthz` (`example2_availability_monitoring_citybite.py`); remove pod from Service. |
| **Postgres primary failure** — data loss or stale promotion | **Sync vs async** replication roles; **RPO** discipline; controlled failover; avoid blind promote of lagging replica (Part 3). |
| **Retry storm** — CityBite amplifies outage | **Breaker OPEN / fail fast**, **async outbox** or “pay later” fallback, rate limits on client retries; protect PSP and own thread pools. |
