# Part 1 – Component and Connector Design
## Document Processing Pipeline

**Assignment:** Composable Document Pipeline – Composition and Connectors  
**Chapter:** 7 – Composability and Connectors  
**Deliverable:** `part1_components_and_connectors.md`

---

## Architectural Framing

Before enumerating components, it is worth being precise about the C&C vocabulary used throughout this document, following Chapter 7.

- **Component** — an independently deployable unit with a well-defined interface, doing domain work (validation, extraction, classification, etc.). A component is a *box* in the C&C diagram.
- **Connector** — the mechanism that mediates communication between components: a synchronous call, a message queue, an event bus, etc. A connector is an *arrow with semantics* in the C&C diagram.
- **Infrastructure element** (Job Queue, Event Bus) — not pipeline components in the domain sense, but first-class architectural elements that realise specific connector types. They appear explicitly in the diagram as named infrastructure nodes rather than being hidden inside arrow labels.

This design exposes **five domain components** plus two named infrastructure elements. The API Gateway is treated as a true component (it has a deployable boundary, its own interface, and domain logic — routing, authentication, mode-splitting) while the Job Queue and Event Bus are connector infrastructure.

Both interaction modes are supported through a single, consistent component model:

- **Synchronous mode** — the client requests a result and the Gateway coordinates a blocking in-process call chain (Validator → Extractor-Sync → Classifier-Sync) capped by a configurable timeout (default 30 s). This path is restricted by a size threshold (≤ 5 MB, native-text only, no OCR) to keep latency bounded and predictable.
- **Asynchronous mode** — for any document exceeding the size threshold, requiring OCR, or explicitly requested by the client; the Gateway returns HTTP 202 immediately and the remaining stages execute as event-driven workers.

The two modes share the same component implementations. The Extractor and Classifier expose both a **direct-call interface** (used by the Gateway on the sync path) and a **queue-consumer interface** (used autonomously on the async path). This avoids maintaining two separate codebases at the cost of a slightly richer component interface, which is explicitly documented below.

---

## 1. Component Decomposition

### Component 1 – API Gateway

**Single Responsibility:** Accept all inbound document upload requests from clients (web app, batch job, API consumer), enforce authentication and rate limits, apply the sync/async routing decision, and return an appropriate HTTP response to the caller.

| Attribute | Detail |
|-----------|--------|
| **Inputs** | `HTTP POST /process` — `multipart/form-data` body containing the document file (binary bytes) **or** a `{ url }` JSON body for URL-referenced documents, plus options: `{ mode:"sync"\|"async", extractTextOnly:bool, fullOCR:bool, callbackUrl?:string }` |
| **Outputs — sync result** | `HTTP 200 OK` with body `{ jobId, status:"complete", schemaVersion:"1.0", extractedText, classification, confidence, structuredFields, processedAtMs }` |
| **Outputs — async receipt** | `HTTP 202 Accepted` with body `{ jobId, status:"pending", pollUrl:"/jobs/{jobId}" }` |
| **Outputs — validation failure** | `HTTP 400 / 413 / 415` with body `{ code:"VALIDATION_ERROR", reason, field? }` — returned before any queue or downstream interaction |
| **Sync / Async (caller view)** | **Always synchronous** — the client always receives an immediate HTTP response |

**Routing logic:** The Gateway applies the following decision in order:  
1. Call Validator (blocking, in-process). On failure → return 4xx immediately.  
2. If `mode=sync` AND `sizeBytes ≤ 5 MB` AND `mimeType` is a native-text format AND `fullOCR=false` → invoke Extractor and Classifier via their direct-call interfaces (blocking), return 200.  
3. Otherwise (any async trigger) → publish to Job Queue, return 202.

**Resilience:** The Gateway applies a 30-second hard timeout on the sync path. If the timeout fires, it automatically downgrades to async mode: it publishes the job to the queue, stores a `TIMEOUT_DOWNGRADE` status in the Storage Service, and returns `HTTP 202` with a note in the response body. The client is never left hanging.

**Status polling:** The Gateway owns the `GET /jobs/{jobId}` endpoint. It queries the Storage Service's read path (C12) with a 500 ms timeout and a circuit-breaker (3 failures in 10 s → open circuit, return `503 Retry-After: 5`).

