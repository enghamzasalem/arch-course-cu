# Part 3 – API and Usage
## Task 3.1: Pipeline API Design

**Assignment:** Composable Document Pipeline – Composition and Connectors  
**Chapter:** 7 – Composability and Connectors  
**Deliverable:** `part3_api_design.md`

---

## 1. API Overview

The pipeline exposes a versioned REST API under the base path `/api/v1/pipeline`. All requests and responses use `application/json` unless the endpoint accepts a file upload, in which case `multipart/form-data` is used. All responses include a `Content-Type: application/json` header and a `X-Request-Id` header containing the server-assigned request trace ID.

Authentication uses Bearer tokens (`Authorization: Bearer <token>`). Rate limiting is enforced at the API Gateway: 100 requests/minute per token for synchronous endpoints, 500 requests/minute for asynchronous job submission.

---

## 2. Endpoints

### 2.1 Synchronous Endpoint — `POST /api/v1/pipeline/run`

Submits a document for immediate, blocking processing. The connection is held open until the pipeline completes and the full result is returned in the response body. Suitable for small, native-text documents where the client requires an inline result.

**Constraints:** Maximum document size 5 MB. OCR (`fullOCR: true`) is not permitted on this endpoint — it is redirected automatically to the async path. If processing exceeds the 30-second server timeout, the server downgrades automatically to async, closes the connection with `HTTP 202`, and the client may poll for the result.

#### Request

```
POST /api/v1/pipeline/run
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | binary | Yes (or `url`) | Document file bytes (PDF, PNG, JPEG, TIFF, DOCX) |
| `url` | string | Yes (or `file`) | HTTPS URL to a remotely hosted document |
| `extractTextOnly` | boolean | No (default: `false`) | Skip classification; return extracted text only |
| `language` | string | No (default: `"en"`) | BCP-47 language hint for OCR (e.g. `"de"`, `"fr"`) |

#### Success response — `HTTP 200 OK`

```json
{
  "jobId":          "a3f2c1d4-...",
  "status":         "complete",
  "schemaVersion":  "1.0",
  "document": {
    "mimeType":     "application/pdf",
    "sizeBytes":    204800,
    "pageCount":    3
  },
  "extraction": {
    "rawText":      "Invoice No. 4821\nDate: ...",
    "pages": [
      { "pageNumber": 1, "text": "...", "confidence": 0.98 },
      { "pageNumber": 2, "text": "...", "confidence": 0.97 }
    ],
    "ocrUsed":      false,
    "durationMs":   412
  },
  "classification": {
    "category":     "invoice",
    "confidence":   0.94,
    "structuredFields": {
      "invoiceNumber": "4821",
      "vendorName":    "Acme Corp",
      "totalAmount":   "£1,250.00",
      "invoiceDate":   "2026-03-01"
    }
  },
  "processedAtMs":  1711929600000
}
```

#### Timeout downgrade response — `HTTP 202 Accepted`

Returned when the 30-second timeout fires before processing completes. The job continues asynchronously.

```json
{
  "jobId":   "a3f2c1d4-...",
  "status":  "pending",
  "note":    "Processing time exceeded sync threshold. Job continues asynchronously.",
  "pollUrl": "/api/v1/pipeline/jobs/a3f2c1d4-..."
}
```

#### Validation error response — `HTTP 422 Unprocessable Entity`

```json
{
  "status": "failed",
  "error": {
    "code":   "VALIDATION_ERROR",
    "reason": "File type not supported",
    "field":  "file"
  }
}
```

---

### 2.2 Asynchronous Job Submission — `POST /api/v1/pipeline/jobs`

Submits a document for background processing. Returns immediately with a `jobId`. The client either polls for the result or provides a `callbackUrl` to receive a webhook push when done. No size restriction beyond the server upload limit (500 MB). Supports OCR.

#### Request

```
POST /api/v1/pipeline/jobs
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | binary | Yes (or `url`) | Document file bytes |
| `url` | string | Yes (or `file`) | HTTPS URL to a remotely hosted document |
| `extractTextOnly` | boolean | No (default: `false`) | Skip classification |
| `fullOCR` | boolean | No (default: `false`) | Force full OCR even on native-text documents |
| `language` | string | No (default: `"en"`) | BCP-47 language hint |
| `callbackUrl` | string | No | HTTPS webhook URL to notify on completion |
| `idempotencyKey` | string | No | Client-supplied key; identical key within 24 h returns the same `jobId` without re-processing |

#### Success response — `HTTP 202 Accepted`

```json
{
  "jobId":     "b7e4d2f9-...",
  "status":    "pending",
  "pollUrl":   "/api/v1/pipeline/jobs/b7e4d2f9-...",
  "createdAt": "2026-03-21T10:00:00Z"
}
```

#### Validation error response — `HTTP 422 Unprocessable Entity`

Same structure as the sync endpoint. Validation is synchronous on both paths — bad documents are rejected before any queue interaction.

