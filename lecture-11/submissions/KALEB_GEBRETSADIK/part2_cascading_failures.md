# Part 2.2: Cascading Failures & Circuit Breaker

**Narrative: Amplification & Containment:** 
When the payment gateway starts returning 500s or slows down, CityBite's HTTP threads block waiting for responses. Frustrated users refresh their app, sending duplicate requests (a retry storm). This amplifies the load, exhausting CityBite's threads and DB connection pools. The localized failure in the payment gateway cascades, bringing down the entire CityBite API for all users, even those just trying to browse the menu.

**Circuit Breaker Policy (Payment Gateway):**
- **Thresholds:** Open if 50% of requests fail or timeout within a 10-second rolling window (min 20 requests).
- **Open Duration:** Keep open for 30 seconds to give the gateway time to recover before attempting a half-open probe.
- **Fallback:** Queue the order with a "Payment Pending" state. Notify the user we received their order and will process payment in the background, preventing a total checkout failure.

**Timeouts & Bulkheads:**
- **Timeouts** prevent threads from blocking infinitely. They pair with breakers because timeout exceptions count towards the breaker's failure threshold.
- **Bulkheads** (e.g., dedicated thread pools per dependency) ensure a slow payment gateway only exhausts payment threads, leaving threads available to serve menu and routing requests.

**Canary Request:**
When deploying a new, complex order-pricing worker, we use a canary request pattern by routing 5% of incoming calculate-price requests to the new worker. If the new worker crashes on a suspicious payload, only 5% of traffic is impacted, containing the blast radius before full rollout.
