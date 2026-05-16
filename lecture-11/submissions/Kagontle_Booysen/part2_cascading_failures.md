# Part 2 — Task 2.2: Cascading Failures & Circuit Breaker
**Assignment:** Software Architecture — Lecture 11 (Availability and Services)  
**Product:** CityBite  
**Component:** Order API → Payment Gateway integration

---

## 2.2.1 Narrative: Payment Gateway 500 + Client Retry Storm

### The amplification sequence

At 19:42 on a Friday evening — peak order volume — the payment gateway begins returning HTTP 500 on authorization requests. The root cause is irrelevant to CityBite for the first few minutes; what matters is the cascade that follows inside CityBite's own infrastructure.

**T+0 s:** The gateway starts returning 500. The first batch of checkout requests in the Order API receives an error on the payment call. The retry logic — configured as three attempts with a 200 ms fixed delay — fires immediately.

**T+0 to T+30 s:** Each failing checkout attempt now generates three gateway calls instead of one. With 200 concurrent checkouts per minute at peak, the gateway is receiving approximately 600 requests per minute from CityBite instead of 200. The gateway, already degraded, is now receiving three times the expected load from CityBite alone — plus identical amplification from every other customer of the same gateway. This is the **retry storm**: a well-intentioned resilience mechanism becomes an attack on an already-failing dependency.

**T+30 s:** Inside each Order API pod, checkout handlers are blocking on gateway calls for the full retry duration (~600 ms per attempt × 3 = up to 1.8 s per checkout, before application timeout). Each blocked handler holds a Postgres connection open (the order row is locked in `PENDING` state until payment resolves). The DB connection pool — flagged in Task 2.1's Alert 2 — begins climbing past 70 % utilisation.

**T+60 s:** Pool utilisation crosses 80 %. The readiness probe starts returning 503. Kubernetes removes the first pod from the load balancer. The remaining pods absorb its traffic share, which accelerates their own pool exhaustion. This is **cascading failure**: the failure of one pod increases load on surviving pods, causing them to fail faster.

**T+90 s:** Three of ten pods are now removed from the endpoint pool. The synthetic probe (Task 2.1.3) fires its alert. On-call is paged. But the system is still degrading — because the retry storm continues unabated on the seven remaining pods.

**T+120 s:** The Order API is functionally unavailable. Customers see timeout errors. The error budget (Task 1.2) is burning at roughly 50× — the entire 30-day budget will exhaust in under two hours.

This sequence is precisely the amplification pattern that `example1_availability_circuit_breaker_citybite.py` is designed to prevent. The circuit breaker's role is not to fix the gateway — it cannot. Its role is to **stop CityBite from making the gateway's problem worse**, and to **fail fast** so that customer-facing errors appear cleanly and quickly rather than after a 1.8 s timeout that exhausts every available resource.

---

## 2.2.2 Circuit Breaker Policy

### Thresholds (CLOSED → OPEN transition)

The circuit breaker monitors a **rolling 20-second window** of payment gateway calls made by the Order API. It transitions from CLOSED (calls pass through) to OPEN (calls are rejected immediately) when either of two conditions is met: (a) the error rate in the window exceeds **40 %** of total gateway calls, or (b) the p99 latency of gateway calls exceeds **2 000 ms** — even if those calls eventually succeed. The latency threshold is critical: a slow gateway that returns 200 after 3 seconds is, from the user's perspective and from the connection-pool's perspective, as harmful as one that returns 500. The 40 % error threshold is deliberately set below 50 % to open the circuit while a majority of calls still succeed — because the retry amplification described in Section 2.2.1 means that even a 40 % failure rate, if sustained, will exhaust the connection pool within 60 seconds. These thresholds align with the breaker configuration demonstrated in `example1_availability_circuit_breaker_citybite.py`, where the breaker tracks consecutive failures and opens after a configurable threshold rather than allowing unbounded retry accumulation.

### Open duration and half-open probe

