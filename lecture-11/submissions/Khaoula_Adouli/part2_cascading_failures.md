# Part 2.2 — Cascading Failures & Circuit Breaker

## Failure Scenario: Payment Gateway Issue

If the payment gateway becomes slow or returns errors:

1. Order API sends payment request
2. Gateway responds slowly or fails
3. API retries the request multiple times
4. Many users retry at the same time

=> This creates a **retry storm**

Result:
- API becomes overloaded
- Database connections increase
- System latency increases
- Entire system may fail

---

## Circuit Breaker Strategy

### 1. Threshold
- If more than 50% of requests fail → trigger breaker

---

### 2. Open State
- Stop sending requests to payment gateway
- Immediately fail requests (fail fast)

---

### 3. Cooldown Period
- Wait 30–60 seconds before retrying

---

### 4. Fallback Strategy

Possible options:
- Allow "pay later"
- Queue the order for later processing
- Return clear message to user

---

## Timeouts & Bulkhead

### Timeouts
- Limit request time (e.g. 2 seconds)
- Prevent long waiting

---

### Bulkhead Isolation
- Separate connection pools per dependency
- Limit number of calls to payment gateway

=> Prevent one failure from affecting entire system

---

## Canary Request (Optional)

Example:
- Send one test request to payment gateway after failure

If it succeeds:
- Close circuit breaker

If it fails:
- Keep breaker open

---

## Why This Matters

Without these mechanisms:
- Small failures become system-wide outages
- External dependencies can bring down the whole platform

With circuit breaker:
- Failures are contained
- System stays partially available