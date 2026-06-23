# Part 1.1: Component and Connector Design — Document Processing Pipeline

This document decomposes the pipeline into components, defines connectors between them, and justifies sync vs async usage.

**Scenario:** Documents (PDF, images) flow through: **Validate → Extract (text/OCR) → Classify → Store → Notify**. Clients include web app (sync), batch (async), and API (both).

---

## 1. Components (at least 5)

| # | Component | Single responsibility | Inputs | Outputs | Caller perspective (sync/async) |
|---|-----------|----------------------|--------|---------|----------------------------------|
| 1 | **Document Intake / API Gateway** | Accept uploads (multipart file or URL), validate HTTP/auth, attach correlation id | HTTP request (file, URL, options) | Normalized `DocumentJob` (metadata + pointer to blob or URL) | **Sync** (request/response until handoff to next step) |
| 2 | **Validator** | Check format, size, MIME, virus scan, optional password hints | `DocumentJob` + bytes or signed URL | `ValidationResult` (ok / errors) | **Sync** when called inline; can be **async** if offloaded to worker |
| 3 | **Extractor** | OCR / text extraction (full OCR vs text-only per options) | Validated document reference | `ExtractedContent` (text, layout hints, page count) | **Async** from product perspective (CPU-heavy); often **sync call** inside orchestrator thread with timeout |
| 4 | **Classifier** | Classify document type (e.g. invoice vs form vs other) | `ExtractedContent` + optional metadata | `ClassificationResult` (label, confidence) | **Sync** call (fast model) or **async** if large batch |
| 5 | **Storage Service** | Persist original + derived artifacts (text, thumbnails) | Blobs + metadata + classification | `StorageRef` (URIs, keys) | **Async** (write behind acceptable); API often waits on **sync** acknowledgment |
| 6 | **Notifier** | Send webhook, email, or push when job completes | `job_id`, status, result summary | Delivery ack / log | **Async** (fire-and-forget or queue) |

*Note: Intake + Validator are sometimes merged; here they are separated so “accept HTTP” vs “validate document” are distinct.*

---

## 2. Connectors (between communicating pairs)

| From → To | Connector name | Type | Sync / Async | Protocol / format |
|-----------|----------------|------|--------------|-------------------|
| Client → API Gateway | `HTTPS Upload` | REST HTTP | **Sync** (request until response or job accepted) | JSON + multipart (`multipart/form-data`) |
| API Gateway → Validator | `ValidateRequest` | Direct call (in-process) or **RPC** (gRPC/HTTP) | **Sync** | JSON or protobuf `ValidateRequest` / `ValidationResult` |
| Validator → Extractor | `ExtractionTrigger` | Direct call or **message queue** | **Async** preferred at scale (queue); **Sync** in MVP | Internal DTO or queue message (JSON) |
| Extractor → Classifier | `FeaturesPayload` | Direct call | **Sync** (small payload) | JSON `ExtractedContent` → `ClassificationResult` |
| Classifier → Storage | `PersistArtifacts` | REST HTTP or **async queue** | **Async** (queue + worker) or **Sync** PUT | JSON metadata + binary to object storage API |
| Storage → Notifier | `JobCompleteEvent` | **Event bus** / webhooks | **Async** | CloudEvents or JSON `{ job_id, status, storage_ref }` |
| API Gateway → Job queue (async path) | `EnqueuePipelineJob` | **Message queue** (e.g. SQS, RabbitMQ) | **Async** | JSON job envelope |

---

## 3. Justification: Where Sync vs Async

- **Sync (immediate feedback):**
  - **Validation** (format, size, MIME) should return quickly so the client gets **400** before expensive work.
  - **Classifier** after extraction is often fast; orchestrator may call it **synchronously** to simplify tracing.
  - **Sync API path:** Orchestrator calls Validator → Extractor → Classifier → Storage (blocking) → returns JSON in one HTTP response.

- **Async (scale, long work):**
  - **OCR / extraction** is CPU/GPU heavy; running via **queue + workers** avoids blocking HTTP threads and allows horizontal scaling.
  - **Storage** writes can be pipelined; **Notifier** should never block the critical path—use **async** events or queue.
  - **Async API path:** API returns `job_id` immediately; workers consume queue; **Notifier** fires when pipeline completes.

---

## 4. Summary

- **Five+ components:** Intake/API Gateway, Validator, Extractor, Classifier, Storage, Notifier.
- **Connectors:** Mix of REST, direct/RPC, message queue, and event bus—chosen per latency and coupling needs.
- **Sync vs async:** Sync for validation and end-to-end “small doc” path; async for heavy extraction, durable storage fan-out, and notifications at scale.
