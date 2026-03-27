# Part 2: Orchestration vs Choreography
## Task 2.3: Comparison and Recommendation

## 1. Comparison Table

| Criteria | Orchestration | Choreography (Event-Driven) |
|----------|--------------|-----------------------------|
| Ease of changing pipeline order | Easy – change logic in one central orchestrator | Difficult – must modify multiple event producers/consumers |
| Ease of adding new steps | Moderate – update orchestrator logic | Easy – new component can subscribe to events without affecting others |
| Debugging and tracing | Easy – flow is centralized and explicit | Difficult – flow is distributed across events |
| Latency | Slightly higher (sequential execution) | Lower (parallel event processing possible) |
| Scalability | Limited – orchestrator can become bottleneck | High – components scale independently |
| Coupling | Tighter coupling to orchestrator | Loose coupling between components |
| Fault isolation | Lower – orchestrator failure impacts system | Higher – failures isolated to individual components |

---

## 2. Recommendation

### Recommended Approach: Hybrid (Orchestration + Choreography)

For the document processing pipeline, a **hybrid approach** is the most suitable design.

- Use **orchestration** for:
  - Initial steps like **validation and request handling**
  - Ensuring immediate feedback to the user

- Use **choreography (event-driven design)** for:
  - Heavy processing steps like **extraction, classification, storage, and notification**
  - Enabling scalability and asynchronous processing

---

## 3. Justification

A pure orchestration approach provides strong control but limits scalability, while pure choreography improves scalability but makes debugging complex.

The hybrid approach combines the strengths of both:

- **Fast user response** through synchronous validation
- **Scalable processing** through asynchronous event-driven pipeline
- **Loose coupling** between backend components
- **Better system resilience and fault isolation**

This makes the hybrid model ideal for a real-world document processing system that must handle both **interactive (sync)** and **background (async)** workloads efficiently.

---

## 4. Summary

The hybrid architecture balances:
- Control (from orchestration)
- Flexibility and scalability (from choreography)

This results in a system that is:
- Efficient
- Maintainable
- Scalable
- Suitable for production environments