Once OPEN, the circuit remains open for a **30-second base cooldown**. During this window, all payment gateway calls in the Order API are **rejected immediately** without touching the network — the breaker's `call()` method raises `CircuitOpenError` in under 1 ms. This fast-fail behaviour is what releases the Postgres connections that were being held by blocked handlers; the pool drains within seconds, readiness probes recover, and pods are re-added to the load balancer. After 30 seconds, the breaker enters HALF-OPEN state and allows a single probe request through to the gateway. If that probe succeeds (HTTP 2xx within 1 000 ms), the breaker closes and normal traffic resumes. If it fails, the breaker re-opens for another 30-second window, with the cooldown doubling on each consecutive re-open (exponential backoff: 30 s → 60 s → 120 s → cap at 300 s). This prevents the circuit from oscillating rapidly if the gateway is recovering slowly, which would itself re-trigger pool pressure on each half-open attempt.

### Fallback behaviour (OPEN state)

When the circuit is open, CityBite must present a coherent experience rather than a silent 500 error. The fallback strategy is tiered by order value and customer context. For orders below €30 with a returning customer (verified by checking order history in the read model), the Order API **queues the order** in a durable Redis stream with status `PAYMENT_PENDING` and returns HTTP 202 Accepted with a message: *"Your order has been received. We'll confirm payment and notify you within 5 minutes."* The Dispatch Worker holds the order in `PENDING` state and a background job retries the gateway call once the circuit closes. For orders above €30, or for first-time customers where the trust signal is lower, the API **declines cleanly** with HTTP 503 and the message: *"Payment is temporarily unavailable. Please try again in a few minutes — your cart has been saved."* This two-tier fallback avoids the worst outcome (silently accepting an order that cannot be fulfilled) while preserving revenue on lower-risk orders. Under no circumstances does the fallback expose the raw gateway error message to the customer — the internal error is logged with full detail, but the customer-facing message is always explicit about what happened and what to do next.

---

## 2.2.3 Timeouts and Bulkhead

### Timeouts

A circuit breaker only opens *after* enough failures have accumulated to cross the threshold. Before that point, each individual gateway call can still block for its full timeout duration. This makes the **per-call timeout** the first line of defence, and it must be set independently from the retry policy. The Order API configures the following timeout hierarchy for the payment gateway integration:

| Timeout type | Value | Rationale |
|---|---|---|
| Connection timeout | 500 ms | Time to establish TCP connection; > 500 ms indicates a routing or DNS problem, not a slow handler |
| Read timeout | 1 500 ms | Time to receive first byte after sending the request; covers the gateway's processing time for a normal authorization |
| Total request timeout | 2 000 ms | Hard ceiling on the entire call including retries within a single attempt; ensures a single gateway call never holds a DB connection longer than 2 s |
| Retry budget | Max 1 retry, 100 ms exponential backoff | Not 3 retries — exactly 1, because the second retry is only attempted if the first attempt received a connection error (not a 5xx), meaning the request never reached the gateway |

The single-retry, connection-error-only policy is a direct response to the amplification problem in Section 2.2.1. A 5xx response from the gateway means the request *was received and failed* — retrying it immediately sends a duplicate charge authorization, which the gateway must deduplicate, adding load. Only a connection error (no response received) justifies a retry, because in that case the original request may not have been processed at all.

### Bulkhead

The bulkhead pattern partitions the Order API's thread pool (or async worker pool) so that a slow dependency cannot consume all available concurrency. Without a bulkhead, the payment gateway's degradation occupies every available worker in the Order API, leaving none to handle requests that do not need the gateway — for example, `GET /v1/orders/{id}` (order status lookup, used by the tracker screen) or `POST /v1/orders/{id}/cancel` (cancellations, which bypass payment). With a bulkhead, the pool is divided as follows:

| Pool partition | Max concurrent workers | Serves |
|---|---|---|
| `payment-gateway-pool` | 20 | Outbound payment gateway calls |
| `db-read-pool` | 30 | Order reads, restaurant menu fetches |
| `db-write-pool` | 20 | Order creation, status updates |
| `general-pool` | 10 | All other handlers (auth, health, admin) |

