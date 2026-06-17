# Task 2.3 – Comparison and Recommendation

## Comparison

| Criteria | Orchestration | Choreography |
|----------|---------------|--------------|
| **Ease of changing pipeline order** | Easier - order is controlled in one place | Harder - order depends on events and subscriptions |
| **Ease of adding new steps** | Harder - requires changes to the orchestrator | Easier - new component can subscribe to existing events |
| **Debugging and tracing** | Easier - flow is visible in one component | Harder - flow is distributed across components |
| **Latency** | Lower - direct calls, no event bus overhead | Higher - events add serialization and queue latency |
| **Scalability** | Limited - orchestrator can become bottleneck | Better - components process events independently |
| **Error handling** | Simpler - orchestrator controls retries | Complex - requires dead letter queues and retry policies |

## Recommendation

For this document pipeline, a **hybrid approach** is the best choice.

**Why hybrid:**
- Use orchestration for the **synchronous path** because the client expects an immediate response and the flow is easier to control and debug
- Use choreography for the **asynchronous path** because background processing, OCR extraction, and webhook notifications work better with events

This combination fits the requirements better than using only one approach. The pipeline supports both sync (web app users) and async (batch jobs) clients, and each path uses the appropriate composition style.

**Implementation summary:**
- Sync path (`POST /pipeline/run`): Orchestrated by API Gateway
- Async path (`POST /pipeline/jobs`): Event-driven with Job Queue