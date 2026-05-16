# Part 1 — Task 1.2: SLI / SLO / Error Budget
**Assignment:** Software Architecture — Lecture 11 (Availability and Services)  
**Product:** CityBite  
**User Journey:** Place Paid Order

---

## 1.2.1 User Journey Selection

**Journey: "Place Paid Order"**

A customer opens the CityBite app, adds items to their cart, enters payment details, and taps **Place Order**. The journey is complete when the customer receives an HTTP 200 response from the Order API containing a confirmed `order_id` and the order row is durably persisted in Postgres with status `CONFIRMED`. This journey was chosen because it is the single most revenue-critical path in the product — no other journey generates direct GMV — and it crosses the most external trust boundaries (Auth → Order API → Payment Gateway → Postgres → Dispatch queue), making it the highest-risk sequence to keep available.

---

## 1.2.2 Service Level Indicator (SLI)

### Definition

> **SLI — Checkout Success Ratio:**  
> The fraction of "Place Paid Order" requests that complete successfully within a latency threshold, measured over a rolling 5-minute window.

### Formal expression

```
SLI = (valid_requests - bad_events) / valid_requests
```

Where:

- **`valid_requests`** — all HTTP POST requests to `/v1/orders` that reach the Order API with a well-formed body and a valid auth token (i.e., not rejected at the WAF or load balancer before application logic runs).
- **`bad_events`** — any valid request that results in:
  - HTTP 5xx response from the Order API, **or**
  - HTTP 200 response returned after **> 3 000 ms** end-to-end (slow success treated as failure for user experience purposes), **or**
  - A timeout with no response within 10 s (connection dropped).

Requests that return HTTP 4xx (malformed input, invalid card number, insufficient funds) are **excluded** from `valid_requests` — these are user errors, not availability failures, and must not inflate the error budget.

### Why this SLI is measurable

The Order API already emits structured logs on every request (consistent with the logging assumed in `example2_availability_monitoring_citybite.py`). Each log line carries:

```json
{
  "endpoint": "/v1/orders",
  "method": "POST",
  "status_code": 201,
  "duration_ms": 412,
  "order_id": "ord_8f3a...",
  "payment_status": "AUTHORIZED"
}
```

A Prometheus counter scraping these logs can produce two metrics directly:

| Metric | Description |
|--------|-------------|
| `citybite_checkout_requests_total{result="valid"}` | All non-4xx POST /v1/orders |
| `citybite_checkout_requests_total{result="bad"}` | 5xx + slow (>3 s) + timeout |

The SLI ratio is then:

```
1 - (rate(citybite_checkout_requests_total{result="bad"}[5m])
     / rate(citybite_checkout_requests_total{result="valid"}[5m]))
```

This is fully derivable from existing application logs with no additional instrumentation beyond what the readiness-probe pattern in `example2_availability_monitoring_citybite.py` already establishes.

---

## 1.2.3 Service Level Objective (SLO)

### Statement

> **SLO:** 99.5 % of valid "Place Paid Order" requests must satisfy the SLI (complete with HTTP 2xx within 3 000 ms) measured over a **rolling 30-day calendar window**.

### Justification for 99.5 %

| Candidate target | Monthly error budget | Rationale |
|-----------------|---------------------|-----------|
| 99.9 % | ~43 min / month | Requires near-zero tolerance for deploys and dependency incidents; unrealistic given Payment Gateway and Maps API are external with their own SLAs of ~99.95 % individually but uncorrelated |
| **99.5 %** | **~3 h 39 min / month** | Matches realistic external dependency budget; allows one planned deploy window plus one minor incident per month without exhausting budget |
| 99.0 % | ~7 h 18 min / month | Too permissive; a single Friday payment-gateway incident could consume the entire budget and leave no room for intentional change |

99.5 % is deliberately set *below* what individual infrastructure components can achieve so that the SLO is owned by the **product team**, not just the infrastructure team — if the payment gateway degrades CityBite's checkout success rate, that counts against the SLO regardless of whether CityBite's own pods are healthy. This forces product ownership of vendor risk.

### Monthly error budget calculation

```
Total minutes in 30 days          = 30 × 24 × 60 = 43 200 min
Allowed failure fraction          = 1 - 0.995    = 0.005
Error budget (time equivalent)    = 43 200 × 0.005 = 216 min  ≈ 3 h 36 min
```