---

### Component 2 – Validator

**Single Responsibility:** Verify that a received document satisfies all structural and policy prerequisites before any processing cost is incurred.

**Deployment boundary:** The Validator is deployed as a **separate microservice** reachable over an internal network, not an in-process library. This gives it an independently testable, scalable, and replaceable boundary consistent with the C&C definition of a component. The latency cost is minimal (sub-millisecond on the same LAN) and is accepted in exchange for true composability. The Gateway calls it via a lightweight internal REST call on the sync path (C2).

| Attribute | Detail |
|-----------|--------|
| **Inputs** | `{ documentId:uuid, bytes:Buffer, mimeType:string, sizeBytes:int, options:Options }` via internal REST `POST /validate` |
| **Outputs — success** | `HTTP 200` `{ documentId, mimeType, sizeBytes, detectedEncoding, pageCountEstimate, validatedAt }` |
| **Outputs — failure** | `HTTP 422` `{ code:"VALIDATION_ERROR", reason:string, field?:string, documentId }` |
| **Sync / Async (caller view)** | **Synchronous** — called as a blocking step before any routing decision is made |

**Checks performed:** MIME type detection (magic bytes, not just declared type), file size limit (configurable, default 500 MB), format well-formedness (PDF cross-reference table, JPEG SOI/EOI markers, etc.), absence of password encryption, virus/malware scan result (delegated to an internal ClamAV sidecar).

**Validation cost and the sync justification:** A critic may note that scanning 500 MB is not instantaneous. In practice, MIME detection and magic-byte checks complete in < 5 ms regardless of file size; the full integrity check (cross-reference table, structure validation) is bounded at 2 s by an internal timeout. If the integrity check exceeds 2 s, the Validator returns a partial-pass result flagging `integrityCheckSkipped:true`, and the Extractor performs its own integrity check before processing. This keeps the Gateway's blocking window bounded and predictable regardless of document size.

---

### Component 3 – Extractor

**Single Responsibility:** Extract the full textual content from a validated document. For native-text formats it parses the document structure directly; for image-based documents it invokes an OCR engine.

**Dual interface:** The Extractor exposes two interfaces sharing the same core implementation:
- **Direct-call interface** (sync path): `POST /extract` — internal REST, synchronous, used by the Gateway on the sync fast-lane.
- **Queue-consumer interface** (async path): AMQP worker that pulls from the Job Queue, used for all async jobs.

| Attribute | Detail |
|-----------|--------|
| **Inputs (direct call)** | `POST /extract` with `{ documentId, storageRef, options }` |
| **Inputs (queue)** | AMQP message: `{ jobId, documentId, storageRef, options, submittedAt }` |
| **Outputs (direct call)** | `HTTP 200` `{ jobId, documentId, rawText, pages:[{pageNumber,text,confidence}], ocrUsed:bool, durationMs, schemaVersion:"1.0" }` |
| **Outputs (queue/async)** | Event published to Event Bus, topic `extraction.completed`, same payload schema as above + `jobId` |
| **Sync / Async (caller view)** | **Synchronous** when called via direct interface; **Asynchronous** when consuming from the queue |

**Idempotency:** Each extraction job carries a `jobId` (UUID v4). If the Extractor receives the same `jobId` twice (e.g. due to at-least-once queue redelivery), it checks a Redis idempotency cache keyed by `jobId`. On a cache hit it re-publishes the cached result event without re-running OCR. Cache TTL is 24 hours.

**Error handling:** If extraction fails (corrupt file detected mid-stream, OCR engine crash), the Extractor publishes an `extraction.failed` event: `{ jobId, documentId, code, reason, attempt, maxAttempts:3 }`. After three failed attempts the job is moved to a dead-letter queue and the Storage Service is updated with status `FAILED`.

**Scaling:** Multiple Extractor instances consume from the same AMQP queue. OCR-heavy jobs are naturally load-balanced across available workers. Prefetch count is set to 1 so a slow OCR job does not block a worker from picking up fast text-extraction jobs.

---

### Component 4 – Classifier

**Single Responsibility:** Analyse extracted text to assign a document category and extract the structured fields relevant to that category.

