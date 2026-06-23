# Part 2.1: API Design — Exposing pdf-parse as an HTTP/REST API

This document defines how to expose the pdf-parse library as an HTTP/REST API service: endpoints, request/response formats, and design decisions.

---

## 1. Base URL and Versioning

- **Base URL:** `https://api.example.com/api/v1`
- **Versioning:** Path-based `v1` to allow future `v2` without breaking clients.

---

## 2. API Endpoints

All extraction endpoints accept the PDF via **one** of: **multipart file upload**, **JSON body with `url`**, or **JSON body with `base64`**. Response structure varies by operation.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/extract/text` | Extract text from PDF |
| POST | `/api/v1/extract/info` | Get metadata (page count, etc.) |
| POST | `/api/v1/extract/images` | Extract embedded images |
| POST | `/api/v1/extract/tables` | Extract tabular data |
| POST | `/api/v1/screenshot` | Render pages as PNG images |

### 2.1 Input: How the Client Provides the PDF

**Option A — Multipart form data (file upload):**

```
POST /api/v1/extract/text
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

<binary PDF bytes>
------WebKitFormBoundary--
```

**Option B — JSON with URL:**

```json
POST /api/v1/extract/text
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "password": "optional-password"
}
```

**Option C — JSON with base64:**

```json
POST /api/v1/extract/text
Content-Type: application/json

{
  "base64": "JVBERi0xLjQKJeLjz9MK...",
  "password": "optional-password"
}
```

**Rule:** Exactly one of `file` (multipart), `url`, or `base64` must be provided. If multiple are sent, the server may reject with **400 Bad Request** or define a precedence (e.g. file > url > base64).

---

## 3. Endpoint Specifications

### 3.1 `POST /api/v1/extract/text`

**Request:** PDF via file, `url`, or `base64` as above. Optional JSON/multipart fields:
- `password` (string, optional)
- `pages` (array `[start, end]`, optional) — e.g. `[1, 3]` for pages 1–3; omit for full document

**Response (200 OK):**

```json
{
  "text": "Full extracted text...",
  "pages": 5,
  "pageRange": [1, 5]
}
```

---

### 3.2 `POST /api/v1/extract/info`

**Request:** PDF via file, `url`, or `base64`; optional `password`.

**Response (200 OK):**

```json
{
  "pageCount": 5,
  "metadata": {
    "title": "Document Title",
    "author": "Author",
    "creator": "PDF Generator",
    "producer": "Producer"
  }
}
```

---

### 3.3 `POST /api/v1/extract/images`

**Request:** PDF via file, `url`, or `base64`; optional `password`, optional `page` (number) to limit to one page.

**Response (200 OK):**

```json
{
  "images": [
    {
      "index": 0,
      "page": 1,
      "mimeType": "image/png",
      "data": "base64-encoded-image-data..."
    }
  ],
  "count": 1
}
```

Alternative: return short-lived URLs (e.g. signed) instead of inline base64 for large payloads; document in API description.

---

### 3.4 `POST /api/v1/extract/tables`

**Request:** PDF via file, `url`, or `base64`; optional `password`, optional `page`.

**Response (200 OK):**

```json
{
  "tables": [
    {
      "page": 1,
      "rows": [
        ["Header1", "Header2"],
        ["Cell1", "Cell2"]
      ]
    }
  ]
}
```

---

### 3.5 `POST /api/v1/screenshot`

**Request:** PDF via file, `url`, or `base64`; optional `password`. Optional query or body params:
- `pages` (array of numbers, e.g. `[1, 2, 3]`) — default: all pages
- `scale` (number, e.g. `2` for 2x resolution) — default: `1`

**Response (200 OK):**

```json
{
  "screenshots": [
    {
      "page": 1,
      "mimeType": "image/png",
      "data": "base64-encoded-png..."
    }
  ]
}
```

---

## 3.6 Common Request Schema

All endpoints accept a PDF input using one of the following fields:

| Field | Type | Description |
|------|------|------|
| file | multipart file | Uploaded PDF file |
| url | string | Remote PDF URL |
| base64 | string | Base64-encoded PDF |

Optional parameters:

| Field | Type | Description |
|------|------|------|
| password | string | Password for encrypted PDFs |
| pages | array | Page range or list of pages |
| page | number | Specific page to process |
| scale | number | Rendering scale for screenshots |

Rule: exactly one of `file`, `url`, or `base64` must be provided.

---

## 4. Error Responses

| HTTP Code | Meaning | When |
|-----------|---------|------|
| 400 | Bad Request | Invalid body, missing PDF input, or more than one of file/url/base64. |
| 413 | Payload Too Large | PDF exceeds server limit (e.g. 50 MB). |
| 422 | Unprocessable Entity | File is not a valid PDF or password required/wrong. |
| 500 | Internal Server Error | Parse failure, worker crash, or unexpected error. |

**Error body (consistent shape):**

```json
{
  "error": {
    "code": "INVALID_PDF",
    "message": "The provided file could not be parsed as a PDF.",
    "details": {}
  }
}
```

---

## 5. Design Decisions

### Sync vs async
- **Default: synchronous.** Client sends request and waits for response. Suitable for small/medium PDFs and low concurrency.
- **Large files / long-running:** For very large PDFs or strict timeouts, support **async**:
  - `POST /api/v1/jobs` with same input options → returns `jobId`.
  - `GET /api/v1/jobs/:jobId` → status and, when complete, result or link to result.
  - Optional webhook callback when job completes.

### Size limits and timeouts
- **Max PDF size:** e.g. 50 MB (configurable); respond with **413** if exceeded.
- **Request timeout:** e.g. 60 s for sync; client should be able to rely on timeout and retry or switch to async job.
- **URL fetch:** If input is `url`, server fetches the PDF; enforce max size and timeout (e.g. 30 s) for that fetch.

### Authentication and rate limiting
- **Authentication:** Optional API key in header `Authorization: Bearer <token>` or `X-API-Key: <key>`. Return **401** if required but missing/invalid.
- **Rate limiting:** Optional per-client limits (e.g. 100 req/min) with headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and **429 Too Many Requests** when exceeded.

---
## 5.1 Architecture Diagram 

The API architecture that implements these endpoints is described in Part 2.2.  
The diagram shows how clients send requests to the HTTP API layer, which then invokes a PDF parsing service that wraps the redesigned pdf-parse interfaces.

Data flow:

Client → API Layer → PDF Parsing Service → pdf-parse Library → Response
---
## 6. Summary

- **One endpoint per operation** for clarity and caching/versioning; PDF input is uniform (file / url / base64) across endpoints.
- **JSON request/response** with a consistent error shape.
- **Sync by default;** optional async job API for large files.
- **Limits and timeouts** to protect the server; optional auth and rate limiting for production use.

This design maps the library operations (getText, getInfo, getImage, getTable, getScreenshot) directly to REST resources and keeps the API predictable and reusable from web, mobile, CLI (e.g. curl), and batch jobs.
