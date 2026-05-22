# Part 2.3 — Orchestration vs. Choreography: Comparison and Recommendation

## Comparison Table

| Criterion | Orchestration | Choreography |
|---|---|---|
| **Changing pipeline order** | Easy — edit one file (the Orchestrator) | Hard — must trace which component publishes the event that the next one consumes, and update subscriptions |
| **Adding a new step** | Medium — add call in Orchestrator and register new component | Easy — new component subscribes to an existing event; nothing else changes |
| **Removing a step** | Easy — remove call from Orchestrator | Medium — must ensure nothing breaks if the event that step published is no longer published |
| **Debugging and tracing** | Easy — full flow visible in one place; logs are sequential per job | Hard — must correlate events across multiple components using job_id; a missing event leaves a job silently stuck |
| **Error handling** | Centralized — retry policies, compensation, and fallbacks in one place | Distributed — each component handles its own failures; consistent policy requires coordination across teams |
| **Latency** | Adds orchestrator overhead for every call | Minimal — components react directly to events with no intermediary logic layer |
| **Scalability** | Orchestrator can become a bottleneck if it handles high volume | High — each component scales independently; event bus absorbs bursts |
| **Team independence** | Low — every pipeline change requires touching the Orchestrator | High — teams can deploy new subscribers without touching other components |
| **Operational complexity** | Lower — one stateful component to monitor | Higher — distributed state across event bus, dead-letter queues, component logs |

---

## Recommendation: Hybrid (Orchestrated Core, Choreographed Periphery)

For a document processing pipeline at a small-to-medium scale, a **hybrid**
is the right choice.

**Keep orchestration for the core processing sequence:**
Validate → Extract → Classify → Store.
These four steps always run in a fixed order, and the error handling between
them is tightly coupled (an extraction failure must stop classification).
An Orchestrator makes this flow explicit, easy to trace, and easy to change.
The course's point about synchronous connectors is relevant here: within the
worker, these steps run fast enough that the overhead of an event-driven hop
between them adds latency with no availability benefit.

**Use choreography for the periphery:**
Two places benefit from event-driven decoupling:

1. **Job enqueuing** (API Gateway → Worker queue): the API Gateway publishes
   `document.received` and returns immediately.  The worker consumes it when
   ready.  This is where async availability matters — the API must not block
   waiting for OCR.

2. **Notification** (Worker → Notifier): after Storage completes, the worker
   publishes `document.stored` and the Notifier handles delivery independently.
   Webhook retries, failure escalation, and notification policy can evolve
   without touching the core worker.

**Why not pure choreography?**  
The pipeline has a fixed, sequential dependency chain with meaningful failure
handling between steps.  Distributing that logic across six components makes
the system harder to debug and the retry policy harder to keep consistent.
The scalability benefit of pure choreography is real but not needed until
the pipeline reaches high throughput — at which point the Orchestrator can
be extracted into its own scalable worker pool.

**Why not pure orchestration?**  
The client-facing async path genuinely benefits from a queue between upload
and processing.  Blocking the HTTP thread on OCR is not acceptable.  Some
choreography is necessary at the entry and exit points of the pipeline.
