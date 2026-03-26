# Part 1.1 — Components and Connectors

## 1. Component Decomposition

The document processing pipeline is decomposed into the following components:

---

### 1. API Gateway / Pipeline API
- **Responsibility:** Entry point for clients (web app, batch jobs, API users)
- **Input:** Document (file or URL), processing options
- **Output:** 
  - Sync: extracted data
  - Async: job_id
- **Interaction style:** Sync (HTTP request/response)

---

### 2. Validator
- **Responsibility:** Validate document format, size, and input parameters
- **Input:** Document + metadata
- **Output:** Validation result (valid/invalid, error message)
- **Interaction style:** Sync (caller waits for validation result)

---

### 3. Extractor (OCR/Text Extraction)
- **Responsibility:** Extract text from document (OCR if needed)
- **Input:** Validated document
- **Output:** Extracted text/content
- **Interaction style:** Typically async (triggered via queue)

---

### 4. Classifier
- **Responsibility:** Classify document type (e.g. invoice, form)
- **Input:** Extracted text
- **Output:** Document category/labels
- **Interaction style:** Typically async

---

### 5. Storage Service
- **Responsibility:** Store document and extracted data
- **Input:** Document + extracted text + classification result
- **Output:** Storage confirmation, document ID
- **Interaction style:** Typically async

---

### 6. Notifier
- **Responsibility:** Notify user when processing is complete
- **Input:** Processing result + user contact (email/webhook)
- **Output:** Notification sent
- **Interaction style:** Async

---

## 2. Connectors

| Source → Target | Connector Name | Type | Sync/Async | Protocol |
|----------------|--------------|------|------------|----------|
| Client → API | submit_request | REST | Sync | JSON over HTTP |
| API → Validator | validate_request | Direct call / REST | Sync | JSON |
| Validator → Extractor | extraction_request | Message Queue | Async | JSON message |
| Extractor → Classifier | classification_request | Message Queue | Async | JSON message |
| Classifier → Storage | storage_request | Message Queue | Async | JSON message |
| Storage → Notifier | notify_event | Event Bus | Async | Event message |
| API → Job Manager | create_job | REST | Sync | JSON over HTTP |
| Job Manager → Queue | enqueue_job | Message Queue | Async | JSON message |

---

## 3. Justification: Sync vs Async

### Sync Communication (API → Validator)
- Required for **immediate feedback**
- Prevents unnecessary processing of invalid documents
- Keeps user experience responsive

---

### Async Communication (Processing Steps)
- Extraction, classification, and storage are **computationally expensive**
- Using message queues:
  - Improves scalability
  - Enables parallel processing
  - Decouples components

---

### Event-Driven Notification
- Notification is triggered via **event bus**
- Allows multiple subscribers (e.g. email service, logging, analytics)



---
![Part 1 Component & Connector Diagram](part1_component_connector_diagram.png)