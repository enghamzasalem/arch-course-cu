# Assignment: CityBite Split with Care — Flexibility & Microservices

## Overview

You **document how CityBite could evolve** toward finer-grained services **without** creating a **distributed monolith**, using **Chapter 12: Flexibility and Microservices**: **bounded contexts**, **Conway’s Law**, **database per service**, **API evolution**, **strangler fig** / **branch by abstraction**, and a **saga** sketch for at least one cross-context flow.

Assume the **Kubernetes** + **Postgres** baseline from Lecture 9, **scalability** from Lecture 10, and **availability** patterns from Lecture 11. This assignment is **design + narrative + diagrams** — no requirement to implement microservices in production.

Align vocabulary with **`example1_flexibility_coupling_citybite.py`** (ports/adapters) and **`example2_flexibility_api_evolution_citybite.py`** (additive vs breaking API change).

---

## Learning Objectives

By completing this assignment, you will:

- Explain **flexibility / modifiability** as a quality and name **concrete** change drivers for CityBite  
- Propose **bounded contexts** with **clear** language and **integration** style between them  
- Argue **monolith vs modular monolith vs microservices** for **current** team size — no buzzword split  
- Describe **API evolution** rules (versioning or additive JSON) for **one** public surface  
- Sketch a **saga** (choreography or orchestration) for **one** multi-step business journey  
- Plan a **strangler** / **facade** migration slice — not a big-bang rewrite  

---

## Baseline (given)

| Aspect | Today |
|--------|-------|
| Product | CityBite — customers, restaurants, dispatch, payments, notifications |
| Runtime | K8s, APIs, workers, managed **Postgres**, external SaaS (maps, SMS, gateway) |
| Pain | One **schema** slows teams; risky “extract payment” debates; mobile clients break on **silent** API changes |

Your design must name **at least four** distinct **flexibility** mechanisms (e.g. strangler, database per service, saga, contract tests) and **one** explicit **trade-off** (flexibility vs latency, consistency, or ops cost).

---

## Part 1: Contexts & Conway

### Task 1.1: Bounded context map

**Objective:** Divide CityBite into **business**-aligned contexts — not “DAO layer” services.

**Requirements:**

1. **List three to five** bounded contexts — each with **name**, **ubiquitous language** (≥ 4 terms), **primary user**, **owns** (data/behavior).  
2. For **each pair** of adjacent contexts: integration style (**sync API**, **async event**, **batch**) and **why**.  
3. One paragraph: **Conway’s Law** — if you keep **one** team for all contexts, what architecture do you **predict**?

**Deliverable:** `part1_contexts_conway.md`

**Grading:** 32 points

---

### Task 1.2: Anti-pattern check — distributed monolith

**Objective:** Prove you can spot **fake** microservices.

**Requirements:**

1. **Three red flags** that would mean CityBite’s “microservices” are still a **distributed monolith** (cite lecture definitions).  
2. **One** mitigation per red flag (process, tech, or boundary change).

**Deliverable:** `part1_distributed_monolith.md`

**Grading:** 18 points

---

## Part 2: Data, APIs, sagas

### Task 2.1: Database per service (paper design)

**Objective:** Own data per context — accept **no cross-context SQL joins**.

**Requirements:**

1. For **two** contexts: propose **separate** datastore **logical** schemas (table/collection **names** only is fine).  
2. Identify **one** query you **lose** with split databases — how you **replace** it (API aggregation, read model, event).  
3. Short **RPO/RTO** intuition for **one** context if you use **async** replication (Lecture 11 link).

**Deliverable:** `part2_database_per_service.md`

**Grading:** 28 points

---

### Task 2.2: Public API evolution

**Objective:** Rules so mobile apps do not break every sprint.

**Requirements:**

1. Pick **one** JSON endpoint (e.g. `GET /orders/{id}`).  
2. Document **two additive** changes safe for old clients — reference **`example2`** themes.  
3. Document **one breaking** change — how you **version** (URL `v2`, header, or content negotiation) and **deprecation** window.  
4. **Consumer-driven contract** idea — **one** sentence on who generates tests.

**Deliverable:** `part2_api_evolution.md`

**Grading:** 22 points

---

### Task 2.3: Saga sketch

**Objective:** Cross-context flow **without** a distributed two-phase commit fantasy.

**Requirements:**

1. Pick **one** journey (e.g. “place paid order” or “refund after cancellation”).  
2. **List local steps** per context with **compensating** actions if a later step fails.  
3. State **choreography** vs **orchestration** choice — **two** pros and **one** con for your choice.

**Deliverable:** `part2_saga_sketch.md`

**Grading:** 25 points

---

## Part 3: Migration & diagram

### Task 3.1: Strangler / branch by abstraction

**Objective:** Incremental extraction — not stop-the-world.

**Requirements:**

1. Choose **one** context to extract **first** — justify **risk**, **team**, and **customer** value.  
2. **Strangler** plan: **facade** (gateway, BFF, or route split), **traffic %** ramp idea, **rollback** trigger.  
3. **Branch by abstraction:** which **interface** you introduce in the monolith **before** split (tie to **`example1`**).

**Deliverable:** `part3_strangler_plan.md`

**Grading:** 25 points

---

### Task 3.2: Diagram — current vs target

**Objective:** Visualize contexts and integrations.

**Requirements:**

1. **draw.io**: **left** current monolith-style deployment; **right** target with **bounded contexts** and **async** vs **sync** edges labeled.  
2. Numbered flows (**minimum 4**), **legend**, title block.  
3. Export **`part3_contexts_current_vs_target.png`** alongside `.drawio`.

**Deliverables:** `part3_contexts_current_vs_target.drawio` + `.png`

**Grading:** 22 points

---

## Deliverables checklist

| File | Part |
|------|------|
| `part1_contexts_conway.md` | 1.1 |
| `part1_distributed_monolith.md` | 1.2 |
| `part2_database_per_service.md` | 2.1 |
| `part2_api_evolution.md` | 2.2 |
| `part2_saga_sketch.md` | 2.3 |
| `part3_strangler_plan.md` | 3.1 |
| `part3_contexts_current_vs_target.drawio` | 3.2 |
| `part3_contexts_current_vs_target.png` | 3.2 |

**Total: 150 points**

---

## Submission

GitHub Pull Request per `../lecture-3/SUBMISSION_GUIDE.md`.  
Suggested PR title: `Assignment Lecture 12: CityBite flexibility — <Your Name>`
