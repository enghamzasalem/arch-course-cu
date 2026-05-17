# Part 2 – Task 2.1: API Design

## Overview

This document defines a **RESTful API design** that exposes the redesigned pdf-parse architecture as a service. The API maps core extraction capabilities (text, metadata, images, tables, screenshots) to HTTP endpoints with clear request/response contracts, error handling, and scalability considerations.

---

## 1. API Design Approach

### 1.1 Design Strategy

Two possible approaches were considered:

| Approach           | Description                         | Decision       |
| ------------------ | ----------------------------------- | -------------- |
| Multiple endpoints | One endpoint per operation          | ✅ Selected     |
| Unified endpoint   | Single `/extract` with action param | ❌ Not selected |

### Rationale

* Clear separation of concerns
* Easier validation and documentation
* Better API discoverability

---

## 2. Base URL and Versioning

```
/api/v1
```

* Versioning ensures backward compatibility
* Future changes can be introduced via `/v2`

---

## 3. Input Methods

Clients can provide PDF input in three ways:

### 3.1 File Upload (Multipart)

```
Content-Type: multipart/form-data
file: <PDF_FILE>
```

### 3.2 URL Input

```json
{
  "url": "https://example.com/sample.pdf"
}
```

### 3.3 Base64 Input

```json
{
  "base64": "JVBERi0xLjQKJ..."
}
```

### Validation Rules

* Only one input type allowed per request
* Max file size enforced (e.g., 10MB)

---

## 4. API Endpoints

### 4.1 Extract Text

**POST** `/api/v1/extract/text`

#### Request

* multipart OR JSON (url/base64)

#### Response

```json
{
  "text": "Full extracted text...",
  "pages": 10
}
```

---

### 4.2 Extract Metadata

**POST** `/api/v1/extract/info`

#### Response

```json
{
  "title": "Sample PDF",
  "author": "John Doe",
  "pages": 10,
  "creationDate": "2024-01-01"
}
```

---

### 4.3 Extract Images

**POST** `/api/v1/extract/images`

#### Response

```json
{
  "images": [
    {
      "page": 1,
      "data": "base64-image-data"
    }
  ]
}
```

---

### 4.4 Extract Tables

**POST** `/api/v1/extract/tables`

#### Response

```json
{
  "tables": [
    {
      "page": 2,
      "rows": [["A1", "B1"], ["A2", "B2"]]
    }
  ]
}
```

---

### 4.5 Screenshot (Render Pages)

**POST** `/api/v1/screenshot`

#### Request Parameters

```json
{
  "pages": [1, 2],
  "scale": 2
}
```

#### Response

```json
{
  "images": ["base64-png-data"]
}
```

---

## 5. Error Handling

| Status Code | Description                        |
| ----------- | ---------------------------------- |
| 400         | Invalid input (no file/url/base64) |
| 413         | File too large                     |
| 422         | Parsing failed                     |
| 500         | Internal server error              |

### Example Error Response

```json
{
  "error": {
    "code": 422,
    "message": "Failed to parse PDF",
    "details": "Corrupted or unsupported format"
  }
}
```

---

## 6. Design Decisions

### 6.1 Synchronous vs Asynchronous

#### Current Design: Synchronous

* Suitable for small to medium PDFs
* Simple request-response model

#### Future Enhancement: Asynchronous Jobs

```
POST /api/v1/jobs
GET /api/v1/jobs/{id}
```

* For large files or long-running tasks

---

### 6.2 Size Limits and Timeouts

* Max file size: 10MB (configurable)
* Timeout: 30 seconds

---

### 6.3 Authentication (Optional)

* API Key-based authentication

```
Authorization: Bearer <API_KEY>
```

---

### 6.4 Rate Limiting

* Prevent abuse
* Example: 100 requests/minute per client

---

## 7. Mapping to Internal Architecture

| API Layer        | Internal Component |
| ---------------- | ------------------ |
| Input handling   | IPDFSource         |
| Session creation | IPDFParser         |
| Extraction       | IPDFExtractor      |

Flow:

Client → API → Service Layer → Parser → Extractor → Response

---

## 8. Benefits of the API Design

### 8.1 Reusability

* Same backend supports multiple clients:

  * Web apps
  * Mobile apps
  * CLI tools

### 8.2 Scalability

* Can be extended with async processing
* Stateless API design

### 8.3 Maintainability

* Clear endpoint separation
* Easy to extend (e.g., `/extract/links`)

---

## 9. Conclusion

This API design cleanly exposes pdf-parse capabilities through:

* Well-defined endpoints
* Consistent input/output formats
* Strong separation of concerns

It aligns with the redesigned interface architecture and ensures high reusability across different platforms and use cases.