Expressed as a **request count** budget (more operationally useful):

```
Assume average load: 200 checkout requests / minute
Total valid requests / month      = 200 × 43 200 = 8 640 000
Allowed bad events / month        = 8 640 000 × 0.005 = 43 200 bad requests
```

The error budget can therefore be monitored as a running counter of bad checkout events. When that counter crosses 43 200 within the current 30-day window, the SLO is breached.

---

## 1.2.4 Error Budget Policy

### Budget states and burn rate

The error budget is not a cliff — it is a resource to be actively managed. CityBite defines three operational states based on **burn rate**, which measures how fast the budget is being consumed relative to the rate at which it accrues.

A **burn rate of 1×** means the budget is being consumed exactly as fast as it accrues (spend the whole 216 min over 30 days). A burn rate of **14.4×** means the entire 30-day budget would be exhausted in 50 hours.

| State | Condition | Burn rate | Budget remaining | Action |
|-------|-----------|-----------|-----------------|--------|
| 🟢 **Nominal** | Budget consumption on track | < 2× | > 50 % remaining | Normal operations; deploys proceed |
| 🟡 **Elevated** | Budget burning faster than expected | 2× – 5× | 25 %–50 % remaining | Feature freeze for the affected journey; all deploys to Order API require SRE sign-off; incident review opens within 24 h |
| 🔴 **Critical** | Budget nearly exhausted or burning rapidly | > 5× | < 25 % remaining | **Full deploy freeze** on Order API, Payment integration, and Dispatch Worker; on-call incident declared; rollback of any change deployed in last 72 h evaluated immediately |
| ⛔ **Breached** | 30-day SLO target missed | — | 0 % (budget gone) | Post-mortem within 48 h; no new features shipped to checkout path until root cause is resolved and SLO is restored for 7 consecutive days |

### Concrete policy rules

**At 🟡 Elevated burn:**
- Automated PagerDuty alert fires to the on-call engineer and the product manager who owns the checkout journey.
- No new feature flags may be enabled on the `/v1/orders` path.
- Circuit breaker thresholds (aligned with `example1_availability_circuit_breaker_citybite.py`) are reviewed and tightened if they were recently relaxed.

**At 🔴 Critical burn:**
- The Order API deployment is locked in CI/CD; GitHub branch protections require SRE approval to merge to `main`.
- A canary analysis is run on any pod that was rolled out in the past 3 days: if the canary's SLI is worse than baseline by more than 0.5 %, it is automatically rolled back.
- The payment gateway circuit breaker is evaluated: if the gateway's error rate is contributing more than 50 % of bad events, the fallback processor (see Task 1.1) is activated manually.

**At ⛔ Breached:**
- The engineering leadership and product leadership hold a joint review. The SLO target itself is re-examined — a repeated breach may indicate the target is miscalibrated, not that the system is poorly operated.
- The 30-day window resets, but the team carries a **reliability debt** item into the next sprint planning cycle.

### Why this policy matters: retries and the burn rate trap

A common mistake is to configure the Order API client to **retry** failed checkout requests aggressively (e.g., 3 retries with no backoff). If the payment gateway is slow rather than hard-down, each retry adds latency and additional load to an already-degraded dependency, causing retry storms. From the SLI's perspective, a single customer checkout that retries three times and eventually succeeds after 9 seconds still counts as **one bad event** (latency > 3 s threshold exceeded), but it has now consumed three times the gateway quota and inflated the error rate seen by the gateway's own SLO.

The circuit breaker pattern (as implemented in `example1_availability_circuit_breaker_citybite.py`) prevents this: once the gateway's error rate crosses the circuit breaker threshold, further requests are **failed fast** without hitting the gateway at all. This has two effects on the error budget:

1. Bad events continue to accrue (the SLI is still failing), but at a controlled rate rather than an amplified one.
2. The gateway is given time to recover without being overwhelmed — meaning the circuit breaker's half-open probe can restore service faster.

The error budget policy therefore works in concert with the circuit breaker: a 🔴 Critical burn is precisely the signal to check whether the circuit is open and whether the half-open cooldown period needs adjustment.

---

*Continues in Part 2: monitoring strategy, cascading failure controls, replication design, and optional event-sourcing.*
