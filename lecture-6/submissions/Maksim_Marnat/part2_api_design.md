# Part 2.1: API Design for pdf-parse Service

- REST, HTTPS, JSON, `/api/v1`.
- Input: `multipart/file`, JSON `{ url }`, or `{ base64 }` (same pattern for all `/extract/*`).

## Endpoints

### `POST /api/v1/extract/text`

**200:**
```json
{
  "text": "....",
  "pages": 12,
  "range": { "from": 1, "to": 3 }
}
```

### `POST /api/v1/extract/info`

```json
{
  "metadata": { "Title": "Sample", "Author": "A" },
  "pageCount": 12
}
```

### `POST /api/v1/extract/images`

```json
{
  "images": [
    { "page": 2, "mime": "image/png", "data": "base64..." }
  ]
}
```

### `POST /api/v1/extract/tables`

```json
{
  "tables": [
    { "page": 4, "rows": [["H1", "H2"], ["A", "B"]] }
  ]
}
```

### `POST /api/v1/screenshot`

Params: `pages`, `scale`.

```json
{
  "images": ["base64_png_page_1", "base64_png_page_2"]
}
```

## Errors

```json
{
  "error": {
    "code": "PARSE_ERROR",
    "message": "Failed to parse PDF",
    "details": { "operation": "extract/text" }
  }
}
```

- `400` — bad request / missing input
- `413` — payload too large
- `422` — parse/extract failure
- `500` — server error

## Decisions

- Default synchronous responses; large files → job API below.
- Max size 20 MB (configurable).
- Timeout 30 s.
- API key + rate limit for public deploy.

## Jobs (large files)

- `POST /api/v1/jobs/extract/text` → `202`, `jobId`
- `GET /api/v1/jobs/{jobId}` → `queued|running|done|failed`
- `GET /api/v1/jobs/{jobId}/result` → payload
