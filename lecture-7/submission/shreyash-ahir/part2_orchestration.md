# Part 2.1 — Orchestrated Pipeline Design

## The Orchestrator

The **PipelineOrchestrator** is a dedicated component that runs inside the
async worker process.  It is activated when a job message is dequeued.
All other components (Validator, Extractor, Classifier, Storage, Notifier)
are passive — they perform work only when the Orchestrator calls them.

---

## Exact Call Sequence

```
1.  Dequeue message: { job_id, doc_id, storage_url, options }
2.  Orchestrator → Validator.validate(doc_id, storage_url)
    ├── OK  → continue to step 3
    └── FAIL → Orchestrator marks job FAILED, calls Notifier.notifyError(job_id, reason) → STOP
3.  Orchestrator → Extractor.extract(doc_id, storage_url, options)
    ├── OK  → extraction_result → continue to step 4
    └── FAIL → Orchestrator retries up to 3 times with exponential back-off
               After 3 failures → marks job FAILED, notifies → STOP
4.  Orchestrator → Classifier.classify(doc_id, extraction_result.text)
    ├── OK  → classification_result → continue to step 5
    └── FAIL → logs warning, uses label="unclassified", continues (non-blocking failure)
5.  Orchestrator → Storage.store(doc_id, raw_bytes, extraction_result, classification_result)
    ├── OK  → storage_result (file_url, result_url) → continue to step 6
    └── FAIL → Orchestrator retries up to 3 times; after 3 failures → job FAILED → STOP
6.  Orchestrator → Notifier.notify(job_id, webhook_url, storage_result)
    └── publishes job.complete message to notification queue; Orchestrator marks job DONE
```

---

## Error and Retry Handling

The Orchestrator is the single place where all error handling logic lives.
This is the key advantage of orchestration: retry policies, partial failure
treatment, and compensation logic are all visible in one place.

- **Validator failure**: Hard stop.  Invalid documents are rejected immediately.
  No retries — the document itself is the problem.

- **Extractor failure**: Retried up to 3 times with exponential back-off
  (2s, 4s, 8s).  OCR failures are often transient (worker memory pressure,
  temporary GPU unavailability).

- **Classifier failure**: Non-blocking — the Orchestrator substitutes
  `label="unclassified"` and continues.  Classification is enrichment; losing
  it does not lose the document.

- **Storage failure**: Retried up to 3 times.  If all retries fail, the job
  is marked FAILED and the client is notified of failure.

- **Notifier failure**: The Notifier handles its own retries independently.
  The Orchestrator's responsibility ends after enqueueing the notification.

---

## One Advantage

**Centralized visibility and control.**  
The entire pipeline flow — the sequence, the retry policies, the error
handling — is encoded in one component.  When a developer asks "what
happens if extraction fails on step 3?", the answer is in a single file.
Adding a new step (e.g. an AuditLogger between Storage and Notifier) means
editing the Orchestrator and nowhere else.  This directly applies the
"few interfaces" principle: components communicate with as few others as
possible, and the Orchestrator mediates all of them.

## One Disadvantage

**Single point of coupling.**  
The Orchestrator must know the interface of every component in the pipeline.
If the Extractor's input format changes, the Orchestrator must be updated.
If a new team wants to add a step without touching the Orchestrator, they
cannot — every pipeline change goes through this one component.  In a large
team, this creates a bottleneck and makes the Orchestrator a high-churn,
high-risk file.
