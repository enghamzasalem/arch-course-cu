# Part 3.1 — Strangler & branch by abstraction (CityBite)

## First context to extract: **Payment Settlement**

**Risk:** Money correctness, PCI scope, PSP webhooks—highest blast radius if wrong.  
**Team:** Small dedicated **payments + risk** squad already handles on-call for PSP incidents.  
**Customer value:** Isolates **fraud rules and PSP upgrades** from restaurant peak deploys—fewer full-platform freezes.

## Strangler fig plan

| Phase | Action |
|-------|--------|
| **Facade** | Edge **API gateway** (or **BFF** for mobile) implements the **strangler fig** peel: routes `/v1/internal/payments/**` to **new Payment service**; all other traffic stays monolith until the next slice. |
| **Traffic ramp** | **5% → 25% → 100%** canary by `customer_id` hash; compare **error budget** on authorize latency vs monolith path. |
| **Rollback trigger** | PSP **5xx** > SLO, **checkout conversion** drop > 0.3 pp vs control, or **webhook signature** mismatch spike → flip gateway flag to **monolith adapter** in under 5 minutes. |

Dual-run: during migration the monolith still serves reads/writes through the **`PaymentPort`** adapter—implementation may call **legacy in-process** code or **HTTP** to the new service; **no dual-write** to two payment primaries without a reconciliation job.

## Branch by abstraction (before split)

Introduce **`PaymentPort`** with `authorize_payment` / `capture` as in **`OrderServiceLoose`** (`example1_flexibility_coupling_citybite.py`): production binds **`StripePaymentAdapter`**, tests use **`FakePayment`**, strangler phase binds **HTTP adapter** to new service. **Order domain** never imports `StripePaymentGateway` directly—extraction is a **wiring change**, not a rewrite.
