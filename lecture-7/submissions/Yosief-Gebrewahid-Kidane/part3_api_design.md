# Part 3.1 — Pipeline API Design

## 1. API Endpoints

The system exposes both **synchronous** and **asynchronous** endpoints to support different client needs.

---

### 1.1 Synchronous API

#### Endpoint
POST /api/v1/pipeline/run

#### Description
Processes the document immediately and returns the result in the response.

#### Request Body (JSON)
{
  "document_url": "https://example.com/doc.pdf",
  "options": {
    "ocr": true,
    "extract_text_only": false
  }
}

#### Response (Success)
{
  "status": "completed",
  "extracted_text": "...",
  "classification": "invoice"
}

#### Response (Error)
{
  "status": "failed",
  "error": "validation_error"
}

---

### 1.2 Asynchronous API

#### Create Job
POST /api/v1/pipeline/jobs

#### Description
Creates a background processing job and returns a job ID.

#### Request Body (JSON)
{
  "document_url": "https://example.com/doc.pdf",
  "options": {
    "ocr": true
  },
  "callback_url": "https://client.com/webhook"
}

#### Response
{
  "job_id": "job-12345",
  "status": "pending"
}

---

#### Get Job Status
GET /api/v1/pipeline/jobs/{job_id}

#### Response (In Progress)
{
  "job_id": "job-12345",
  "status": "processing"
}

#### Response (Completed)
{
  "job_id": "job-12345",
  "status": "completed",
  "result": {
    "extracted_text": "...",
    "classification": "invoice"
  }
}

---

## 2. Sync Processing Flow

1. Client sends request to `/pipeline/run`
2. API calls **Validator** (sync)
3. If valid:
   - Calls **Extractor**
   - Calls **Classifier**
   - Calls **Storage**
   - Calls **Notifier**
4. API returns final result to client



---

## 3. Async Processing Flow

1. Client sends request to `/pipeline/jobs`
2. API creates job via **Job Manager**
3. Job is placed in **Message Queue**
4. Worker processes pipeline:
   - Validator → Extractor → Classifier → Storage
5. **Event Bus** triggers notification
6. Result stored and optionally sent to `callback_url`

👉 Uses **message queue + event-driven choreography**

---

## 4. Key Design Decisions

- **Sync API**
  - Immediate validation and extraction
  - Simple, good for small documents or interactive clients

- **Async API**
  - Handles long-running or resource-intensive processing
  - Uses event-driven design for decoupling and scalability

- **Hybrid approach**
   - Orchestration for initial steps
   - Choreography for downstream processing (storage, notification)

---
![Part 3 Sequence Diagram](part3_sequence_diagram.png)