**Dual interface:** Like the Extractor, the Classifier exposes both a direct-call interface (used by the Gateway on the sync path after extraction) and an event-driven interface (subscribed to `extraction.completed` on the async path).

| Attribute | Detail |
|-----------|--------|
| **Inputs (direct call)** | `POST /classify` with `{ jobId, documentId, rawText, pages, options }` |
| **Inputs (event)** | Event from Event Bus, topic `extraction.completed`: same payload |
| **Outputs (direct call)** | `HTTP 200` `{ jobId, documentId, category, confidence, structuredFields:{[name]:value}, schemaVersion:"1.0", classifiedAt }` |
| **Outputs (event)** | Event published to Event Bus, topic `classification.completed`, same payload schema |
| **Sync / Async (caller view)** | **Synchronous** when called via direct interface; **Asynchronous** when subscribing to the event bus |

**Supported categories:** invoice, purchase order, tax form, contract, identity document, medical record, bank statement, other.

**Idempotency:** Same pattern as the Extractor — `jobId`-keyed Redis cache with 24-hour TTL. A duplicate `extraction.completed` event for the same `jobId` is detected and dropped before any ML inference is invoked.

**Schema versioning:** All events carry `schemaVersion:"1.0"`. The Classifier reads this field before processing. If it receives an event with an unrecognised schema version it publishes a `classification.failed` event with `code:"UNSUPPORTED_SCHEMA_VERSION"` rather than silently producing garbage output. This is the mechanism that decouples the Classifier from schema changes in the Extractor — a new Extractor schema version is deployed alongside a Classifier version that handles it, with the old version rejecting unknown schemas rather than corrupting data.

**Error handling:** Classification failures (ML service unavailable, confidence below minimum threshold) publish a `classification.failed` event with the same retry/dead-letter pattern as the Extractor.

---

### Component 5 – Storage Service

**Single Responsibility:** Persist all pipeline artefacts to durable storage, maintain the canonical job status record, and emit a `document.stored` event when all writes are committed.

| Attribute | Detail |
|-----------|--------|
| **Inputs** | Event from Event Bus, topic `classification.completed`: `{ jobId, documentId, category, confidence, structuredFields, schemaVersion, classifiedAt }` |
| **Write outputs** | Document bytes → Object Store (S3-compatible); extracted text + structured fields → Document Database (MongoDB); job status record updated to `COMPLETE` or `FAILED` in a Status Store (PostgreSQL) |
| **Event output** | Event published to Event Bus, topic `document.stored`: `{ jobId, documentId, status, callbackUrl?, clientId, schemaVersion:"1.0", storedAt }` |
| **Read output** | Synchronous `GET /internal/jobs/{jobId}` → `{ jobId, status, result?, updatedAt }` — used by the API Gateway for polling clients |
| **Sync / Async (caller view)** | **Asynchronous** (event-driven write path); **Synchronous** (read path only) |

**Idempotency:** The Status Store uses a unique constraint on `jobId`. If the same `classification.completed` event is delivered twice, the second write attempt fails silently (upsert with `ON CONFLICT DO NOTHING`) and the `document.stored` event is still published (idempotent publish via outbox pattern).

**Transactional integrity:** All three writes (object store, document database, status store) are coordinated via a local saga with compensating actions. If the object store write succeeds but the database write fails, the object store write is rolled back before the error is surfaced.

**Resilience of C12 (status poll):** The read path is served from a read replica with a 500 ms query timeout. The API Gateway applies a circuit-breaker (see Component 1). Cache-aside with a 2-second TTL is applied for high-frequency pollers.

---

### Component 6 – Notifier

**Single Responsibility:** Deliver the final processing outcome to the originating client via the appropriate channel once the Storage Service has confirmed all writes are durable.

| Attribute | Detail |
|-----------|--------|
| **Inputs** | Event from Event Bus, topic `document.stored`: `{ jobId, documentId, status, callbackUrl?, clientId, storedAt }` |
| **Outputs** | Outbound `HTTP POST` to `callbackUrl` (webhook) **or** SSE frame to connected web client **or** SMTP email — all carrying `{ jobId, status, result }` |
| **Sync / Async (caller view)** | **Asynchronous** — fire-and-forget from the pipeline's perspective |

