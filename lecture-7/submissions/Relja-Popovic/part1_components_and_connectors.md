# Part 1.1 – Component and Connector Design

## Components

### 1. Validator
**Responsibility:** Checks that the incoming document is well-formed, within size limits, and of a supported format.

| | |
|---|---|
| **Inputs** | Raw file bytes or URL, declared MIME type |
| **Outputs** | `ValidationResult { valid: boolean, error?: string }` |
| **Caller perspective** | Sync - must complete before the pipeline can proceed |

---

### 2. Extractor
**Responsibility:** Performs text extraction or full OCR depending on the requested options.

| | |
|---|---|
| **Inputs** | Validated document bytes, extraction options |
| **Outputs** | `ExtractionResult { text: string, pages: PageData[], confidence: number }` |
| **Caller perspective** | Async - CPU/time-intensive; runs in a background worker |

---

### 3. Classifier
**Responsibility:** Assigns a document type based on the extracted content.

| | |
|---|---|
| **Inputs** | `ExtractionResult` |
| **Outputs** | `ClassificationResult { type: string, confidence: number, tags: string[] }` |
| **Caller perspective** | Async - depends on Extractor output; runs after extraction completes |

---

### 4. Storage
**Responsibility:** Persists the original document and the structured extraction and classification results. 

| | |
|---|---|
| **Inputs** | Original document bytes, `ExtractionResult`, `ClassificationResult`, job metadata |
| **Outputs** | `StorageResult { documentId: string, storageUrl: string }` |
| **Caller perspective** | Async - pipeline continues once saving is completed |

---

### 5. Notifier
**Responsibility:** Delivers a completion notification to the client via webhook when async processing finishes.

| | |
|---|---|
| **Inputs** | `StorageResult`, `ClassificationResult`, client callback URL, job ID |
| **Outputs** | HTTP POST to client webhook; internal delivery receipt event |
| **Caller perspective** | Async - fire-and-forget from the pipeline's perspective |

---

## Connectors

### Client → Validator
| Property | Value |
|---|---|
| **Type** | REST over HTTPS |
| **Style** | Sync |
| **Format** | `multipart/form-data` for file upload; `application/json` for URL input |

---

### Validator → Extractor
| Property | Value |
|---|---|
| **Type** | Message queue (e.g. RabbitMQ / SQS) |
| **Style** | Async - Validator enqueues the job and returns a `jobId` to the client |
| **Format** | JSON: `{ jobId, documentRef, options, callbackUrl }` |

---

### Extractor → Classifier
| Property | Value |
|---|---|
| **Type** | Event bus (publish / subscribe) |
| **Style** | Async - Extractor publishes `extraction.completed` |
| **Format** | JSON event: `{ jobId, ExtractionResult }` |

---

### Classifier → Storage
| Property | Value |
|---|---|
| **Type** | Event bus |
| **Style** | Async - Classifier publishes `classification.completed` |
| **Format** | JSON event: `{ jobId, ExtractionResult, ClassificationResult, documentRef }` |

---

### Storage → Notifier
| Property | Value |
|---|---|
| **Type** | Event bus |
| **Style** | Async - Storage publishes `storage.completed` |
| **Format** | JSON event: `{ jobId, documentId, storageUrl, callbackUrl }` |

---

## Sync vs Async Justification

| Step | Style | Reason |
|---|---|---|
| Client → Validator | Sync | no value in queuing an invalid document |
| Validator → Extractor | Async | Extraction is CPU-intensive and long-running; must not block the HTTP request |
| Extractor → Classifier | Async | Naturally follows async extraction; event-driven keeps components independent |
| Classifier → Storage | Async | I/O-bound |
| Storage → Notifier | Async | Fire-and-forget; delivery failure must not roll back upstream steps |