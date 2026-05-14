# Task 3.1 - Strangler / branch by abstraction

## Which context to extract first

**Choice: Payments.**

### Justification

**Risk.** This is not the lowest-risk first extraction (Notifications would be safer), but I choose it because the boundary is clean - Payments already talks to an external gateway through a narrow interface, so the seam is easy to draw - and the payoff is high. Starting here also forces us to take strangler and rollback seriously from day one, which sets the right discipline before we attempt other extractions.

**Team.** Payments work tends to be owned by a small group of people who already deal with the gateway, refunds, and finance reporting. There is a natural team that can own the new service without reshuffling everyone else.

**Customer value.** Adding a new payment method, plugging in a fallback gateway, or reacting to a fee change today means touching the monolith and going through one shared release train. Once Payments is its own service, those changes ship without coordinating with Orders or Dispatch teams - direct customer value in the form of faster reaction time and lower checkout failure risk.

The other contexts come later: Notifications is a safer first step in pure risk terms but the value is low; Dispatch is heavily coupled to the maps / routing API; Orders is the core and should be extracted last, once we have learned from the others.

## Branch by abstraction (phase 1, inside the monolith)

Before any traffic moves to a new service, we change the monolith first. Inside the monolith we introduce an interface for payments - the same shape as the `PaymentPort` protocol used in the coupling example: one method like `authorize_payment(cents, customer_ref) -> reference`, with the existing gateway code wrapped in an adapter that implements it. `OrderService` (and any other caller) now depends only on `PaymentPort`, not on the concrete gateway class.

Once that interface exists, we add a second adapter behind it:

- `InProcessPaymentAdapter` - the current code, calling the gateway directly from inside the monolith.
- `HttpPaymentAdapter` - calls the new Payments service over HTTP.

Both adapters live in `main` at the same time. No long-lived feature branch. Which one is wired in is decided by configuration at runtime.

The key dependency rule: the rest of the monolith depends on `PaymentPort`, not on any concrete adapter or gateway SDK. If anyone reaches around the interface to call the old gateway class directly, extraction is blocked until that import is removed.

## Strangler plan (phase 2, ramping traffic to the new service)

### Facade

The facade is the `PaymentPort` interface itself. Callers do not know whether a payment call ends in the old in-process code or in an HTTP call to the new service. The decision is made by configuration inside the monolith, per call, based on a feature flag.

### Traffic ramp

We do not flip 100% on day one. We move in stages and watch metrics at each stage before the next:

1. 1% of payment calls go to `HttpPaymentAdapter` (the rest stay on `InProcessPaymentAdapter`). Enough to prove that authorization and refund work end to end on real traffic.
2. 10% - enough to see error rate and latency clearly.
3. 50% - the new service now handles half of all payments; we are confident in capacity and on-call.
4. 100% - the in-process adapter is no longer called.

After 100% stays clean for a while, the old code path is deleted. The `PaymentPort` interface stays - it is now permanent architecture.

### Rollback trigger

Rollback is a one-line config change: flip the feature flag back to `InProcessPaymentAdapter`. The triggers are kept explicit and small:

- payment authorization error rate on the new service goes above the baseline by a clear margin
- p95 latency on `authorize_payment` goes clearly above the baseline
- unexpected mismatch between the new service's records and the monolith's records during periodic reconciliation checks (run as a background job, no double calls to the gateway)

If any of these fires, we flip the flag back to the in-process path and investigate. No "we will fix it forward under load" - the point of the ramp is exactly to make rollback boring.