# Task 3.1: Strangler / branch by abstraction

## Context to Extract First: Payment

### Justification

**Risk:** Payment is a well-defined, narrow context with a clear boundary — it receives a charge request and returns a success or failure. It has fewer inbound callers than Ordering (only the checkout flow) and its data model is relatively small. This makes it the lowest-risk first extraction compared to, say, Ordering (which is the core of the system and touches everything).

**Team:** A dedicated Payment team already exists (or can be formed) because payment compliance (PCI-DSS) creates a natural organisational boundary. Isolating payment code into its own service also reduces the PCI audit scope for the rest of the monolith — a strong business incentive.

**Customer value:** Extracting Payment allows the team to swap or add payment providers (e.g. add Adyen alongside Stripe) without touching the Ordering codebase. It also enables independent scaling of the payment processing path during peak checkout periods, directly improving the availability story from Lecture 11.

---

## Strangler Plan

### Step 1: Introduce the Facade (API Gateway / Route Split)

Before any code is extracted, a **facade** is placed in front of the monolith. In CityBite's case this is the existing Kubernetes Ingress + a lightweight API Gateway (e.g. Kong or AWS API Gateway). The gateway routes all traffic to the monolith initially:

```
POST /internal/payments/charge  →  100% → Monolith (existing PaymentService class)
```

No behaviour changes yet. The facade is purely a routing layer.

### Step 2: Build the Payment Microservice in Parallel

The new Payment service is built as a standalone K8s Deployment with its own Postgres schema. It exposes the same internal API contract:

```
POST /internal/payments/charge
Body: { "order_id": "...", "cents": 1850, "customer_ref": "cus_abc" }
Response: { "transaction_id": "txn_...", "status": "succeeded" }
```

The new service is deployed but receives 0% of traffic. It is tested via integration tests and the consumer-driven contract tests (Pact) that the Ordering context already publishes.

### Step 3: Traffic % Ramp

| Phase | Traffic to new service | Trigger to advance |
|-------|------------------------|-------------------|
| Canary | 1% | Zero errors over 30 minutes |
| Early | 10% | Error rate < 0.1% over 24 hours |
| Majority | 50% | Error rate < 0.1% over 48 hours; latency p99 ≤ monolith |
| Full | 100% | Stable for 1 week |

Both the monolith's payment path and the new service run simultaneously during the ramp. Responses are compared (shadow mode) during the canary phase to catch subtle behavioural differences.

### Rollback Trigger

The gateway rolls back to 100% monolith automatically if any of the following are observed:
- Payment error rate exceeds **0.5%** over a 5-minute window (alert from Lecture 11 monitoring)
- p99 latency of `POST /charge` exceeds **3 seconds**
- Circuit breaker on the new Payment service opens (Lecture 11 pattern)

Rollback is a single gateway config change — no code deployment required.

### Step 4: Decommission the Monolith Payment Path

Once the new service handles 100% of traffic stably for one week, the payment code in the monolith is deleted and the Postgres payment tables are migrated to the new service's schema. The monolith's `PaymentService` class is removed.

---

## Branch by Abstraction — Interface in the Monolith Before Split

This is where `example1_flexibility_coupling_citybite.py` is directly applicable.

**Current state (tight coupling):**

```python
class OrderServiceTight:
    def __init__(self):
        self._gw = StripePaymentGateway()  # concrete dependency

    def checkout(self, cents, stripe_customer_id):
        return self._gw.charge_card(cents, stripe_customer_id)
```

**Step 1 — Introduce the `PaymentPort` interface** (branch by abstraction):

```python
class PaymentPort(Protocol):
    def authorize_payment(self, cents: int, customer_ref: str) -> str: ...
```

`OrderServiceLoose` (from `example1`) already depends on `PaymentPort`, not on `StripePaymentGateway` directly. This is the interface introduced **inside the monolith before any extraction happens**.

**Step 2 — Add an HTTP adapter** that calls the new Payment microservice:

```python
class HttpPaymentAdapter:
    def __init__(self, base_url: str):
        self._url = base_url

    def authorize_payment(self, cents: int, customer_ref: str) -> str:
        response = requests.post(f"{self._url}/charge",
                                 json={"cents": cents, "customer_ref": customer_ref})
        response.raise_for_status()
        return response.json()["transaction_id"]
```

**Step 3 — Wire by feature flag:**

```python
if settings.USE_PAYMENT_MICROSERVICE:
    payments = HttpPaymentAdapter(settings.PAYMENT_SERVICE_URL)
else:
    payments = StripePaymentAdapter(StripePaymentGateway())

order_service = OrderServiceLoose(payments=payments)
```

The monolith now has two implementations of `PaymentPort` behind a feature flag. The traffic ramp in the strangler plan is controlled by this flag (or by the gateway). At no point is there a big-bang cutover — the abstraction allows the two implementations to coexist safely until the migration is complete.
