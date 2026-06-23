# Part 2.2 – Choreographed (Event-Driven) Design

## Events

- `DocumentReceived` – client submitted a document for processing
- `ValidationComplete` – document passed validation
- `ExtractionComplete` – text/OCR extraction finished
- `ClassificationComplete` – document type assigned
- `StorageComplete` – document and results persisted
- `ValidationFailed` / `ExtractionFailed` / `StorageFailed` – step-level failure events

---

## Component Behaviour

| Component | Subscribes to | Publishes |
|---|---|---|
| **Validator** | `DocumentReceived` | `ValidationComplete` or `ValidationFailed` |
| **Extractor** | `ValidationComplete` | `ExtractionComplete` or `ExtractionFailed` |
| **Classifier** | `ExtractionComplete` | `ClassificationComplete` |
| **Storage** | `ClassificationComplete` | `StorageComplete` or `StorageFailed` |
| **Notifier** | `StorageComplete`, `ExtractionFailed`, `StorageFailed` | *(none - terminal)* |

No component calls another directly. Each reacts to an event, does its work, and publishes the next event.

---

## Advantage

Components are fully decoupled - a new step can be added by subscribing to an existing event and publishing a new one, with no changes to any other component.

## Disadvantage

The overall flow is implicit and distributed across all components, making it harder to trace a failing job or reason about the end-to-end sequence than in an orchestrated design.