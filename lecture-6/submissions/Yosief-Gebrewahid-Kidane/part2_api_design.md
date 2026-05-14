# Part 2 – Task 2.1
# API Design for Exposing pdf-parse as an HTTP/REST Service

## 1. Objective

Design a REST API that exposes the functionality of the **pdf-parse** library as a web service.  
This allows different clients such as **web applications, mobile apps, CLI tools, and backend services** to interact with the PDF parsing functionality through HTTP requests.

---

# 2. API Overview

The API follows REST principles and uses **JSON-based requests and responses**.

## Base URL

```
/api/v1
```

## Supported Operations

| Endpoint | Description |
|--------|-------------|
| `POST /api/v1/extract/text` | Extract text from a PDF |
| `POST /api/v1/extract/info` | Extract metadata and document information |
| `POST /api/v1/extract/images` | Extract embedded images |
| `POST /api/v1/extract/tables` | Extract tables from the PDF |
| `POST /api/v1/screenshot` | Render PDF pages as PNG images |

Each endpoint accepts a PDF document as input and returns structured JSON output.

---

# 3. Input Methods

Clients can provide a PDF using **three supported input formats**.

## 3.1 File Upload (Multipart)

```
POST /api/v1/extract/text
Content-Type: multipart/form-data
```

Example:

```
file: document.pdf
```

This method is commonly used for **browser file uploads**.

---

## 3.2 URL Input

Clients may provide a public URL to the PDF.

Example request body:

```json
{
  "url": "https://example.com/document.pdf"
}
```

The server downloads the PDF and processes it.

---

## 3.3 Base64 Input

Clients can send the PDF as a Base64 encoded string.

Example request body:

```json
{
  "base64": "JVBERi0xLjQKJ..."
}
```

This approach is useful for **API integrations and mobile apps**.

---

# 4. API Endpoints

## 4.1 Extract Text

### Endpoint

```
POST /api/v1/extract/text
```

### Request Example

```json
{
  "url": "https://example.com/sample.pdf"
}
```

Optional parameters:

| Parameter | Description |
|----------|-------------|
| `pages` | Specify pages to extract |
| `password` | Password for encrypted PDFs |

Example:

```json
{
  "url": "https://example.com/sample.pdf",
  "pages": [1,2,3]
}
```

### Response Example

```json
{
  "text": "This is the extracted text from the PDF...",
  "pages": 10
}
```

---

# 4.2 Extract Metadata (Info)

### Endpoint

```
POST /api/v1/extract/info
```

### Request Example

```json
{
  "url": "https://example.com/document.pdf"
}
```

### Response Example

```json
{
  "title": "Sample Document",
  "author": "John Doe",
  "pages": 12,
  "creationDate": "2024-02-10"
}
```

---

# 4.3 Extract Images

### Endpoint

```
POST /api/v1/extract/images
```

### Request Example

```json
{
  "url": "https://example.com/document.pdf"
}
```

### Response Example

```json
{
  "images": [
    {
      "page": 2,
      "format": "png",
      "data": "base64EncodedImage..."
    },
    {
      "page": 5,
      "format": "jpeg",
      "data": "base64EncodedImage..."
    }
  ]
}
```

Images are returned as **Base64 encoded data**.

---

# 4.4 Extract Tables

### Endpoint

```
POST /api/v1/extract/tables
```

### Request Example

```json
{
  "url": "https://example.com/document.pdf"
}
```

### Response Example

```json
{
  "tables": [
    {
      "page": 3,
      "data": [
        ["Name", "Age", "City"],
        ["Alice", "25", "Berlin"],
        ["Bob", "30", "London"]
      ]
    }
  ]
}
```

Tables are returned as **structured arrays**.

---

# 4.5 Render Screenshot

### Endpoint

```
POST /api/v1/screenshot
```

### Request Example

```json
{
  "url": "https://example.com/document.pdf",
  "pages": [1],
  "scale": 2
}
```

### Response Example

```json
{
  "screenshots": [
    {
      "page": 1,
      "image": "base64EncodedPNG"
    }
  ]
}
```

---

# 5. Request Format Summary

All JSON requests follow this general format:

```json
{
  "url": "string (optional)",
  "base64": "string (optional)",
  "password": "string (optional)",
  "pages": [1,2,3]
}
```

Only **one input method** should be provided per request:

- `file`
- `url`
- `base64`

---

# 6. Response Format

Successful responses return:

```
HTTP 200 OK
```

Example:

```json
{
  "status": "success",
  "data": {}
}
```

---

# 7. Error Handling

The API uses standard HTTP status codes.

| Status Code | Meaning |
|-------------|--------|
| **400** | Invalid request or missing PDF |
| **413** | File too large |
| **422** | PDF parsing failed |
| **500** | Internal server error |

Example error response:

```json
{
  "status": "error",
  "message": "Invalid PDF file"
}
```

---

# 8. Design Decisions

## 8.1 Synchronous vs Asynchronous Processing

Small PDF files can be processed synchronously.

However, large files may require **asynchronous processing**.

Possible approach:

1. Client uploads PDF
2. API returns a **job ID**
3. Client polls `/api/v1/job/{id}` for results

Example:

```
POST /api/v1/jobs
GET /api/v1/jobs/{jobId}
```

This approach prevents long HTTP request timeouts.

---

## 8.2 File Size Limits

To prevent abuse and excessive resource usage:

| Limit | Value |
|------|------|
| Maximum PDF size | 20 MB |
| Maximum pages | 500 |
| Request timeout | 30 seconds |

These limits protect server performance.

---

## 8.3 Authentication 

For production use, the API may require authentication.

Example:

```
Authorization: Bearer API_KEY
```

This prevents unauthorized usage of the service.

---

## 8.4 Rate Limiting

Rate limiting can prevent abuse.

Example limits:

| Client Type | Limit |
|-------------|-------|
| Free tier | 100 requests/hour |
| Paid tier | 1000 requests/hour |

This ensures fair resource usage.

---

# 9. Rationale

This API design provides several advantages:

| Benefit | Explanation |
|-------|-------------|
| Clear REST endpoints | Each extraction feature has a dedicated endpoint |
| Flexible input | Supports file uploads, URLs, and Base64 data |
| Structured JSON output | Easy to integrate with web and mobile apps |
| Scalable architecture | Supports asynchronous processing for large files |
| Security support | Allows authentication and rate limiting |



![API Architecture](part2_api_architecture.png)