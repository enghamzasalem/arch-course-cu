## Task 2.2

### Retry Storm Narrative

When the payment gateway starts returning 500 errors, the Order API retries each failed request. With many customers checking out simultaneously, each retry multiplies the number of outbound calls. The gateway, already struggling, receives even more traffic, making recovery harder. Meanwhile, threads inside the Order API are all busy waiting on payment responses, so unrelated requests (menu browsing, order tracking) start queuing too. This is the amplification pattern described in `example1`: a single slow dependency holds connections open, and retries turn a partial outage into a full one.

### Circuit Breaker Policy

**Thresholds:** If more than 50% of payment gateway calls fail within a 30-second window (minimum 10 requests), the circuit opens.

**Open duration:** The circuit stays open for 60 seconds. During this time no payment calls are attempted, the fallback is used immediately.

**Fallback:** Customers see a clear message: "Payment is temporarily unavailable, your order has been saved. We will process it automatically within the next 10 minutes or you can retry." The order is written to the DB with status `PENDING_PAYMENT` and a worker retries payment once the circuit half-opens and the gateway recovers. This avoids data loss and gives customers a message of "we'll only take a moment", rather than a generic error or direct decline.

### Timeouts and Bulkhead

Every outbound call to the payment gateway has a hard timeout, if the gateway does not respond, the call fails fast rather than holding a thread. A bulkhead limits payment calls to a separate thread pool. Timeouts and bulkheads pair with the circuit breaker: timeouts ensure individual calls fail quickly so the breaker's failure count accumulates fast enough to open before threads are exhausted, and the bulkhead ensures one dependency cannot consume all available capacity while the breaker is opening.

### Canary Request

The pattern is most useful when you want to test a suspicious or novel payload against one worker before broadcasting it. For example, detecting malformed orders before they corrupt the DB. CityBite's payment calls are uniform HTTPS requests to an external vendor; there is no internal worker logic to canary. A more applicable use of the canary idea is deploying a new Order API version to one pod and routing a part of traffic to it before a full rollout.