**Webhook security:** Outbound webhook POSTs are signed with HMAC-SHA256 using a shared secret established at client registration. The signature is delivered in the `X-Pipeline-Signature: sha256=<hex>` header, allowing the client to verify authenticity. The `callbackUrl` is validated at job submission time against an allowlist to prevent SSRF attacks — only HTTPS URLs are accepted, and the host is checked against a blocklist of RFC 1918 private ranges.

**Idempotency:** The Notifier logs each delivered `jobId` to a delivered-set in Redis (TTL 48 h). Duplicate `document.stored` events for the same `jobId` are detected and dropped before any outbound call is made.

**Retry policy:** Failed webhook deliveries are retried with truncated exponential back-off: 3 attempts at 5 s, 25 s, and 125 s. After three failures the job is written to a dead-letter log and an internal alert is raised. The client may re-request delivery via `POST /jobs/{jobId}/notify`.

**Channel routing:** The Notifier determines the delivery channel from the `clientId` — the channel preference (webhook URL, SSE connection ID, email address) is looked up from a client registry at delivery time, not stored in the event payload.

---

### Component Summary Table

| # | Component | Single Responsibility | Deployment Boundary | Sync / Async (caller view) |
|---|-----------|-----------------------|--------------------|-----------------------------|
| 1 | API Gateway | Route, auth, mode-split, timeout guard | Standalone service | Sync (always returns immediately) |
| 2 | Validator | Format, integrity, size, malware check | Standalone microservice | Sync |
| 3 | Extractor | Text extraction / OCR | Scalable worker pool | Sync (direct call) or Async (queue) |
| 4 | Classifier | Document category + structured fields | Scalable worker pool | Sync (direct call) or Async (event) |
| 5 | Storage Service | Persist results, maintain job status | Standalone service | Async (write); Sync (read) |
| 6 | Notifier | Deliver outcome to client | Standalone service | Async |

---

## 2. Connector Definitions

The table below enumerates every communicating pair, the connector used, and the protocol/format. Connector IDs match the labels in the Task 1.2 diagram.

| ID | From | To | Connector Name | Connector Type | Sync / Async | Protocol / Format | Idempotency / Delivery |
|----|------|----|----------------|----------------|--------------|-------------------|------------------------|
| **C1** | External Client | API Gateway | Client–Gateway HTTP | REST over HTTPS | **Sync** | HTTP/1.1 + TLS 1.3; `multipart/form-data` upload; response `application/json`; schema version in `X-Schema-Version` header | Stateless; client retries on 5xx with idempotency key in `Idempotency-Key` header |
| **C2** | API Gateway | Validator | Gateway–Validator Internal REST | REST (internal) | **Sync** | `POST /validate` over internal HTTP; `application/json`; 2 s timeout | At-most-once; failure returns 4xx to client immediately |
| **C3** | API Gateway | Job Queue | Job Submission | Message Queue (producer) | **Async** | AMQP 0-9-1 (RabbitMQ); persistent messages; JSON body: `{ jobId, documentRef, options, callbackUrl, schemaVersion:"1.0", submittedAt }` | At-least-once; publisher confirms enabled |
| **C4** | Job Queue | Extractor | Job Dispatch | Message Queue (consumer) | **Async** | AMQP; prefetch=1; manual ack after successful processing; nack+requeue on failure up to 3 attempts | At-least-once; idempotency via `jobId` Redis cache in Extractor |
| **C5** | Extractor | Event Bus | Extraction Complete | Event Bus (publish) | **Async** | Topic `extraction.completed`; JSON; `schemaVersion:"1.0"`; transactional outbox pattern ensures publish-after-commit | At-least-once; idempotency enforced by consumers |
| **C6** | Event Bus | Classifier | Extraction Event Subscription | Event Bus (subscribe) | **Async** | Topic `extraction.completed`; durable consumer group; push delivery | At-least-once; Classifier deduplicates by `jobId` |
| **C6b** | Event Bus | Extractor (sync→async fallback) | Extraction Timeout Subscription | Event Bus (subscribe) | **Async** | Topic `extraction.timeout`; used when Gateway downgrades sync→async mid-flight | At-least-once |
| **C7** | Classifier | Event Bus | Classification Complete | Event Bus (publish) | **Async** | Topic `classification.completed`; JSON; `schemaVersion:"1.0"`; outbox pattern | At-least-once; idempotency enforced by consumers |
| **C8** | Event Bus | Storage Service | Classification Event Subscription | Event Bus (subscribe) | **Async** | Topic `classification.completed`; durable consumer group; push delivery | At-least-once; Storage deduplicates by `jobId` via DB unique constraint |
| **C9** | Storage Service | Event Bus | Document Stored | Event Bus (publish) | **Async** | Topic `document.stored`; JSON; `schemaVersion:"1.0"`; outbox pattern | At-least-once; idempotency enforced by consumers |
| **C10** | Event Bus | Notifier | Stored Event Subscription | Event Bus (subscribe) | **Async** | Topic `document.stored`; durable consumer group; push delivery | At-least-once; Notifier deduplicates by `jobId` via Redis delivered-set |
| **C11** | Notifier | External Client | Outbound Notification | Webhook / SSE / WebSocket / SMTP | **Async** | `HTTPS POST` signed with `HMAC-SHA256`; `application/json`; `X-Pipeline-Signature` header; SSRF-safe URL validation | Retry: 3 attempts with truncated exponential back-off; dead-letter on exhaustion |
| **C12** | API Gateway | Storage Service | Job Status Poll | REST (internal read path) | **Sync** | `GET /internal/jobs/{jobId}`; `application/json`; 500 ms timeout; circuit-breaker on Gateway side; cache-aside TTL 2 s | Read-only; idempotent by nature |

