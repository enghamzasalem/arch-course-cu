# Part 2.2 — Choreographed (Event-Driven) Design

## 1. Event-Driven Approach

The pipeline is designed using **choreography**, where there is **no central orchestrator**.  
Instead, components communicate by **publishing and subscribing to events** via an **event bus**.

Each component reacts to events and may publish new events, creating a distributed workflow.

---

## 2. Event Definitions

The following events define the pipeline flow:

- `DocumentReceived` — document uploaded by client
- `ValidationCompleted` — validation finished (success/failure)
- `ExtractionCompleted` — text extraction finished
- `ClassificationCompleted` — document classified
- `DocumentStored` — data successfully stored
- `NotificationSent` — user notified

---

## 3. Component Responsibilities (Event-Based)

### API Gateway
- **Publishes:** `DocumentReceived`

---

### Validator
- **Subscribes to:** `DocumentReceived`
- **Publishes:** `ValidationCompleted` with payload `{ valid: true/false, document_id }`
- Downstream components only act if `valid: true`

---

### Extractor
- **Subscribes to:** `ValidationCompleted`
- **Condition:** only if validation is successful
- **Publishes:** `ExtractionCompleted`

---

### Classifier
- **Subscribes to:** `ExtractionCompleted`
- **Publishes:** `ClassificationCompleted`

---

### Storage Service
- **Subscribes to:** `ClassificationCompleted`
- **Publishes:** `DocumentStored`

---

### Notifier
- **Subscribes to:** `DocumentStored`
- **Publishes:** `NotificationSent`

---

### Flow of Execution
1. API publishes `DocumentReceived`
2. Validator processes
   - If valid → publishes `ValidationCompleted`
   - If invalid → publishes `ValidationCompleted` (valid: false), downstream ignores
3. Extractor reacts → publishes `ExtractionCompleted`
4. Storage reacts → publishes `DocumentStored`
5. Notifier reacts → sends notification


---

## 5. Advantage of Choreography

- **Loose coupling**
  - Components are independent
  - New components can be added without modifying existing ones

---

## 6. Disadvantage of Choreography

- **Harder to understand and debug**
  - No single place shows the full workflow
  - Tracing execution across events is more complex

