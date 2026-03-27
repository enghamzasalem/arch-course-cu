# Part 1: Component and Connector Design

## Task 1.1: Component Decomposition

### 1. Components

Based on the pipeline requirements, the system is decomposed into the following five core components:

**1. Validator Component**
* **Name:** Validator
* **Single Responsibility:** Performs immediate checks on the incoming document (e.g., virus scanning, file size checks, format validation) to ensure it is safe and correctly formatted prior to processing.
* **Inputs:** Raw document file/URL and client options.
* **Outputs:** Validation result (success or failure) and document metadata.
* **Sync/Async:** Synchronous from the caller’s perspective.

**2. Extractor Component**
* **Name:** Extractor
* **Single Responsibility:** Handles parsing and Optical Character Recognition (OCR) to extract raw text and structural data from the document.
* **Inputs:** Validated document file/content.
* **Outputs:** Extracted text and OCR confidence scores.
* **Sync/Async:** Asynchronous from the caller’s perspective (compute-heavy).

**3. Classifier Component**
* **Name:** Classifier
* **Single Responsibility:** Analyzes the extracted text using machine learning or heuristics to classify the document type (e.g., Invoice, Tax Form, Personal Letter).
* **Inputs:** Extracted textual data.
* **Outputs:** Classification tags, categories, and metadata.
* **Sync/Async:** Asynchronous from the caller’s perspective.

**4. Storage Component**
* **Name:** StorageService
* **Single Responsibility:** Persists the processed document, extracted data, and classification results to long-term storage (e.g., an object store and a database).
* **Inputs:** Original document, extracted text, and classification results.
* **Outputs:** Storage confirmation (e.g., record IDs or object URIs).
* **Sync/Async:** Asynchronous from the overall pipeline flow.

**5. Notifier Component**
* **Name:** Notifier
* **Single Responsibility:** Responsible for broadcasting the completion status to external clients (e.g., triggering webhooks, sending emails) once pipeline processing completes.
* **Inputs:** Pipeline completion events, final result payload, client callback URL/details.
* **Outputs:** Delivery status logs.
* **Sync/Async:** Asynchronous.

---

### 2. Connectors

The interactions between the above components are handled through specific connectors to satisfy both synchronous request/response requirements and asynchronous event-driven needs:

**1. API Gateway / Orchestrator ↔ Validator**
* **Connector Name:** `Validation-Call`
* **Type:** Direct RPC or REST API call.
* **Sync/Async:** Synchronous.
* **Protocol/Format:** JSON over HTTP/gRPC.

**2. Validator ↔ Extractor**
* **Connector Name:** `Extraction-Task-Queue`
* **Type:** Message Queue (e.g., RabbitMQ, AWS SQS).
* **Sync/Async:** Asynchronous.
* **Protocol/Format:** internal task messages using JSON over AMQP.

**3. Extractor ↔ Classifier**
* **Connector Name:** `Classification-Task-Queue`
* **Type:** Message Queue.
* **Sync/Async:** Asynchronous.
* **Protocol/Format:** internal task messages using JSON over AMQP.

**4. Classifier ↔ StorageService**
* **Connector Name:** `Storage-Write-Connection`
* **Type:** Direct Database Driver / REST Call.
* **Sync/Async:** Synchronous from the Classifier's execution thread (but deferred/asynchronous relative to the origin client request).
* **Protocol/Format:** SQL or JSON over HTTP (for NoSQL databases).

**5. StorageService ↔ Notifier**
* **Connector Name:** `Notification-Event-Bus`
* **Type:** Pub/Sub Event Bus (e.g., Apache Kafka, AWS SNS).
* **Sync/Async:** Asynchronous.
* **Protocol/Format:** Event payload using JSON over EventStream/AMQP.

---

### 3. Justification of Sync vs Async

* **Validation (Synchronous):** Document validation acts as the system's gatekeeper. It must be synchronous so that the API can immediately verify file type and size limitations and quickly return a `400 Bad Request` to the client if the document is fraudulent or invalid. Queuing bad data wastes backend processing capability and delays error feedback to the user.
* **Extraction & Classification (Asynchronous):** OCR and NLP logic require immense CPU and memory resources and can take varying amounts of time to complete (seconds to minutes based on document length). Decoupling these via asynchronous message queues guarantees horizontal scalability, fault tolerance (messages can be retried on failure), and prevents these tasks from blocking web-server threads.
* **Storage (Asynchronous):** Persisting large text blobs and documents heavily relies on network/disk I/O. Doing this asynchronously with respect to the client allows the API to remain highly responsive. 
* **Notification (Asynchronous):** External notifications (such as dialing external webhooks or sending emails) can often encounter latency or external server downtimes. An asynchronous, pub-sub model allows the Notification component to reliably retry deliveries in the background without holding up the rest of the internal pipeline workflow.