---

### Connector Infrastructure Nodes

**Job Queue** (realises connectors C3/C4): An AMQP message queue (e.g. RabbitMQ) providing work-queue semantics — exactly one Extractor worker processes each job message, messages are persisted to disk, and unacknowledged messages are requeued after a visibility timeout. This is the correct connector for "distribute this unit of work to exactly one worker." A separate dead-letter queue receives messages that have exhausted their retry limit.

**Event Bus** (realises connectors C5–C10): A durable pub/sub broker (e.g. Apache Kafka or RabbitMQ topic exchanges with durable queues) allowing multiple independent consumers to subscribe to the same event stream without coupling to each other or to the producer. This is the correct connector for "broadcast this fact to all interested parties." Adding a new consumer (e.g. an Audit Logger subscribing to `classification.completed`) requires zero changes to any existing component.

---

## 3. Sync vs. Async Justification

### Synchronous Connectors

**C1 — Client to API Gateway (REST HTTPS)**  
HTTP is fundamentally request/response. Every client must receive either a final result (sync mode) or an immediate `202 + jobId` (async mode) before the connection closes. This is a protocol constraint, not a design choice.

**C2 — API Gateway to Validator (internal REST)**  
The Gateway cannot make a routing decision — enqueue async job vs. execute sync pipeline — without first knowing whether the document is valid. Validation is therefore a mandatory precondition that must complete before any other action. Making it asynchronous would require the client to wait for a "validation failed" event they cannot use until they poll again: an unnecessary round-trip for a step that takes at most 2 seconds and gates everything else. Fast-fail on bad input is a first-class requirement. The Validator is a separate microservice (not an in-process library) to maintain a clean component boundary, independent deployability, and the ability to scale or replace it independently; the sub-millisecond LAN latency cost is negligible.

**C12 — API Gateway to Storage Service (status poll)**  
Polling clients issue point-in-time reads. The read path is a simple indexed query (< 5 ms on a read replica) served behind a 500 ms timeout and a circuit-breaker. Adding queue or bus indirection to a trivial read would increase latency, add infrastructure complexity, and provide no scalability benefit.

### Asynchronous Connectors

**C3/C4 — Job Queue (Gateway → Queue → Extractor)**  
OCR on a multi-page scanned PDF can take 30 seconds to several minutes. No HTTP connection can remain open that long, nor should any client be forced to wait. The message queue also absorbs burst traffic (e.g. a batch client uploading 500 documents simultaneously) without overwhelming the fixed-size worker pool — the queue acts as a buffer that smooths demand spikes.

