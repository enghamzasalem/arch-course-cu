# Part 2: Comparison and Recommendation

## 2.1 Orchestration vs. Choreography Comparison

| Criteria | Orchestration  | Choreography  |
| :--- | :--- | :--- |
| **Changing Order** | **Easy:** Just change the code/logic in the central Manager. | **Hard:** You have to update multiple services to subscribe to different events. |
| **Adding New Steps** | **Moderate:** Update the Manager to call the new service. | **Easy:** Just point the new service at an existing event; no other service changes. |
| **Debugging & Tracing** | **Easy:** One central log shows the status of the entire process. | **Hard:** Requires distributed tracing to follow a "breadcrumb trail" across services. |
| **Scalability** | **Limited:** The Manager can become a bottleneck or crash. | **High:** Each service works independently; the system is highly distributed. |
| **Latency** | **Lower (Sync):** Direct calls are faster for simple tasks. | **Higher (Async):** Message queues and event buses add slight overhead. |

---

## 2.2 Recommendation: The Hybrid Approach

For this Document Processing Pipeline, I recommend a **Hybrid Approach**. 

### Justification
I suggest using **Orchestration for the "Critical Path"** (Validation → Extraction) and **Choreography for the other non-critical paths** (Storage → Notifier). 

The user needs to know quickly if their document is valid and if the text was pulled successfully, so having a central Manager coordinate those initial steps ensures we can return errors immediately. However, once the data is extracted, "choreographing" the storage and notification steps makes the system more flexible. For example, if we later want to add a "Data Analytics" service or a "Security Audit" service, we can simply have them listen for the `ExtractionCompleted` event without ever touching the core Pipeline Manager code. This gives us the best of both worlds: control over the main process and the ability to scale up features easily.