# Part 1: Component and Connector Design
## Task 1.1: Component Decomposition

## 1. Overview
The Document Processing Pipeline is designed as a composable system where independent components are connected using well-defined connectors. The pipeline processes documents through the following stages:

Upload → Validate → Extract → Classify → Store → Notify

The system supports:
- **Synchronous flow**: Immediate response (e.g., validation + quick extraction)
- **Asynchronous flow**: Background processing with notification

---

## 2. Component Decomposition

### 2.1 API Gateway / Ingestion Service
- **Responsibility**: Accept document upload (file/URL) and user options
- **Input**: HTTP request (file/URL, options)
- **Output**:
  - Sync: validation result or extracted data
  - Async: job ID
- **Type**: Sync (entry point), triggers async pipeline

---

### 2.2 Validator
- **Responsibility**: Validate file type, size, format, and basic integrity
- **Input**: Document metadata + file
- **Output**:
  - Validated document OR error response
- **Type**: Sync

---

### 2.3 Extractor (OCR/Text Extraction)
- **Responsibility**: Extract text/content from documents (OCR for images, parsing for PDFs)
- **Input**: Validated document
- **Output**: Extracted text/content
- **Type**: Async

---

### 2.4 Classifier
- **Responsibility**: Classify document type (e.g., invoice, receipt, form)
- **Input**: Extracted text
- **Output**: Document category + metadata
- **Type**: Async

---

### 2.5 Storage Service
- **Responsibility**: Persist document, extracted data, and classification results
- **Input**: Processed data (text + classification)
- **Output**: Storage confirmation (document ID, metadata)
- **Type**: Async

---

### 2.6 Notifier
- **Responsibility**: Notify client when processing is complete
- **Input**: Processing result + user callback/webhook
- **Output**: Notification (email/webhook/API callback)
- **Type**: Async

---

## 3. Connector Design

| Source → Target | Connector Name | Type | Sync/Async | Protocol/Format |
|----------------|---------------|------|-----------|-----------------|
| Client → API Gateway | Upload API | REST HTTP | Sync | JSON + multipart file |
| API Gateway → Validator | Validate Request | Direct Call / REST | Sync | JSON |
| API Gateway → Extractor | Submit Job | Message Queue | Async | JSON message |
| Validator → Extractor | Validated Document | Message Queue | Async | Internal message format |
| Extractor → Classifier | Extracted Data | Event Bus / Queue | Async | JSON |
| Classifier → Storage | Store Results | Message Queue | Async | JSON |
| Storage → Notifier | Processing Complete Event | Event Bus | Async | Event message |
| Notifier → Client | Callback/Webhook | REST HTTP | Async | JSON |

---

## 4. Connector Details

### 4.1 Synchronous Connectors
- **Client → API Gateway**
- **API Gateway → Validator**

**Reason:**
- Immediate feedback required (invalid file, wrong format)
- Improves user experience
- Prevents unnecessary processing

---

### 4.2 Asynchronous Connectors
- **API Gateway → Extractor**
- **Extractor → Classifier**
- **Classifier → Storage**
- **Storage → Notifier**

**Reason:**
- OCR and classification are compute-intensive
- Enables scalability (parallel processing)
- Improves system responsiveness
- Decouples components (failure isolation)

---

## 5. Message Passing Design

### Example Internal Message Format (JSON)
```json
{
  "job_id": "12345",
  "document_url": "s3://bucket/doc.pdf",
  "options": {
    "ocr": true,
    "extract_only": false
  },
  "status": "validated"
}