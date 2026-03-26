# Part 1 — Components and connectors

## Components (6)

| Component | Responsibility | Inputs | Outputs | Caller view |
|-----------|----------------|--------|---------|---------------|
| **Pipeline API** | Accept uploads/URLs + options; route sync vs async; authorize | HTTP: file/URL, `mode`, options | Sync: result JSON; Async: `job_id` | **Sync** (blocking) or **Async** (202 + poll) |
| **Validator** | Format/malware/size checks; reject early | Document ref (blob id/URL), options | `ValidationResult` (ok + metadata or error) | **Sync** (caller waits) |
| **Extractor** | Text / OCR from PDF or images | Validated ref, extract options | `ExtractionArtifact` (text, layout hints) | **Sync** (small path) / **Async** (worker + queue) |
| **Classifier** | Label doc type (invoice, form, …) | Extracted text + metadata | `Classification` (label, confidence) | **Sync** (fast model call) |
| **Storage** | Persist original + derived artifacts | Blobs + labels + `job_id` | Stored URIs / keys | **Sync** (ack write) from caller; can enqueue replica async |
| **Notifier** | Webhook / email / internal bus when job completes | `job_id`, summary, callback URL | Delivery status (best-effort) | **Async** (fire-and-forget) |

## Connectors

| From | To | Connector | Type | Sync/async | Format |
|------|----|-----------|------|------------|--------|
| Client | Pipeline API | `HTTPS_JSON` | REST | Sync or Async (HTTP) | JSON (+ multipart) |
| Pipeline API | Validator | `Internal_RPC` | gRPC / in-proc | **Sync** | Protobuf / DTO |
| Pipeline API | Job queue | `PipelineCommands` | Message queue | **Async** | JSON command envelope |
| Job queue | Worker (API tier) | `Dequeue` | Message queue | **Async** | JSON command envelope |
| Worker (API tier) | Validator | `Internal_RPC` | gRPC | **Sync** | DTO |
| Validator | Extractor | `ExtractRequest` | Direct call or queue | **Sync** (inline) / **Async** (queue) | Internal message |
| Extractor | Classifier | `ClassifyRequest` | Direct call | **Sync** | Internal DTO |
| Classifier | Storage | `StoreArtifacts` | REST / SDK to object store | **Sync** (PUT) | Binary + JSON metadata |
| Storage | Notifier | `CompletionEvents` | Event bus / topic | **Async** | CloudEvents-style JSON |
| Pipeline API | Notifier | `NotifyClient` | HTTPS webhook client | **Async** | JSON POST |

## Sync vs async (why)

- **Sync:** Validation and classification are fast and give immediate errors or labels the client may need in one round-trip; sync API path chains them under a timeout budget.
- **Async:** OCR/extraction and end-to-end batch scale horizontally; a **queue** buffers work; **Notifier** and event bus avoid blocking the API on webhooks and fan-out.
