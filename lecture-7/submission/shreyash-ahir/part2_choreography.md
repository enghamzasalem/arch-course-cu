# Part 2.2 — Choreographed (Event-Driven) Pipeline Design

## No Central Orchestrator

In the choreographed design, no single component knows the full pipeline.
Each component subscribes to one event, does its work, and publishes the
next event.  The pipeline flow emerges from the chain of subscriptions.
The event bus is the only shared infrastructure.

---

## Event Catalogue

| Event | Payload (key fields) | Published by | Consumed by |
|---|---|---|---|
| `document.received` | `job_id, doc_id, storage_url, options, webhook_url` | API Gateway | Validator |
| `document.validated` | `job_id, doc_id, storage_url, options` | Validator | Extractor |
| `document.invalid` | `job_id, reason` | Validator | Notifier |
| `extraction.complete` | `job_id, doc_id, text, confidence` | Extractor | Classifier |
| `extraction.failed` | `job_id, attempt, error` | Extractor | Extractor (retry) / Notifier |
| `classification.complete` | `job_id, doc_id, label, confidence` | Classifier | Storage |
| `document.stored` | `job_id, file_url, result_url` | Storage | Notifier |
| `storage.failed` | `job_id, attempt, error` | Storage | Storage (retry) / Notifier |
| `notification.sent` | `job_id` | Notifier | (terminal — logging only) |

---

## Component Behaviour

### API Gateway

**Subscribes to:** nothing  
**Publishes:**
- `document.received` — immediately after accepting a valid HTTP upload and
  writing the file to object store.  Does not wait for any other component.
  Returns `{ job_id }` to the HTTP client at this point.

---

### Validator

**Subscribes to:** `document.received`  
**Publishes:**
- `document.validated` — if the document passes all format and size checks.
- `document.invalid` — if validation fails (wrong type, too large, corrupted).

No retry logic needed here — validation is deterministic.

---

### Extractor

**Subscribes to:** `document.validated`  
**Publishes:**
- `extraction.complete` — when OCR/text extraction succeeds.
- `extraction.failed` — on error (with `attempt` counter).

**Retry pattern:** The Extractor subscribes to its own `extraction.failed`
event (up to attempt 3); on attempt > 3, it publishes to a dead-letter
queue and fires a final `extraction.failed` event that the Notifier watches.

---

### Classifier

**Subscribes to:** `extraction.complete`  
**Publishes:**
- `classification.complete` — always (uses `label="unclassified"` on internal
  failure; classification errors do not stop the pipeline).

---

### Storage

**Subscribes to:** `classification.complete`  
**Publishes:**
- `document.stored` — after persisting document and result to DB + object store.
- `storage.failed` — on I/O error (retried up to 3 times, same pattern as Extractor).

---

### Notifier

**Subscribes to:** `document.stored`, `document.invalid`, `extraction.failed`
(dead-letter), `storage.failed` (dead-letter)  
**Publishes:**
- `notification.sent` — after delivering the webhook POST or updating the
  job status record.

The Notifier handles both success and failure paths by subscribing to the
appropriate terminal events.

---

## One Advantage

**Independent deployability and scalability.**  
Each component can be scaled, deployed, and updated independently.  If
document processing volume spikes, only the Extractor's worker pool scales
out — it simply consumes more events from the same queue.  Adding a new
subscriber (e.g. an AuditLogger that subscribes to `document.stored`) adds
zero changes to any existing component.  Components remain *unaware of each
other*, which is exactly the message bus's core property from the course
material.

## One Disadvantage

**Distributed tracing is hard.**  
Understanding the full path of a single document requires correlating events
across six components using `job_id`.  A failure that silently drops an event
(e.g. a crash between publish and acknowledge) can leave a job stuck with no
error reported.  There is no single file or component where a developer can
read the full pipeline logic — the "what happens next" answer is distributed
across six files.  Debugging a stuck job requires querying the event bus,
the job store, and each component's logs.
