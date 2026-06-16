# Part 2 – Orchestration vs Choreography
## Task 2.1: Orchestrated Pipeline Design

**Assignment:** Composable Document Pipeline – Composition and Connectors  
**Chapter:** 7 – Composability and Connectors  
**Deliverable:** `part2_orchestration.md`

---

## 1. The Orchestrator

### Which component acts as orchestrator

In the orchestrated design, a dedicated **Pipeline Orchestrator** service assumes central control of the entire processing flow. This is a new, purpose-built component — it is not the API Gateway from Part 1. The Gateway's responsibility remains unchanged: accept HTTP requests, authenticate, and return an immediate response to the client. The Gateway delegates all post-validation work to the Orchestrator by invoking it directly after the Validator returns a pass result.

The Orchestrator is the sole component that knows the full sequence of pipeline steps. No other component — Extractor, Classifier, Storage Service, Notifier — knows what comes before or after it. Each processing component exposes a simple request/response interface and waits to be called. The Orchestrator is the only one that holds the state of a job in flight.

**Technology choice:** The Orchestrator is implemented as a stateful workflow engine, for example using [Temporal](https://temporal.io) or [AWS Step Functions](https://aws.amazon.com/step-functions/). This gives it durable execution: if the Orchestrator process crashes mid-workflow, the workflow resumes from the last completed step when the process restarts, without re-running already-completed steps. The sequence of calls, their outcomes, and any compensating actions are all recorded in the workflow history.

---

## 2. Exact Sequence of Calls

The Orchestrator executes the following steps in strict order. Each step is a synchronous, blocking call to the named component. The Orchestrator waits for a response before proceeding to the next step.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Pipeline Orchestrator                         │
│                                                                      │
│  receive(jobId, documentRef, options, callbackUrl)                   │
│     │                                                                │
│  Step 1 ──► Validator.validate(documentRef, options)                 │
│     │         ◄── { documentId, mimeType, sizeBytes, validatedAt }   │
│     │         on failure → ABORT, update status=FAILED, notify       │
│     │                                                                │
│  Step 2 ──► Extractor.extract(documentId, storageRef, options)       │
│     │         ◄── { rawText, pages, ocrUsed, durationMs }            │
│     │         on failure → retry (up to 3×), then ABORT              │
│     │                                                                │
│  Step 3 ──► Classifier.classify(documentId, rawText, pages)          │
│     │         ◄── { category, confidence, structuredFields }         │
│     │         on failure → retry (up to 3×), then ABORT              │
│     │                                                                │
│  Step 4 ──► StorageService.store(documentId, extractionResult,       │
│     │                           classificationResult)                │
│     │         ◄── { storedAt, statusUpdated }                        │
│     │         on failure → retry (up to 3×), then ABORT              │
│     │                                                                │
│  Step 5 ──► Notifier.notify(jobId, callbackUrl, result)              │
│               ◄── { deliveredAt } or { failed, reason }              │
│               on failure → log, continue (non-blocking)              │
└──────────────────────────────────────────────────────────────────────┘
```

### Step-by-step detail

**Step 1 — Validate**

The Orchestrator calls `Validator.validate(documentRef, options)`. If the Validator returns a failure response, the Orchestrator immediately terminates the workflow: it updates the job status to `FAILED` with reason `VALIDATION_ERROR`, calls `Notifier.notify` with the failure detail, and returns. No retry is attempted on validation failure — a malformed document will not become valid on a second attempt, so retrying wastes resources and delays the client from receiving a clear error.

**Step 2 — Extract**

The Orchestrator calls `Extractor.extract(documentId, storageRef, options)`. This is the most expensive and failure-prone step (OCR, file parsing, I/O). The Orchestrator applies a retry policy: up to three attempts with truncated exponential back-off (5 s, 25 s, 125 s). Between attempts the Orchestrator records the attempt number in the workflow history so that if the Orchestrator itself crashes during a retry window, it resumes from the correct attempt count. If all three attempts fail, the Orchestrator proceeds to the abort sequence (Step 2 Abort, below).

**Step 3 — Classify**

The Orchestrator calls `Classifier.classify(documentId, rawText, pages)` with the extraction result from Step 2. The same retry policy applies (3 attempts, back-off). If classification fails after exhausting retries, the Orchestrator proceeds to the abort sequence.

**Step 4 — Store**

The Orchestrator calls `StorageService.store(documentId, extractionResult, classificationResult)`. The Storage Service performs all three writes (object store, document database, status store) atomically from its own perspective; if any internal write fails, it returns an error to the Orchestrator without partially committing. The same retry policy applies. If storage fails after exhausting retries, the Orchestrator proceeds to the abort sequence.

**Step 5 — Notify**

The Orchestrator calls `Notifier.notify(jobId, callbackUrl, result)`. Notification is treated as a best-effort, non-critical step. If notification fails, the Orchestrator logs the failure and marks the job `COMPLETE_NOTIFICATION_FAILED` rather than failing the whole job — the document has been processed and stored successfully; only the delivery of the result to the client has failed. The client can still poll for the result via `GET /jobs/{jobId}`.

### Abort Sequence

If Steps 2, 3, or 4 exhaust their retries, the Orchestrator executes the abort sequence:

1. Call `StorageService.updateStatus(jobId, FAILED, errorDetail)` — ensures the job status is recorded durably even when processing failed, so polling clients receive a clear terminal state.
2. Call `Notifier.notify(jobId, callbackUrl, { status: "FAILED", code, reason })` — informs the client of the failure via their registered channel.
3. Write the workflow to the dead-letter log with the full step history for operational debugging.

---

## 3. Error and Retry Handling

### Retry policy

All retryable steps (2, 3, 4) share the same retry policy, controlled entirely by the Orchestrator:

| Parameter | Value |
|-----------|-------|
| Max attempts | 3 |
| Back-off strategy | Truncated exponential (5 s, 25 s, 125 s) |
| Idempotency guarantee | Each call carries the `jobId`; components use it to detect and ignore duplicate calls |
| Timeout per attempt | 120 s for Extractor (OCR may be slow), 30 s for Classifier, 10 s for Storage |

### Idempotency under retry

Because the Orchestrator may call the same component multiple times on retries, every component must be idempotent with respect to the `jobId`. The Extractor and Classifier check a short-lived cache keyed by `jobId` before processing; if the result already exists, they return it immediately without re-running. The Storage Service uses an upsert (`ON CONFLICT DO NOTHING`) on the `jobId` primary key. This means retries are safe even if the first attempt partially succeeded before a timeout.

### Timeout handling

Each step call is wrapped in a timeout enforced by the Orchestrator. If the Extractor does not respond within 120 seconds, the Orchestrator treats the call as a failure and begins the retry sequence. The component itself continues running in the background (the Orchestrator has no way to cancel it), but the Orchestrator will not wait for it and the component's eventual response will be discarded — its idempotency cache will prevent duplicate processing if the Orchestrator retries with the same `jobId`.

### Compensating actions

The pipeline has no destructive side-effects that require explicit rollback (documents are stored, never deleted mid-pipeline), so no saga-style compensation is needed for most failures. The one exception is a partial write in the Storage Service: if Step 4 fails after partially writing to the object store but before updating the status store, the Storage Service itself is responsible for cleaning up — it exposes a `cleanup(jobId)` method that the Orchestrator calls as part of the abort sequence to ensure no orphaned objects accumulate in storage.

---

## 4. Advantage of the Orchestrated Design

**Advantage: Full observability and debuggability of the pipeline flow**

Because the Orchestrator holds the complete workflow state in a single, central location, it is straightforward to answer the question "what is this job doing right now?" at any point in time. The workflow history records every step, its start time, its outcome, and the number of attempts made. An operator can inspect a failing job and see immediately that it succeeded at extraction, failed twice at classification, and is currently waiting for its third attempt. This is far harder to achieve in a choreographed design, where the current state of a job must be reconstructed by correlating events from multiple independent components across the event bus.

This observability advantage is especially valuable during incident response: when a client reports that their document has not been processed, an operator can query the Orchestrator for that `jobId` and receive a complete audit trail in a single lookup, rather than having to search event logs across four or five different services.

---

## 5. Disadvantage of the Orchestrated Design

**Disadvantage: The Orchestrator is a single point of failure and a scalability bottleneck**

Every job must pass through the Orchestrator. If the Orchestrator service becomes unavailable — due to a crash, a deployment, or resource exhaustion — no new jobs can be processed and in-flight jobs are stalled until the Orchestrator recovers. Even with durable execution (which allows jobs to resume after a restart), the recovery window means clients experience delays.

The scalability dimension is equally significant. As job volume increases, all workflow state management, retry scheduling, and step sequencing is concentrated in one service. While workflow engines can be scaled horizontally, doing so introduces distributed coordination complexity that is entirely absent in the choreographed design, where each component scales independently with no shared state. For the document processing pipeline — where OCR jobs in particular are highly variable in duration and the system must handle large, unpredictable bursts — the Orchestrator's central position creates a coordination overhead that grows with both job volume and pipeline depth.

---

## 6. Summary

| Aspect | Orchestrated design |
|--------|-------------------|
| Control model | Centralised — Pipeline Orchestrator directs every step |
| Step sequence | Strict: Validate → Extract → Classify → Store → Notify |
| State location | Orchestrator workflow history (durable, single source of truth) |
| Error handling | Retry with back-off (steps 2–4); immediate abort (step 1); best-effort (step 5) |
| Abort handling | Update status → Notify client → Dead-letter log |
| Key advantage | Full observability; single-location audit trail; easy debugging |
| Key disadvantage | Single point of failure; scalability bottleneck under high load |
