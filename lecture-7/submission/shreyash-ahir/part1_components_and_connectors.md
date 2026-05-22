# Part 1.1 — Component and Connector Design

## Component Inventory

The pipeline decomposes into six application-specific components and relies on
two infrastructure connectors (a message queue and a shared database).  Each
component has one responsibility; the connectors between them determine timing
and coupling.

---

### Component 1: API Gateway

**Responsibility:** Accept document uploads from clients, validate request
format (not content), route to the sync or async path, and return the
response.

**Inputs:**
- HTTP POST with `multipart/form-data` (file) or JSON `{ "url": "..." }`
- Optional: `{ "mode": "sync" | "async", "webhook": "..." }`

**Outputs:**
- Sync mode: final `ExtractionResult` JSON (waits for pipeline to finish)
- Async mode: `{ "job_id": "..." }` immediately

**From caller's perspective:** Synchronous (HTTP request/response).  
Internally it may block waiting for the orchestrator, or may return immediately
with a job ID.

---

### Component 2: Validator

**Responsibility:** Confirm that the document is a supported type (PDF,
PNG, JPEG, TIFF), is within size limits, and is not corrupted.  Reject fast
before expensive work begins.

**Inputs:** Raw document bytes + metadata (file name, MIME type, size)

**Outputs:**
- Success: `{ "valid": true, "doc_id": "...", "mime_type": "..." }`
- Failure: `{ "valid": false, "reason": "..." }`

**From caller's perspective:** Synchronous — the orchestrator blocks on this
call because an invalid document should stop the pipeline immediately with a
clear error to the client.  Validation is cheap (milliseconds); making it
async would add latency and complexity with no benefit.

---

### Component 3: Extractor

**Responsibility:** Run OCR and text extraction on the validated document.
Returns structured text per page plus confidence scores.

**Inputs:** `{ "doc_id": "...", "storage_url": "...", "options": { "ocr": true } }`

**Outputs:** `{ "doc_id": "...", "pages": [{ "page": 1, "text": "..." }], "confidence": 0.97 }`

**From caller's perspective:** Asynchronous — OCR is CPU-intensive and can
take seconds to minutes for large documents.  In the async pipeline path this
runs in a worker after dequeuing.  In the sync path the orchestrator awaits
its result but does so after having already dispatched work off the HTTP
thread.

---

### Component 4: Classifier

**Responsibility:** Assign a document type label (invoice, contract, form,
report, other) from the extracted text.  Uses a lightweight ML classifier.

**Inputs:** `{ "doc_id": "...", "text": "..." }`

**Outputs:** `{ "doc_id": "...", "label": "invoice", "confidence": 0.91 }`

**From caller's perspective:** Asynchronous in the full pipeline; fast enough
(< 200 ms) that it runs synchronously within the async worker after extraction.

---

### Component 5: Storage

**Responsibility:** Persist the document file and its extraction result
(text, label, metadata) to durable storage.  Returns a stable document URL.

**Inputs:** Raw document bytes + `ExtractionResult`

**Outputs:** `{ "doc_id": "...", "file_url": "...", "result_url": "..." }`

**From caller's perspective:** Asynchronous — I/O bound.  Called after
classification; result is needed before Notifier fires.

---

### Component 6: Notifier

**Responsibility:** Deliver the final result to the client via the webhook
URL they supplied (if any), or update the job record so a polling client
can see it as done.

**Inputs:** `{ "job_id": "...", "webhook_url": "...", "result": { ... } }`

**Outputs:** HTTP POST to webhook (fire-and-forget with retries) or a status
write to the job store.

**From caller's perspective:** Asynchronous — decoupled from the processing
worker; runs after storage completes.

---

## Connector Inventory

### C1: HTTP (REST) — Client → API Gateway

| Property | Value |
|---|---|
| Type | REST over HTTP/HTTPS |
| Direction | Client → API Gateway |
| Sync/Async | Synchronous |
| Format | JSON + multipart/form-data |
| Coupling | Direct (client knows the API URL) |

