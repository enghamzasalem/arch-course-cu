# Task 2.1 — API Design
## Exposing pdf-parse as an HTTP/REST API Service

---

## 1. Overview

The pdf-parse library is wrapped as a stateless HTTP service. Every endpoint accepts a PDF via one of three input modes (file upload, URL reference, or base64 JSON), delegates to the appropriate core library extractor, and returns a structured JSON response. Long-running operations on large files are handled through an async job queue with polling, described in Section 6.

**Base URL:** `https://api.example.com`
**Versioning:** URI-prefixed — `/api/v1/`. Breaking changes increment the version; the previous version is kept alive for a minimum 6-month deprecation window.
**Authentication:** `Authorization: Bearer <token>` on all endpoints.
**Content-Type:** `application/json` for JSON bodies; `multipart/form-data` for file uploads.
**Transport:** All traffic must use HTTPS/TLS 1.2 or higher. Plain HTTP requests are rejected with `301 Moved Permanently`.

---

## 2. Input Modes

All extraction endpoints accept the same three input modes. The client chooses whichever fits its context.

### Mode A — Multipart file upload

```
POST /api/v1/extract/text
Content-Type: multipart/form-data

file=<binary PDF bytes>
options={"pages": [1, 2, 3]}
```

Best for: browser file-picker uploads, CLI tools piping a local file.

### Mode B — URL reference

```json
{
  "source": { "type": "url", "value": "https://example.com/report.pdf" },
  "options": { "pages": [1, 2, 3] }
}
```

Best for: server-to-server workflows where the PDF is already hosted somewhere accessible.

### Mode C — Base64 JSON

```json
{
  "source": { "type": "base64", "value": "JVBERi0xLjQK..." },
  "options": { "pages": [1, 2, 3] }
}
```

Best for: mobile apps, embedded systems, or pipelines where the PDF is already in memory and a file upload round-trip is undesirable.

**Design decision — why three modes?**
Different consumers have fundamentally different contexts. Forcing a browser app to base64-encode a 10 MB file before uploading is wasteful; forcing a server pipeline to open a multipart stream for an in-memory buffer is unnecessary overhead. Accepting all three modes at every endpoint means the API adapts to the caller rather than the other way around.

---

## 3. JSON Schemas

The following schemas define the request and response contracts for every endpoint. Each per-endpoint request schema extends the common base by adding its specific `options` fields.

### 3.1 Common Request Schema (base)

Shared by all endpoints. Per-endpoint schemas extend `options` with additional properties.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/request-base.json",
  "title": "PDF Extraction Request — base",
  "type": "object",
  "required": ["source"],
  "properties": {
    "source": {
      "oneOf": [
        {
          "title": "URL source",
          "type": "object",
          "required": ["type", "value"],
          "properties": {
            "type":  { "type": "string", "const": "url" },
            "value": { "type": "string", "format": "uri" }
          },
          "additionalProperties": false
        },
        {
          "title": "Base64 source",
          "type": "object",
          "required": ["type", "value"],
          "properties": {
            "type":  { "type": "string", "const": "base64" },
            "value": { "type": "string", "contentEncoding": "base64" }
          },
          "additionalProperties": false
        }
      ]
    },
    "options": {
      "type": "object",
      "properties": {
        "password": {
          "type": "string",
          "description": "Decryption password for encrypted PDFs"
        },
        "pages": {
          "type": "array",
          "items": { "type": "integer", "minimum": 1 },
          "minItems": 1,
          "description": "1-indexed page numbers to process. Omit for all pages."
        }
      }
    },
    "async": {
      "type": "boolean",
      "default": false,
      "description": "If true, enqueue the job and return 202 with a jobId for polling."
    }
  },
  "additionalProperties": false
}
```

### 3.2 Per-Endpoint Request Schemas

#### `POST /api/v1/extract/text` — request

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/request-text.json",
  "title": "Extract Text Request",
  "$ref": "request-base.json",
  "properties": {
    "options": {
      "type": "object",
      "properties": {
        "password":        { "type": "string" },
        "pages":           { "type": "array", "items": { "type": "integer", "minimum": 1 } },
        "normalizeSpaces": { "type": "boolean", "default": true,
                             "description": "Collapse consecutive whitespace into a single space" }
      },
      "additionalProperties": false
    }
  }
}
```

