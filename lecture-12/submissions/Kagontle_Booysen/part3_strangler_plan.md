# Part 3 — Task 3.1: Strangler / Branch by Abstraction

---

## Context Chosen for First Extraction: Payment

### Justification

**Risk profile — highest isolation, clearest boundary.**
Payment is the context most frequently named in CityBite's baseline pain: "risky 'extract payment' debates." Paradoxically, this makes it the *right* first extraction target, not a reason to avoid it. Payment already has the clearest business boundary of any context — it owns authorisations, captures, and refunds and nothing else touches those concepts meaningfully. Its schema surface is small (six tables, identified in Task 2.1) compared to, say, Ordering, which owns the order lifecycle state machine that every other context indirectly depends on. Extracting Payment leaves the Ordering state machine intact; extracting Ordering first would destabilise everything that listens to order events.

**Team fit — Finance team already owns this domain.**
The Finance team is already responsible for reconciliation, chargeback handling, and gateway contract management. They have a natural motivation to own the Payment service's deployment pipeline and on-call rotation independently. Conway's Law (Task 1.1) works here: giving Finance an autonomous service boundary reinforces — rather than fights — the communication structure that already exists.

**Customer value — enables gateway switching.**
The `PaymentPort` abstraction in `example1_flexibility_coupling_citybite.py` was introduced precisely to make `OrderServiceLoose` independent of the Stripe SDK. Once Payment is extracted, the Finance team can swap the gateway adapter (Stripe → Adyen, Adyen → in-house acquiring) without touching the Ordering codebase, without a multi-team release window, and without risking the order state machine. This is a direct, observable business capability that management can fund.

**Risk floor — auth is sync, compensation is defined.**
Because the Ordering → Payment call is synchronous (established in Task 1.1 and the saga in Task 2.3), the extraction does not require an async event migration at the same time. The interface is already a request/reply HTTP call from Ordering's perspective. The saga's `PaymentPort` already exists as an abstraction in the monolith — we are not inventing new structure; we are promoting an existing internal boundary to a network boundary.

---

## Strangler Plan

### Phase 0 — Branch by Abstraction (in the monolith, before any split)

Before any network call is introduced, the internal `PaymentPort` interface in the monolith is hardened:

```
PaymentPort (interface)
    ↑
    ├── StripePaymentAdapter      (existing — wraps Stripe SDK)
    └── HttpPaymentAdapter        (new — wraps HTTP call to future Payment service)
```

The `HttpPaymentAdapter` is written, unit-tested, and merged to main but **not activated** — the dependency injection container continues to wire `StripePaymentAdapter`. This is the branch by abstraction step: the seam exists in the codebase, no traffic crosses it yet, and a rollback is a single DI configuration change. See Section 3 for full detail.

---

### Phase 1 — Introduce the Facade (API Gateway Route Split)

A **route split at the existing Kubernetes ingress / API gateway** is the facade mechanism. The Payment service is deployed as a new K8s Deployment alongside the monolith — it runs the same `StripePaymentAdapter` logic, backed by its own separate Postgres instance (the `payment` schema migrated from the shared DB per Task 2.1).

```
Ingress
  /v1/internal/payment/*  →  [monolith]          (100% initially)
  /v2/internal/payment/*  →  [payment-service]   (0% initially)
```

The monolith's `OrderService` continues to call its local `StripePaymentAdapter`. The Payment service is deployed, health-checked, and reconciled against the gateway's real transaction history — but carries no live traffic.

**Why ingress route split rather than BFF or application-level feature flag:**
- An ingress route split is observable in access logs without instrumentation changes — every request has a URL that shows which backend handled it.
- It does not require the monolith to gain knowledge of the new service's existence before the traffic shift. The monolith's DI wiring is unchanged during Phase 1.
- A BFF would introduce an additional network hop and a new service to maintain. For an internal service-to-service call (Ordering calls Payment), the overhead is not justified.

---

### Phase 2 — Traffic Ramp (Canary by Order Volume)

Traffic is shifted by switching the Ordering service's DI wiring from `StripePaymentAdapter` to `HttpPaymentAdapter` for a percentage of orders, controlled by a **feature flag** evaluated per request:

