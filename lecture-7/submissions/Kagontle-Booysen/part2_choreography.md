# Part 2 – Orchestration vs Choreography
## Task 2.2: Choreographed (Event-Driven) Pipeline Design

**Assignment:** Composable Document Pipeline – Composition and Connectors  
**Chapter:** 7 – Composability and Connectors  
**Deliverable:** `part2_choreography.md`

---

## 1. Overview

In the choreographed design there is no central orchestrator. No single component knows the full pipeline sequence. Instead, each component reacts to events published by the component before it and publishes its own event when its work is done. The pipeline flow is an emergent property of the event subscriptions — it exists nowhere explicitly, but arises from the sum of each component's independent behaviour.

The event bus (Apache Kafka or RabbitMQ with durable topic exchanges) is the only shared infrastructure. It delivers events to all registered subscribers and retains unacknowledged events so that a temporarily unavailable component can resume processing from where it left off without data loss.

All events conform to a shared schema carrying a `correlationId` (the `jobId` assigned at upload time) that allows any downstream system to link all events belonging to the same document back to a single client request.

---

## 2. Event Catalogue

The following events are the complete set used by the pipeline. Every event carries the base envelope below; the payload column lists the fields added in the `data` object.

### Base event envelope

```json
{
  "specversion": "1.0",
  "id":          "<uuid>",
  "source":      "<emitting-component>",
  "type":        "<event.type>",
  "time":        "<iso8601>",
  "datacontenttype": "application/json",
  "data": {
    "jobId":         "<uuid>",
    "documentId":    "<uuid>",
    "schemaVersion": "1.0",
    "payload":       {}
  }
}
```

### Event definitions

| Event name | Emitted by | Trigger | Key payload fields |
|------------|-----------|---------|-------------------|
| `document.uploaded` | API Gateway | Client HTTP request accepted | `documentRef`, `callbackUrl?`, `options` |
| `document.validated` | Validator | Document passes all checks | `mimeType`, `sizeBytes`, `pageCountEstimate` |
| `document.invalid` | Validator | Document fails any check | `errorCode`, `reason`, `field?` |
| `extraction.completed` | Extractor | Text/OCR extraction finishes | `rawText`, `pages[]`, `ocrUsed`, `durationMs` |
| `extraction.failed` | Extractor | Extraction fails after max retries | `errorCode`, `reason`, `attempt`, `maxAttempts` |
| `classification.completed` | Classifier | Category assigned successfully | `category`, `confidence`, `structuredFields{}` |
| `classification.failed` | Classifier | Classification fails after max retries | `errorCode`, `reason`, `attempt`, `maxAttempts` |
| `document.stored` | Storage Service | All writes committed durably | `storageRefs{}`, `status`, `storedAt` |
| `storage.failed` | Storage Service | Write saga fails after max retries | `errorCode`, `reason`, `attempt`, `maxAttempts` |
| `document.dead_lettered` | Dead Letter Handler | Any `*.failed` event exhausts retries | `originEvent`, `failedStep`, `finalReason` |

**Schema versioning:** Every event carries `schemaVersion: "1.0"`. Consumers check this field before processing. An unrecognised version triggers a `*.failed` event with `errorCode: UNSUPPORTED_SCHEMA_VERSION` rather than silently corrupting data. This is the mechanism that decouples producers and consumers from each other's deployment cycles.

---

## 3. Component Event Subscriptions and Publications

Each component is described by the single question it answers: "what event tells me to start, and what event do I emit when I am done?"

---

### 3.1 API Gateway

**Role in choreography:** Entry point. Accepts HTTP requests and fires the first event. Has no knowledge of what happens after.

| | Event | Condition |
|--|-------|-----------|
| **Subscribes to** | *(none — entry point)* | — |
| **Publishes** | `document.uploaded` | After authentication, rate-limit check, and basic request parsing succeed |

**Behaviour:** Receives `HTTP POST /process`. Performs only authentication and rate limiting (no document-level validation — that belongs to the Validator). Stores the document bytes to the object store, assigns a `jobId`, writes an initial `PENDING` status record, publishes `document.uploaded`, and immediately returns `HTTP 202 Accepted { jobId, pollUrl }` to the client. The Gateway's job is complete at this point.

**On failure:** If publishing `document.uploaded` fails, the Gateway returns `HTTP 503` to the client. No event is orphaned on the bus. The client may retry.

---

### 3.2 Validator

**Role in choreography:** First consumer in the pipeline. Decides whether the document is worth processing.

| | Event | Condition |
|--|-------|-----------|
| **Subscribes to** | `document.uploaded` | Always |
| **Publishes** | `document.validated` | Document passes all checks |
| **Publishes** | `document.invalid` | Document fails any check |