#### `POST /api/v1/extract/info` — request

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/request-info.json",
  "title": "Extract Info Request",
  "$ref": "request-base.json",
  "properties": {
    "options": {
      "type": "object",
      "properties": {
        "password": { "type": "string" }
      },
      "additionalProperties": false
    }
  }
}
```

#### `POST /api/v1/extract/images` — request

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/request-images.json",
  "title": "Extract Images Request",
  "$ref": "request-base.json",
  "properties": {
    "options": {
      "type": "object",
      "properties": {
        "password":    { "type": "string" },
        "pages":       { "type": "array", "items": { "type": "integer", "minimum": 1 } },
        "includeData": { "type": "boolean", "default": false,
                         "description": "When true, include base64 pixel data in each image object" }
      },
      "additionalProperties": false
    }
  }
}
```

#### `POST /api/v1/extract/tables` — request

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/request-tables.json",
  "title": "Extract Tables Request",
  "$ref": "request-base.json",
  "properties": {
    "options": {
      "type": "object",
      "properties": {
        "password": { "type": "string" },
        "pages":    { "type": "array", "items": { "type": "integer", "minimum": 1 } }
      },
      "additionalProperties": false
    }
  }
}
```

#### `POST /api/v1/screenshot` — request

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/request-screenshot.json",
  "title": "Screenshot Request",
  "$ref": "request-base.json",
  "properties": {
    "options": {
      "type": "object",
      "properties": {
        "password": { "type": "string" },
        "pages":    { "type": "array", "items": { "type": "integer", "minimum": 1 },
                      "default": [1], "maxItems": 20 },
        "scale":    { "type": "number", "minimum": 0.1, "maximum": 4.0, "default": 1.0 },
        "format":   { "type": "string", "enum": ["png", "jpeg"], "default": "png" }
      },
      "additionalProperties": false
    }
  }
}
```

### 3.3 Per-Endpoint Response Schemas

#### `POST /api/v1/extract/text` — response

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/response-text.json",
  "title": "Extract Text Response",
  "type": "object",
  "required": ["requestId", "pageCount", "pages", "text"],
  "properties": {
    "requestId": { "type": "string" },
    "pageCount": { "type": "integer", "minimum": 1 },
    "pages": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["page", "text"],
        "properties": {
          "page": { "type": "integer", "minimum": 1 },
          "text": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "text": {
      "type": "string",
      "description": "All requested pages concatenated with newline separators"
    }
  },
  "additionalProperties": false
}
```

#### `POST /api/v1/extract/info` — response

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/response-info.json",
  "title": "Extract Info Response",
  "type": "object",
  "required": ["requestId", "metadata"],
  "properties": {
    "requestId": { "type": "string" },
    "metadata": {
      "type": "object",
      "required": ["pageCount"],
      "properties": {
        "title":       { "type": "string" },
        "author":      { "type": "string" },
        "subject":     { "type": "string" },
        "keywords":    { "type": "array", "items": { "type": "string" } },
        "creator":     { "type": "string" },
        "producer":    { "type": "string" },
        "createdAt":   { "type": "string", "format": "date-time" },
        "modifiedAt":  { "type": "string", "format": "date-time" },
        "pageCount":   { "type": "integer", "minimum": 1 },
        "isEncrypted": { "type": "boolean" },
        "pdfVersion":  { "type": "string" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

#### `POST /api/v1/extract/images` — response

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/response-images.json",
  "title": "Extract Images Response",
  "type": "object",
  "required": ["requestId", "images"],
  "properties": {
    "requestId": { "type": "string" },
    "images": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "page", "width", "height", "mimeType", "sizeBytes"],
        "properties": {
          "id":        { "type": "string" },
          "page":      { "type": "integer", "minimum": 1 },
          "width":     { "type": "integer", "minimum": 1 },
          "height":    { "type": "integer", "minimum": 1 },
          "mimeType":  { "type": "string", "enum": ["image/jpeg", "image/png", "image/webp"] },
          "sizeBytes": { "type": "integer", "minimum": 0 },
          "data":      { "type": "string", "contentEncoding": "base64",
                         "description": "Only present when options.includeData is true" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

#### `POST /api/v1/extract/tables` — response

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/response-tables.json",
  "title": "Extract Tables Response",
  "type": "object",
  "required": ["requestId", "tables"],
  "properties": {
    "requestId": { "type": "string" },
    "tables": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["page", "tableIndex", "rows", "cols", "cells"],
        "properties": {
          "page":       { "type": "integer", "minimum": 1 },
          "tableIndex": { "type": "integer", "minimum": 0 },
          "rows":       { "type": "integer", "minimum": 1 },
          "cols":       { "type": "integer", "minimum": 1 },
          "cells": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["row", "col", "rowSpan", "colSpan", "text"],
              "properties": {
                "row":     { "type": "integer", "minimum": 0 },
                "col":     { "type": "integer", "minimum": 0 },
                "rowSpan": { "type": "integer", "minimum": 1 },
                "colSpan": { "type": "integer", "minimum": 1 },
                "text":    { "type": "string" }
              },
              "additionalProperties": false
            }
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

#### `POST /api/v1/screenshot` — response

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/response-screenshot.json",
  "title": "Screenshot Response",
  "type": "object",
  "required": ["requestId", "renders"],
  "properties": {
    "requestId": { "type": "string" },
    "renders": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["page", "width", "height", "mimeType", "data"],
        "properties": {
          "page":     { "type": "integer", "minimum": 1 },
          "width":    { "type": "integer", "minimum": 1 },
          "height":   { "type": "integer", "minimum": 1 },
          "mimeType": { "type": "string", "enum": ["image/png", "image/jpeg"] },
          "data":     { "type": "string", "contentEncoding": "base64" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

### 3.4 Error Response Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://api.example.com/schemas/error.json",
  "title": "API Error",
  "type": "object",
  "required": ["requestId", "error"],
  "properties": {
    "requestId": { "type": "string" },
    "error": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code":    { "type": "string",
                     "description": "Machine-readable error code — see Section 5" },
        "message": { "type": "string",
                     "description": "Human-readable explanation" },
        "details": { "type": "object",
                     "description": "Optional structured context, e.g. which field failed validation" }
      },
      "additionalProperties": false
    }
  }
}
```

