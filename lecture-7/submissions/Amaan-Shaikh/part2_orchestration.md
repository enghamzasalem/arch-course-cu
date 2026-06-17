# Task 2.1 – Orchestrated Design

## Orchestrator Component

The **Pipeline Orchestrator** (implemented as part of the API Gateway) acts as the central coordinator.

**Sequence of calls:**

1. Orchestrator receives document from client (POST /pipeline/run)
2. Orchestrator calls Validator → waits for result
3. If validation passes, orchestrator calls Extractor → waits for result
4. Orchestrator calls Classifier → waits for result
5. Orchestrator calls Storage → waits for confirmation
6. Orchestrator calls Notifier (async, fire-and-forget)
7. Orchestrator returns final result to client

**Error handling and retries:**

- Validation failure: return 400 error immediately, no retry
- Extraction failure: retry up to 3 times with backoff
- Classification failure: use default category "unknown"
- Storage failure: retry up to 3 times, then return error
- Notifier failure: log and continue (does not affect client response)

## Advantage of Orchestration

**Easier debugging and monitoring:** The entire flow is visible in one place. You can log each step, measure timing, and trace exactly where failures occur. Adding metrics and distributed tracing is straightforward because all calls pass through the orchestrator.

## Disadvantage of Orchestration

**Single point of bottleneck:** The orchestrator handles every request. Under high load, it can become a performance bottleneck. All processing is serialized through one component, which limits throughput even if downstream services are fast.