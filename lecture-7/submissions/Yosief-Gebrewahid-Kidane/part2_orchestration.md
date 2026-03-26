# Part 2.1 — Orchestrated Design

## 1. Orchestrator Component

The pipeline is designed using an **orchestration pattern**, where a central component controls the entire workflow.

### Orchestrator: PipelineOrchestrator (inside API Service)

- The **PipelineOrchestrator** is responsible for coordinating all steps in the pipeline.
- It receives the request from the API and calls each component in a defined sequence.
- It ensures that each step completes successfully before moving to the next.

---

## 2. Sequence of Execution

The orchestrator executes the pipeline in the following order:

1. **Validate Document**
   - Calls `Validator` (synchronous)
   - If validation fails → return error immediately

2. **Extract Text (OCR)**
   - Calls `Extractor`
   - Waits for extracted content

3. **Classify Document**
   - Calls `Classifier`
   - Receives document type (e.g. invoice, form)

4. **Store Results**
   - Calls `Storage Service`
   - Saves document and extracted data

5. **Send Notification**
   - Calls `Notifier`
   - Sends email or webhook notification

6. **Return Response**
   - Sync: return extracted data
   - Async: return job completion status

---

## 3. Error Handling and Retries

- **Validation errors**
  - Immediately returned to the client (no retry)

- **Extractor / Classifier failures**
  - Retry mechanism (e.g. 2–3 attempts)
  - If still failing → mark job as failed

- **Storage failures**
  - Critical step → retry until success or fail job

- **Notification failures**
  - Non-critical → retry in background
  - Does not block pipeline completion

---

## 4. Advantages of Orchestration

- **Centralized control**
  - Entire workflow is visible in one place
  - Easy to understand and modify

---

## 5. Disadvantages of Orchestration

- **Single point of bottleneck**
  - Orchestrator handles all logic
  - Can limit scalability and increase coupling

