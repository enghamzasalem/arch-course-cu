# Part 3: Pipeline API Design

## 3.1 Proposed API Endpoints

The API supports two primary interaction patterns: **Synchronous** (for immediate results) and **Asynchronous** (for background processing) along with management utilities.

### 1. Synchronous Endpoint (Immediate Result)
**`POST /api/v1/pipeline/run`**
* **Request Body:** ```json
    {
      "document_url": "[https://document-pipeline.com/invoice_001.pdf](https:/document-pipeline.com/invoice_001.pdf)",
      "options": { "ocr_enabled": true, "language": "en" }
    }
    ```
* **Response (200 OK):**
    ```json
    {
      "status": "completed",
      "data": { "text": "Extracted text content...", "type": "Invoice" }
    }
    ```

### 2. Asynchronous Endpoint (Job-Based)
**`POST /api/v1/pipeline/jobs`**
* **Request Body:** Same as sync, with optional `"callback_url": "https://document-pipeline.com/webhook"`.
* **Response (202 Accepted):** Returns a `job_id` and a `check_status_url`.

**`GET /api/v1/pipeline/jobs/{job_id}`**
* **Response (200 OK):** Returns current status (`queued`, `processing`, `failed`, or `completed`).

### 3. Management & Utility Endpoints (New)
**`DELETE /api/v1/pipeline/jobs/{job_id}`**
* **Purpose:** Cancels a pending job or deletes the processed data from the cache.
* **Response (204 No Content):** Successfully removed.

**`GET /api/v1/pipeline/health`**
* **Purpose:** Used by monitoring tools to check if the Gateway and its connectors (Queue, DB) are alive.
* **Response (200 OK):** `{"status": "healthy", "services": {"database": "up", "queue": "up"}}`

**`GET /api/v1/pipeline/jobs`**
* **Purpose:** Lists the last 10 jobs submitted by the user (useful for a "recent activity" dashboard).
* **Response (200 OK):** A list of job summary objects.

---

## 3.2 Backend Execution Logic

### The Synchronous Path (Direct Orchestration)
When a user calls the `/run` endpoint, the **API Gateway** acts as a strict Orchestrator. It calls the **Validator** and waits. If valid, it calls the **Extractor** and waits. This continues in a "blocking" chain until the final result is gathered and returned in the HTTP response. 
* **Connector Type:** Mostly REST/gRPC (Sync).
* **Usage:** Best for single, small documents where the user is waiting at a loading spinner.

### The Asynchronous Path (Queues & Events)
When a user calls the `/jobs` endpoint, the **API Gateway** performs a quick validation, generates a `job_id`, and immediately pushes a message onto the **Extraction Queue**. 
1.  The Gateway returns `202 Accepted` to the user so they aren't left waiting.
2.  The **Extractor** picks up the message when it has capacity.
3.  Once finished, the **Classifier** and **Storage** components process the data using the **Event-Driven (Choreography)** logic.
4.  Finally, the **Notifier** sends a "Post" request to the user's `callback_url` to let them know the job is done.
* **Connector Type:** Message Queues and Event Bus (Async).