# Composable Document Processing Pipeline  
## Architecture Assignment Submission  

**Student:** Vamshi Krishna Jinka  
**Submission Date:** [26-03-2026]  

----

# Overview

This submission presents the architectural design of a **Composable Document Processing Pipeline**.

The system processes documents (PDFs, images) through multiple stages:

- Validation
- Text Extraction (OCR)
- Classification
- Storage
- Notification

The pipeline supports both:
- **Synchronous processing** (immediate response)
- **Asynchronous processing** (background jobs with notifications)

The architecture applies concepts from **Composability and Connectors**, including:
- Component-based design
- Sync vs Async communication
- Orchestration vs Choreography
- Event-driven architecture

---

# Part 1 – Component and Connector Design

### part1_components_and_connectors.md
Defines the system as a composition of independent components:

- API Gateway / Ingestion Service
- Validator
- Extractor (OCR)
- Classifier
- Storage Service
- Notifier

Includes:
- Component responsibilities
- Inputs and outputs
- Sync vs async behavior
- Connector types (REST, Message Queue, Event Bus)
- Justification of design decisions

---

### part1_component_connector_diagram.drawio  
### part1_component_connector_diagram.png  

Contains the **Component and Connector Diagram** showing:

- All system components as modular units
- Communication flow between components
- Connector types:
  - REST (sync)
  - Message Queue (async)
  - Event Bus (async)
- Layered architecture:
  - Client Layer
  - Gateway Layer
  - Processing Layer
  - Infrastructure Layer
- Legend explaining sync vs async communication

---

# Part 2 – Orchestration vs Choreography

### part2_orchestration.md

Describes the pipeline using an **Orchestrated Design**:

- Central component: **PipelineOrchestrator**
- Controls execution sequence:
  - Validate → Extract → Classify → Store → Notify
- Includes:
  - Step-by-step workflow
  - Error handling and retry strategies
  - Advantages and disadvantages

---

### part2_choreography.md

Describes the pipeline using a **Choreographed (Event-Driven) Design**:

- No central controller
- Components communicate via events:
  - DocumentReceived
  - ValidationComplete
  - ExtractionComplete
  - ClassificationComplete
  - DocumentStored
- Each component:
  - Subscribes to events
  - Publishes new events

Includes:
- Event definitions
- Component responsibilities
- Event-driven flow
- Advantages and disadvantages

---

### part2_comparison.md

Provides a comparison between orchestration and choreography:

- Ease of modification
- Scalability
- Debugging complexity
- Coupling and fault isolation

Includes:
- Comparison table
- Recommendation: **Hybrid Architecture**

---

## Recommended Approach: Hybrid

- **Orchestration** for:
  - Validation and request handling (sync)
- **Choreography** for:
  - Extraction, classification, storage, notification (async)

This ensures:
- Fast user response
- High scalability
- Loose coupling

---

# Part 3 – API and Usage

### part3_api_design.md

Defines REST APIs for interacting with the pipeline:

#### Synchronous API
- `POST /api/v1/pipeline/run`
- Returns processed result immediately

#### Asynchronous API
- `POST /api/v1/pipeline/jobs` → returns job_id
- `GET /api/v1/pipeline/jobs/{job_id}` → fetch status/result
- Optional webhook callback support

Includes:
- Request/response formats
- Processing flow explanation
- Connector usage (sync vs async)

---

### part3_sequence_diagram.drawio  
### part3_sequence_diagram.png  

Contains a **Sequence Diagram (Async Flow)** showing:

- End-to-end document processing lifecycle
- Participants:
  - Client
  - API Gateway
  - Message Queue
  - Extractor Worker
  - Classifier
  - Storage
  - Notifier
- Interaction types:
  - REST (sync)
  - Message Queue (async)
  - Event-driven communication
  - Webhook notification

---

# Architectural Summary

The Document Processing Pipeline uses:

- **Component-Based Architecture**
- **Hybrid Communication Model**
  - Sync (REST)
  - Async (Message Queue + Event Bus)
- **Event-Driven Architecture (EDA)**
- **Pipeline Processing Pattern**

Key design characteristics:

- Modular and composable components
- Clear separation of concerns
- Scalable asynchronous processing
- Flexible API design

---

# Conclusion

This assignment demonstrates a comprehensive application of:

- Component decomposition
- Connector design (sync vs async)
- Orchestration and choreography patterns
- API design for real-world usage
- Event-driven system design

The final architecture achieves:

- **Scalability**
- **Maintainability**
- **Flexibility**
- **Performance efficiency**

The hybrid approach ensures the system can handle both real-time and large-scale background processing effectively.