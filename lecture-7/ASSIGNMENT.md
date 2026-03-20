# Assignment: Composable Document Pipeline – Composition and Connectors

## Overview

This assignment requires you to **design the architecture** of a **Document Processing Pipeline** as a composable system: define components, connector types, and composition style (orchestration vs choreography). You will apply **Chapter 7: Composability and Connectors** and produce diagrams and documentation.

**Scenario:** A system that accepts documents (e.g. PDF, images), runs them through validation → OCR/extraction → classification → storage and notification. It must support both synchronous “process and return result” and asynchronous “process in background and notify when done.”

## Learning Objectives

By completing this assignment, you will:
- Identify components and connectors in a multi-step pipeline
- Choose connector types (sync vs async) and justify them
- Compare orchestration vs choreography for the pipeline
- Design an event-driven option and a request/response option
- Document composition and connector decisions

## Pipeline Requirements (Summary)

- **Input:** Document upload (file or URL) and optional options (e.g. extract text only, full OCR).
- **Steps (conceptual):** Validate → Extract (text/OCR) → Classify (e.g. invoice vs form) → Store → Notify.
- **Output:** Synchronous: return extracted data. Asynchronous: job id, later callback or webhook when done.
- **Clients:** Web app (sync), batch job (async), API (both).

---

## Part 1: Component and Connector Design

### Task 1.1: Component Decomposition

**Objective:** Decompose the pipeline into components and define connectors.

**Requirements:**
1. Propose **at least 5 components** (e.g. Validator, Extractor, Classifier, Storage, Notifier). For each:
   - Name and single responsibility
   - Inputs and outputs (data/events)
   - Whether it is sync or async from the caller’s perspective

2. Define **connectors** between components:
   - For each pair that communicates: connector name, type (e.g. direct call, REST, message queue, event bus), sync vs async
   - Protocol or format (e.g. JSON over HTTP, internal message format)

3. Justify **where you use sync vs async** (e.g. validate sync for immediate feedback; extract/classify/store async for scale).

**Deliverable:** `part1_components_and_connectors.md`

**Grading:** 30 points

---

### Task 1.2: Component and Connector Diagram

**Objective:** Draw the pipeline architecture.

**Requirements:**
1. Create a **component-and-connector diagram** (draw.io) showing:
   - All components (boxes)
   - All connectors (arrows) with labels (connector type, sync/async)
   - Optional: data flow or sequence numbers

2. Include a **legend** (e.g. sync direct call, async queue, REST).

**Deliverables:**
- `part1_component_connector_diagram.drawio`
- `part1_component_connector_diagram.png`

**Grading:** 20 points

---

## Part 2: Orchestration vs Choreography

### Task 2.1: Orchestrated Design

**Objective:** Design the pipeline as an **orchestrated** flow.

**Requirements:**
1. Describe the **orchestrator**:
   - Which component is the orchestrator (e.g. PipelineOrchestrator or API service)
   - Exact sequence of calls to other components
   - How errors and retries are handled (conceptually)

2. Describe **one advantage** and **one disadvantage** of this orchestrated design for your pipeline.

**Deliverable:** `part2_orchestration.md`

**Grading:** 15 points

---

### Task 2.2: Choreographed (Event-Driven) Design

**Objective:** Design the same pipeline as **choreography** (event-driven).

**Requirements:**
1. List **events** (e.g. `DocumentReceived`, `ValidationComplete`, `ExtractionComplete`, `DocumentStored`).

2. For each component, state:
   - Which events it **subscribes** to
   - Which events it **publishes** and when
   - No central orchestrator; flow emerges from events

3. Describe **one advantage** and **one disadvantage** of this choreographed design.

**Deliverable:** `part2_choreography.md`

**Grading:** 15 points

---

### Task 2.3: Comparison and Recommendation

**Objective:** Compare both styles and recommend one (or a hybrid).

**Requirements:**
1. Create a short **comparison table**: orchestration vs choreography on criteria such as:
   - Ease of changing the pipeline order
   - Ease of adding new steps
   - Debugging and tracing
   - Latency and scalability (conceptual)

2. **Recommend** one approach (or hybrid) for your document pipeline and justify in a short paragraph.

**Deliverable:** `part2_comparison.md`

**Grading:** 10 points

---

## Part 3: API and Usage

### Task 3.1: Pipeline API Design

**Objective:** Define how clients trigger the pipeline (sync and async).

**Requirements:**
1. Propose **API endpoints** (REST or RPC-style), e.g.:
   - **Sync:** `POST /api/v1/pipeline/run` – body: document (file/URL) + options; response: extracted data (or error).
   - **Async:** `POST /api/v1/pipeline/jobs` – body: document + options; response: `job_id`. `GET /api/v1/pipeline/jobs/{job_id}` – status and result when done. Optional: webhook/callback URL in request.

2. Describe briefly how the **sync** path uses your components/connectors (e.g. orchestrator calls Validator → Extractor → … and returns). Describe how the **async** path uses a queue or events.

**Deliverable:** `part3_api_design.md`

**Grading:** 20 points

---

### Task 3.2: Sequence Diagram (One Flow)

**Objective:** Show one end-to-end flow.

**Requirements:**
1. Create a **sequence diagram** (draw.io) for either:
   - Sync: Client → API → Orchestrator → Validator → Extractor → … → Response  
   - Async: Client → API → Enqueue → Worker → Validator → Extractor → … → Store → Notify

2. Include at least 5 participants and labeled messages.

**Deliverables:**
- `part3_sequence_diagram.drawio`
- `part3_sequence_diagram.png`

**Grading:** 10 points

---

## Submission Requirements

### Submission Method

GitHub Pull Request. See `../lecture-3/SUBMISSION_GUIDE.md` if needed.

### File Structure

```
submissions/YOUR_NAME/
├── part1_components_and_connectors.md
├── part1_component_connector_diagram.drawio
├── part1_component_connector_diagram.png
├── part2_orchestration.md
├── part2_choreography.md
├── part2_comparison.md
├── part3_api_design.md
├── part3_sequence_diagram.drawio
├── part3_sequence_diagram.png
└── README.md
```

### Diagrams

- Provide **both** `.drawio` and `.png` for every diagram.

---

## Grading Rubric

| Part | Task | Points |
|------|------|--------|
| Part 1 | Components and connectors design | 30 |
| Part 1 | Component and connector diagram | 20 |
| Part 2 | Orchestration design | 15 |
| Part 2 | Choreography design | 15 |
| Part 2 | Comparison and recommendation | 10 |
| Part 3 | API design (sync + async) | 20 |
| Part 3 | Sequence diagram | 10 |
| **Total** | | **120** |

### Quality Criteria

- **Components:** Clear responsibilities and boundaries
- **Connectors:** Types and sync/async chosen and justified
- **Orchestration vs choreography:** Both described and compared
- **API:** Sync and async usage of the pipeline are clear
- **Diagrams:** Match the written design and are readable

---

## Getting Started

1. **Review** `example1_composition_and_connectors.py` and `example2_orchestration_vs_choreography.py`.
2. **List** pipeline steps, then assign each to a component.
3. **Choose** connector type per link (sync when you need immediate result; async when you can defer).
4. **Sketch** orchestrated flow (one component calls the next); then event list and subscribers for choreography.

---

## Deadline

**Due date:** [To be announced by instructor]

**Submission:** GitHub Pull Request to `arch-course-cu/lecture-7/submissions/YOUR_NAME/`

Good luck.
