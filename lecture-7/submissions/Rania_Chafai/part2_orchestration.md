# Part 2.1: Orchestrated Design — Document Processing Pipeline

## 1. Orchestrator

**Component:** **`PipelineOrchestrator`** (implemented inside the **API / BFF service** or a dedicated worker process).

**Role:** A single component owns the **workflow**. It invokes other components in a **fixed sequence** and aggregates results or errors. No event bus is required for the happy path; calls are explicit.

---

## 2. Exact sequence of calls

1. **Receive** normalized `DocumentJob` from **API Gateway** (already authenticated and with storage pointer).
2. **Validator.validate(job)** → if failure, return error to client (sync path) or mark job failed (async path).
3. **Extractor.extract(job)** → produce `ExtractedContent`.
4. **Classifier.classify(extracted)** → produce `ClassificationResult`.
5. **Storage.persist(job, extracted, classification)** → produce `StorageRef`.
6. **Notifier.notify(job_id, success, storage_ref)** → optional; may be async fire-and-forget after orchestrator commits success.

**Error handling (conceptual):**

- **Per-step try/catch:** On failure, orchestrator records `job_id`, status `FAILED`, error code, and optionally calls **Notifier** with failure.
- **Retries:** Transient errors (network to Storage) → **retry with backoff** (e.g. 3 attempts). Non-retryable (invalid PDF) → fail fast.
- **Idempotency:** `job_id` + document hash used so retries do not duplicate storage writes.
- **Timeouts:** Each step has a max duration; if exceeded, fail job or escalate to dead-letter queue.

---

## 3. One advantage

**Clear control flow:** Developers can read the orchestrator code and see **exact order** of steps, making onboarding and **debugging** straightforward. Centralized policies (timeouts, retries) apply in one place.

---

## 4. One disadvantage

**Tight coupling to sequence:** Changing order or adding a conditional branch (e.g. skip classification for “text only”) requires **editing the orchestrator** and redeploying. In a large system, this can become a **bottleneck** compared to event-driven choreography where subscribers change independently.
