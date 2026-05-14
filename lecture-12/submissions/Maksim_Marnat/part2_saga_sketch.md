# Part 2.3 — Saga sketch: “place paid order” (CityBite)

**Journey:** Customer pays → order accepted for kitchen → payment captured (or reversed).

**No distributed 2PC:** each step commits **locally** in one database; global outcome is **sagas + compensations** only—no two-phase commit across Postgres instances (per assignment: avoid “2PC fantasy”).

**Style choice: orchestration** — a dedicated **CheckoutOrchestrator** (later extractable) issues commands and tracks saga state; contexts do **not** implicitly infer global state from peer events alone. **Durability:** saga step state + outbound commands use an **outbox** (or idempotent command ids) so retries after crashes do not **double-capture** or **double-place** orders.

| Step | Context | Local action | On later failure — compensation |
|------|---------|--------------|----------------------------------|
| 1 | Order & Checkout | Create `checkout_sessions` row `PENDING_PAY` | Delete / expire session |
| 2 | Payment Settlement | **Authorize** via PSP; store `payment_intents` `AUTHORIZED` | **Void authorization** |
| 3 | Order & Checkout | Insert `orders` + lines `PLACED`; emit `OrderPlaced` | Mark order `CANCELLED`; emit `OrderCancelled` |
| 4 | Restaurant Fulfillment | Consume `OrderPlaced`; enqueue **kitchen ticket** | **Stop ticket** / mark `VOID` if kitchen never started |
| 5 | Payment Settlement | **Capture** when kitchen accepts (or T+ policy) | **Refund / reverse capture** per PSP rules |

**Choreography vs orchestration — chosen: orchestration**

**Pros (two):**

1. **Single place** for timeouts, idempotency keys, and **compensation order**; easier audits for payments regulators.  
2. **Saga instance id** correlates PSP, Order, and Restaurant logs without inferring global state from **event order alone**.

**Con (one):** The orchestrator is a **single locus of failure and latency**—it must be HA and strictly bounded in logic, or it becomes a **smart god service** that recentralizes what microservices were meant to split.
