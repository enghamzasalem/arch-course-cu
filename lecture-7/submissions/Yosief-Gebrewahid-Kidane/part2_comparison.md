# Part 2.3 — Comparison and Recommendation

## 1. Comparison: Orchestration vs Choreography

| Criteria | Orchestration | Choreography |
|----------|--------------|-------------|
| **Control** | Centralized (one orchestrator) | Distributed (event-driven) |
| **Ease of changing pipeline order** | Easy — modify orchestrator logic | Harder — must change multiple event handlers |
| **Adding new steps** | Requires updating orchestrator | Easy — add new event subscriber |
| **Debugging & tracing** | Easier — flow visible in one place | Harder — flow spread across components |
| **Coupling** | Tighter coupling | Looser coupling |
| **Scalability** | Limited by orchestrator | Highly scalable |
| **Latency** | Can be higher (blocking calls) | Lower perceived latency (async processing) |

---

## 2. Recommendation

For the document processing pipeline, a **hybrid approach** is recommended:

- Use **orchestration** for the initial steps (API → validation) where immediate feedback is required.
- Use **choreography (event-driven)** for the processing stages (extraction, classification, storage, notification) to improve scalability and decoupling.

### Justification

- Validation must be **synchronous** to quickly reject invalid input.
- Processing steps (OCR, classification, storage) are **resource-intensive** and benefit from asynchronous execution.
- Event-driven design allows adding new features (e.g. analytics, auditing) without modifying existing components.
- Hybrid design combines the **clarity of orchestration** with the **scalability of choreography**.

