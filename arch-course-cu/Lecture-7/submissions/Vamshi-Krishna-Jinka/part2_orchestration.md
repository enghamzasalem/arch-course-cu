# Part 2: Orchestration vs Choreography
## Task 2.1: Orchestrated Design

## 1. Overview
In the orchestrated design, a central component controls the entire document processing pipeline. This component is responsible for invoking each step in sequence and managing the workflow.

Pipeline Flow:
Upload → Validate → Extract → Classify → Store → Notify

---

## 2. Orchestrator Component

### Name: PipelineOrchestrator (implemented within API Gateway or as a separate service)

### Responsibility:
- Control the execution flow of the pipeline
- Invoke each component in order
- Handle responses, failures, and retries
- Return results (sync) or job status (async)

---

## 3. Sequence of Calls

### Step-by-step flow:

1. **Client → Orchestrator**
   - Upload document via REST API

2. **Orchestrator → Validator (Sync)**
   - Sends document for validation
   - If validation fails → return error immediately

3. **Orchestrator → Extractor (Sync or Async depending on mode)**
   - Sends validated document for text extraction (OCR)

4. **Orchestrator → Classifier (Sync)**
   - Sends extracted text for classification

5. **Orchestrator → Storage (Sync)**
   - Stores processed document and metadata

6. **Orchestrator → Notifier (Async)**
   - Sends notification to user (email/webhook)

7. **Orchestrator → Client**
   - Sync mode: returns extracted + classified data
   - Async mode: returns job ID

---

## 4. Error Handling and Retries

### Error Handling Strategy:

- **Validation Errors**
  - Immediately returned to client
  - No further processing

- **Extraction / Classification Failures**
  - Orchestrator retries (e.g., 2–3 attempts)
  - If still failing → mark job as failed

- **Storage Failures**
  - Retry with backoff strategy
  - Critical step → must succeed before completion

- **Notification Failures**
  - Logged and retried asynchronously
  - Does not block pipeline completion

---

### Retry Mechanism:
- Fixed retry count (e.g., 3 retries)
- Exponential backoff (e.g., 1s → 2s → 4s)
- Dead-letter handling for persistent failures

---

## 5. Advantages of Orchestration

### Advantage: Centralized Control
- Easy to understand and manage workflow
- Clear sequence of execution
- Debugging and monitoring are simpler
- Changes to workflow can be made in one place

---

## 6. Disadvantages of Orchestration

### Disadvantage: Tight Coupling and Bottleneck
- Orchestrator becomes a single point of failure
- High dependency on orchestrator for all operations
- Harder to scale independently
- Can become complex as pipeline grows

---

## 7. Summary

The orchestrated design provides a structured and controlled approach where a central orchestrator manages the entire pipeline. While it simplifies control and debugging, it introduces scalability and coupling challenges, especially in distributed systems.