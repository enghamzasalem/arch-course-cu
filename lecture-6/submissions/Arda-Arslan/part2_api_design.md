# API Design for pdf-parse REST Service

## Base URL

```
/api/v1
```

---

## Input Methods

Each request must include exactly one of:

- `file` — multipart/form-data upload
- `url` — PDF URL in JSON body
- `base64` — base64-encoded PDF in JSON body

---

## Endpoints

### POST /api/v1/extract/text

Request:

```json
{
  "url": "https://example.com/file.pdf",
  "pages": [1, 2]
}
```

Response:

```json
{
  "success": true,
  "text": "Extracted text...",
  "pages": [
    { "page": 1, "text": "Page 1 text" },
    { "page": 2, "text": "Page 2 text" }
  ]
}
```

---

### POST /api/v1/extract/info

Request:

```json
{
  "url": "https://example.com/file.pdf",
  "parsePageInfo": true
}
```

Response:

```json
{
  "success": true,
  "totalPages": 12,
  "info": {
    "Title": "Sample PDF",
    "Author": "John Doe"
  }
}
```

---

### POST /api/v1/extract/images

Request:

```json
{
  "url": "https://example.com/file.pdf",
  "imageThreshold": 80,
  "pages": [1]
}
```

Response:

```json
{
  "success": true,
  "pages": [
    {
      "page": 1,
      "images": [
        { "width": 320, "height": 240, "mimeType": "image/png", "base64": "iVBORw0KGgo..." }
      ]
    }
  ]
}
```

---

### POST /api/v1/extract/tables

Request:

```json
{
  "url": "https://example.com/file.pdf",
  "pages": [2]
}
```

Response:

```json
{
  "success": true,
  "pages": [
    {
      "page": 2,
      "tables": [
        [["Name", "Age"], ["Alice", "24"]]
      ]
    }
  ]
}
```

---

### POST /api/v1/screenshot

Request:

```json
{
  "url": "https://example.com/file.pdf",
  "pages": [1],
  "scale": 1.5
}
```

Response:

```json
{
  "success": true,
  "pages": [
    { "page": 1, "width": 1024, "height": 1448, "mimeType": "image/png", "base64": "iVBORw0KGgo..." }
  ]
}
```

---

## Error Responses

- **400** `BAD_REQUEST` — missing or invalid input
- **413** `FILE_TOO_LARGE` — file exceeds size limit
- **422** `PARSE_ERROR` — valid input but PDF cannot be parsed
- **500** `INTERNAL_ERROR` — unexpected server error

Example:

```json
{
  "success": false,
  "error": { "code": "BAD_REQUEST", "message": "Provide exactly one input source." }
}
```

---

## Design Decisions

**Sync vs async:** Synchronous processing is used. Most operations return results immediately. For very large files, async job-based processing could be added in a future version.

**Size limits:** Maximum file size is 20 MB. Maximum processing time is 30 seconds.

**Authentication:** Optional. API key via `X-API-Key` header is recommended for public deployments.