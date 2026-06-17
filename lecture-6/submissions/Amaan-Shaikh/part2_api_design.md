# REST API Design for pdf-parse Service

## Base Path

All endpoints are exposed under the following base path:

```
/api/v1
```

This version prefix allows future API changes without breaking existing clients.

---

## Supported Input Formats

Every request must provide exactly one PDF source.  
The API accepts the following input types:

- Multipart file upload using `file`
- Remote URL using JSON body `{ "url": "..." }`
- Base64 encoded data using JSON body `{ "base64": "..." }`

Only one of these may be present in a single request.

---

## API Endpoints

### POST /api/v1/extract/text

Extracts text content from the PDF file.

Request example:

```json
{
  "url": "https://example.com/document.pdf",
  "pages": [1, 2]
}
```

Response example:

```json
{
  "success": true,
  "text": "Full extracted text",
  "pages": [
    { "page": 1, "text": "Text from page 1" },
    { "page": 2, "text": "Text from page 2" }
  ]
}
```

---

### POST /api/v1/extract/info

Returns metadata and general information about the PDF.

Request example:

```json
{
  "url": "https://example.com/document.pdf",
  "parsePageInfo": true
}
```

Response example:

```json
{
  "success": true,
  "totalPages": 12,
  "info": {
    "Title": "Example",
    "Author": "John Doe"
  }
}
```

---

### POST /api/v1/extract/images

Extracts embedded images from the PDF.

Request example:

```json
{
  "url": "https://example.com/document.pdf",
  "pages": [1],
  "imageThreshold": 80
}
```

Response example:

```json
{
  "success": true,
  "pages": [
    {
      "page": 1,
      "images": [
        {
          "width": 320,
          "height": 240,
          "mimeType": "image/png",
          "base64": "iVBORw0KGgo..."
        }
      ]
    }
  ]
}
```

---

### POST /api/v1/extract/tables

Extracts table data detected in the document.

Request example:

```json
{
  "url": "https://example.com/document.pdf",
  "pages": [2]
}
```

Response example:

```json
{
  "success": true,
  "pages": [
    {
      "page": 2,
      "tables": [
        [
          ["Name", "Age"],
          ["Alice", "24"]
        ]
      ]
    }
  ]
}
```

---

### POST /api/v1/screenshot

Renders selected pages as images.

Request example:

```json
{
  "url": "https://example.com/document.pdf",
  "pages": [1],
  "scale": 1.5
}
```

Response example:

```json
{
  "success": true,
  "pages": [
    {
      "page": 1,
      "width": 1024,
      "height": 1448,
      "mimeType": "image/png",
      "base64": "iVBORw0KGgo..."
    }
  ]
}
```

---

## Error Handling

The API uses standard HTTP status codes.

| Code | Name | Description |
|------|---------|------------|
| 400 | BAD_REQUEST | Invalid request or missing input |
| 413 | FILE_TOO_LARGE | Uploaded file exceeds allowed size |
| 422 | PARSE_ERROR | PDF is valid but cannot be parsed |
| 500 | INTERNAL_ERROR | Unexpected server failure |

Example error response:

```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Exactly one input source must be provided"
  }
}
```

---

## Design Considerations

### Processing Model

The API uses synchronous processing by default.  
Most PDF operations complete quickly, so the result is returned in the same request.

For very large files, a future version may support asynchronous jobs where the client receives a job ID and polls for the result.

---

### Limits

- Maximum file size: 20 MB
- Maximum execution time: 30 seconds

These limits prevent server overload and ensure predictable performance.

---

### Authentication (Optional)

Authentication is not required for local use, but for public deployment an API key can be used.

Example header:

```
X-API-Key: your_key_here
```

This allows rate limiting and access control if the service is exposed online.