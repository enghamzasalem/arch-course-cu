# Extra Assignment: LLM API Wrapper – Monitoring & Anomaly Detection Architecture

## Overview

Design the **architecture** for a system that wraps OpenAI and/or Gemini APIs to help applications **track**, **monitor**, and **detect anomalies** in LLM API usage. You will produce architecture diagrams and documentation; implementation is optional.

This assignment applies concepts from **Chapters 1–5**: components and connectors, quality attributes, definitions, modeling (C4/UML), and modularity.

## Learning Objectives

By completing this assignment, you will:
- Design an architecture for a cross-cutting concern (observability)
- Define components for proxying, tracking, and anomaly detection
- Balance quality attributes (latency, reliability, observability)
- Document the system with standard diagrams (C4, component, sequence)
- Justify trade-offs and technology choices

## System Purpose

The system acts as a **wrapper/proxy** around LLM APIs (OpenAI, Google Gemini, etc.) so that:

1. **Track** – Every request/response is recorded (who, when, model, tokens, cost).
2. **Monitor** – Metrics and health are exposed (throughput, latency, error rate, token usage).
3. **Anomaly detection** – Unusual patterns are detected (e.g. spike in calls, high latency, cost drift, unexpected error rates).

Applications call your wrapper instead of the LLM APIs directly; the wrapper forwards calls and adds tracking, monitoring, and anomaly detection.

## Part 1: Context and High-Level Architecture

### Task 1.1: System Context Diagram (C4 Level 1)

**Objective**: Show the wrapper system in its ecosystem.

**Requirements**:
1. Draw a **system context diagram** with:
   - **Your system**: “LLM API Wrapper (Track, Monitor, Anomaly Detection)”
   - **Users**: e.g. Application Service, Backend API, Batch Job
   - **External systems**: OpenAI API, Gemini API, and optionally (e.g. database, alerting)

2. Label relationships (e.g. “Sends prompts”, “Returns completions”, “Stores metrics”).

**Deliverables**:
- `part1_context_diagram.drawio`
- `part1_context_diagram.png`

**Grading**: 15 points

---

### Task 1.2: Container Diagram (C4 Level 2)

**Objective**: Define the main applications/services inside your wrapper system.

**Requirements**:
1. Propose **at least 4 containers**, for example:
   - **Proxy/Gateway** – Receives LLM requests, forwards to OpenAI/Gemini, returns responses
   - **Tracking/Ingestion** – Records each call (metadata, tokens, cost, latency)
   - **Metrics/Monitoring** – Aggregates metrics, exposes dashboards/APIs (e.g. Prometheus, health)
   - **Anomaly Detection** – Analyzes streams/metrics and raises alerts or events

2. Add **datastores** if needed (e.g. for logs, metrics, anomaly state).

3. Show **connections** between containers (sync/async, protocol).

4. Briefly note **technology** per container (e.g. language, framework, or “to be chosen”).

**Deliverables**:
- `part1_container_diagram.drawio`
- `part1_container_diagram.png`
- `part1_container_descriptions.md` – Short description and responsibility of each container

**Grading**: 20 points

---

## Part 2: Component Design and Data Flow

### Task 2.1: Component Diagram for One Container

**Objective**: Decompose one important container (e.g. Proxy or Anomaly Detection) into components.

**Requirements**:
1. Choose **one container** from Part 1 (e.g. “Proxy” or “Anomaly Detection”).
2. Decompose it into **at least 4 components** with clear responsibilities.
3. Show **interfaces** (provided/required) and **dependencies** between components.
4. Apply **modularity**: single responsibility, clear boundaries.

**Example (Proxy container)**:
- RequestValidator, ProviderRouter (OpenAI vs Gemini), ResponseNormalizer, TrackingEmitter.

**Example (Anomaly Detection container)**:
- MetricsIngester, BaselineCalculator, AnomalyScorer, AlertPublisher.

**Deliverables**:
- `part2_component_diagram.drawio`
- `part2_component_diagram.png`
- `part2_component_rationale.md` – Why these components and interfaces

**Grading**: 25 points

---

### Task 2.2: Sequence Diagram – Request Path and Anomaly Flow

**Objective**: Show how a single LLM request flows through the system and how an anomaly is detected and reported.

**Requirements**:
1. **Sequence diagram 1 – Happy path**: From “Application sends prompt” to “Application receives completion”, passing through your Proxy and Tracking (and optionally Monitoring).
2. **Sequence diagram 2 – Anomaly path**: From “Metrics/Monitoring receive data” to “Anomaly detected” to “Alert/event produced” (e.g. to dashboard or alerting system).

You may use one draw.io file with two pages or two separate files.

**Deliverables**:
- `part2_sequence_request.drawio` and `.png` (and optionally `part2_sequence_anomaly.drawio`/`.png` if separate)
- Or one file with two pages and two exported PNGs

