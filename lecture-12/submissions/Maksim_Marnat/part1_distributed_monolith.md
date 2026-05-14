# Part 1.2 — Distributed monolith: red flags & mitigations (CityBite)

**Lecture 12 definition (Pautasso):** a **distributed monolith** is a set of separately deployed components that still behave like **one application** because they share **fate** through **shared databases**, **chatty synchronous** call graphs, and **release or schema coupling**—so you pay network **latency and failure modes** without gaining true **team or data autonomy**.

Below: three **red flags** that CityBite would exhibit that pattern, each with one mitigation.

## Red flag 1 — Shared database across “services”

**Symptom:** Order, Payment, and Dispatch “microservices” all **JOIN** the same Postgres schema; schema migrations require **global lockstep**.

**Mitigation:** **Logical database per bounded context** (physical split when ready); only **integration APIs or events** cross the boundary—no cross-context SQL (Part 2.1).

## Red flag 2 — Chatty synchronous fan-out

**Symptom:** Checkout path performs **5+ internal HTTP calls** in one request to “micro” endpoints; failure in any hop fails the sale (**latency + blast radius**).

**Mitigation:** **Synchronous surface only where the domain demands** (pay-now); push **kitchen/dispatch** to **async events**; introduce **BFF** or orchestrator with **timeouts/bulkheads** (Lecture 11 alignment).

## Red flag 3 — Cannot deploy one context alone

**Symptom:** Every Friday release needs **full regression** because teams share types, tables, and feature flags with hidden coupling (the **Stripe-shaped** leak in `OrderServiceTight` vs `PaymentPort` in `example1_flexibility_coupling_citybite.py`).

**Mitigation:** **Consumer-driven contract tests** (mobile + BFF as consumers); **ports/adapters** inside the monolith **before** extract; **strangler** slice with **feature-flagged routing** (Part 3).
