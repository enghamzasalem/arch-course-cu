# Part 2.1 — HTTP/REST API Design

## Design Decisions

### One endpoint per operation vs. unified endpoint

A unified endpoint (`POST /parse?action=text`) with an action parameter
feels simpler at first.  It is worse in practice: every client must know the
valid values for `action`; routing logic lives in application code, not in
the HTTP layer; you cannot apply different size limits or timeouts per
operation.

The design below uses **one endpoint per operation** — one route per
extraction type.  This maps cleanly to the `IPDFExtractor<T>` interface
from Part 1 (one extractor class per endpoint), and allows per-route
middleware (auth, rate limits, size limits) without conditional logic.

### Sync vs. async

Text, info, and table extraction run synchronously — the response is
returned directly.  Screenshot and image extraction can be slow for large
documents.  For these, the API offers an optional `async=true` query
parameter that returns a job ID and a polling endpoint.  Small documents
(< 5 pages) always return synchronously.

### Input format

All endpoints accept either:
- `multipart/form-data` with a `file` field (standard upload)
- `application/json` with `{ "url": "..." }` or `{ "data": "<base64>" }`

This mirrors the `IPDFSource` redesign: the server constructs the
appropriate source object based on which field is present.

---

## Base URL

```
https://api.example.com/api/v1
```

Version is in the URL path.  The course advises explicit versioning of all
API changes; a path prefix makes version visible to all clients (proxies,
logs, load balancers) without requiring header inspection.

---

## Endpoints

### POST /api/v1/extract/text

Extract all text content from a PDF.

**Request (multipart upload):**
```http
POST /api/v1/extract/text
Content-Type: multipart/form-data

file=<binary PDF>
pages=1,2,3         (optional; default: all pages)
```

**Request (JSON with URL):**
```json
{
  "url": "https://example.com/document.pdf",
  "password": "secret",
  "pages": [1, 2, 3]
}
```

**Response 200:**
```json
{
  "pages": [
    { "pageNumber": 1, "text": "Introduction\nThis document..." },
    { "pageNumber": 2, "text": "Chapter 1..." }
  ],
  "totalPages": 12
}
```

---

### POST /api/v1/extract/info

Extract PDF metadata (title, author, creation date, page count).

**Request:** Same as `/extract/text` (file, url, or base64).  
No `pages` parameter — metadata is document-level.

**Response 200:**
```json
{
  "title": "Annual Report 2024",
  "author": "Finance Team",
  "subject": null,
  "creator": "Adobe Acrobat",
  "creationDate": "2024-03-15T10:00:00Z",
  "pageCount": 48,
  "encrypted": false,
  "pdfVersion": "1.7"
}
```

---

### POST /api/v1/extract/images

Extract embedded images from a PDF.

**Request:**
```json
{
  "url": "https://example.com/report.pdf",
  "pages": [1, 2],
  "format": "base64"
}
```
`format` is `"base64"` (default) or `"url"` (server stores image and returns
a short-lived URL — useful for large images).

**Response 200:**
```json
{
  "images": [
    {
      "pageNumber": 1,
      "imageIndex": 0,
      "mimeType": "image/jpeg",
      "width": 800,
      "height": 600,
      "data": "<base64>"
    }
  ]
}
```

---

### POST /api/v1/extract/tables

Extract tabular data from a PDF.

**Request:** File upload or JSON source + optional `pages`.

**Response 200:**
```json
{
  "tables": [
    {
      "pageNumber": 3,
      "tableIndex": 0,
      "rows": [
        ["Name", "Value", "Unit"],
        ["Revenue", "1200000", "EUR"],
        ["Cost",    "800000",  "EUR"]
      ]
    }
  ]
}
```

---

### POST /api/v1/screenshot

Render PDF pages as PNG images.

**Request:**
```json
{
  "url": "https://example.com/slides.pdf",
  "pages": [1, 2, 3],
  "scale": 1.5,
  "async": false
}
```

**Response 200 (sync):**
```json
{
  "screenshots": [
    {
      "pageNumber": 1,
      "width": 1240,
      "height": 1754,
      "data": "<base64 PNG>"
    }
  ]
}
```

**Response 202 (async, when `async=true` or file > 20 pages):**
```json
{
  "jobId": "job_a1b2c3",
  "status": "queued",
  "pollUrl": "/api/v1/jobs/job_a1b2c3"
}
```

---

### GET /api/v1/jobs/{jobId}

Poll status of an async job.

**Response 200 (pending):**
```json
{ "jobId": "job_a1b2c3", "status": "processing", "progress": 40 }
```

**Response 200 (done):**
```json
{ "jobId": "job_a1b2c3", "status": "done", "result": { ... } }
```

---

## Error Responses

| HTTP Code | Error Type | When |
|---|---|---|
| 400 | `INVALID_INPUT` | Missing file/url, bad JSON |
| 413 | `FILE_TOO_LARGE` | File exceeds 50 MB limit |
| 415 | `UNSUPPORTED_TYPE` | Not a PDF (MIME check) |
| 422 | `PARSE_ERROR` | Valid upload, but PDF is malformed or wrong password |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected library failure |
| 504 | `TIMEOUT` | Parsing took > 30 s |

**Error body format (consistent across all endpoints):**
```json
{
  "error": {
    "code": "PARSE_ERROR",
    "message": "The PDF is encrypted and no password was provided.",
    "requestId": "req_x9y8z7"
  }
}
```

---

## Constraints and Limits

| Constraint | Value | Rationale |
|---|---|---|
| Max file size | 50 MB | Prevent memory exhaustion |
| Max pages for sync screenshot | 20 | Screenshots are CPU-heavy |
| Request timeout | 30 s | Prevent worker starvation |
| Rate limit (unauthenticated) | 10 req/min | Basic abuse prevention |
| Rate limit (authenticated) | 120 req/min | Reasonable production use |

---

## Authentication

Authentication is optional for the current design.  When enabled, callers
pass a Bearer token in the `Authorization` header.  Unauthenticated requests
are allowed but rate-limited more aggressively.  The API layer validates the
token before dispatching to the PDF service — the library itself never handles
auth concerns.