**C5/C6 — Event Bus: extraction.completed (Extractor → Classifier)**  
The Classifier's dependency on completed extraction is expressed as an event subscription rather than a direct call for three reasons: (1) the Extractor does not need to know the Classifier exists — new consumers can be added without touching the Extractor; (2) if the Classifier is temporarily unavailable, the event remains on the bus and is delivered when the Classifier recovers, with no data loss; (3) multiple consumers (Classifier, Audit Logger, Monitoring) can all react to the same event independently.

**C7/C8 — Event Bus: classification.completed (Classifier → Storage)**  
Storage I/O (object store uploads, database writes) is the most I/O-intensive and failure-prone stage. Decoupling via the event bus means a transient storage failure does not propagate back to the Classifier: the event remains on the bus, and the Storage Service retries its write independently. The saga-with-compensation pattern within the Storage Service handles partial write failures without any upstream component being aware.

**C9/C10 — Event Bus: document.stored (Storage → Notifier)**  
Notifications are a side-effect of pipeline completion, not part of processing. Triggering the Notifier via an event means: (1) the Storage Service does not need to know which notification channels exist; (2) adding a new channel (SMS, Slack) requires only a new subscriber with zero changes to any other component; (3) notification failures do not affect the stored data or the job status.

**C11 — Notifier to Client (webhook / SSE / email)**  
By the time the Notifier acts, the async pipeline has been running for potentially minutes. The client cannot hold an open connection that long. Push notification is the only viable pattern. Polling via C12 is provided as an explicit fallback for clients that cannot accept webhooks.

### Decision Table

| Connector | Decision | Primary Justification |
|-----------|----------|-----------------------|
| C1 – Client → Gateway | **Sync** | HTTP protocol constraint; client must receive a receipt |
| C2 – Gateway → Validator | **Sync** | Mandatory pre-routing gate; fast-fail; 2 s bounded latency |
| C3 – Gateway → Job Queue | **Async** | OCR latency unbounded; burst absorption; immediate 202 |
| C4 – Queue → Extractor | **Async** | Work-queue distribution; one worker per job; retry on failure |
| C5 – Extractor → Bus | **Async** | Decouples producer from N consumers; resilient to consumer downtime |
| C6 – Bus → Classifier | **Async** | Triggered only when data is ready; no polling; independent scaling |
| C7 – Classifier → Bus | **Async** | Same rationale as C5; storage failures do not propagate upstream |
| C8 – Bus → Storage | **Async** | Resilient to I/O failures; retry within Storage without upstream impact |
| C9 – Storage → Bus | **Async** | Notification is a side-effect; decouples Storage from channel knowledge |
| C10 – Bus → Notifier | **Async** | Independent scaling; new channels added without touching other components |
| C11 – Notifier → Client | **Async** | Pipeline duration exceeds any viable HTTP timeout; push is the only option |
| C12 – Gateway → Storage (poll) | **Sync** | Point-in-time read; < 5 ms; no benefit from indirection |

---

## 4. Cross-Cutting Concerns

### Idempotency

Because all async connectors use at-least-once delivery, every consumer must be idempotent — receiving the same event twice must produce the same outcome as receiving it once. The strategy applied at each stage:

| Consumer | Idempotency Mechanism |
|----------|-----------------------|
| Extractor | Redis cache keyed by `jobId`; hit → re-publish cached result, skip OCR |
| Classifier | Redis cache keyed by `jobId`; hit → re-publish cached result, skip ML inference |
| Storage Service | DB unique constraint on `jobId`; duplicate write silently ignored (upsert) |
| Notifier | Redis delivered-set keyed by `jobId`; hit → drop event, no outbound call |

### Error Propagation

Each component publishes a failure event on error, following a consistent pattern:

```
extraction.failed   { jobId, documentId, code, reason, attempt, maxAttempts:3 }
classification.failed { jobId, documentId, code, reason, attempt, maxAttempts:3 }
storage.failed      { jobId, documentId, code, reason, attempt, maxAttempts:3 }
```

After `maxAttempts` are exhausted:
1. The job message is moved to the dead-letter queue.
2. The Storage Service updates the job status to `FAILED` with the error detail.
3. The Notifier receives the `document.stored` event (with `status:"FAILED"`) and notifies the client of the failure via the same delivery channel as a success.

