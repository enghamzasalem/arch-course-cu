# Part 3.2 – Quality Attributes and Trade-offs

## Overview

This section explains the main qualities we care about for the LLM API wrapper and some trade-offs we made while designing the system.

---

## 1. Latency

- **Why it matters:** Users don’t want to wait longer because we are adding tracking and anomaly detection.  
- **How we support it:** The proxy is fast and handles request/response quickly. Telemetry is sent **asynchronously** to the event bus so it doesn’t block the main request.  
- **Trade-off:** Adding telemetry could slow down responses. We fix this by making telemetry async and non-blocking.

---

## 2. Observability

- **Why it matters:** We need to know how the system is performing and detect problems early.  
- **How we support it:** Every request is tracked, metrics are stored in TimescaleDB, and the anomaly engine checks for spikes or unusual patterns.  
- **Trade-off:** Collecting lots of metrics can increase storage and processing. We mitigate this by storing aggregated metrics and using an event bus to decouple processing.

---

## 3. Reliability / Availability

- **Why it matters:** Applications rely on this wrapper, so it should not fail or block requests.  
- **How we support it:** We have multiple LLM providers (OpenAI/Gemini) and failover in the provider router. The event bus buffers telemetry in case downstream services are slow.  
- **Trade-off:** Adding failover and buffering adds complexity. We keep it manageable by centralizing routing and using a simple queue like Redis or Kafka.

---

## Scalability

The system can scale horizontally:

- **Proxy Gateway:** Can be duplicated behind a load balancer to handle more LLM requests.  
- **Event Bus:** Can scale with multiple consumers for telemetry ingestion.  
- **Anomaly Engine:** Can run in multiple instances or split by metric type for faster processing.  

This means the system can handle spikes in traffic without blocking users or losing metrics.

---

## Summary

We designed the wrapper to be **fast, observable, and reliable**, while keeping the system simple enough to maintain. The main trade-offs are around telemetry overhead and complexity from failover logic, which we solved with asynchronous processing and modular design.