```
feature_flag: payment_service_canary
  → 5%   of orders  →  HttpPaymentAdapter  →  Payment service (new)
  → 95%  of orders  →  StripePaymentAdapter →  monolith Payment module (old)
```

The feature flag is evaluated at the `PaymentPort` injection site, not inside business logic — the `OrderService` remains unmodified and unaware of the routing decision. This is the direct payoff of the `OrderServiceLoose` pattern from `example1`: swapping the adapter behind the port requires no change to `checkout()`.

**Ramp schedule:**

| Week | Canary % | Criterion to advance |
|---|---|---|
| 1 | 5% | Zero payment discrepancies in Finance reconciliation; P99 latency ≤ 1.5× monolith baseline |
| 2 | 25% | Same criteria; error rate on `/v2/internal/payment/*` ≤ monolith error rate |
| 3 | 50% | Same criteria; no saga compensation triggered by Payment service errors |
| 4 | 100% | Monolith Payment module becomes read-only; Finance team owns deployment |
| Week 6 | — | Monolith Payment module code deleted; shared schema tables dropped |

**Why order volume rather than user cohort:**
Payment is stateless per-transaction (each authorisation is independent). Routing 5% of *orders* (not 5% of *users*) to the new service avoids a situation where a user's partial order history is split across two backends, which would complicate the Finance reconciliation read model.

---

### Phase 3 — Rollback Triggers

A rollback is defined as: flip the feature flag canary percentage back to 0%, which routes all new `authorize_payment` calls back through the monolith's `StripePaymentAdapter`. Because the saga (Task 2.3) commits payment state locally in the Payment service's own Postgres before replying to Ordering, in-flight authorisations at rollback time are not lost — the Finance team's post-deployment reconciliation job (referenced in Task 2.1 RPO section) can re-apply any webhook events that arrived during the rollback window.

**Automatic rollback triggers (monitored by the ingress / service mesh):**

| Signal | Threshold | Action |
|---|---|---|
| Payment service HTTP error rate | > 1% of authorisation requests over 5-minute window | Flag to 0%; PagerDuty alert to Finance on-call |
| P99 latency on `/v2/internal/payment/*` | > 3× monolith P99 for two consecutive 1-minute windows | Flag to 0%; alert |
| Saga compensation rate | > 0.1% of orders trigger VoidAuthorisation due to Payment error | Flag to 0%; manual investigation required before re-ramp |
| Finance reconciliation mismatch | Any gateway-vs-DB discrepancy in the 15-minute reconciliation window | Flag to 0%; Finance team escalation |

**Why these four signals and not just "5xx rate":**
A payment gateway may return a syntactically valid 200 response containing a soft decline — the saga handles this correctly, but the Finance reconciliation will catch a mismatch between the gateway ledger and the `payment_intents` table if the adapter serialises the response incorrectly. HTTP error rate alone would miss this class of failure.

---

## Branch by Abstraction — Interface in the Monolith

### The Existing Seam (from example1)

`example1_flexibility_coupling_citybite.py` already defines the exact port/adapter structure needed:

```python
class PaymentPort(Protocol):
    def authorize_payment(self, cents: int, customer_ref: str) -> str: ...

class StripePaymentAdapter:          # existing: wraps Stripe SDK
    def authorize_payment(self, ...) -> str: ...

class OrderServiceLoose:
    payments: PaymentPort            # depends only on the protocol
    def checkout(self, ...) -> str:
        return self.payments.authorize_payment(...)
```

The `OrderServiceTight` antipattern — where `OrderService` holds a concrete `StripePaymentGateway` instance — is what the monolith currently looks like internally. The branch-by-abstraction migration has three concrete steps inside the monolith codebase, all completed *before* any network call is introduced:

### Step A — Introduce `PaymentPort` Protocol

The `PaymentPort` Protocol (already illustrated in `example1`) is declared in the Ordering module. This is a pure code change — no behaviour changes, no deployment needed.

```python
# ordering/ports.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class PaymentPort(Protocol):
    def authorize_payment(self, cents: int, customer_ref: str) -> str: ...
    def void_authorisation(self, auth_token: str) -> None: ...
    def capture(self, auth_token: str, cents: int) -> str: ...
```

Note that `void_authorisation` and `capture` are added to the port — the saga's compensation step (Task 2.3 Step 2) requires these operations, and defining them now means the `HttpPaymentAdapter` will implement the full saga contract from day one.

