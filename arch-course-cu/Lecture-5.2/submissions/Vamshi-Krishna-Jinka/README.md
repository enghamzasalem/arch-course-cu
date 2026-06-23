# LLM API Wrapper Monitoring System  
## Architecture Assignment Submission  

**Student:** Vamshi Krishna Jinka  
**Submission date:** [12-03-2026]

---

# Overview

This submission presents the architectural design and analysis of an **LLM API Wrapper System** designed to monitor and manage interactions with large language model providers such as **OpenAI** and **Google Gemini**.

The system acts as a **proxy layer** between applications and external LLM APIs and provides additional capabilities including:

- Tracking every request and response
- Monitoring system performance and usage metrics
- Detecting abnormal system behavior
- Generating alerts when anomalies occur

Applications interact with the **LLM API Wrapper** instead of calling LLM APIs directly.  
The wrapper forwards requests to the provider while collecting metrics and detecting anomalies.

---

# Part 1 – System Architecture Design

## part1_context_diagram.drawio / part1_context_diagram.png

Contains the **C4 Level 1 – System Context Diagram** showing:

- The **LLM API Wrapper** as the main system
- External users such as:
  - Application Service
  - Backend API
  - Batch Job
- External systems including:
  - OpenAI API
  - Gemini API
  - Metrics Database
  - Alerting System

The diagram illustrates how applications interact with the wrapper and how the wrapper communicates with external LLM providers and monitoring infrastructure.

---

## part1_container_diagram.drawio / part1_container_diagram.png

Contains the **C4 Level 2 – Container Diagram** describing the main applications/services inside the wrapper system.

Main containers include:

- **Proxy Gateway** – Receives LLM requests and forwards them to the appropriate provider.
- **Tracking Service** – Records request metadata such as tokens, latency, and cost.
- **Monitoring Service** – Aggregates metrics and exposes monitoring information.
- **Anomaly Detection Service** – Detects abnormal system behavior.
- **Logs Database** – Stores request logs.
- **Metrics Database** – Stores monitoring metrics.

The diagram also shows communication between containers and external LLM APIs.

---

## part1_container_descriptions.md

Provides a **brief description of each container**, including:

- Responsibilities
- Technology choices
- Role within the architecture

This document explains how each container contributes to system functionality.

---

# Part 2 – Component and Interaction Modeling

## part2_component_diagram.drawio / part2_component_diagram.png

Contains the **Component Diagram for the Proxy Gateway container**.

The Proxy container is decomposed into modular components:

- **RequestValidator** – Validates incoming LLM requests.
- **ProviderRouter** – Selects the LLM provider (OpenAI or Gemini).
- **ResponseNormalizer** – Converts responses into a consistent format.
- **TrackingEmitter** – Sends request metadata to the tracking system.

The diagram illustrates component responsibilities, interfaces, and dependencies.

---

## part2_component_rationale.md

Explains the **design decisions behind the component decomposition**, including:

- Why each component exists
- How interfaces are defined
- How modularity principles are applied:
  - Single Responsibility Principle
  - Low Coupling
  - High Cohesion

---

## part2_sequence_request.drawio / part2_sequence_request.png

Sequence diagram representing the **normal request flow**:

1. Application sends prompt
2. Proxy Gateway processes request
3. Request is routed to the LLM provider
4. Response is returned to the application
5. Request metadata is recorded for monitoring

This diagram shows the **happy path request lifecycle**.

---

## part2_sequence_anomaly.drawio / part2_sequence_anomaly.png

Sequence diagram representing the **anomaly detection workflow**:

1. Tracking service sends metrics to monitoring system
2. Monitoring service aggregates metrics
3. Anomaly detection analyzes the metrics
4. Alerts are generated if abnormal patterns are detected

This diagram illustrates how the system detects and reports anomalies.

---

# Part 3 – Monitoring and Quality Design

## part3_anomaly_detection.md

Defines how the system detects abnormal behavior.

The document identifies several anomaly types including:

- Request rate spikes
- Latency degradation
- Error rate spikes
- Token or cost drift

For each anomaly type the document describes:

- Input metrics
- Detection approach (threshold or statistical rule)
- Generated outputs such as alerts or events

It also explains the design choice of **real-time anomaly detection**.

---

## part3_quality_attributes.md

Analyzes key **quality attributes** supported by the architecture:

- **Latency** – Ensuring fast request processing
- **Availability** – Maintaining system reliability
- **Observability** – Monitoring usage and system health

Each attribute includes:

- Why it is important
- How the architecture supports it
- Trade-offs and mitigation strategies

The document also discusses **system scalability** and how containers can scale independently.

---

# Architectural Summary

The LLM API Wrapper architecture follows a **modular and observable system design**.

Key architectural characteristics include:

- Proxy-based LLM request routing
- Modular container-based architecture
- Integrated monitoring and tracking
- Real-time anomaly detection
- Scalable container services

The design emphasizes:

- Observability
- Reliability
- Performance
- Cost monitoring
- Modular architecture principles

---

# Conclusion

This submission demonstrates the application of **software architecture modeling techniques**, including:

- C4 architecture diagrams
- Container and component decomposition
- Sequence diagrams for system interactions
- Quality attribute analysis
- Monitoring and anomaly detection design

The architecture provides a scalable and observable system for managing interactions with external LLM APIs while enabling monitoring, tracking, and anomaly detection capabilities.