**Behaviour:** Consumes `document.uploaded`. Downloads the document from the object store reference in the event payload. Performs MIME detection, file size check, format well-formedness check, and malware scan. On success, publishes `document.validated` with enriched metadata. On failure, publishes `document.invalid` — this is a terminal event for the job; no downstream component subscribes to `document.invalid` except the Dead Letter Handler and the Notifier, which will inform the client.

**Idempotency:** Uses a Redis cache keyed by `jobId`. A redelivered `document.uploaded` event for the same `jobId` is detected and dropped.

---

### 3.3 Extractor

**Role in choreography:** Performs the most expensive processing step, triggered entirely by a single event.

| | Event | Condition |
|--|-------|-----------|
| **Subscribes to** | `document.validated` | Always |
| **Publishes** | `extraction.completed` | Text or OCR extraction succeeds |
| **Publishes** | `extraction.failed` | Extraction fails after 3 attempts |

**Behaviour:** Consumes `document.validated`. Determines the extraction method from `mimeType` in the event payload: native text parsing for PDF/DOCX, OCR for image-based formats. Processes the document and publishes `extraction.completed` with the full text and per-page confidence scores. If extraction fails, retries up to three times with truncated exponential back-off (5 s, 25 s, 125 s) before publishing `extraction.failed`.

**Idempotency:** A redelivered `document.validated` for the same `jobId` returns the cached extraction result without re-running OCR.

**No knowledge of downstream:** The Extractor does not know that a Classifier exists. It publishes `extraction.completed` and its job is done. Any component interested in extracted text subscribes to that topic.

---

### 3.4 Classifier

**Role in choreography:** Reacts to completed extraction; assigns a document category.

| | Event | Condition |
|--|-------|-----------|
| **Subscribes to** | `extraction.completed` | Always |
| **Publishes** | `classification.completed` | Category assigned with sufficient confidence |
| **Publishes** | `classification.failed` | ML inference fails or confidence is below threshold after 3 attempts |

**Behaviour:** Consumes `extraction.completed`. Runs the document text through a classification model to assign a category (invoice, purchase order, tax form, contract, identity document, other) and extract structured fields. Publishes `classification.completed` with the result. The Classifier has no knowledge of Storage or Notifier — it simply publishes its result and stops.

**Idempotency:** A redelivered `extraction.completed` for the same `jobId` returns the cached classification result without re-running inference.

---

### 3.5 Storage Service

**Role in choreography:** Persists all artefacts and updates the canonical job status, then signals completion.

| | Event | Condition |
|--|-------|-----------|
| **Subscribes to** | `classification.completed` | Always |
| **Publishes** | `document.stored` | All three writes commit successfully |
| **Publishes** | `storage.failed` | Write saga fails after 3 attempts |

**Behaviour:** Consumes `classification.completed`. Executes three writes in a local saga: (1) moves the document bytes to cold storage, (2) writes extracted text and structured fields to the document database, (3) updates the job status record to `COMPLETE`. All three writes must succeed before `document.stored` is published — if any write fails, the saga runs compensating actions and retries the whole set. Publishes `document.stored` on success. The Storage Service does not know a Notifier exists.

**Idempotency:** Uses a DB unique constraint on `jobId`. A redelivered `classification.completed` triggers an upsert that silently succeeds if the record already exists, then re-publishes `document.stored` (via the outbox pattern) without double-writing.

---

### 3.6 Notifier

**Role in choreography:** Terminal consumer. Delivers the final outcome to the client via their registered channel.

| | Event | Condition |
|--|-------|-----------|
| **Subscribes to** | `document.stored` | Pipeline succeeded |
| **Subscribes to** | `document.invalid` | Validation rejected the document |
| **Subscribes to** | `extraction.failed` | Extraction exhausted retries |
| **Subscribes to** | `classification.failed` | Classification exhausted retries |
| **Subscribes to** | `storage.failed` | Storage exhausted retries |
| **Publishes** | *(none — terminal component)* | — |

**Behaviour:** Consumes any terminal event (success or failure). Looks up the client's notification preference (webhook URL, SSE connection, email) from a client registry using the `jobId`. Delivers the result payload via the appropriate channel. Webhook deliveries are signed with HMAC-SHA256. Failed deliveries are retried with exponential back-off (3 attempts). After exhaustion, the delivery failure is logged to a dead-letter record but the pipeline job itself is not failed — the document was processed successfully; only the notification was not delivered.

**Idempotency:** A Redis delivered-set keyed by `jobId` ensures duplicate terminal events do not trigger duplicate notifications.

---

### 3.7 Dead Letter Handler

**Role in choreography:** Catches any event that could not be processed after all retries. Ensures no job disappears silently.

