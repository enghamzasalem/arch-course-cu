# Part 2: Orchestration vs Choreography

## Task 2.2: Choreographed (Event-Driven) Design

### 1. Events List

In a choreographed architecture, the explicit command flow is replaced by components reacting to core domain events. The pipeline relies on an event bus (e.g., Apache Kafka, RabbitMQ Topic Exchange) producing the following events:

*   `DocumentReceived`: Fired when a client has successfully uploaded a new document explicitly to the API Gateway.
*   `ValidationCompleted`: Fired when the document successfully passes initial structural, size, and security checks.
*   `ValidationFailed`: Fired when the document fails the aforementioned security or format checks.
*   `ExtractionCompleted`: Fired when raw text and tabular structures are successfully extracted from the validated file.
*   `ClassificationCompleted`: Fired when the extracted text is parsed, mapped, and classified into a document category (e.g., Invoice).
*   `DocumentStored`: Fired when all processed document insights and metadata are persisted securely in the database.

---

### 2. Component Event Subscriptions and Publishing

Because there is no central orchestrator deciding what happens next, the end-to-end flow naturally emerges from the autonomous components reacting to ("subscribing to") and broadcasting ("publishing") events:

**1. API Gateway**
*   **Subscribes to:** None (for pipeline progression).
*   **Publishes:** `DocumentReceived` (published immediately upon accepting the client payload).

**2. Validator Component**
*   **Subscribes to:** `DocumentReceived`
*   **Publishes:** 
    *   `ValidationCompleted` (with validated document metadata if successful).
    *   `ValidationFailed` (with descriptive error logs if validation fails, actively stopping further positive flow).

**3. Extractor Component**
*   **Subscribes to:** `ValidationCompleted`
*   **Publishes:** `ExtractionCompleted` (with the attached raw textual data and OCR scores).

**4. Classifier Component**
*   **Subscribes to:** `ExtractionCompleted`
*   **Publishes:** `ClassificationCompleted` (with generated classification tags, category names, and models).

**5. Storage Component**
*   **Subscribes to:** `ClassificationCompleted`
*   **Publishes:** `DocumentStored` (containing the new DB Record ID/URL confirming successful persistence).
*(Note: Storage could equivalently subscribe to various events if incremental saves are desired, but in this specific linear flow, it subscribes to the final classification phase to execute a unified save).*

**6. Notifier Component**
*   **Subscribes to:** `DocumentStored` (for successful job completion alerts) AND `ValidationFailed` (for immediate task-failed alerts).
*   **Publishes:** None (it reaches out to external client webhooks, websockets, or emails directly).

---

### 3. Advantages and Disadvantages

**One Advantage:**
*   **Extreme Scalability and High Decoupling:** In a choreographed design, components are completely decoupled from each other. The Classifier has absolutely no knowledge of the Extractor or the Storage component; it only knows about `ExtractionCompleted` events. This implies there is no central orchestrator bottleneck to overload. When OCR volume surges severely, DevOps can independently spin up 100 new Extractor instances to drain the `ValidationCompleted` queue without requiring any other components or a master brain to scale recursively alongside it.

**One Disadvantage:**
*   **Complex Tracing and Operational Blindness:** Because there is no master component explicitly tracking state ("Is Document 990422 in extraction or classification?"), understanding the global workflow status is intensely difficult. Flow emerges spontaneously, meaning a failure inside the Classifier implies the pipeline quietly stalls, and fixing it requires engineers to use distributed tracing (e.g., OpenTelemetry, correlation ID logs) across multiple isolated services to figure out where the event chain broke.
