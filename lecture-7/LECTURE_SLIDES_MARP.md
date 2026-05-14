---
marp: true
theme: default
paginate: true
header: 'Software Architecture — Lecture 7'
footer: 'Composability and Connectors'
style: |
  section { font-size: 28px; }
  h1 { color: #1e40af; }
---

<!-- 
  Export to PowerPoint:
  - Install "Marp for VS Code" extension, open this file, click Export → PPTX
  - Or: npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o Lecture7.pptx
-->

# Composability and Connectors

**Chapter 7** — Software Architecture (Pautasso)

How components are composed into systems and how they communicate

---

## Learning objectives

- Compose components into larger systems
- Design and choose **connectors**
- Message passing (sync vs async)
- Event-driven composition
- **Orchestration** vs **choreography**

---

## What is composition?

**Composition** = assembling smaller **components** into a system

- Clear responsibility per component
- Components linked by **connectors**
- Architecture ≈ **components + connectors**

---

## Connectors

A **connector** is how two components communicate

- Protocol, direction, sync/async
- Wrong choice → coupling, latency, failures

---

## Connector types

| Type | Typical use | Often |
|------|-------------|--------|
| Direct call | Same process | Sync |
| RPC / REST | Network services | Sync |
| Message queue | Decouple | Async |
| Event bus | Pub/sub | Async |

---

## Message passing

**Synchronous** — wait for reply (simple, blocking)

**Asynchronous** — send and continue (scale, decouple)

---

## When sync vs async?

- **Sync** — need immediate result to proceed
- **Async** — work can be deferred (notifications, reports)
- Queues/events absorb spikes and isolate failures

---

## Composition patterns

- **Pipeline** — stages in sequence
- **Layered** — strict call direction
- **Services** — APIs + messaging

---

## Orchestration

One **orchestrator** controls the flow and calls services in order

- **+** Flow visible in one place
- **−** Bottleneck, central coupling

---

## Choreography

No central driver — services react to **events**

- **+** Loose coupling, add subscribers easily
- **−** Harder to trace global flow

---

## Orchestration vs choreography

| | Orchestration | Choreography |
|---|---------------|--------------|
| Control | Central | Distributed |
| Visibility | High | Lower |
| Good for | Clear workflows | Many consumers |

---

## Event-driven architecture

- **Events** — something happened (`OrderPlaced`)
- **Broker / bus** — delivers to subscribers
- Watch: ordering, duplicates, eventual consistency

---

## Architectural connectors

- Affect **quality attributes** (reliability, latency)
- Show in **deployment** and **runtime** views
- Label diagrams: REST, gRPC, AMQP, …

---

## Course examples

- `example1_composition_and_connectors.py`
- `example2_orchestration_vs_choreography.py`

---

# Assignment (overview)

**Composable Document Processing Pipeline**

- Apply **Chapter 7**: components, connectors, orchestration vs choreography
- Full spec: **`ASSIGNMENT.md`** (this deck only orients you — **does not** solve it)

---

## Assignment: scenario

Design the **architecture** of a pipeline that:

- **Ingests** documents (e.g. PDF, images) with optional options
- **Runs** conceptual steps: validate → extract (text/OCR) → classify → store → notify
- **Serves** clients that need **sync** (“process and return now”) **and** **async** (“job id, notify when done”)

You document **design choices**, not production code.

---

## What you produce (big picture)

| Area | You decide & justify |
|------|----------------------|
| Components | ≥5, responsibilities, I/O, sync/async view |
| Connectors | Types, protocols, where sync vs async |
| Styles | One **orchestrated** and one **choreographed** design + comparison |
| API | Sync + async client entry points |
| Diagrams | Component-and-connector + one sequence diagram |

---

## Part 1 — Components & connectors

**Task 1.1** (written)

- **≥5 components** — each: name, single responsibility, inputs/outputs, caller’s sync vs async
- **Connectors** between communicating pairs: name, type (call, REST, queue, bus, …), sync/async, format
- **Justify** sync vs async (e.g. fast feedback vs deferred heavy work)

**Deliverable:** `part1_components_and_connectors.md` — **30 pts**

---

## Part 1 — Diagram

**Task 1.2**

- **draw.io** component-and-connector diagram: components as boxes, connectors as **labeled** arrows (type + sync/async)
- **Legend** for notation

**Deliverables:** `.drawio` **and** `.png` — **20 pts**

---

## Part 2 — Orchestration

**Task 2.1**

- Which component **orchestrates**; **order** of calls to others
- **Errors / retries** (conceptually)
- **One** advantage **and** **one** disadvantage for *your* pipeline

**Deliverable:** `part2_orchestration.md` — **15 pts**

---

## Part 2 — Choreography

**Task 2.2**

- **Event** names for the lifecycle (you define the set)
- Per component: **subscribes** to which events, **publishes** which and when
- **No** central orchestrator — flow from events
- **One** pro **and** **one** con vs your orchestrated view

**Deliverable:** `part2_choreography.md` — **15 pts**

---

## Part 2 — Compare & recommend

**Task 2.3**

- **Table**: e.g. changing order, adding steps, debugging/tracing, latency & scale (conceptual)
- **Recommendation**: orchestration, choreography, or **hybrid** — short **justification**

**Deliverable:** `part2_comparison.md` — **10 pts**

---

## Part 3 — API (sync & async)

**Task 3.1**

- **Endpoints** (REST or RPC-style): e.g. sync “run now” vs async “create job” + status (optional webhook)
- Briefly map **sync path** and **async path** to **your** components/connectors (queues/events as you designed)

**Deliverable:** `part3_api_design.md` — **20 pts**

---

## Part 3 — Sequence diagram

**Task 3.2**

- **One** end-to-end flow: **either** full sync **or** async (enqueue → worker → … → notify)
- **≥5 participants**, labeled messages

**Deliverables:** `.drawio` **and** `.png` — **10 pts**

---

## Submission & grading

- **PR** to `lecture-7/submissions/YOUR_NAME/` — see `SUBMISSION_GUIDE.md`
- **Total: 120 points** — rubric in `ASSIGNMENT.md`
- Every diagram: **both** source and **PNG**

---

## Before you start (hints, not answers)

1. Re-read the **two Python examples** in this lecture folder
2. List **pipeline steps**, then **assign** steps to components (your split)
3. Pick **connector** per link: sync when you must wait; async when you can defer
4. Sketch **orchestrator call chain**, then **events + subscribers** for the other style

---

## Takeaways

1. Systems = **components + connectors**
2. Match connector and sync/async to requirements
3. **Orchestration** vs **choreography** for service composition
4. Events enable scalable, loose coupling

---

# Questions?

**Next:** Chapter 8 — Compatibility and Coupling
