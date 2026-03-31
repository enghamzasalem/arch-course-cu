# Part 1: Component and Connector Design

## 1.1 Component Decomposition

Below are the core components that make up the Document Processing Pipeline. Each is designed to be decoupled and independently scalable, enforcing the Single Responsibility Principle.

| Component  | Responsibility | Inputs | Outputs | Mode |
| :--- | :--- | :--- | :--- | :--- |
| **API Gateway** | I use this as the entry point of the system. It receives requests from users and forwards them. | File or URL + options | Clean request data | **Sync** |
| **Validator** | I use this to check if the file is valid (correct type, size, not corrupted). | Uploaded file | Pass or Fail | **Sync** |
| **Extractor (OCR)** | I use this to extract text from the document (especially for PDFs/images). | Valid file | Extracted text | **Async** |
| **Classifier** | I use this to figure out what type of document it is (e.g. invoice, form). | Extracted text | Document type | **Async** |
| **Storage** | I use this to save the file and processed data. | Data + metadata | Save confirmation | **Async** |
| **Notifier** | I use this to notify the user when processing is finished. | Job result | Notification (email/webhook) | **Async** |


---

## 1.2 Connector Definitions

These connectors define the transport and protocol used for communication between components.

| Connection Pair | Connector Name | Type | Protocol / Format | Sync/Async |
| :--- | :--- | :--- | :--- | :--- |
| **Gateway → Validator** | Validation Link | Direct REST Call | JSON over HTTPS | **Sync** |
| **Validator → Extractor** | Extraction Queue | Message Queue  | JSON Message (S3 Link) | **Async** |
| **Extractor → Classifier** | Processing Bus | Event Bus | Internal Event Schema | **Async** |
| **Classifier → Storage** | Persistence Link | Message Queue / RPC | JSON / Avro | **Async** |
| **Storage → Notifier** | Completion Signal | Event Bridge / Topic | JSON Event | **Async** |

---

## 1.3 Sync vs. Async Justification

In this architecture, I’ve chosen a "Hybrid" approach to balance immediate user feedback with backend system reliability:

* **Sync for Validation:** We use a **Synchronous** connection for the Validator because users need to know immediately if their upload was rejected due to a virus or an unsupported file type. Fast-failing here prevents wasting downstream resources.
    
* **Async for Extraction and Beyond:** OCR, Classification, and Storage/Notification are "heavy" or "external" tasks. 
    1. **Resource Intensity:** OCR can take 10+ seconds. A sync connection would likely timeout the client's browser.
    2. **Resilience:** By using Asynchronous message queues, if the Classifier or Notifier goes down, the messages are buffered and processed once the service recovers—no data is lost.
    3. **Throughput:** The API Gateway can return a `job_id` instantly, allowing the system to handle thousands of concurrent uploads without waiting for a full process completion.