# Part 2: Cascading Failures & Circuit Breaker
## Task 2.2: Cascading Failures & Circuit Breaker

## 1. Narrative: Payment Gateway Failure and Retry Storm

A common availability problem for CityBite is a payment gateway outage or a slow 500 response from the partner API. If the gateway starts failing, clients may automatically retry, and CityBite’s own API may also retry before returning an error. This creates a retry storm: every failed request produces even more downstream calls, which increases load on the Order API, fills worker queues, consumes DB connections, and makes the whole system slower. The result is cascading failure: one external dependency becomes unhealthy, but CityBite’s own API also degrades because it keeps spending capacity on doomed requests instead of protecting core checkout work. The lecture circuit-breaker example shows the key idea clearly: retries can multiply load on a sick dependency, while a breaker protects your own capacity by failing fast.  

---

## 2. Circuit Breaker Policy

### Thresholds
- Open the circuit after **3 consecutive failures** from the payment gateway.
- Consider timeouts as failures too, not only explicit 500 responses.
- Move to half-open after a cooldown period so one test request can check recovery.

### Open duration
- Keep the circuit **open for 30 to 60 seconds** as an initial policy.
- During this time, fail fast instead of sending more traffic to the gateway.

### Fallback
- If payment is unavailable, the API can:
  - return a clear “payment temporarily unavailable” response,
  - offer “pay later” only if the business flow allows it,
  - or queue the order in a pending-payment state if the product supports that workflow.
- The fallback must be explicit so the customer knows whether the order is confirmed or not.

A circuit breaker is not only a safety feature for the partner dependency; it is also a protection for CityBite’s own API, because it reduces wasted calls during an outage and prevents the retry loop from consuming all available capacity. This matches the lecture example where a breaker reduces pile-on when a downstream service is failing. fileciteturn4file1

---

## 3. Timeouts and Bulkheads

### Timeouts
Every call to the payment gateway should have a strict timeout, for example **800 ms to 1.5 s**, depending on the user experience target. Without timeouts, the API can hold threads or async slots too long while waiting for a partner that is already failing. Timeouts are important because they stop requests from hanging forever and turn a slow dependency into a fast, controlled failure.

### Bulkheads
CityBite should isolate dependencies with separate connection pools or thread pools. For example:
- one pool for payment gateway calls,
- one pool for database access,
- one pool for notification jobs.

Bulkheads prevent one bad dependency from consuming all workers in the Order API. They pair well with circuit breakers because the breaker stops repeated calls, while the bulkhead limits the damage from the calls that still get through. Together, they keep payment failures from starving database work or blocking unrelated customer requests.

---

## 4. Canary Request Use Case

A canary request is useful when CityBite introduces a risky change, such as a new worker that processes payment-adjacent events or a new parser for suspicious order payloads. In that case, send a small number of test requests to one worker or one pod first and watch the result before sending the full traffic stream. This helps detect failure early and limits blast radius.

One practical CityBite example is sending a suspicious or newly formatted payload to a single worker first after a release. If the worker handles it correctly, traffic can be expanded gradually. If not, the issue is contained to one small slice of the system instead of affecting every order job. This is a good fit for availability because it reduces the chance that a bad deployment causes a large outage.

---

## 5. Summary

CityBite must expect partner failures and design for containment. Retries alone can make the outage worse, so the system needs circuit breakers, timeouts, and bulkheads to stop amplification. Canary requests add another safety layer by limiting blast radius during risky changes. The main goal is to keep the Order API responsive even when a downstream dependency is unhealthy.
