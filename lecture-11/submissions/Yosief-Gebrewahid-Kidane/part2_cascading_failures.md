# Part 2 — Cascading Failures and Circuit Breakers (CityBite)

## 1. Overview

CityBite depends on several external services, especially the payment gateway used during checkout. If one dependency becomes slow or unavailable, failures can quickly spread across the platform. Without proper controls, retry storms and blocked requests can overload the entire system.

This section explains how CityBite contains cascading failures using circuit breakers, timeouts, bulkheads, and controlled degradation strategies.

---

## 2. Payment Gateway Failure Scenario

During peak dinner traffic, the payment provider begins returning HTTP 500 errors and occasional long response delays.

At first:
- Customer checkout requests slow down
- API workers wait for payment responses
- Request queues begin growing

If the API blindly retries failed payment requests:
- The number of outbound calls increases dramatically
- The payment provider becomes even more overloaded
- API threads remain blocked for longer periods
- Kubernetes scales more API pods, which creates even more retries

This creates a classic retry storm similar to the lecture example in `example1_availability_circuit_breaker_citybite.py`.

Eventually:
- Database connections become exhausted
- API latency spikes
- Customers experience timeouts and duplicate submissions
- The outage spreads beyond payments into the overall ordering system

---

## 3. Circuit Breaker Strategy

CityBite uses a circuit breaker between the Order API and the payment gateway.

---

## 3.1 Failure Threshold

The circuit breaker monitors recent payment failures.

### Example Policy
- Open breaker after 3 consecutive failures
- Also open if response latency exceeds threshold repeatedly
- Track failures over a short rolling time window

This prevents the API from continuously sending traffic to a dependency that is already failing.

---

## 3.2 Open Duration

Once the breaker opens:
- Requests fail fast immediately
- No further payment calls are sent temporarily

### Example Cooldown
- Breaker remains open for 30 seconds
- After cooldown, system enters HALF-OPEN state
- Small number of test requests are allowed through

If the dependency recovers:
- Breaker closes normally

If failures continue:
- Breaker reopens immediately

This limits unnecessary pressure on the external provider and protects CityBite’s own infrastructure.

---

## 3.3 Fallback Behavior

When the breaker is open, CityBite can apply controlled fallback strategies.

### Possible Fallbacks

- Display clear “payments temporarily unavailable” message
- Allow “cash on delivery” or “pay later” option
- Queue unpaid orders for later retry
- Disable only affected payment methods

The fallback choice depends on business policy and fraud risk tolerance.

The key goal is graceful degradation instead of total system collapse.

---

## 4. Timeouts and Bulkheads

Circuit breakers work best when combined with timeouts and bulkheads.

---

## 4.1 Timeouts

Every external request should have a strict timeout.

### Example
- Payment API timeout: 2 seconds
- Maps API timeout: 1 second

Without timeouts:
- Threads remain blocked indefinitely
- Request queues grow uncontrollably
- System capacity collapses under load

Short timeouts reduce resource exhaustion during incidents.

---

## 4.2 Bulkhead Isolation

CityBite isolates dependency usage using separate thread pools or connection pools.

### Example
- Payment requests use dedicated worker pool
- Notification workers use separate queue consumers
- Maps API calls cannot consume all API threads

This prevents one failing dependency from starving unrelated services.

Bulkheads reduce blast radius during outages.

---

## 5. Canary Request Pattern

CityBite can use canary-style validation when deploying risky payment integrations.

### Example Use Case
Before routing all traffic to a new payment provider version:
1. Route a very small percentage of requests first
2. Monitor latency and failure metrics
3. Expand rollout gradually if healthy

If problems appear:
- Roll back quickly
- Limit customer impact

This reduces deployment risk for critical checkout workflows.

