# Part 3 — Strangler / Branch by Abstraction (CityBite)

## 1. Overview

CityBite should avoid a risky “big bang” migration from monolith to microservices. Rewriting everything at once would increase delivery risk, slow feature development, and create operational instability.

Instead, CityBite can evolve gradually using:
- **Strangler pattern**
- **Branch by abstraction**
- Incremental traffic migration

This approach allows the platform to improve flexibility while keeping the system operational during the transition.

---

# 2. First Context to Extract — Payments

## Why Payments Is the Best First Candidate

CityBite chooses the **Payments context** as the first extraction target.

---

## Reasons

### 1. Clear Business Boundary

Payments already has a well-defined responsibility:
- Authorization
- Capture
- Refunds
- Gateway integration

This makes it easier to separate cleanly from the monolith.

---

### 2. External Dependency Isolation

Payments depends heavily on third-party gateways. Isolating this logic reduces the risk that payment outages impact unrelated parts of the system.

---

### 3. Security and Compliance

Payment systems often require:
- Stronger auditing
- Access controls
- Specialized monitoring

Separating Payments improves operational control and future compliance readiness.

---

### 4. Customer Impact

Improving payment reliability directly improves:
- Checkout success rate
- Revenue protection
- Customer trust

This gives the migration clear business value.

---

# 3. Strangler Migration Plan

## Step 1 — Introduce a Facade Layer

Before extracting Payments, CityBite introduces a stable internal interface inside the monolith.

Example abstraction:
```python
class PaymentPort:
    def authorize_payment(...)
```

The rest of the system communicates through this abstraction instead of directly calling Stripe SDK code.

This follows the same idea shown in the lecture example using ports and adapters.

---

## Step 2 — Route Through Gateway / Facade

Initially:
- All payment requests still go to the monolith implementation

Later:
- Some requests are routed to the new Payments service

This allows gradual migration without changing checkout logic everywhere.

---

# 4. Traffic Ramp Strategy

CityBite gradually increases traffic to the new Payments service.

---

## Example Rollout

| Phase | Traffic Routed to New Service |
|---|---|
| Phase 1 | 5% |
| Phase 2 | 25% |
| Phase 3 | 50% |
| Phase 4 | 100% |

During rollout:
- Metrics are monitored continuously
- Error rates are compared against baseline
- Rollback remains possible at every stage

---

# 5. Rollback Trigger

CityBite immediately rolls back traffic if:
- Payment success rate drops significantly
- Gateway latency spikes
- Error rates exceed thresholds
- Duplicate charges are detected

Because the old monolith implementation still exists behind the abstraction layer, rollback can happen quickly without redeploying the entire system.

---

# 6. Branch by Abstraction

## Purpose

Branch by abstraction allows teams to change implementations gradually without rewriting all callers immediately.

---

## Abstraction Introduced

```python
class PaymentPort:
    def authorize_payment(...)
```

---

## Old Implementation

```python
StripePaymentAdapter
```

---

## New Implementation

```python
RemotePaymentServiceAdapter
```

The Ordering system depends only on the abstraction (`PaymentPort`) rather than concrete gateway code.

This means:
- New implementations can be swapped safely
- Testing becomes easier
- Migration risk decreases

---

# 7. Why This Approach Is Safer

A gradual extraction strategy provides several advantages:

- Lower operational risk
- Easier rollback
- Incremental learning
- Reduced downtime risk
- Safer team coordination

Instead of freezing development for a full rewrite, CityBite can continue shipping features while modernizing the architecture step by step.

---

# 8. Key Trade-off

Improving flexibility introduces additional complexity:
- More network communication
- More monitoring requirements
- Higher operational overhead
- Eventual consistency challenges

CityBite accepts this trade-off because long-term team scalability and independent service evolution become increasingly important as the platform grows.

