# Part 2.2 — Cascading Failures & Circuit Breaker

## 1. Narrative: Payment Gateway 500 + Retry Storm

Imagine it is Friday evening — CityBite's peak traffic window. The payment gateway begins returning HTTP 500 errors intermittently. Each customer who hits a failed checkout sees a generic error and clicks "Try again", which the frontend also does automatically (up to 3 retries with no backoff). The Order API, following the same naive retry logic shown in `example1_availability_circuit_breaker_citybite.py`'s `run_naive_trials`, fires up to 5 gateway calls per checkout attempt. With 200 concurrent checkout attempts per second, a 55% gateway failure rate multiplies the outbound call volume to the gateway by roughly 3–4×. The gateway, already struggling, receives this amplified load and degrades further — a textbook **retry storm**.

Inside CityBite's own API, the picture is equally bad. Each gateway call blocks a thread (or an async task slot) for the full request timeout (say, 10 seconds). Thread pool slots fill up. New incoming requests queue behind them. The Order API's response time climbs from 300 ms to 8 seconds. Kubernetes readiness probes start failing because the DB pool is also exhausted by requests that are stuck waiting for gateway responses. Pods are removed from the load balancer, reducing capacity further. Within minutes, a **partial gateway outage has cascaded into a full CityBite outage** — even for customers who are not trying to pay, because the API is saturated. This is the amplification pattern `example1` is designed to prevent.

---

## 2. Circuit Breaker Policy

### Thresholds

Using the `CircuitBreaker` class from `example1` as a reference model:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `failure_threshold` | 5 consecutive failures | Avoids tripping on a single transient error |
| `open_seconds` (cooldown) | 30 seconds | Long enough for the gateway to recover; short enough to resume quickly |
| Half-open probe | 1 trial request | If it succeeds, close the breaker; if it fails, reopen for another 30 s |

### Open State — Fail Fast

When the breaker is OPEN, the `call()` method raises `circuit_open_fail_fast` immediately without touching the gateway. This is the key protection: CityBite's threads are freed instantly rather than blocking for 10 seconds each. Gateway call volume drops to near zero, giving the vendor breathing room to recover.

### Fallback Behaviour

When the breaker is open, CityBite does not simply return an error. Instead, the checkout handler applies a tiered fallback:

1. **Queue the order for async payment** ("Pay Later"): the order is persisted to Postgres with `status: pending_payment`. A background worker retries the payment charge every 30 seconds. The customer sees: "Your order is confirmed — payment will be processed shortly." This is the preferred fallback for low-value orders where the restaurant can begin preparation optimistically.
2. **Decline with clear UX**: for high-value orders or when the queue is also backed up, the API returns a user-friendly message: "Payment is temporarily unavailable. Please try again in a few minutes." The customer is not shown a generic 500 error. This preserves trust even during an outage.

The fallback choice is controlled by a feature flag so the product team can adjust the policy without a deployment.

---

## 3. Timeouts & Bulkhead

**Timeouts** are the first line of defence. Every outbound call to the payment gateway must have an explicit timeout — in CityBite's case, **3 seconds** for the initial attempt and **1.5 seconds** for any retry. Without a timeout, a single slow gateway response holds a thread indefinitely, and the thread pool drains silently. Timeouts ensure that a slow dependency cannot consume unbounded resources.

**Bulkheads** isolate the blast radius. CityBite uses a separate, bounded thread pool (or connection semaphore) for each external dependency:

- Payment gateway: max 20 concurrent in-flight requests
- Maps/routing API: max 10 concurrent in-flight requests
- SMS/push provider: max 5 concurrent in-flight requests

If the payment gateway is slow and all 20 slots are occupied, new checkout requests fail fast (or queue briefly) rather than spilling over into the thread pool used for DB queries or internal service calls. This means a gateway outage cannot starve the Order API of the resources it needs to serve non-payment operations (e.g. order status lookups, restaurant menu reads).

Timeouts and bulkheads **pair with the circuit breaker** because they operate at different timescales: timeouts bound individual request latency, bulkheads bound concurrent resource consumption, and the circuit breaker stops all calls once a failure pattern is detected. Together they form a layered defence — each mechanism catches what the others miss.

---

## 4. Canary Request

**Use case: suspicious or oversized order payload routed to one worker first.**

When CityBite receives an order with unusual characteristics — an unusually large number of items, a cart total above a configurable threshold (e.g. > $500), or a restaurant/customer combination that has triggered fraud flags before — the API routes the checkout to a single designated "canary worker" before committing the order to the main processing queue.

The canary worker performs the full validation and payment charge. If it succeeds, the order is confirmed normally. If it fails (payment declined, validation error, or the worker crashes), only that one order is affected — the main worker pool is untouched. This is valuable because a malformed payload that causes an unhandled exception in the worker would otherwise crash all worker replicas simultaneously if the order were broadcast to the full pool.

This pattern is directly analogous to the lecture's canary request concept: send one representative request to a single instance first, observe the outcome, and only proceed to the full fleet if the canary survives. In CityBite's context it also serves as a lightweight fraud and anomaly detection gate.
