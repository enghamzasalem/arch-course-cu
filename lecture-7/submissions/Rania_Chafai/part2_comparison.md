# Part 2.3: Orchestration vs Choreography — Comparison and Recommendation

## 1. Comparison table

| Criterion | Orchestration | Choreography (event-driven) |
|-----------|---------------|-----------------------------|
| **Ease of changing pipeline order** | Change orchestrator code and redeploy; order is explicit in one place. | Add/remove subscribers; order can be implicit—risk of wrong order if events misconfigured. |
| **Ease of adding new steps** | Insert call in orchestrator; may need to touch error paths and types. | New microservice subscribes/publishes; often **no change** to existing services. |
| **Debugging and tracing** | Single stack trace in orchestrator; straightforward. | Requires correlation IDs, event logs, distributed tracing across services. |
| **Latency and scalability (conceptual)** | Sync path can add latency if steps are sequential; scale by scaling orchestrator + workers. | Natural **async** scaling; workers scale per event type; possible extra latency from queue hops. |

---

## 2. Recommendation: **Hybrid**

For this **document pipeline**, a **hybrid** works well:

- **Orchestration** inside a **Pipeline Worker** or **API** for the **core sequence** Validate → Extract → Classify → Store so that ordering, retries, and timeouts stay **clear and testable**.
- **Choreography** for **downstream** concerns: after `DocumentStored`, publish **`PipelineCompleted`** (or `DocumentStored`) so **Notifier**, **analytics**, and **billing** subscribe **without** bloating the orchestrator.

**Justification:** Document processing needs a **reliable ordered core** (orchestration). Notifications and side effects benefit from **decoupled events** (choreography). This balances debuggability with extensibility.