### Step B — Wrap `StripePaymentGateway` Behind `StripePaymentAdapter`

The existing tight coupling in `OrderServiceTight` is refactored to `OrderServiceLoose`. The `StripePaymentGateway` SDK calls are moved inside `StripePaymentAdapter`, which implements `PaymentPort`. This is the exact transformation shown in `example1`. No behaviour change; this commit is deployable in isolation.

```python
# ordering/adapters/stripe_adapter.py
class StripePaymentAdapter:
    def __init__(self, inner: StripePaymentGateway) -> None:
        self._inner = inner
    def authorize_payment(self, cents: int, customer_ref: str) -> str:
        return self._inner.charge_card(cents, customer_ref)
    def void_authorisation(self, auth_token: str) -> None:
        self._inner.void(auth_token)
    def capture(self, auth_token: str, cents: int) -> str:
        return self._inner.capture(auth_token, cents)
```

### Step C — Write `HttpPaymentAdapter` (dark-launched, not activated)

The `HttpPaymentAdapter` implements `PaymentPort` by calling the Payment service's HTTP API. It is merged to main and deployed with the monolith but **the DI container wires `StripePaymentAdapter` exclusively** — `HttpPaymentAdapter` is not in the active object graph.

```python
# ordering/adapters/http_payment_adapter.py
import httpx

class HttpPaymentAdapter:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
    def authorize_payment(self, cents: int, customer_ref: str) -> str:
        resp = httpx.post(f"{self._base_url}/authorise",
                          json={"cents": cents, "customerRef": customer_ref},
                          timeout=5.0)
        resp.raise_for_status()
        return resp.json()["authToken"]
    def void_authorisation(self, auth_token: str) -> None:
        httpx.post(f"{self._base_url}/void/{auth_token}", timeout=5.0).raise_for_status()
    def capture(self, auth_token: str, cents: int) -> str:
        resp = httpx.post(f"{self._base_url}/capture",
                          json={"authToken": auth_token, "cents": cents},
                          timeout=5.0)
        resp.raise_for_status()
        return resp.json()["captureRef"]
```

**Why this is safe to merge dark:**
`OrderServiceLoose` only holds a reference to `PaymentPort`. The DI container decides at startup which concrete adapter to inject. `HttpPaymentAdapter` has no effect on production traffic until the feature flag routes a request to it. The `FakePayment` adapter used in CI tests (illustrated in `example1`'s flexibility lesson) continues to work unchanged — it also satisfies `PaymentPort`.

### Activation (Phase 2 of Strangler Plan)

When the canary feature flag fires for a given order:

```python
# ordering/container.py
def build_payment_adapter(config, flag_client) -> PaymentPort:
    if flag_client.is_enabled("payment_service_canary"):
        return HttpPaymentAdapter(config.payment_service_url)
    return StripePaymentAdapter(StripePaymentGateway(config.stripe_api_key))
```

The `OrderService.checkout()` method is never touched. It calls `self.payments.authorize_payment(cents, customer_ref)` — identical whether the adapter is in-process or over the network. This is the flexibility lesson from `example1` made operational.

---

## Migration Checklist Summary

| Phase | Action | Rollback |
|---|---|---|
| Branch by abstraction | Introduce `PaymentPort`, refactor to `StripePaymentAdapter`, merge dark `HttpPaymentAdapter` | Delete new files; no behaviour changed |
| Phase 1 — Facade | Deploy Payment service; add ingress route; run reconciliation in shadow | Undeploy Payment service K8s resources; remove ingress route |
| Phase 2 — Ramp | Activate feature flag at 5%; ramp weekly per criteria | Set feature flag to 0%; automatic via monitoring trigger |
| Phase 3 — Cutover | 100% canary; monolith Payment module read-only; delete module at Week 6 | Not applicable — full extraction complete |

---

*Vocabulary aligned with Lecture 12 (strangler fig, branch by abstraction, facade, canary deployment), example1_flexibility_coupling_citybite.py (PaymentPort, StripePaymentAdapter, OrderServiceLoose vs OrderServiceTight, FakePayment), Lecture 9 (K8s deployment, Postgres baseline), Lecture 11 (availability — rollback triggers reference circuit breaker thresholds).*
