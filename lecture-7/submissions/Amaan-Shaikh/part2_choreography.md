# Task 2.2 – Choreographed (Event-Driven) Design

## Events

| Event Name | Triggered By | Contains |
|------------|--------------|----------|
| DocumentReceived | Validator after receiving document | documentId, file, options |
| ValidationComplete | Validator after successful validation | documentId, validatedDoc |
| ExtractionComplete | Extractor after text extraction | documentId, extractedText, metadata |
| ClassificationComplete | Classifier after categorization | documentId, category, confidence |
| DocumentStored | Storage after saving | documentId, recordId |
| NotificationSent | Notifier after callback | documentId, status |

## Component Subscriptions and Publications

### Validator
**Subscribes to:** DocumentReceived
**Publishes:** ValidationComplete (or ValidationFailed)

### Extractor
**Subscribes to:** ValidationComplete
**Publishes:** ExtractionComplete

### Classifier
**Subscribes to:** ExtractionComplete
**Publishes:** ClassificationComplete

### Storage
**Subscribes to:** ClassificationComplete
**Publishes:** DocumentStored

### Notifier
**Subscribes to:** DocumentStored
**Publishes:** NotificationSent

**No central orchestrator** – each component reacts to events and publishes new events. The flow emerges from the subscriptions.

## Advantage of Choreography

**Better scalability:** Components process events independently. The Extractor can run on multiple workers consuming from the same event stream. Adding more workers increases throughput without changing other components.

## Disadvantage of Choreography

**Harder to debug:** The flow is distributed across multiple components. Tracing a single document through the system requires correlating events across different services. Understanding why a document failed requires checking multiple logs and event streams.