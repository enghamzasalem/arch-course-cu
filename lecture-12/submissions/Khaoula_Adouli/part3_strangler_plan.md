# Part 3.1: Strangler / Branch by Abstraction — First Extraction Slice

## 1. Which context to extract first — **Billing & Payments**

**Justification**

| Lens | Reason |
|------|--------|
| **Risk** | Money bugs are high severity; extracting early forces **clear contracts** and audit boundaries—but volume is lower than catalog reads, so blast radius is manageable with feature flags. |
| **Team** | Small team: one “platform/payments” owner can own the adapter boundary while others keep monolith features. |
| **Customer value** | Faster PCI scope reduction, safer key rotation, independent PSP migration (Stripe → multi-PSP) without rewiring all order code at once. |

---

## 2. Strangler plan (incremental, not big-bang)

**Facade / routing**

- Introduce an **API gateway route** or **BFF** endpoint `/checkout` that internally calls either:
  - **legacy in-process** payment path, or
  - **new Billing service** HTTP adapter.

**Traffic ramp**

- Week 1: **1%** canary (internal + beta users).
- Week 2–4: ramp **10% → 50% → 100%** if error budget and p95 latency stay green.

**Rollback trigger**

- Automatic rollback if: payment capture error rate > baseline + threshold, charge volume mismatch alerts, or idempotency collisions spike.

---

## 3. Branch by abstraction (before split) — tie to `example1`

In the monolith, replace `OrderServiceTight` (direct `StripePaymentGateway`) with **`OrderServiceLoose`** pattern:

- Introduce **`PaymentPort`** (`authorize_payment`, `capture`, `refund`) in core Ordering code.
- Behind the port:
  - **Adapter A:** in-process Stripe (today).
  - **Adapter B:** HTTP client to Billing microservice (strangled slice).

This is **branch by abstraction**: the **interface exists before** the network boundary; extraction becomes a **wiring change**, not a rewrite.

---

## Flexibility mechanisms & explicit trade-off (assignment requirement recap)

**Mechanisms used here:** strangler fig + branch by abstraction + **database per service** (later) + **saga** for paid order + **contract tests** at the port boundary.

**Trade-off:** **Flexibility vs operational cost** — more services and adapters increase **deployments, monitoring, and incident complexity**; we buy **independent evolution** of payments and safer scaling of sensitive workloads.

---

## Assignment checklist — four flexibility mechanisms (named)

1. **Strangler fig / facade routing** — gradual traffic shift to Billing service behind gateway/BFF.  
2. **Branch by abstraction** — `PaymentPort` + adapters in the monolith before the network split (`example1`).  
3. **Database per service** (paper) — separate logical schemas; no cross-context SQL joins (`part2_database_per_service.md`).  
4. **Saga** — orchestrated place-paid-order with compensations (`part2_saga_sketch.md`).  
5. **Consumer-driven contracts** — mobile fixtures gate API evolution (`part2_api_evolution.md`).