| | Event | Condition |
|--|-------|-----------|
| **Subscribes to** | `document.invalid` | Validation failure |
| **Subscribes to** | `extraction.failed` | Extraction failure |
| **Subscribes to** | `classification.failed` | Classification failure |
| **Subscribes to** | `storage.failed` | Storage failure |
| **Publishes** | `document.dead_lettered` | On receipt of any above event |

**Behaviour:** Writes the original event and its full history to a durable dead-letter store for operational investigation. Updates the job status record to `FAILED` with the error detail. Triggers an operations alert. The dead-letter store provides a replay mechanism: an operator can re-inject a `document.uploaded` event once the underlying fault is fixed, without requiring the client to re-upload.

---

## 4. How the Flow Emerges

No component calls another directly. The complete pipeline sequence arises purely from the chain of event subscriptions:

```
Client
  │
  │  HTTP POST /process
  ▼
API Gateway  ──publishes──►  document.uploaded
                                   │
                         Validator subscribes
                                   │
              ┌────────────────────┴──────────────────────┐
              ▼ (pass)                                     ▼ (fail)
   document.validated                            document.invalid
              │                                            │
    Extractor subscribes                     Notifier + DL Handler subscribe
              │
  ┌───────────┴──────────────┐
  ▼ (success)                ▼ (fail → retry → exhausted)
extraction.completed     extraction.failed
  │                           │
Classifier subscribes    Notifier + DL Handler subscribe
  │
  ├──────────────────────────┐
  ▼ (success)                ▼ (fail → retry → exhausted)
classification.completed  classification.failed
  │                           │
Storage subscribes       Notifier + DL Handler subscribe
  │
  ├────────────────────────┐
  ▼ (success)              ▼ (fail → retry → exhausted)
document.stored         storage.failed
  │                          │
Notifier subscribes     Notifier + DL Handler subscribe
  │
  ▼
HTTP POST to callbackUrl (webhook / SSE / email)
```

The sequence — Validate → Extract → Classify → Store → Notify — is never written down anywhere in any single component. It is the consequence of each component subscribing to exactly the right upstream event and publishing exactly the right downstream event.

---

## 5. Advantage of the Choreographed Design

**Advantage: Each component scales independently with no coordination overhead**

Because no component calls another directly, each one can be scaled in complete isolation. When a batch client submits 500 scanned PDFs simultaneously, the Job Queue fills and the Extractor worker pool can be scaled out from 2 to 20 instances without touching the Classifier, Storage Service, Notifier, or any other component. Each worker simply consumes the next available event from the bus. The event bus absorbs the burst; the workers drain it at their natural throughput.

This is especially important for this pipeline because OCR processing is the bottleneck: it is slow, CPU-intensive, and highly variable in duration. A single scanned PDF may take 30 seconds; a 200-page document may take 10 minutes. In the orchestrated design, the Orchestrator must track all of these in-flight jobs and manage their timeouts centrally. In the choreographed design, the Extractor simply takes a job, works on it for as long as it takes, publishes the result, and takes the next. The bus handles back-pressure naturally. There is no coordination layer that can become a bottleneck.

---

## 6. Disadvantage of the Choreographed Design

**Disadvantage: The pipeline sequence is invisible — debugging a stuck job requires correlating events across multiple independent components**

When a client reports that their document has not been processed after 20 minutes, there is no single place to look. An operator must query the event bus logs for the `jobId` correlation ID, identify which was the last event successfully published, determine which component should have consumed that event and check whether it did, then inspect that component's own logs to find why it failed or stalled.

For this pipeline specifically, the problem compounds because OCR duration is legitimately variable — a job that has been "stuck" in the Extractor for 8 minutes may be processing normally, or it may have silently failed. Distinguishing between these requires inspecting the Extractor's internal metrics or setting up distributed tracing with full event correlation (e.g. OpenTelemetry with a shared `correlationId` propagated through every event). That infrastructure adds non-trivial operational complexity. In the orchestrated design, the same question — "where is job X right now?" — is answered by a single lookup in the Orchestrator's workflow history, in one service, in one query.

---

## 7. Component Summary

| Component | Subscribes to | Publishes | Terminal? |
|-----------|--------------|-----------|-----------|
| API Gateway | *(none)* | `document.uploaded` | No |
| Validator | `document.uploaded` | `document.validated`, `document.invalid` | No |
| Extractor | `document.validated` | `extraction.completed`, `extraction.failed` | No |
| Classifier | `extraction.completed` | `classification.completed`, `classification.failed` | No |
| Storage Service | `classification.completed` | `document.stored`, `storage.failed` | No |
| Notifier | `document.stored`, `*.failed` | *(none)* | Yes |
| Dead Letter Handler | `*.failed` | `document.dead_lettered` | Yes |
