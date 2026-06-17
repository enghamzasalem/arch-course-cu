# Task 1.1 – Components and Connectors

## Components

### 1. Validator

**Responsibility:** Validate document format, size, and basic integrity before processing.

**Inputs:** Raw document (file buffer or URL) + options (max size, allowed formats)

**Outputs:** Validated document or error with reason

**Sync/Async:** Sync (caller waits for validation result)

---

### 2. Extractor

**Responsibility:** Extract text content from documents using OCR for images or native extraction for PDFs.

**Inputs:** Validated document + extraction options (OCR language, page range)

**Outputs:** Extracted text with metadata (page numbers, confidence score)

**Sync/Async:** Async (OCR can be slow; should not block the caller)

---

### 3. Classifier

**Responsibility:** Categorize document type (invoice, form, contract, receipt, etc.) based on extracted text.

**Inputs:** Extracted text + classification model

**Outputs:** Document category with confidence score

**Sync/Async:** Sync (fast operation, immediate result needed for routing)

---

### 4. Storage

**Responsibility:** Save extracted data, classification results, and document metadata to database.

**Inputs:** Extracted data, category, metadata

**Outputs:** Record ID and storage confirmation

**Sync/Async:** Sync (caller needs confirmation that data is saved)

---

### 5. Notifier

**Responsibility:** Send completion notifications to clients via webhook or callback URL.

**Inputs:** Record ID, callback URL, result data

**Outputs:** Notification delivery status

**Sync/Async:** Async (notifications should not block the main pipeline)

---

## Connectors

| From | To | Connector Type | Sync/Async | Protocol/Format |
|------|-----|----------------|------------|-----------------|
| Client | API Gateway | REST | Sync | JSON over HTTP |
| Client | Queue | HTTP POST | Async | JSON over HTTP |
| API Gateway | Validator | Direct Call | Sync | Internal message |
| Queue | Validator | Message Queue | Async | Job message |
| Validator | Extractor | Direct Call | Sync | Internal message |
| Extractor | Classifier | Direct Call | Sync | Text + metadata |
| Classifier | Storage | Direct Call | Sync | JSON |
| Storage | Notifier | Direct Call | Async | Record ID + callback |
| Notifier | Webhook | HTTP POST | Async | JSON over HTTPS |

---

## Sync vs Async Justification

**Sync (Validator, Classifier, Storage):**
- Validation needs immediate feedback to reject invalid documents early
- Classification is fast and results are needed immediately for routing
- Storage confirmation is needed before notifying the client

**Async (Extractor, Notifier):**
- OCR extraction can be slow (seconds to minutes) - should not block
- Notifications can fail or be delayed without affecting the core result

**Dual Path (Queue):**
- The pipeline supports both sync (API Gateway direct) and async (Queue)
- Clients choose based on their needs: web app uses sync, batch jobs use async