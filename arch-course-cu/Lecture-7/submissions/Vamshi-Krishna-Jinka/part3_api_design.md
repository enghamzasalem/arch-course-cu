# Part 3: API and Usage
## Task 3.1: Pipeline API Design

## 1. Overview

The Document Processing Pipeline exposes REST APIs to support both:

- **Synchronous processing** → immediate response with extracted data  
- **Asynchronous processing** → background execution with job tracking  

The API is designed to handle document input (file or URL) along with processing options.

---

## 2. API Endpoints

### 2.1 Synchronous API

**Endpoint:**
POST /api/v1/pipeline/run

**Description:**
Processes the document immediately and returns the result.

**Request Body (JSON):**
json
{
  "document_url": "https://example.com/doc.pdf",
  "options": {
    "extract_text_only": false,
    "use_ocr": true
  }
}

Response (Success):
{
  "status": "success",
  "classification": "invoice",
  "extracted_data": {
    "text": "Sample extracted content..."
  }
}

Response (Error):
{
  "status": "error",
  "message": "Invalid file format"
}

### 2.2 Asynchronous API
Create Job

Endpoint:
POST /api/v1/pipeline/jobs

Description:
Submits a document for background processing.

Request Body (JSON):
{
  "document_url": "https://example.com/doc.pdf",
  "options": {
    "use_ocr": true
  },
  "callback_url": "https://client.com/webhook"
}

Response:
{
  "status": "accepted",
  "job_id": "job_12345"
}

Check Job Status

Endpoint:
GET /api/v1/pipeline/jobs/{job_id}

Response (In Progress):
{
  "job_id": "job_12345",
  "status": "processing"
}

Response (Completed):
{
  "job_id": "job_12345",
  "status": "completed",
  "result": {
    "classification": "invoice",
    "extracted_data": {
      "text": "Sample extracted content..."
    }
  }
}

Webhook Callback (Optional)

Description:
If a callback URL is provided, the system sends results when processing is complete.

Webhook Payload:
{
  "job_id": "job_12345",
  "status": "completed",
  "result": {
    "classification": "invoice"
  }
}

## 3. Synchronous Processing Flow
Client sends request to /pipeline/run
API Gateway / Orchestrator receives request
Calls components sequentially:
Validator (sync)
Extractor (sync)
Classifier (sync)
Storage (sync)
Returns final result to client

Connector Usage:

Direct REST calls (sync)
Immediate request-response pattern

Characteristics:

Low latency for small documents
Suitable for interactive applications

## 4. Asynchronous Processing Flow
Client sends request to /pipeline/jobs
API Gateway:
Validates input
Generates job_id
Publishes job to message queue
Background processing:
Extractor consumes job
Publishes events to event bus
Classifier, Storage, Notifier process events
Result is:
Stored in database
Returned via API or webhook

Connector Usage:

Message Queue → job submission
Event Bus → communication between components
REST → optional webhook callback

Characteristics:

High scalability
Suitable for large documents and batch jobs
Non-blocking for clients


## 5. Summary

The API design supports both:

Synchronous mode for quick, real-time processing using direct calls
Asynchronous mode for scalable, event-driven processing using queues and events

This dual approach ensures:

Flexibility for different clients
Efficient resource utilization
Better user experience