---

### 2.3 Job Status and Result — `GET /api/v1/pipeline/jobs/{job_id}`

Retrieves the current status of an async job, and the full result if the job has completed.

#### Request

```
GET /api/v1/pipeline/jobs/b7e4d2f9-...
Authorization: Bearer <token>
```

#### Response — job in progress — `HTTP 200 OK`

```json
{
  "jobId":      "b7e4d2f9-...",
  "status":     "processing",
  "currentStep": "extraction",
  "createdAt":  "2026-03-21T10:00:00Z",
  "updatedAt":  "2026-03-21T10:00:08Z"
}
```

#### Response — job complete — `HTTP 200 OK`

```json
{
  "jobId":         "b7e4d2f9-...",
  "status":        "complete",
  "schemaVersion": "1.0",
  "document": { ... },
  "extraction": { ... },
  "classification": { ... },
  "processedAtMs": 1711929660000
}
```

The `extraction` and `classification` objects have the same structure as the sync `POST /run` response.

#### Response — job failed — `HTTP 200 OK`

```json
{
  "jobId":      "b7e4d2f9-...",
  "status":     "failed",
  "failedStep": "extraction",
  "error": {
    "code":   "EXTRACTION_ERROR",
    "reason": "Document is password-protected and cannot be parsed"
  },
  "updatedAt":  "2026-03-21T10:02:14Z"
}
```

Note: a failed job returns `HTTP 200` with a `status: "failed"` body rather than a 4xx or 5xx. The request itself succeeded — the pipeline ran and produced a terminal result. A 4xx would mean the request was malformed; a 5xx would mean the server itself failed.

#### Response — job not found — `HTTP 404 Not Found`

```json
{
  "error": {
    "code":   "JOB_NOT_FOUND",
    "reason": "No job exists with the given ID, or it has expired"
  }
}
```

---

### 2.4 Webhook Notification (push, no polling required)

When `callbackUrl` is provided in the async job submission, the Notifier component delivers the result via an outbound `HTTP POST` to that URL once the job reaches a terminal state (complete or failed). The client does not need to poll.

#### Outbound webhook request

```
POST <callbackUrl>
Content-Type: application/json
X-Pipeline-Signature: sha256=<hmac-sha256-hex>
X-Pipeline-Job-Id: b7e4d2f9-...
X-Pipeline-Event: document.stored
```

The body is identical to the `GET /jobs/{job_id}` complete or failed response.

**Signature verification:** The `X-Pipeline-Signature` header contains an HMAC-SHA256 of the raw request body, keyed with the client's webhook secret established at registration. Clients must verify this header before trusting the payload.

**Retry policy:** If the webhook endpoint returns a non-2xx response or times out (10 s), the Notifier retries with truncated exponential back-off: 3 attempts at 5 s, 25 s, and 125 s. After exhaustion the delivery is logged and the client may retrieve the result via polling.

---

### 2.5 Endpoint Summary

| Method | Path | Mode | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/pipeline/run` | Sync | Submit document; receive full result in response |
| `POST` | `/api/v1/pipeline/jobs` | Async | Submit document; receive `jobId` immediately |
| `GET` | `/api/v1/pipeline/jobs/{job_id}` | Sync read | Poll for job status and result |
| `POST` | `<callbackUrl>` (outbound) | Async push | Webhook delivery of result to client |

---

## 3. How the Sync Path Uses the Components

When a client calls `POST /api/v1/pipeline/run`, the API Gateway executes the following sequence, holding the HTTP connection open throughout:

```
Client (HTTP connection held open)
  │
  │  POST /api/v1/pipeline/run
  ▼
API Gateway
  │
  │  C2: POST /validate  (internal REST, sync, ≤2 s)
  ▼
Validator ──► pass ──► API Gateway
  │
  │  Direct call: POST /extract  (internal REST, sync, ≤30 s total budget)
  ▼
Extractor ──► ExtractionResult ──► API Gateway
  │
  │  Direct call: POST /classify  (internal REST, sync)
  ▼
Classifier ──► ClassificationResult ──► API Gateway
  │
  │  Assembles full result payload
  │
  └──► HTTP 200 { jobId, extraction, classification, ... }