---

## 4. Endpoints

### 4.1 `POST /api/v1/extract/text`

Extracts plain text content from a PDF, optionally scoped to a page range.

**Request (URL mode example):**

```json
{
  "source": { "type": "url", "value": "https://example.com/report.pdf" },
  "options": {
    "pages": [1, 2, 3],
    "normalizeSpaces": true
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | object | Yes | PDF input — see Section 2 |
| `options.pages` | number[] | No | 1-indexed page numbers. Default: all pages |
| `options.normalizeSpaces` | boolean | No | Collapse whitespace runs. Default: `true` |
| `options.password` | string | No | Decryption password for encrypted PDFs |

**Response `200 OK`:**

```json
{
  "requestId": "req_a1b2c3",
  "pageCount": 48,
  "pages": [
    { "page": 1, "text": "Introduction\nThis report covers..." },
    { "page": 2, "text": "Chapter 1 — Methodology..." },
    { "page": 3, "text": "..." }
  ],
  "text": "Introduction\nThis report covers...\nChapter 1..."
}
```

| Field | Description |
|---|---|
| `requestId` | Unique identifier for this request, useful for support and logging |
| `pageCount` | Total number of pages in the document |
| `pages` | Per-page text objects in page order |
| `text` | All requested pages concatenated with newline separators |

---

### 4.2 `POST /api/v1/extract/info`

Returns document-level metadata.

**Request:**

```json
{
  "source": { "type": "base64", "value": "JVBERi0x..." }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | object | Yes | PDF input — see Section 2 |
| `options.password` | string | No | Decryption password for encrypted PDFs |

**Response `200 OK`:**

```json
{
  "requestId": "req_d4e5f6",
  "metadata": {
    "title": "Annual Report 2024",
    "author": "Acme Corporation",
    "subject": "Financial results Q1–Q4",
    "keywords": ["finance", "annual", "report"],
    "creator": "Microsoft Word",
    "producer": "Adobe PDF Library",
    "createdAt": "2024-01-15T09:00:00Z",
    "modifiedAt": "2024-03-01T14:22:00Z",
    "pageCount": 48,
    "isEncrypted": false,
    "pdfVersion": "1.7"
  }
}
```

All metadata fields except `pageCount` are optional — a PDF may omit any of them. Fields absent in the document are omitted from the response (not returned as `null`) so consumers can use a simple `"title" in response.metadata` check.

---

### 4.3 `POST /api/v1/extract/images`

Returns metadata for all images embedded in the PDF. Does **not** return pixel data by default — pixel data is fetched separately via the `includeData` option or the `GET /images/{id}` endpoint. This two-step design avoids forcing expensive decoding on callers who only need inventory information.

**Request:**

```json
{
  "source": { "type": "url", "value": "https://example.com/brochure.pdf" },
  "options": {
    "pages": [1, 2],
    "includeData": false
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | object | Yes | PDF input — see Section 2 |
| `options.pages` | number[] | No | Pages to scan. Default: all |
| `options.includeData` | boolean | No | Include base64 pixel data in response. Default: `false` |
| `options.password` | string | No | Decryption password for encrypted PDFs |

**Response `200 OK`:**

```json
{
  "requestId": "req_g7h8i9",
  "images": [
    {
      "id": "img_001",
      "page": 1,
      "width": 800,
      "height": 600,
      "mimeType": "image/jpeg",
      "sizeBytes": 45231
    },
    {
      "id": "img_002",
      "page": 2,
      "width": 200,
      "height": 200,
      "mimeType": "image/png",
      "sizeBytes": 8104
    }
  ]
}
```

**Fetch pixel data for one image — `GET /api/v1/extract/images/{imageId}`:**

For URL-sourced PDFs, pass the PDF URL as a query parameter. For base64 or file-upload sources, use a `POST` to the same path with the source in the request body.

```
GET /api/v1/extract/images/img_001?source=https%3A%2F%2Fexample.com%2Fbrochure.pdf
```

**Response `200 OK`:**

```json
{
  "requestId": "req_j1k2l3",
  "image": {
    "id": "img_001",
    "page": 1,
    "width": 800,
    "height": 600,
    "mimeType": "image/jpeg",
    "sizeBytes": 45231,
    "data": "<base64-encoded JPEG bytes>"
  }
}
```

**Design decision — `GET` for single-image fetch:**
Fetching a known resource by ID is a read operation with no side effects — `GET` is the correct HTTP verb. `GET` also enables HTTP caching via `Cache-Control` and `ETag` headers, so repeated fetches of the same image can be served from cache without re-parsing the PDF. The `POST` form is provided as a fallback for base64 and file-upload sources that cannot be expressed as a URL query parameter.

**Design decision — why split list from data?**
A PDF with 50 embedded images could easily contain 50 MB of pixel data. A caller building an image inventory UI only needs `id`, `width`, `height`, and `mimeType` to render a table. Sending all pixel data by default would make the list endpoint unnecessarily slow. The `includeData` flag and the per-image sub-endpoint let callers opt in to payload decoding exactly when they need it.

---

### 4.4 `POST /api/v1/extract/tables`

Detects and returns table structures from the specified pages.

**Request:**

```json
{
  "source": { "type": "url", "value": "https://example.com/financials.pdf" },
  "options": {
    "pages": [3, 4, 5]
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | object | Yes | PDF input — see Section 2 |
| `options.pages` | number[] | No | Pages to scan. Default: all |
| `options.password` | string | No | Decryption password for encrypted PDFs |

**Response `200 OK`:**

```json
{
  "requestId": "req_m4n5o6",
  "tables": [
    {
      "page": 3,
      "tableIndex": 0,
      "rows": 5,
      "cols": 4,
      "cells": [
        { "row": 0, "col": 0, "rowSpan": 1, "colSpan": 1, "text": "Product" },
        { "row": 0, "col": 1, "rowSpan": 1, "colSpan": 1, "text": "Q1" },
        { "row": 0, "col": 2, "rowSpan": 1, "colSpan": 1, "text": "Q2" },
        { "row": 0, "col": 3, "rowSpan": 1, "colSpan": 1, "text": "Q3" },
        { "row": 1, "col": 0, "rowSpan": 1, "colSpan": 1, "text": "Widget A" },
        { "row": 1, "col": 1, "rowSpan": 1, "colSpan": 1, "text": "1,200" }
      ]
    }
  ]
}
```

`rowSpan` and `colSpan` are always present (defaulting to `1`) so clients can reconstruct merged cells without special-casing.

---

### 4.5 `POST /api/v1/screenshot`

Renders one or more PDF pages as raster images.

**Request:**

```json
{
  "source": { "type": "url", "value": "https://example.com/slides.pdf" },
  "options": {
    "pages": [1, 2],
    "scale": 1.5,
    "format": "png"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | object | Yes | PDF input — see Section 2 |
| `options.pages` | number[] | No | Pages to render. Default: `[1]`. Max: 20 pages |
| `options.scale` | number | No | Render scale factor. Default: `1.0`. Range: `0.1`–`4.0` |
| `options.format` | `"png"` or `"jpeg"` | No | Output image format. Default: `"png"` |
| `options.password` | string | No | Decryption password for encrypted PDFs |

**Response `200 OK`:**

```json
{
  "requestId": "req_p7q8r9",
  "renders": [
    {
      "page": 1,
      "width": 1224,
      "height": 1584,
      "mimeType": "image/png",
      "data": "<base64-encoded PNG bytes>"
    },
    {
      "page": 2,
      "width": 1224,
      "height": 1584,
      "mimeType": "image/png",
      "data": "<base64-encoded PNG bytes>"
    }
  ]
}
```

---

## 5. Error Responses

All errors follow a consistent envelope regardless of the endpoint or error type:

```json
{
  "requestId": "req_a1b2c3",
  "error": {
    "code": "PDF_ENCRYPTED",
    "message": "The PDF is encrypted. Provide a password via the 'options.password' field.",
    "details": {}
  }
}
```

### Error Code Reference

| HTTP Status | Error Code | Cause |
|---|---|---|
| `400 Bad Request` | `MISSING_SOURCE` | No `source` field and no file attached |
| `400 Bad Request` | `INVALID_SOURCE_TYPE` | `source.type` is not `"url"` or `"base64"` |
| `400 Bad Request` | `INVALID_BASE64` | `source.value` is not valid base64 |
| `400 Bad Request` | `INVALID_PAGE_NUMBER` | A requested page number is ≤ 0 or not an integer |
| `401 Unauthorized` | `MISSING_TOKEN` | No `Authorization` header present |
| `401 Unauthorized` | `INVALID_TOKEN` | Token is expired or does not exist |
| `413 Content Too Large` | `FILE_TOO_LARGE` | Uploaded file exceeds the 50 MB size limit |
| `422 Unprocessable` | `NOT_A_PDF` | Bytes do not parse as a valid PDF |
| `422 Unprocessable` | `PDF_ENCRYPTED` | PDF is encrypted; no password or wrong password provided |
| `422 Unprocessable` | `PAGE_OUT_OF_RANGE` | Requested page number exceeds the document's page count |
| `422 Unprocessable` | `IMAGE_NOT_FOUND` | `imageId` in URL path does not exist in the document |
| `422 Unprocessable` | `RENDER_UNAVAILABLE` | Screenshot renderer not available in this deployment tier |
| `429 Too Many Requests` | `RATE_LIMITED` | Client has exceeded their request quota |
| `500 Internal Server Error` | `INTERNAL_ERROR` | Unexpected server error |
| `503 Service Unavailable` | `QUEUE_FULL` | Async job queue is at capacity |

**Design decision — why `422` for parse errors instead of `400`?**
`400 Bad Request` signals that the HTTP request itself was malformed — missing required fields, wrong content-type. `422 Unprocessable Entity` signals that the request was structurally valid but the server could not act on the content. A PDF that is corrupted, encrypted, or references a non-existent page is a content problem, not a protocol problem. Using the correct status code lets clients distinguish "I sent a bad request" from "my PDF has a problem" without parsing the error body.

---

## 6. Sync vs Async Design

### Synchronous path (default)

All endpoints are synchronous by default. The server parses the PDF, runs the extraction, and returns the result in a single HTTP response. This is appropriate for:

- Files up to **10 MB**
- `extract/text`, `extract/info`, `extract/tables` operations on typical documents
- Screenshot requests for **1–3 pages**

Synchronous timeout: **30 seconds**. If extraction does not complete in time, the server returns `408 Request Timeout` with error code `EXTRACTION_TIMEOUT`.

### Asynchronous path (large files and bulk operations)

For files larger than 10 MB, screenshot requests across many pages, or image extraction with `includeData: true` on large documents, the client opts in to asynchronous processing by adding `"async": true` to the request body.

**Step 1 — Submit job:**

```json
{
  "source": { "type": "url", "value": "https://example.com/large-report.pdf" },
  "options": { "pages": [1, 2, 3, 4, 5] },
  "async": true
}
```

**Response `202 Accepted`:**

```json
{
  "jobId": "job_x9y8z7",
  "status": "queued",
  "estimatedSeconds": 12,
  "pollUrl": "https://api.example.com/api/v1/jobs/job_x9y8z7"
}
```

**Step 2 — Poll for result (`GET /api/v1/jobs/{jobId}`):**

```json
{
  "jobId": "job_x9y8z7",
  "status": "complete",
  "result": {
    "requestId": "req_a1b2c3",
    "pageCount": 48,
    "pages": [ ... ],
    "text": "..."
  }
}
```

| `status` | Meaning |
|---|---|
| `queued` | Waiting in the queue |
| `processing` | Extraction in progress |
| `complete` | Result available in the `result` field |
| `failed` | Extraction failed; see `error` field |

Jobs are deleted **1 hour** after completion. Polling more frequently than once every 2 seconds is rate-limited.

**Design decision — why not always async?**
Async adds latency and client complexity for small files. A 200 KB PDF text extraction takes under 200 ms — forcing the client through a poll cycle makes the API worse. The opt-in `"async": true` flag keeps simple cases fast and synchronous while giving large or batch workloads an appropriate processing model.

---

## 7. Size Limits and Timeouts

| Constraint | Value | Rationale |
|---|---|---|
| Maximum file size | 50 MB | Covers the vast majority of real-world PDFs |
| Synchronous timeout | 30 seconds | Prevents long-running extractions from blocking server workers |
| Async job TTL | 1 hour | Balances storage cost against client polling windows |
| Maximum pages per screenshot request | 20 | Rendering is the most CPU-intensive operation; caps prevent abuse |
| Maximum scale factor | 4.0 | Scale of 4 on A4 produces ~4900×6900 px; above this the base64 response body becomes impractically large |
| Rate limit (default) | 100 requests / minute per token | Protects shared infrastructure; configurable per pricing tier |
| Minimum poll interval (async) | 2 seconds | Prevents polling storms from overwhelming the job queue |

---

## 8. Authentication and Rate Limiting

**Authentication** uses bearer tokens: `Authorization: Bearer <token>`. All endpoints return `401 Unauthorized` if the token is absent or invalid. Token issuance is handled by a separate `/auth/token` endpoint outside the scope of this document.

**Rate limiting** is enforced per token at 100 requests per minute by default. When exceeded the server returns `429 Too Many Requests` with:

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Retry after 23 seconds.",
    "retryAfterSeconds": 23
  }
}
```

The response also sets the standard `Retry-After: 23` HTTP header so clients and libraries can back off automatically without parsing the body.

**Versioning and deprecation** — when a breaking change is introduced, a new version prefix (`/api/v2/`) is deployed. The old version continues to function and returns `Deprecation: true` and `Sunset: <RFC 7231 date>` headers on every response, giving clients at least 6 months to migrate before the old version is removed.

---

## 9. Endpoint Summary

| Method | Path | Operation | Sync / Async |
|---|---|---|---|
| `POST` | `/api/v1/extract/text` | Extract plain text, per-page + full | Both |
| `POST` | `/api/v1/extract/info` | Document metadata | Sync only |
| `POST` | `/api/v1/extract/images` | List embedded images (metadata) | Both |
| `GET` | `/api/v1/extract/images/{imageId}` | Pixel data for one image | Sync only |
| `POST` | `/api/v1/extract/tables` | Table structures | Both |
| `POST` | `/api/v1/screenshot` | Render pages as PNG / JPEG | Both |
| `GET` | `/api/v1/jobs/{jobId}` | Poll async job status | — |