Justification: HTTP is the standard web integration point. Synchronous
because the client must at least receive a job ID or a result.

---

### C2: Direct In-Process Call — API Gateway → Validator

| Property | Value |
|---|---|
| Type | Direct (in-process function call) |
| Sync/Async | Synchronous |
| Format | Internal function arguments (no serialization) |
| Coupling | Direct |

Justification: Validation is cheap and must fail fast.  Using a queue here
would add latency for a step that takes < 10 ms.  The API Gateway and
Validator run in the same process.  As the course notes: *synchronous
connectors require both components to be available at the same time* — here
that is acceptable because they are co-located.

---

### C3: Message Queue — API Gateway → Worker (async path)

| Property | Value |
|---|---|
| Type | Message queue (e.g. RabbitMQ / BullMQ) |
| Direction | API Gateway publishes; Worker subscribes |
| Sync/Async | Asynchronous |
| Format | JSON message: `{ "job_id", "doc_id", "storage_url", "options" }` |
| Coupling | Indirect — publisher and subscriber only agree on queue name |

Justification: Decouples upload acceptance from processing.  The API
Gateway returns `job_id` immediately without waiting for OCR.  If the
Extractor is slow or down, messages accumulate in the queue without
dropping — exactly the availability benefit of async connectors described
in the course material.

---

### C4: Direct In-Process Call — Worker: Extractor → Classifier

| Property | Value |
|---|---|
| Type | Direct in-process call |
| Sync/Async | Synchronous (within the worker process) |
| Format | Internal function call |
| Coupling | Direct |

Justification: Classification follows extraction in a fixed sequence inside
the same worker.  No availability benefit from a queue here; adding one
would increase latency and operational complexity for a 200 ms step.

---

### C5: Shared Database + Object Store — Worker → Storage

| Property | Value |
|---|---|
| Type | Shared database (PostgreSQL for metadata) + object store (S3) |
| Sync/Async | Synchronous call (await response before continuing) |
| Format | SQL INSERT + S3 PUT (JSON result, binary file) |
| Coupling | Indirect — components share a schema, not a direct call |

Justification: Storage must complete before the Notifier fires (so the
result URL exists).  The shared database is the correct connector here
because the result must outlive the process that produced it.

---

### C6: Message Queue — Worker → Notifier

| Property | Value |
|---|---|
| Type | Message queue (same bus as C3) |
| Direction | Worker publishes `job.complete`; Notifier subscribes |
| Sync/Async | Asynchronous |
| Format | JSON: `{ "job_id", "webhook_url", "result_url" }` |
| Coupling | Indirect |

Justification: Notification is fully decoupled from processing.  If the
webhook endpoint is slow or temporarily down, the Notifier can retry
independently without blocking or failing the worker.  This is the message
bus's key advantage: *components connected indirectly remain unaware of
each other's availability*.

---

### C7: HTTP (Webhook) — Notifier → Client

| Property | Value |
|---|---|
| Type | HTTP POST (outbound webhook) |
| Sync/Async | Asynchronous (fire-and-forget with retries) |
| Format | JSON: `{ "job_id", "status": "done", "result": { ... } }` |
| Coupling | Direct to webhook URL |

Justification: Webhook is the standard push notification pattern for async
APIs.  The Notifier retries on failure (exponential back-off, max 5 attempts)
before marking the job as notification-failed.

---

## Summary: Sync vs Async Justification

| Step | Connector | Sync/Async | Reason |
|---|---|---|---|
| Client → API | HTTP | Sync | Standard request/response |
| Validate | Direct call | Sync | Fast; fail-fast on bad input |
| Enqueue job | Message queue | Async | Decouple upload from processing |
| Extract text | Worker internal | Async (dequeued) | CPU-heavy; must not block HTTP thread |
| Classify | Direct call | Sync (in worker) | Fast; same process as extract |
| Store result | DB + object store | Sync (in worker) | Must complete before notify |
| Notify client | Message queue + webhook | Async | Decouple retry from worker lifecycle |
