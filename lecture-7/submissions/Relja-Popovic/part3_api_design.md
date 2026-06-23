# Part 3.1 – Pipeline API Design

## Endpoints

### Sync
```
POST /api/v1/pipeline/run
```
**Request:** `multipart/form-data` with `file` or `{ "url": "..." }` + optional `options` (`extractOnly`, `fullOCR`).

**Response `200 OK`:**
```json
{
  "documentId": "doc_abc123",
  "type": "invoice",
  "text": "Extracted text...",
  "pages": 3
}
```
**Error responses:** `400` invalid input, `422` extraction failed, `500` internal error.

---

### Async
```
POST /api/v1/pipeline/jobs
```
**Request:** same body as sync, plus optional `callbackUrl`.

**Response `202 Accepted`:**
```json
{ "jobId": "job_xyz789" }
```

---

```
GET /api/v1/pipeline/jobs/{job_id}
```
**Response:**
```json
{
  "jobId": "job_xyz789",
  "status": "pending | running | done | failed",
  "result": { ... }
}
```
`result` is populated only when `status` is `done`.

---

## How the Paths Use the Pipeline

**Sync path:** The PipelineOrchestrator runs all steps inline - Validator → Extractor → Classifier → Storage - and returns the result directly in the HTTP response. Suitable for small documents where the full pipeline completes within the request timeout.

**Async path:** After validation, the orchestrator enqueues a job and immediately returns the `jobId`. A background worker picks up the job, runs Extractor → Classifier → Storage, then triggers the Notifier which POSTs the result to the `callbackUrl` if provided. The client can also poll `GET /jobs/{job_id}` for status.