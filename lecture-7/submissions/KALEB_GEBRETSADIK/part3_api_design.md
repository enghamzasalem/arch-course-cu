# Part 3: API and Usage

## Task 3.1: Pipeline API Design

### 1. API Endpoints

The document processing pipeline operates as a dual-tier RESTful service, exposing paths for developers who require real-time execution and paths for handling high-volume deferred bulk workflows.

**Synchrounous Execution Strategy**
*   **Endpoint:** `POST /api/v1/pipeline/run`
*   **Description:** Processes a document synchronously. The HTTP connection remains open and blocks until the entire pipeline is cleared and parsed.
*   **Request Body:** A standard multipart/form payload containing `document` (binary blob) and a JSON string of `options` (e.g., `{"extract_text_only": false}`).
*   **Success Response (HTTP 200 OK):** A JSON string outputting the full payload containing extracted text, structural meta, and classification type. 
*   **Failure Response (HTTP 400 Bad Request):** If validation throws an immediate safety failure error.

**Asynchrounous Execution Strategy**
*   **Endpoint 1:** `POST /api/v1/pipeline/jobs`
*   **Description:** Rejects blocking loops and instead instantly queues an async job into the pipeline worker brokers.
*   **Request Body:** `document`, `options`, and an optional `webhook_url` to be invoked when processing completes.
*   **Response (HTTP 202 Accepted):** An immediate receipt containing `{"job_id": "8b9e-...-f79a"}` and an estimation timestamp.
*   **Endpoint 2:** `GET /api/v1/pipeline/jobs/{job_id}`
*   **Description:** A polling endpoint clients use exactly to track progress states. 
*   **Response (HTTP 200 OK):** Tracks granular progression logic `{"status": "PROCESSING", "step": "Classification"}` or, if completed gracefully, the identical data response block native to `/v1/pipeline/run`.

---

### 2. Connectors and Components Pipeline Execution

**How the Sync Path Operates:**
1.  **Direct Blocking Orchestration:** When the client hits `POST /api/v1/pipeline/run`, the API controller orchestrator maps all inner workflow connections linearly and synchronously via direct inter-service HTTP/RPC calls. 
2.  It strictly delegates the request memory stream buffer directly to the local **Validator**. 
3.  Upon success, the API controller locks awaiting a response stream block directly from the **Extractor**. 
4.  Once returned, it natively hands that text string to the immediate thread execution of the **Classifier**. 
5.  All processed metadata is asynchronously mirrored to the **StorageService** for record-keeping, and the payload is successfully mapped back directly returning an HTTP 200 payload body onto the client's hanging TCP request socket exactly as demanded.

**How the Async Path Operates:**
1.  **Message Queue/Event Bus Delegation:** When a user hits `POST /api/v1/pipeline/jobs`, the API validates the file schema explicitly fast and then radically shifts architecture logic via decoupling. 
2.  It inserts a JSON work message bearing the target document URI directly into the **Extraction Message Queue** via an AMQP/Kafka connector natively rendering the primary request thread officially closed allowing HTTP 202 creation back to the browser cleanly.
3.  In the background, horizontal **Extractor Worker** instances consume the queue passively, autonomously performing lengthy OCR analysis.
4.  Once OCR resolves, the Extractor inherently publishes onto exactly the subsequent **Classification Message Queue** seamlessly maintaining distributed orchestration/choreography event boundaries without HTTP protocol overhead timeouts explicitly.
5.  A secondary parallel **StorageService** driver receives all final state changes locking the final database transaction exactly to COMPLETED. If the user configured an aforementioned `webhook_url`, the dedicated **Notifier Component** reads this unified state change off the asynchronous Bus stream implicitly routing a delivery webhook ping to the external developer's endpoint notifying task completeness gracefully.
