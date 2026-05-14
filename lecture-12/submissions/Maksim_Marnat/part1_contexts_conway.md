# Part 1.1 — Bounded contexts & Conway (CityBite)

## Continuity with Lectures 9–11

CityBite already runs on **Kubernetes + managed Postgres** (Lecture 9): services are **deployable units**, not yet autonomous **data** domains. Lecture **10** (scalability) implies checkout and kitchen peaks differ—**async boundaries** reduce useless horizontal scale of the whole DB. Lecture **11** (availability: SLOs, circuit breakers, readiness vs shallow health) is why we keep **sync** money on a short path with **timeouts/bulkheads**, while **kitchen/dispatch** tolerate **eventual** projections. **SMS/push** (Lecture 11 “services map”) remain **external SaaS** behind **ports/adapters**, not a separate bounded context in this slice.

## Flexibility / modifiability — quality & change drivers

**Flexibility** here means **safe evolution** under change: new PSP, new market regulations, mobile release cadence, and restaurant POS integrations. **Concrete drivers** forcing seams: (1) **shared schema** contention between payments and operations teams; (2) **silent JSON** drift breaking apps (baseline pain); (3) **independent deploy** desire for PSP adapter changes; (4) **audit** and reconciliation workloads isolating finance rules.

## Bounded contexts (four)

### 1. Order & Checkout

| Field | Content |
|--------|---------|
| **Ubiquitous language** | *shopping cart*, *checkout session*, *order id*, *promised delivery window*, *cart freeze* |
| **Primary user** | End customer (mobile / web) |
| **Owns** | Cart state, checkout orchestration, correlation ids, **read models** of order status for the customer UI (not financial truth). |

### 2. Payment Settlement

| Field | Content |
|--------|---------|
| **Ubiquitous language** | *authorization*, *capture*, *idempotency key*, *webhook signature*, *chargeback window* |
| **Primary user** | Customer (payer); Finance / Risk (internal) |
| **Owns** | Ledger of payment intents/outcomes, PSP correlation, reconciliation exports, refund policy state. |

### 3. Restaurant Fulfillment

| Field | Content |
|--------|---------|
| **Ubiquitous language** | *kitchen ticket*, *prep queue*, *order accepted*, *ready for pickup*, *prep SLA* |
| **Primary user** | Restaurant operator / kitchen display |
| **Owns** | Acceptance/rejection, prep timestamps, capacity throttling per site—not courier assignment. |

### 4. Dispatch & Delivery

| Field | Content |
|--------|---------|
| **Ubiquitous language** | *assignment*, *route manifest*, *courier slot*, *proof of delivery*, *ETA revision* |
| **Primary user** | Courier app; dispatch coordinator |
| **Owns** | Live location stream, assignment decisions, delivery completion events—not payment capture. |

---

## Adjacent pairs — integration style & rationale

Topology: **Order** sits between customer money flow and operations; edges **Order↔Payment**, **Order↔Restaurant**, **Restaurant↔Dispatch**, **Dispatch↔Order** (status projection).

| Adjacent pair | Style | Why |
|---------------|--------|-----|
| **Order & Checkout** ↔ **Payment Settlement** | **Synchronous HTTPS** (internal call today; service call tomorrow) | Customer expects an immediate **authorize/capture** outcome before the UI confirms “paid”; choreography-only money flow would worsen UX and fraud windows. |
| **Order & Checkout** ↔ **Restaurant Fulfillment** | **Async domain event** (e.g. `OrderPlacedForKitchen`) | Restaurant needs **at-least-once** intake; peak lunch decouples checkout spikes from kitchen DB; retries must not double-charge—money stays in Payment context. |
| **Restaurant Fulfillment** ↔ **Dispatch & Delivery** | **Async event** (`ReadyForPickup` / `HandoffToCourier`) | Dispatch optimizes globally; kitchen should not block on routing APIs or map latency. |
| **Dispatch & Delivery** ↔ **Order & Checkout** | **Async event** + **CQRS read path** (`DeliveryCompleted` → customer projection) | Customer timeline updates are **eventual**; no tight sync loop from courier GPS into checkout DB. |

**Batch (assignment integration type):** PSP **settlement / reconciliation** files and tax exports are loaded into **Payment Settlement** on a **schedule** (batch ETL), not during synchronous checkout—heavy, idempotent, tolerant of delay.

---

## Conway’s Law (one team)

If **one** product team owns all four contexts, Conway predicts a **modular monolith** (clear packages/modules, shared release) or a **distributed monolith** if management insists on separate deployables without true data/API autonomy. Practically: **one schema** and **shared ORM** persist; boundaries live as **namespaces and ports** (`PaymentPort` in `example1_flexibility_coupling_citybite.py`) but **deployment stays single** until headcount and on-call pain justify real service splits.

## Monolith vs modular monolith vs microservices (today’s team size)

For a **small platform team** (≤ ~8 engineers) with **one** on-call rotation, the economically rational default is a **modular monolith**: **one deploy**, **ports/adapters** (`example1`), **additive APIs** (`example2`), and **feature flags**—maximum throughput per person. **Microservices** pay off only when **cognitive load**, **release frequency**, or **compliance isolation** (e.g. payments) force **separate deploy + separate data** with dedicated owners; until then, premature splitting recreates a **distributed monolith** (Part 1.2).

---

## Flexibility mechanisms & trade-off (assignment baseline)

**Named flexibility mechanisms (≥4 required; we use five):** (1) **bounded contexts** and explicit integration choices; (2) **database per service** (Part 2.1); (3) **saga** with compensations (Part 2.3); (4) **strangler fig** + **branch by abstraction** (Part 3); (5) **consumer-driven contract tests** (Part 2.2; mitigation in Part 1.2).

**Trade-off:** **Flexibility vs operational cost and (weaker) read consistency** — autonomous stores and pipelines shorten time-to-change per team but increase **on-call** and **eventual** customer projections (vs one big join); we accept that cost for **deploy and schema autonomy**.
