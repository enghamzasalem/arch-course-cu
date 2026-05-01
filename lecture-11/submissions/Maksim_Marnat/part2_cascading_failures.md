# Part 2.2 — Cascading failures & circuit breaker (CityBite)

## 1. Narrative: PSP 500 + client retry storm (and `example1`)

When the **payment gateway** returns **500** or times out, naive clients and mid-tier retries implement **“try up to N times”** per checkout. That mirrors **`run_naive_trials`** in `example1_availability_circuit_breaker_citybite.py`: each failing checkout still issues **multiple `gw.charge` calls**, so **total gateway invocations explode** (`call_count` grows faster than success count). The PSP falls deeper behind; latencies rise; **Order API worker threads and HTTP client pools fill** waiting on the PSP; **good requests starve**; queues back up—**CityBite’s own API becomes slow or unavailable** even though “our” pods are CPU-idle waiting on I/O. That is **retry-induced cascading failure**: we amplify pain for ourselves and for the already-sick partner.

## 2. Circuit breaker policy

**Thresholds:** After **5 consecutive failures** or **50% error rate over a rolling 1-minute window** (min 20 samples) for PSP calls from a single pod, treat dependency as sick—aligns with the spirit of **consecutive failures** opening the breaker in `CircuitBreaker` (`failure_threshold` in `example1`).

**Open duration:** **30–60 seconds** base cooldown (extend with exponential backoff on repeated opens), then **half-open** trial traffic (single probe or small fraction).

**Fallback (product):** When open or half-open rejects synchronous pay: **fail fast** with clear UX—“Payment temporarily unavailable; save order as **pay later** / **retry**” or **enqueue order** to an **outbox** for async capture when PSP recovers; never infinite spinner. Revenue mode may switch to **cash on delivery** where legally allowed—explicit business rule.

## 3. Timeouts & bulkhead (why they pair with breakers)

**Timeouts** cap how long each PSP call holds a thread—without them, retries + slow PSP **tie up all workers** (`example2` pool analogy extended to HTTP threads). **Bulkheads:** separate **connection pools and executor lanes** per dependency (PSP vs maps vs SMS) so one noisy neighbor cannot exhaust **all** sockets toward every outbound API. Breakers **stop new attempts** while timeouts/bulkheads **bound damage per attempt**—together they contain blast radius.

## 4. Canary request — use case

**Use case:** Before applying a **new PSP webhook signature verification** or payload schema in production, route **one synthetic “probe order”** through the **canary deployment** with production-like credentials in **shadow or sandbox PSP**—validate end-to-end **without** shifting full traffic. Another use: **suspicious refund request** processed by **one dedicated worker** first (rate-limited) to avoid poisoning the whole fleet—**canary-style isolation** per lecture pattern.

If we rejected canaries entirely, we would miss cheap validation before wide rollout; for CityBite, **payment and webhook changes** are the highest-risk surface—canaries are applicable.
