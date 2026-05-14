# Part 2: Choreographed (Event-Driven) Design

## 2.1 The Choreography: Event-Driven Flow

In this design, the Pipeline Manager is removed. Components communicate by publishing events to a central **Message Bus** and subscribing to the events they care about. The flow "emerges" naturally as each component reacts to the previous one's output.

### 1. List of Events
* `DocumentReceived`: Triggered when a new file is uploaded to the Gateway.
* `ValidationPassed`: Triggered when a document is confirmed safe and valid.
* `ExtractionCompleted`: Triggered when text has been successfully pulled from the file.
* `ClassificationCompleted`: Triggered when the document type (e.g., "Invoice") is identified.
* `DocumentStored`: Triggered when the data is safely saved in the database.

### 2. Component Subscriptions and Publications

| Component | Subscribes To (Input) | Publishes (Output) | Trigger Condition |
| :--- | :--- | :--- | :--- |
| **API Gateway** | (External Request) | `DocumentReceived` | When a user uploads a file. |
| **Validator** | `DocumentReceived` | `ValidationPassed` | After malware and format checks pass. |
| **Extractor** | `ValidationPassed` | `ExtractionCompleted` | Once OCR processing is finished. |
| **Classifier** | `ExtractionCompleted` | `ClassificationCompleted` | After AI determines the document type. |
| **Storage** | `ClassificationCompleted` | `DocumentStored` | When data is written to the DB. |
| **Notifier** | `DocumentStored` | (External Email/Webhook) | When the final storage event is seen. |

---

## 2.2 Advantages and Disadvantages

### One Advantage: High Scalability and Flexibility (Decoupling)
This design is incredibly "pluggable." If we want to add a new **Audit** component that keeps a log of every document, we don't have to change any existing code. We simply tell the new Audit component to subscribe to the `DocumentReceived` event. The rest of the system doesn't even need to know the Audit component exists.

### One Disadvantage: Increased Complexity in Monitoring
Since there is no "Manager" holding the map, it’s much harder to see the "big picture." If a document enters the system but the user never gets a notification, you have to hunt through the logs of five different services to find out where the chain broke. You often need expensive "Distributed Tracing" tools just to figure out what happened to a single file.