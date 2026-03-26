# Part 2.2: Choreographed (Event-Driven) Design — Document Processing Pipeline

**Principle:** No central orchestrator. Each component **subscribes** to events and **publishes** new events when its work completes. The **flow emerges** from subscriptions.

---

## 1. Events (examples)

| Event | Payload (conceptual) | When emitted |
|-------|----------------------|--------------|
| `DocumentReceived` | `job_id`, `source_ref`, `options` | After API accepts document (async) or after validation passes |
| `ValidationComplete` | `job_id`, `ok`, `errors?` | Validator finishes |
| `ExtractionComplete` | `job_id`, `extracted_content_ref` | Extractor finishes |
| `ClassificationComplete` | `job_id`, `label`, `confidence` | Classifier finishes |
| `DocumentStored` | `job_id`, `storage_ref` | Storage finishes |
| `PipelineCompleted` | `job_id`, `summary` | Final success (optional aggregate) |
| `PipelineFailed` | `job_id`, `reason` | Any step can emit on failure |

---

## 2. Components: subscribe / publish

| Component | Subscribes to | Publishes when |
|-----------|----------------|----------------|
| **Validator** | `DocumentReceived` | `ValidationComplete` (ok or fail); on fail may publish `PipelineFailed` |
| **Extractor** | `ValidationComplete` (ok=true) | `ExtractionComplete` or `PipelineFailed` |
| **Classifier** | `ExtractionComplete` | `ClassificationComplete` or `PipelineFailed` |
| **Storage** | `ClassificationComplete` | `DocumentStored` or `PipelineFailed` |
| **Notifier** | `DocumentStored`, `PipelineFailed` | May emit external webhook only (no internal event required) |
| **API / Job status** | `DocumentStored`, `PipelineFailed`, `PipelineCompleted` | Updates job status store for `GET /jobs/{id}` |

*No component calls the next by name; the **event bus** routes events to subscribers.*

---

## 3. One advantage

**Loose coupling and extensibility:** New steps (e.g. PII redaction) can **subscribe** to `ExtractionComplete` and **publish** `RedactionComplete` without changing Validator or Extractor code. Teams can evolve services independently.

---

## 4. One disadvantage

**Harder tracing:** End-to-end flow is **implicit** across many handlers. Debugging requires **correlation id** on every event and good observability (distributed tracing); otherwise “why did this job stop?” is harder than in a single orchestrator stack trace.
