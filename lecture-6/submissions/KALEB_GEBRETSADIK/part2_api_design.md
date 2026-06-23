# Part 2: API Design for pdf-parse Service

## 1. API Endpoints
To keep the REST API clean and aligned with the single responsibility principle, I chose dedicated endpoints for each extraction type rather than a single bloated `/parse` endpoint.

- `POST /api/v1/extract/text`
- `POST /api/v1/extract/info`
- `POST /api/v1/extract/images`
- `POST /api/v1/extract/tables`
- `POST /api/v1/screenshot`

**Providing the PDF Input:**
Clients can provide the PDF in two ways for all the above endpoints:
1. **Multipart File Upload:** Sending a standard `multipart/form-data` request containing the physical `.pdf` file.
2. **JSON Payload:** Sending a JSON object with either a URL to fetch from, or a base64 encoded string.

## 2. Request and Response Formats

### 2.1 Request Example (JSON)
```json
{
  "source": {
    "type": "url",
    "data": "https://example.com/sample.pdf",
    "password": "optional_password"
  },
  "options": {
    "pages": "1-5",
    "scale": 1.5
  }
}
```

### 2.2 Response Examples
**Successful Extraction (Text):**
```json
{
  "status": "success",
  "data": {
    "text": "This is the extracted text from the PDF.",
    "totalPages": 5
  }
}
```

**Successful Extraction (Info/Metadata):**
```json
{
  "status": "success",
  "data": {
    "author": "John Doe",
    "title": "Master's Thesis",
    "pageCount": 42
  }
}
```

### 2.3 Error Responses
- **400 Bad Request:** Missing source `data` or invalid JSON structure.
- **413 Payload Too Large:** The uploaded file or the base64 string exceeds the 10MB limit.
- **422 Unprocessable Entity:** The PDF is corrupted, password-protected (with no password provided), or fails to parse.
- **500 Internal Server Error:** Unexpected server crash or memory issue during parsing.

## 3. Design Decisions & Rationale

- **Synchronous vs. Asynchronous:** 
  For this assignment, I decided to keep the API **synchronous** for simplicity. However, PDF parsing can be CPU-intensive. If we were building an enterprise system where users upload 100-page plus PDFs, a synchronous request would likely hit the HTTP timeout. A better future-proof approach would be returning a `202 Accepted` with a Job ID, and letting the client poll an `/api/v1/status/:jobId` endpoint (or use WebHooks).
  
- **Size Limits & Timeouts:** 
  To prevent denial of service (DoS) attacks, I would strictly enforce a **10MB file size limit** and a **30-second request timeout**. Any extraction taking longer than 30 seconds will be killed and return a 500 error.

- **Rate Limiting:**
  Since parsing is expensive, we absolutely need IP-based rate limiting (e.g., max 20 requests per minute per IP) to ensure fair usage of the server CPU.
