# Part 3.1: Strangler / Branch by Abstraction Plan

## Context to Extract First: Payment

**Justification:**
- **Risk:** Medium. Payment is well-bounded — it has a clear input (charge request) and output (authorization result). It does not require knowledge of menu items, drivers, or routes.
- **Team value:** Isolating Payment lets a dedicated team own PCI-DSS compliance, swap payment gateways, and add new payment methods (wallets, BNPL) without touching order logic.
- **Customer value:** Payment reliability directly drives checkout conversion. Extracting it allows independent scaling and faster circuit breaker responses (Lecture 11).

---

## Strangler Plan

**Step 1 — Introduce a Facade (API Gateway route split):**
Add a route rule at the API Gateway (or K8s Ingress) level: all requests to `/payments/*` are proxied to the new Payment service while all other routes continue to hit the monolith. The monolith's internal payment code still runs in parallel initially.

**Step 2 — Traffic % ramp:**
Start at 5% of `/checkout` flows routed to the new Payment service. Monitor error rate, latency p99, and refund reconciliation. Increase to 25%, 50%, 100% over 2-week increments.

**Rollback trigger:**
If the new service's error rate exceeds the monolith's baseline by more than 1% for 5 consecutive minutes, the gateway rule flips back 100% to the monolith path automatically (feature flag).

---

## Branch by Abstraction

Following `example1_flexibility_coupling_citybite.py`:

Before any extraction, introduce a `PaymentPort` interface inside the monolith. `OrderService` is refactored to depend only on `PaymentPort.authorize_payment(cents, customer_ref)` — not on `StripePaymentGateway` directly. Initially, a `LocalPaymentAdapter` wraps the existing monolith payment code and satisfies the interface.

When the new Payment microservice is ready, a `HttpPaymentAdapter` implementing `PaymentPort` replaces `LocalPaymentAdapter` — injected via configuration. No change to `OrderService`. This is the branch by abstraction: the interface was the seam, the adapter swap is the migration step.