**Grading**: 20 points

---

## Part 3: Anomaly Detection and Quality Attributes

### Task 3.1: Anomaly Detection Design

**Objective**: Define what “anomalies” mean and how the system detects them.

**Requirements**:
1. List **at least 4 anomaly types** the system should handle, e.g.:
   - Request rate spike
   - Latency degradation
   - Error rate spike
   - Token/cost drift (e.g. sudden increase in token usage or cost per request)

2. For each type, briefly describe:
   - **Inputs** (what data is used)
   - **Detection approach** (e.g. threshold, baseline, simple statistical rule)
   - **Output** (e.g. event, alert, metric)

3. Describe **one** design decision: e.g. real-time vs batch, or where detection runs (inside proxy vs separate service).

**Deliverable**: `part3_anomaly_detection.md`

**Grading**: 15 points

---

### Task 3.2: Quality Attributes and Trade-offs

**Objective**: Justify how the architecture supports key qualities and trade-offs.

**Requirements**:
1. Discuss **at least 3 quality attributes** (e.g. latency, availability, observability, cost, security).
2. For each:
   - Why it matters for this wrapper
   - How your architecture supports it
   - One trade-off (e.g. “adding tracking adds latency; we mitigate by…”)
3. Optionally: one paragraph on **scalability** (e.g. how the proxy and anomaly service scale under load).

**Deliverable**: `part3_quality_attributes.md`

**Grading**: 15 points

---

## Part 4: Optional – Minimal Code or ADR

**Optional (extra credit or extension)**:

- **Option A**: Implement a **minimal proxy** in Python that:
  - Accepts one LLM request (e.g. prompt + model),
  - Forwards to OpenAI or Gemini (mock or real),
  - Logs request/response and latency to stdout or a file.
- **Option B**: Write **one Architectural Decision Record (ADR)** for a major choice (e.g. “Proxy in-process vs sidecar” or “Where to run anomaly detection”).

**Deliverables**: Code in `code/` and/or `part4_adr.md` (if applicable).

**Grading**: Up to 10 points extra

---

## Submission Requirements

### Submission Method

GitHub Pull Request (same as other assignments). See `../lecture-3/SUBMISSION_GUIDE.md` if needed.

### File Structure

```
submissions/YOUR_NAME/llm-wrapper-assignment/
├── part1_context_diagram.drawio
├── part1_context_diagram.png
├── part1_container_diagram.drawio
├── part1_container_diagram.png
├── part1_container_descriptions.md
├── part2_component_diagram.drawio
├── part2_component_diagram.png
├── part2_component_rationale.md
├── part2_sequence_request.drawio
├── part2_sequence_request.png
├── part2_sequence_anomaly.drawio          # if separate
├── part2_sequence_anomaly.png
├── part3_anomaly_detection.md
├── part3_quality_attributes.md
├── part4_adr.md                          # optional
├── code/                                 # optional
│   └── ...
└── README.md
```

### Diagrams

- Provide **both** `.drawio` and `.png` for every diagram.
- Use consistent naming and notation (e.g. C4 for context/container, UML-style for sequence).

---

## Grading Rubric

| Part | Task | Points |
|------|------|--------|
| Part 1 | Context diagram | 15 |
| Part 1 | Container diagram + descriptions | 20 |
| Part 2 | Component diagram + rationale | 25 |
| Part 2 | Sequence diagrams | 20 |
| Part 3 | Anomaly detection design | 15 |
| Part 3 | Quality attributes & trade-offs | 15 |
| Part 4 | Optional code or ADR | up to 10 extra |
| **Total** | | **110** (100 required + 10 optional) |

### Quality Criteria

- **Clarity** – Diagrams and text are easy to follow.
- **Consistency** – Containers in Part 1 match components and sequences in Part 2.
- **Completeness** – All required elements and deliverables are present.
- **Justification** – Rationale for components, anomaly types, and trade-offs is clear.

---

## Getting Started

1. **Scope**: Decide whether the wrapper supports only OpenAI, only Gemini, or both (and how routing works).
2. **Data**: What do you store per call? (e.g. timestamp, user/app id, model, prompt length, completion length, tokens, latency, status.)
3. **Anomalies**: Start with simple rules (e.g. “latency > X” or “error rate > Y”) then refine.
4. **Diagrams**: Use the lecture-4 C4 and UML examples; keep one concern per diagram.

---

## References

- C4 model: https://c4model.com/
- OpenAI API: https://platform.openai.com/docs/api-reference
- Google Gemini API: https://ai.google.dev/gemini-api/docs
- Draw.io: https://app.diagrams.net/

---

**Due date**: [To be announced by instructor]  
**Submission**: GitHub Pull Request to `arch-course-cu/lecture-5/submissions/YOUR_NAME/llm-wrapper-assignment/`

Good luck.
