## Endpoints

Each library operation maps to a dedicated POST endpoint. All endpoints are versioned under `/api/v1` and accept the PDF via one of three input modes (see Request Format below).

| Method | Endpoint | Maps to |
|---|---|---|
| POST | `/api/v1/extract/text` | `TextExtractor` |
| POST | `/api/v1/extract/info` | `InfoExtractor` |
| POST | `/api/v1/extract/images` | `ImageExtractor` |
| POST | `/api/v1/extract/tables` | `TableExtractor` |
| POST | `/api/v1/extract/screenshot` | `ScreenshotExtractor` |

One endpoint per operation was chosen over a unified `action` parameter because it makes documentation, validation, and per-operation rate limiting straightforward without a discriminated-union request schema.

---

## Request Format

Every endpoint accepts the same three mutually exclusive input modes. Exactly one must be present; providing zero or more than one returns `400`.

**Mode 1 – File upload** (`multipart/form-data`)
```
POST /api/v1/extract/text
Content-Type: multipart/form-data

file=<binary PDF bytes>
pages=1,2,3          (optional, all pages if omitted)
password=secret      (optional)
```

**Mode 2 – URL** (`application/json`)
```json
{
  "url": "https://example.com/report.pdf",
  "pages": [1, 2, 3],
  "password": "secret"
}
```

**Mode 3 – Base64** (`application/json`)
```json
{
  "data": "<base64-encoded PDF bytes>",
  "pages": [1, 2, 3],
  "password": "secret"
}
```

`/api/v1/extract/screenshot` accepts two additional optional fields:
```json
{
  "url": "...",
  "scale": 2.0,
  "format": "png"
}
```

---

## Response Format

All responses share a common envelope:

```json
{
  "success": true,
  "data": { },
  "meta": {
    "pageCount": 12,
    "processedPages": 3,
    "durationMs": 284
  }
}
```

### `POST /api/v1/extract/text`
```json
{
  "success": true,
  "data": {
    "text": "Full concatenated text of all requested pages…",
    "pages": [
      { "pageNumber": 1, "text": "Page 1 content…" },
      { "pageNumber": 2, "text": "Page 2 content…" }
    ]
  },
  "meta": { "pageCount": 12, "processedPages": 2, "durationMs": 310 }
}
```

### `POST /api/v1/extract/info`
```json
{
  "success": true,
  "data": {
    "title": "Annual Report 2024",
    "author": "Finance Dept",
    "producer": "Adobe PDF Library",
    "creationDate": "2024-01-15T09:30:00Z",
    "pageCount": 48,
    "isEncrypted": false,
    "pdfVersion": "1.7"
  },
  "meta": { "durationMs": 95 }
}
```

### `POST /api/v1/extract/images`
```json
{
  "success": true,
  "data": {
    "images": [
      {
        "pageNumber": 1,
        "index": 0,
        "mimeType": "image/jpeg",
        "widthPx": 800,
        "heightPx": 600,
        "data": "<base64-encoded bytes>"
      }
    ]
  },
  "meta": { "pageCount": 12, "processedPages": 12, "durationMs": 420 }
}
```

### `POST /api/v1/extract/tables`
```json
{
  "success": true,
  "data": {
    "tables": [
      {
        "pageNumber": 5,
        "tableIndex": 0,
        "rows": [
          ["Quarter", "Revenue", "Growth"],
          ["Q1 2024", "$4.2M",   "12%"]
        ]
      }
    ]
  },
  "meta": { "pageCount": 12, "processedPages": 12, "durationMs": 680 }
}
```

### `POST /api/v1/extract/screenshot`
```json
{
  "success": true,
  "data": {
    "pages": [
      {
        "pageNumber": 1,
        "widthPx": 1700,
        "heightPx": 2200,
        "format": "png",
        "data": "<base64-encoded PNG>"
      }
    ]
  },
  "meta": { "pageCount": 12, "processedPages": 1, "durationMs": 1150 }
}
```

---

## Error Responses

All errors use the same envelope with `success: false`:

```json
{
  "success": false,
  "error": {
    "code": "PARSE_ERROR",
    "message": "The provided file is not a valid PDF."
  }
}
```

| HTTP Status | `error.code` | Cause |
|---|---|---|
| `400` | `MISSING_INPUT` | No file, URL, or base64 provided |
| `400` | `INVALID_INPUT` | Multiple input modes provided, or malformed base64 |
| `400` | `INVALID_PAGES` | Requested page numbers out of range |
| `413` | `FILE_TOO_LARGE` | Upload exceeds the configured size limit |
| `422` | `PARSE_ERROR` | Bytes are not a valid PDF |
| `422` | `PASSWORD_REQUIRED` | PDF is encrypted and no password was provided |
| `422` | `WRONG_PASSWORD` | Provided password is incorrect |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

---

## Design Decisions

### Sync vs Async
All endpoints are **synchronous** in v1 — the HTTP response contains the result directly. This is appropriate for PDFs up to the configured size limit processed within the request timeout.

For large files where extraction may exceed the timeout, a future async variant can be added without breaking existing callers:
```
POST /api/v1/jobs/extract/text   →  202 Accepted  { "jobId": "abc123" }
GET  /api/v1/jobs/abc123         →  { "status": "pending | running | done | failed" }
GET  /api/v1/jobs/abc123/result  →  same envelope as the synchronous response
```
The synchronous endpoints remain unchanged; async is purely additive.

### Size Limits and Timeouts
| Parameter | Default | Notes |
|---|---|---|
| Max upload (file mode) | 25 MB | Configurable via `PDF_MAX_UPLOAD_MB` |
| Max download (URL mode) | 50 MB | Configurable via `PDF_MAX_URL_MB` |
| Extraction timeout | 30 s | Configurable via `PDF_TIMEOUT_MS` |
| Max pages per request | 500 | Prevents runaway worker time |