If all 20 workers in `payment-gateway-pool` are occupied (because the gateway is slow), new checkout requests that reach the payment step receive a `BulkheadFullError` immediately, which the circuit breaker counts as a failure toward its threshold. Critically, the 30 workers in `db-read-pool` are completely unaffected — the order tracker screen, restaurant dashboard, and dispatch worker status updates all continue operating normally throughout a payment gateway outage. This is the bulkhead's core guarantee: **blast radius containment**. A failure in one dependency degrades exactly the features that depend on it, and no others.

The bulkhead and the circuit breaker are complementary rather than redundant. The bulkhead limits the *concurrency* consumed by a slow dependency before the breaker opens; the breaker then eliminates the *latency* once the failure rate is confirmed. Neither alone is sufficient: a bulkhead without a breaker still allows all 20 payment workers to be blocked simultaneously; a breaker without a bulkhead allows a slow gateway to fill the entire thread pool in the seconds before the breaker threshold is crossed.

---

## 2.2.4 Canary Request Pattern

### Applicability to CityBite

The canary request pattern — routing a suspicious or novel request to a single isolated worker before allowing it to affect the broader pool — is applicable to CityBite in the **Dispatch Worker**, not the Order API. The Order API is a stateless HTTP service where requests are independently validated; there is no meaningful sense in which one checkout request is "suspicious" relative to another in a way that warrants isolation before processing.

The Dispatch Worker, however, processes messages from the order queue and calls the Maps/Routing API to assign drivers. Two scenarios justify a canary pattern here:

### Use case: Novel restaurant onboarding with unusual geofence payload

When a new restaurant is onboarded in a city zone that CityBite has not previously served (e.g., a new suburb with irregular polygon boundaries), its first set of delivery orders will contain geofence coordinates that the routing logic has never processed. A malformed polygon — for example, a self-intersecting geofence submitted by the restaurant onboarding tool — would cause the Maps API call to return a 422 Unprocessable Entity, which the Dispatch Worker currently treats as a fatal error and sends the order to the dead-letter queue.

The canary pattern here works as follows: orders from any restaurant whose `restaurant_id` was created within the last 24 hours are **routed to a dedicated canary Dispatch Worker pod** (a single-replica deployment running the same image as the main worker fleet, but with its queue consumer group isolated). The canary worker processes the first five orders from that restaurant. If all five complete successfully (driver assigned, Maps API call returns 200, order status transitions to `DISPATCHED`), the restaurant's subsequent orders are promoted to the main worker queue automatically. If any of the five fail, the failure is isolated to the canary pod — the main dispatch fleet is unaffected, and the onboarding team is alerted to inspect the restaurant's geofence data before further orders are processed.

This is directly analogous to the canary deployment pattern in Lecture 11: rather than routing a percentage of *all* traffic to a new code version, CityBite routes a category of *structurally novel* requests to an isolated worker before trusting them with production throughput. The isolation boundary is the consumer group, not a separate cluster, so the canary operates at near-zero infrastructure cost.

---

## Overview

| Mechanism | Addresses | Without it |
|-----------|-----------|-----------|
| Circuit breaker (40 % error / 2 s p99) | Retry storm amplification | Gateway outage → CityBite outage in < 2 min |
| Tiered fallback (queue / decline) | Customer experience during OPEN state | Silent failures or raw 500 errors |
| Per-call timeout (2 s total) | Connection pool exhaustion | Single slow call holds DB connection for full retry duration |
| Bulkhead (per-dependency pool partition) | Blast radius containment | Payment failure takes down order tracking and cancellations |
| Canary Dispatch Worker | Novel payload isolation | Malformed geofence from new restaurant crashes main dispatch fleet |

Together these five mechanisms implement the layered containment strategy: the timeout bounds individual call cost, the bulkhead bounds concurrent damage, the circuit breaker prevents systemic amplification, the fallback preserves UX, and the canary contains structural novelty before it reaches production scale.

---

*Continues in Part 3: Replication — sync vs async Postgres, read models, and consistency trade-offs.*
