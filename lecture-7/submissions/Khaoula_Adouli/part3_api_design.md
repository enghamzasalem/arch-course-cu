# Part 3.1: Pipeline API Design — Sync and Async

## 1. Endpoints

**Base:** `https://api.example.com/api/v1`

### 1.1 Synchronous pipeline run

**`POST /api/v1/pipeline/run`**

- **Purpose:** Upload document (or URL) and wait for processing to complete; response contains extracted/classified data (or error).
- **Request:**
  - **Multipart:** `file` (binary) **or** JSON body with `{ "url": "..." , "options": { ... } }`
  - **Options (examples):** `{ "mode": "text_only" | "full_ocr", "language": "en" }`
- **Response (200):**
```json
{
  "text": "...",
  "classification": { "label": "invoice", "confidence": 0.92 },
  "storage_ref": "s3://bucket/key",
  "job_id": "optional-same-as-correlation"
}
```
- **Errors:** `400` validation, `413` too large, `422` unsupported format, `500` internal.

---

### 1.2 Asynchronous job

**`POST /api/v1/pipeline/jobs`**

- **Purpose:** Accept document and return immediately with **`job_id`**; processing continues in background.
- **Request:** Same as sync (multipart or JSON with `url`); optional **`callback_url`** or **`webhook_secret`** for completion notification.
- **Response (202):**
```json
{
  "job_id": "job_abc123",
  "status": "QUEUED",
  "poll_url": "/api/v1/pipeline/jobs/job_abc123"
}
```

**`GET /api/v1/pipeline/jobs/{job_id}`**

- **Response:** `{ "status": "QUEUED"|"RUNNING"|"SUCCEEDED"|"FAILED", "result?": {...}, "error?": {...} }`

**Optional: `POST` webhook** — server POSTs to `callback_url` when status becomes SUCCEEDED or FAILED.

---

## 2. How paths use components and connectors

### Sync path

1. Client → **API Gateway** (`REST HTTP`, sync).
2. **Orchestrator** (in API or worker thread) calls **Validator** → **Extractor** → **Classifier** → **Storage** (direct/RPC **sync** chain within timeout).
3. Response returned in same HTTP request.
4. **Notifier** optional for sync (often skipped) or fire-and-forget email.

### Async path

1. Client → **`POST /jobs`** → API validates **quickly**, stores blob reference, **enqueues** `DocumentJob` on **message queue** (**async** connector).
2. **Worker** pulls job → same logical sequence **Validate → Extract → Classify → Store** (orchestrated inside worker).
3. On completion, **Notifier** publishes **webhook** or event bus **async**; job store updated for **GET /jobs/{id}**.

---

## 3. Summary

| Path | HTTP | Backend |
|------|------|---------|
| Sync | `POST /pipeline/run` | Orchestrator calls components in process; blocking response |
| Async | `POST /pipeline/jobs` + `GET .../jobs/{id}` | Queue + workers; optional webhook |

This matches the assignment: **synchronous “process and return”** and **asynchronous “job id + poll or notify.”**
