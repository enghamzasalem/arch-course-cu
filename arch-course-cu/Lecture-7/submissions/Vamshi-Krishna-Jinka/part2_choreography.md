# Part 2: Orchestration vs Choreography
## Task 2.2: Choreographed (Event-Driven) Design

## 1. Overview
In the choreographed design, there is **no central orchestrator**.  
Each component independently reacts to events and publishes new events after completing its task.

The pipeline flow emerges naturally through event propagation:

DocumentReceived → ValidationComplete → ExtractionComplete → ClassificationComplete → DocumentStored → NotificationSent

---

## 2. Event Definitions

| Event Name | Description |
|------------|-------------|
| DocumentReceived | A new document is uploaded and accepted |
| ValidationComplete | Document has been successfully validated |
| ValidationFailed | Document validation failed |
| ExtractionComplete | Text/content extracted from document |
| ClassificationComplete | Document type identified |
| DocumentStored | Document and metadata stored successfully |
| NotificationSent | User notified about completion |

---

## 3. Component Responsibilities (Event-Based)

### 3.1 API Gateway / Ingestion Service
- **Publishes**:
  - `DocumentReceived` (when user uploads document)
- **Subscribes**:
  - None

---

### 3.2 Validator
- **Subscribes to**:
  - `DocumentReceived`
- **Publishes**:
  - `ValidationComplete` (if valid)
  - `ValidationFailed` (if invalid)

---

### 3.3 Extractor (OCR/Text Extraction)
- **Subscribes to**:
  - `ValidationComplete`
- **Publishes**:
  - `ExtractionComplete` (after extracting text)

---

### 3.4 Classifier
- **Subscribes to**:
  - `ExtractionComplete`
- **Publishes**:
  - `ClassificationComplete` (after identifying document type)

---

### 3.5 Storage Service
- **Subscribes to**:
  - `ClassificationComplete`
- **Publishes**:
  - `DocumentStored` (after saving document and metadata)

---

### 3.6 Notifier
- **Subscribes to**:
  - `DocumentStored`
- **Publishes**:
  - `NotificationSent` (after notifying user)

---

## 4. Flow Without Orchestrator

1. Client uploads document → API publishes `DocumentReceived`
2. Validator processes → publishes `ValidationComplete`
3. Extractor reacts → publishes `ExtractionComplete`
4. Classifier reacts → publishes `ClassificationComplete`
5. Storage reacts → publishes `DocumentStored`
6. Notifier reacts → sends notification

Each component:
- Works independently
- Only knows about events, not other components
- Does not control the entire flow

---

## 5. Error Handling in Choreography

- **ValidationFailed event**
  - Stops further processing
  - Can trigger notification if needed

- **Failures in Extraction/Classification**
  - Retry handled by event consumer
  - Failed events can be sent to dead-letter queue

- **Loose coupling**
  - Failure in one component does not crash entire system

---

## 6. Advantages of Choreography

### Advantage: Loose Coupling and Scalability
- Components are independent
- Easy to add/remove services
- Highly scalable (parallel event processing)
- Supports distributed systems and microservices

---

## 7. Disadvantages of Choreography

### Disadvantage: Harder to Understand and Debug
- No single place to view entire workflow
- Flow is implicit (hidden in events)
- Debugging requires tracking multiple events
- Event ordering and consistency can be challenging

---

## 8. Summary

The choreographed design uses an **event-driven architecture** where components communicate via events instead of direct calls.  
This approach improves scalability and flexibility but makes the system harder to trace and debug compared to orchestration.