```

**Component roles on the sync path:**

The **Validator** is called first, synchronously and blockingly, via its internal REST interface (`POST /validate`). If it returns a failure, the Gateway immediately returns `HTTP 422` to the client — no further components are invoked. Validation is bounded to 2 seconds by an internal timeout within the Validator service.

The **Extractor** is called via its direct-call interface (`POST /extract`) — not via the Job Queue. This is the dual-interface design described in Part 1: the Extractor exposes both a REST interface for the sync fast-lane and an AMQP consumer for the async path, sharing the same core implementation. The Gateway enforces a 30-second hard timeout across the Extractor and Classifier calls combined.

The **Classifier** is called via its direct-call interface (`POST /classify`) with the extraction result as the request body. It returns a synchronous classification result.

The **Storage Service and Notifier are not invoked on the sync path.** The result is assembled in-memory by the Gateway and returned directly. The client has the result; there is nothing to store asynchronously or notify about. A lightweight status record (`jobId → COMPLETE`) is written by the Gateway as a fire-and-forget call to the Storage Service's status endpoint so that the `GET /jobs/{job_id}` endpoint can respond correctly if the client queries it later.

**Timeout downgrade:** If the combined Extractor + Classifier call budget exceeds 30 seconds, the Gateway cancels the blocking call, enqueues the job on the Job Queue (C3), writes a `TIMEOUT_DOWNGRADE` status, and returns `HTTP 202` to the client with the `jobId` and `pollUrl`. The Extractor continues processing the document autonomously and the async path completes as normal.

---

## 4. How the Async Path Uses the Queue and Events

When a client calls `POST /api/v1/pipeline/jobs`, the API Gateway returns `HTTP 202` immediately and the pipeline runs entirely through the event-driven infrastructure described in Part 2.2:

```
Client
  │
  │  POST /api/v1/pipeline/jobs
  ▼
API Gateway
  │  Validates auth, stores document bytes to object store, assigns jobId
  │  Writes job status: PENDING
  │  C3: publishes document.uploaded to Job Queue (AMQP)
  │
  └──► HTTP 202 { jobId, pollUrl }  ← client unblocked immediately
         (connection closed)

                 ┌─────────────────────────────────────┐
                 │         Async pipeline               │
                 │                                     │
                 │  Job Queue ──C4──► Extractor         │
                 │                      │               │
                 │             C5: extraction.completed │
                 │                      ▼               │
                 │               Event Bus              │
                 │                      │               │
                 │             C6: subscribe            │
                 │                      ▼               │
                 │                 Classifier           │
                 │                      │               │
                 │       C7: classification.completed   │
                 │                      ▼               │
                 │               Event Bus              │
                 │                      │               │
                 │             C8: subscribe            │
                 │                      ▼               │
                 │             Storage Service          │
                 │           (writes all artefacts)     │
                 │                      │               │
                 │          C9: document.stored         │
                 │                      ▼               │
                 │               Event Bus              │
                 │                      │               │
                 │            C10: subscribe            │
                 │                      ▼               │
                 │                 Notifier             │
                 │                      │               │
                 └─────────────────────┼───────────────┘
                                       │
                        C11: HTTP POST to callbackUrl
                        (or SSE push / email)
                                       ▼
                                    Client
                        receives { jobId, status, result }
```

**Component roles on the async path:**

The **Job Queue** (AMQP, RabbitMQ) holds job messages durably. If no Extractor worker is available, the message waits. This is what decouples the API Gateway's `HTTP 202` response from the actual processing time — the client is unblocked the moment the message is enqueued, not when OCR completes.

The **Extractor** pulls jobs from the queue with `prefetch=1` (one job per worker at a time) and acknowledges only after successfully publishing `extraction.completed`. If the Extractor crashes mid-job, the unacknowledged message is requeued and picked up by another worker.

The **Event Bus** (Kafka or RabbitMQ topic exchanges) carries all inter-stage events after extraction. Each stage publishes its result to a named topic; the next stage subscribes. No stage knows which component will consume its event — the coupling runs only through the topic name and the shared event schema.

The **Storage Service** is the only component that writes a durable job status record. The `GET /api/v1/pipeline/jobs/{job_id}` endpoint on the API Gateway reads from this record, giving the client a consistent status view regardless of whether they are polling or waiting for a webhook.

The **Notifier** is triggered by the `document.stored` event. If `callbackUrl` was provided in the original request, it delivers the result via webhook. If the client is a web-app holding an SSE connection, it pushes the result over that connection. If neither is available, the result is available via polling only.

**Client polling:** At any point after receiving the `HTTP 202`, the client may call `GET /api/v1/pipeline/jobs/{job_id}`. The API Gateway queries the Storage Service's read path (C12, synchronous internal REST) and returns the current job status. The `currentStep` field in the in-progress response reflects the last event written to the status store, giving the client a coarse-grained progress indicator.

---

## 5. Error Handling Summary

| Scenario | Sync path response | Async path response |
|----------|--------------------|---------------------|
| Invalid document (bad format, malware) | `HTTP 422` immediately | `HTTP 422` immediately (validation is sync on both paths) |
| Extraction fails after 3 retries | `HTTP 500` with error detail | `GET /jobs/{id}` returns `status: failed`; webhook delivers failure notification |
| Classification fails after 3 retries | `HTTP 500` with error detail | Same as above |
| Sync timeout (>30 s) | `HTTP 202` — auto-downgrade to async | N/A |
| Storage unavailable | `HTTP 500` | `GET /jobs/{id}` returns `status: failed` |
| Webhook delivery fails | N/A | Client polls via `GET /jobs/{id}` |
