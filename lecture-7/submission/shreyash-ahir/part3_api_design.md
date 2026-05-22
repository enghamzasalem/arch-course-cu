# Part 3.1 — Pipeline API Design

## Design Decisions

The API exposes two modes for the same pipeline:

- **Sync** (`POST /pipeline/run`): wait for the full pipeline and return the
  result in the HTTP response.  Suitable for small documents (< 5 pages),
  interactive web apps, and low-latency use cases.  Times out after 30 s.
- **Async** (`POST /pipeline/jobs`): return a job ID immediately.  Client
  polls or receives a webhook when done.  Suitable for batch jobs, large
  documents, and any caller that cannot hold a long-lived HTTP connection.

Both paths use the same internal components — only the connection mode
between the API Gateway and the worker differs.

---

## Base URL

```
https://api.example.com/api/v1
```

---

## Endpoints

### POST /api/v1/pipeline/run  (synchronous)

**Purpose:** Process a document and return the result in one HTTP response.

**Request (multipart upload):**
```http
POST /api/v1/pipeline/run
Content-Type: multipart/form-data

file=<binary>
options={ "extract_text": true, "classify": true }
```

**Request (URL input):**
```json
{
  "url": "https://example.com/invoice.pdf",
  "options": { "extract_text": true, "classify": true }
}
```

**Response 200 — success:**
```json
{
  "doc_id": "doc_abc123",
  "status": "done",
  "label": "invoice",
  "label_confidence": 0.94,
  "pages": [
    { "page": 1, "text": "INVOICE\nDate: 2024-06-01\nTotal: €1200" }
  ],
  "file_url": "https://store.example.com/docs/doc_abc123.pdf",
  "processed_at": "2024-06-01T10:05:22Z"
}
```

**Response 422 — invalid document:**
```json
{
  "error": { "code": "VALIDATION_FAILED", "message": "Unsupported file type: .docx" }
}
```

**Response 504 — timeout:**
```json
{
  "error": { "code": "TIMEOUT", "message": "Processing exceeded 30 s. Use async mode for large documents." }
}
```

**Sync path — internal flow:**  
API Gateway → (direct call) → Validator → (direct call) → Extractor →
Classifier → Storage.  All steps run synchronously in the request thread
(or a thread pool).  The Notifier is not involved — the HTTP response
carries the result.

---

### POST /api/v1/pipeline/jobs  (asynchronous)

**Purpose:** Enqueue a document for background processing.  Returns job ID
immediately.

**Request:** Same as sync (multipart or JSON).  Optional `webhook_url`.

```json
{
  "url": "https://example.com/large-report.pdf",
  "options": { "extract_text": true, "classify": true },
  "webhook_url": "https://myclient.example.com/hooks/pdf-done"
}
```

**Response 202 — accepted:**
```json
{
  "job_id": "job_x9y8z7",
  "status": "queued",
  "poll_url": "/api/v1/pipeline/jobs/job_x9y8z7"
}
```

**Async path — internal flow:**  
API Gateway publishes `{ job_id, doc_id, storage_url, options, webhook_url }`
to the message queue.  Returns 202 immediately.  Worker picks up the message,
runs the Orchestrator (Validator → Extractor → Classifier → Storage), then
publishes to the Notifier queue.  Notifier delivers webhook or updates job
store.

---

### GET /api/v1/pipeline/jobs/{job_id}  (poll status)

**Response 200 — still processing:**
```json
{
  "job_id": "job_x9y8z7",
  "status": "processing",
  "step": "extracting",
  "progress_pct": 40,
  "created_at": "2024-06-01T10:00:00Z"
}
```

**Response 200 — complete:**
```json
{
  "job_id": "job_x9y8z7",
  "status": "done",
  "result": {
    "doc_id": "doc_abc123",
    "label": "invoice",
    "pages": [ ... ],
    "file_url": "https://store.example.com/docs/doc_abc123.pdf"
  },
  "completed_at": "2024-06-01T10:02:15Z"
}
```

**Response 200 — failed:**
```json
{
  "job_id": "job_x9y8z7",
  "status": "failed",
  "error": { "code": "EXTRACTION_FAILED", "message": "OCR failed after 3 retries." }
}
```

---

## Error Response Format (all endpoints)

```json
{
  "error": {
    "code": "VALIDATION_FAILED | EXTRACTION_FAILED | TIMEOUT | FILE_TOO_LARGE | INTERNAL_ERROR",
    "message": "Human-readable explanation.",
    "request_id": "req_abc123"
  }
}
```

| HTTP Code | Code | Trigger |
|---|---|---|
| 400 | `INVALID_REQUEST` | Missing file or URL, malformed JSON |
| 413 | `FILE_TOO_LARGE` | File exceeds 100 MB |
| 415 | `UNSUPPORTED_TYPE` | Not PDF/image |
| 422 | `VALIDATION_FAILED` | Valid upload, invalid document content |
| 504 | `TIMEOUT` | Sync path exceeded 30 s |
| 500 | `INTERNAL_ERROR` | Unexpected pipeline failure |

---

## Constraints

| Constraint | Value |
|---|---|
| Max file size | 100 MB |
| Sync timeout | 30 s |
| Webhook retry policy | 5 attempts, exponential back-off (2s, 4s, 8s, 16s, 32s) |
| Job result retention | 7 days |
| Rate limit | 30 req/min per API key |
