# Part 2: Orchestration vs Choreography

## Task 2.3: Comparison and Recommendation

### 1. Comparison Table

| Criterion | Orchestration | Choreography (Event-Driven) |
| :--- | :--- | :--- |
| **Ease of changing pipeline order** | **High:** Modifying the sequence of execution requires changing code in only one centralized place (the orchestrator). | **Low:** Rearranging the order means updating event publishing and subscription mappings across multiple decoupled services. |
| **Ease of adding new steps** | **Medium:** Requires deploying the new service, then modifying the orchestrator workflow logic to explicitly call it. | **High:** A new service (e.g., an `ImageEnhancer` microservice) can simply subscribe to existing events naturally without modifying other services. |
| **Debugging and Tracing** | **High:** The central orchestrator natively maintains state, offering an explicit trail of when and where the document process failed or stalled. | **Low:** Execution flow is implicit. Without advanced distributed tracing (correlation IDs), it is notoriously difficult to determine where the pipeline broke. |
| **Latency and Scalability** | **Medium:** As load spikes exponentially, the orchestrator's stateful transaction management can become an active bottleneck. | **High:** Components operate autonomously. If the OCR engine is congested, it can scale massively without impacting other components' message flow. |

---

### 2. Recommendation

For this specific Document Processing Pipeline, I highly recommend a **hybrid approach** (frequently referred to as **Event-Driven Orchestration** or a **Choreographed Orchestrator** pattern). 

Because the pipeline supports both a synchronous execution path and asynchronous bulk requests—and clients need meaningful status updates (e.g., "Extraction Failed" or "Currently Classifying")—pure choreography is overly complex to trace and recover from. Conversely, pure active orchestration creates a stateful bottleneck during heavy OCR scaling. 

**Justification:** A hybrid design uses a central **PipelineOrchestrator** to track macro-state (acting as the State Machine), but it commands the components asynchronously via an event bus (message queues). The Extractor and Classifier independently pull tasks off these queues without being strictly coupled to the Orchestrator's immediate request thread. Once finished, they emit a `<Task>Completed` event back to the Orchestrator. This perfectly blends the **tracing, debugging, and sequential simplicity** of Orchestration with the **horizontal scalability and decoupled latency** of Choreography.