This means the client always receives a terminal notification — either a success or a structured failure — and never waits indefinitely.

### Schema Versioning and Connector Evolution

All event payloads carry a `schemaVersion` field (currently `"1.0"`). When a schema change is needed:

1. The producing component publishes the new schema version alongside the old (dual-publish during a migration window).
2. Consuming components declare which schema versions they support. An unsupported version triggers a `*.failed` event with `code:"UNSUPPORTED_SCHEMA_VERSION"` rather than silent data corruption.
3. Once all consumers have been upgraded, the old schema version is retired and dual-publish is stopped.

This pattern directly realises the composability principle from Chapter 7: components are substitutable independently as long as they honour the connector contract, and the schema version field makes that contract explicit and verifiable at runtime.

### Sync Path Timeout and Downgrade

The sync path is bounded at 30 seconds. If the Extractor or Classifier does not return within this window:

1. The Gateway cancels the blocking call.
2. The document reference (already stored in the object store at the start of the request) is enqueued as an async job via C3.
3. The Gateway returns `HTTP 202` with `{ jobId, status:"pending", note:"Downgraded to async due to processing time" }`.
4. The client is informed and can poll via C12 or wait for a webhook via C11.

This makes the sync/async boundary a runtime concern rather than a deployment concern — the same components serve both paths.

---

## 5. End-to-End Flow Diagrams

### Synchronous Flow (web app, ≤ 5 MB native-text PDF, mode=`sync`)

```
Client
  │
  │  C1: HTTP POST /process (multipart, mode=sync)
  ▼
API Gateway
  │
  │  C2: POST /validate (internal REST, sync, ≤2 s)
  ▼
Validator ──► [pass] ──► API Gateway
                             │
                             │  Direct call: POST /extract (sync, ≤30 s total)
                             ▼
                         Extractor
                             │  returns ExtractionResult inline
                             ▼
                         API Gateway
                             │
                             │  Direct call: POST /classify (sync)
                             ▼
                         Classifier
                             │  returns ClassificationResult inline
                             ▼
                         API Gateway
                             │
                             │  C1: HTTP 200 { extractedText, classification, structuredFields }
                             ▼
                          Client ✓
```

### Asynchronous Flow (batch job, scanned PDF, mode=`async` or timeout downgrade)

```
Client
  │
  │  C1: HTTP POST /process (multipart, mode=async)
  ▼
API Gateway
  │
  │  C2: POST /validate (sync, ≤2 s)
  ▼
Validator ──► [pass] ──► API Gateway
                             │
                             │  C1: HTTP 202 { jobId, pollUrl }   ← client unblocked here
                             │  C3: AMQP publish to Job Queue
                             ▼
                          Job Queue
                             │
                             │  C4: AMQP consume (prefetch=1, manual ack)
                             ▼
                          Extractor
                             │  [on success]
                             │  C5: publish extraction.completed to Event Bus
                             │  [on failure after 3 attempts]
                             â→ dead-letter queue → Storage.FAILED → Notifier
                             ▼
                          Event Bus (topic: extraction.completed)
                             │
                             │  C6: push to Classifier (durable subscriber)
                             ▼
                          Classifier
                             │  [on success]
                             │  C7: publish classification.completed to Event Bus
                             │  [on failure r 3 attempts]
                             │  → dead-letter queue → Storage.FAILED → Notifier
                             ▼
                          Event Bus (topic: classification.completed)
                             │
                             │  C8: push to Storage Service (durable subscriber)
                             ▼
                          Storage Service
                             │  writes: Object Store + Document DB + Status Store
                             │: publish document.stored to Event Bus
                             ▼
                          Event Bus (topic: document.stored)
                             │
                             │  C10: push to Notifier (durable subscriber)
                             ▼
                          Notifier
                             │  validates SSRF, signs payload, delivers with retry
                             │  C11: HTTPS POST to callbackUrl (signed webhook)
                             ▼
            Client ✓ (receives { jobId, status, result })

Client may poll at any time:
  GET /jobs/{jobId} ──[C12: internal REST, sync]──► Storage Service read path
```
