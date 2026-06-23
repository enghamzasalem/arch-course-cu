# Part 2: Orchestration vs Choreography

## Task 2.1: Orchestrated Design

### 1. The Orchestrator

**Which component is the orchestrator:**
The orchestrator in this architectural approach will be a dedicated **PipelineOrchestrator Service** (often coupled with or acting slightly behind the API Gateway). This centralized component acts as the definitive "brain" of the document processing pipeline, dictating the workflow, maintaining state, and actively commanding downstream services.

**Exact sequence of calls to other components:**
1. **Initiation:** The client uploads a document to the API Gateway, which delegates the job to the PipelineOrchestrator. The Orchestrator creates a new tracking state in its database (e.g., `JobStatus: STARTED`).
2. **Call 1 (Validator):** The Orchestrator synchronously invokes the **Validator**. If the validation fails, the Orchestrator ends the pipeline early and returns an error. If it succeeds, it proceeds.
3. **Call 2 (Extractor):** The Orchestrator dispatches an explicit command message to the **Extractor**. The Orchestrator then waits (either actively or via asynchronous callbacks/promises) for the Extractor to return the extracted raw text.
4. **Call 3 (Classifier):** Upon receiving the Extractor's output, the Orchestrator commands the **Classifier** to analyze the raw text. It waits for the classification tags to be returned.
5. **Call 4 (Storage):** The Orchestrator gathers the original document, extracted text, and classification metadata into a unified packet and synchronously commands the **StorageService** to persist the complete record to the database.
6. **Call 5 (Notifier):** Finally, after receiving a successful persistence confirmation from Storage, the Orchestrator invokes the **Notifier** to send a webhook or email confirming completion to the client. The Orchestrator then marks the job as `COMPLETED`.

**How errors and retries are handled (conceptually):**
In an orchestrated design, error handling and retry mechanisms are managed entirely by the Orchestrator. 
* **Retries:** If a downstream service (e.g., the Classifier or target Database) drops the request or times out, the Orchestrator's central engine automatically implements exponential backoff to retry the failing task.
* **Failure State:** If retries are exhausted, the Orchestrator catches the error, marks the entire workflow state as `FAILED`, and can orchestrate compensating actions (e.g., executing a rollback to clean up temporary extraction files). It can then immediately command the Notifier to alert the client of the failure, supplying centralized pipeline logs.

---

### 2. Advantages and Disadvantages

**One Advantage:**
* **Centralized Tracing and Simplicity:** Having a single orchestrator provides exceptional visibility into pipeline state. Tracking a task's exact status (e.g., identifying that Document #1042 is specifically stuck at the "Extraction" phase) requires only querying the Orchestrator's state database. Modifying the pipeline order (for example, adding an Image Enhancement step before Extraction) is straightforward because the workflow logic exists exclusively in one central location.

**One Disadvantage:**
* **Single Point of Failure and Tight Coupling:** The orchestrator represents a central bottleneck. Even if the individual workers (Extractors, Classifiers) are perfectly healthy and available, if the central Orchestrator crashes or gets overloaded, the entire document pipeline grinds to a halt. Furthermore, the orchestrator introduces tight behavioral coupling; it must natively know the API contracts, commands, and inputs required for every single downstream component.
