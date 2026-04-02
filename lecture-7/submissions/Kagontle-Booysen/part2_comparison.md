# Part 2 – Orchestration vs Choreography
## Task 2.3: Comparison and Recommendation

**Assignment:** Composable Document Pipeline – Composition and Connectors  
**Chapter:** 7 – Composability and Connectors  
**Deliverable:** `part2_comparison.md`

---

## 1. Comparison Table

| Criterion | Orchestration | Choreography |
|-----------|--------------|--------------|
| **Changing pipeline order** | Easy — the sequence is explicit in one place (the Orchestrator). Reordering steps (e.g. classify before extract) requires editing a single workflow definition. No other component is aware of the change. | Hard — order is implicit in which events each component subscribes to. Reordering requires changing the event topics that multiple components publish and subscribe to, with risk of introducing subtle sequencing bugs that are invisible until runtime. |
| **Adding a new step** | Moderate — the new component must be added to the Orchestrator's call sequence, which is a single, auditable change. The downside is that the Orchestrator must be redeployed. | Easy — a new component simply subscribes to the relevant event topic (e.g. `extraction.completed`) and publishes its own result event. No existing component needs to change or be redeployed. The pipeline extends without touching any running code. |
| **Debugging and tracing** | Easy — the Orchestrator holds the complete workflow history in one location. For any job, an operator can inspect a single record to see every step, its outcome, its attempt count, and its timestamps. Failures are immediately visible with full context. | Hard — the current state of a job must be reconstructed by correlating events across multiple services and event bus logs. No single component knows the full picture. Distributed tracing tooling (e.g. OpenTelemetry with a correlation ID) is required to achieve comparable visibility, and even then, the tooling adds operational complexity. |
| **Latency** | Higher — every step passes through the Orchestrator, adding a coordination hop between each component. For a five-step pipeline, this means five round-trips through the Orchestrator rather than direct component-to-component transitions. | Lower — components transition directly via the event bus without a coordination intermediary. Each step begins as soon as the previous step's event is published, with no Orchestrator round-trip in between. |
| **Scalability** | Limited by Orchestrator — all workflow state and retry scheduling is centralised. Under high job volume, the Orchestrator becomes a coordination bottleneck. Horizontal scaling is possible but introduces distributed state management complexity. | High — each component scales independently based on its own queue depth or event backlog. Adding Extractor workers has no effect on the Classifier or Storage Service and requires no coordination. The event bus absorbs burst traffic naturally. |
| **Failure isolation** | Poor — the Orchestrator is a single point of failure. If it becomes unavailable, no jobs can be processed regardless of whether the processing components (Extractor, Classifier, etc.) are healthy. Recovery requires waiting for the Orchestrator to restart and resume durable workflows. | Good — failure of one component (e.g. the Classifier) does not affect others. The Extractor continues to publish events; the Classifier's events simply queue up on the bus and are processed when it recovers. No other component is impacted. |
| **Operational transparency** | High — the pipeline's behaviour is explicit and readable in the Orchestrator's workflow definition. A new team member can understand the entire flow by reading one file. Business logic and sequencing are co-located. | Low — the pipeline's behaviour is distributed across multiple components' subscription configurations. Understanding the full flow requires reading every component's subscription and publication logic. The sequence is an emergent property, not an explicit artefact. |

---

## 2. Recommendation: Hybrid Design

**Recommendation: Use choreography as the primary pattern, with a thin orchestration layer for job lifecycle management only.**

Neither pure orchestration nor pure choreography is the best fit for this pipeline in isolation. Pure orchestration introduces a single point of failure and a scalability ceiling that directly conflict with the pipeline's core non-functional requirements: handling burst traffic (batch uploads of hundreds of documents), tolerating OCR durations of up to several minutes, and scaling Extractor workers independently during peak load. Pure choreography, on the other hand, makes observability unnecessarily difficult: because the pipeline is a strictly sequential, five-step workflow with a single defined order, the "emergent sequence" property of choreography buys nothing — the order never changes dynamically based on events — but costs a great deal in debuggability and incident response time.

The hybrid resolves this tension by separating two concerns that pure patterns conflate. The **event bus (choreography)** handles component-to-component transitions: Extractor publishes, Classifier subscribes, Storage subscribes, Notifier subscribes. Each component scales independently, failure of one does not cascade to others, and adding a new component (e.g. an Audit Logger subscribing to `classification.completed`) requires zero changes to existing code. The **Orchestrator handles only job lifecycle**: it writes the initial `PENDING` status when a job is submitted, listens for the terminal events (`document.stored` or `*.failed`), updates the canonical job status in the Status Store, and triggers the abort notification if the job fails after exhausting retries. This is a lightweight, stateless role that does not sit in the critical path of processing — if the Orchestrator is temporarily unavailable, documents continue to be processed and results stored; only the final status update and client notification are delayed.

This hybrid is the established industry pattern for document and data processing pipelines: event-driven components for throughput and resilience, a thin job-tracking layer for visibility and client-facing status. It directly reflects the architecture described in Part 1, where the event bus mediates processing and the Storage Service's read path serves as the status source of truth.

---

## 3. Summary

| | Pure orchestration | Pure choreography | **Hybrid (recommended)** |
|--|-------------------|-------------------|--------------------------|
| Scalability | ✗ Bottleneck at Orchestrator | ✓ Each component independent | ✓ Processing components independent |
| Failure isolation | ✗ Orchestrator = SPOF | ✓ Component failures contained | ✓ No SPOF in processing path |
| Observability | ✓ Single audit trail | ✗ Requires distributed tracing | ✓ Job lifecycle tracked centrally |
| Adding new steps | ✗ Orchestrator redeploy required | ✓ New subscriber, no change to others | ✓ New subscriber, no change to others |
| Changing step order | ✓ One workflow definition | ✗ Multi-component subscription changes | ✓ Event topics define order; one config change |
| Operational clarity | ✓ Explicit sequence in one file | ✗ Sequence is emergent | ✓ Processing flow explicit in event topology |
