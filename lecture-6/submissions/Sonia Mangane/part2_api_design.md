## Task 2.1: API Design for pdf-parse Service

This section describes a REST API for the redesigned `pdf-parse` library.  
The idea is to follow an API-first approach, so different clients (like web apps or backend services) can use it easily without needing to know how the PDF parsing works internally.

---

## 1. API Endpoints

The API is divided based on what kind of data the user wants to extract from the PDF.  
Each endpoint does one specific task to keep things simple.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/extract/text` | Extracts text content and page count |
| POST | `/api/v1/extract/info` | Gets metadata like author and title |
| POST | `/api/v1/extract/images` | Returns images as base64 strings |
| POST | `/api/v1/extract/tables` | Extracts tables into JSON |
| POST | `/api/v1/extract/screenshot` | Creates PNG screenshots of pages |

---

## 2. Request & Response Format

The API uses:
- JSON for sending and receiving data  
- Standard HTTP status codes  

This makes it easy to use in different programming languages.

---

### 2.1 Request Format (Unified Input)

The user can provide the PDF in different ways:

- **URL** → link to a PDF online  
- **Base64** → encoded string (for smaller files)  
- **Multipart upload** → for bigger files  

#### Example Request

**POST `/api/v1/extract/text`**

```json
{
  "source": {
    "type": "url",
    "value": "https://example.com/document.pdf"
  },
  "options": {
    "pages": [1, 2, 5],
    "verbosity": "low"
  }
}
```

### 2. Response Format

The API returns structured and predictable responses.

Example Success Response (200 OK)

```json
{
  "status": 200,
  "result": {
    "text": "Extracted content from the PDF...",
    "pageCount": 5
  },
  "metadata": {
    "version": "1.4",
    "author": "Gemini"
  }
}
```

## 3. Design Decisions & Rationale

### 3.1 Sync vs. Async Processing

**Decision:**
- Small files (less than 5MB) are processed synchronously  
- Larger files are processed asynchronously using a job-based approach  

**Rationale:**
- Big PDF files can take a while to process and might cause request timeouts  
- Using async processing helps avoid blocking the client and makes the system more responsive  

---

### 3.2 Size Limits & Timeouts

- **Max file size:** 20MB  
- **Timeout:** 30 seconds  

**Rationale:**
- These limits help prevent the server from being overloaded  
- It also keeps the system stable and ensures requests don’t run forever  

---

### 3.3 Error Handling

The API returns clear error codes so developers can easily understand what went wrong.

| Code | Meaning | Description |
|------|--------|-------------|
| 400 | Bad Request | Input is invalid or required fields are missing |
| 413 | Payload Too Large | File is bigger than the allowed 20MB |
| 422 | Unprocessable Entity | PDF is valid but cannot be processed |
| 500 | Internal Server Error | Something unexpected went wrong on the server |

---

## 4. Evolution & Maintenance

To keep the API simple and easy to maintain:

- Only the most important features are included at the start  
- Internal implementation details (like which parsing library is used) are hidden  
- The backend can be changed later without affecting users of the API  

**Overall Goal:**
- Keep the API simple and easy to use  
- Make sure it stays stable over time  
- Still allow room for future improvements  