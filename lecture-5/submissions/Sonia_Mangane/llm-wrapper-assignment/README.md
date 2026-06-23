
# LLM API Wrapper – Monitoring & Anomaly Detection

## Overview

This project is a wrapper around LLM APIs (OpenAI / Google Gemini) that:

- Tracks every request and response
- Monitors performance metrics (latency, error rate, tokens)
- Detects anomalies like spikes, latency degradation, or cost drift
- Sends alerts to Slack / PagerDuty when something unusual happens

Applications call this wrapper instead of calling LLM APIs directly.

---

## Diagrams

- **Context Diagram (C4 Level 1)** – Shows the wrapper system, apps, LLM providers, and alerting.  
- **Container Diagram (C4 Level 2)** – Shows main containers: Proxy, Event Bus, Ingestion Worker, Anomaly Engine, TimescaleDB.  
- **Component Diagram (Proxy)** – Breaks down Proxy into RequestValidator, ProviderRouter, ResponseNormalizer, AsyncTelemetryEmitter.  
- **Sequence Diagrams** – Show request lifecycle (happy path) and anomaly detection flow.

---

## How It Works

1. **Request flow (happy path)**:  
   - App sends prompt → Proxy → LLM Provider → Proxy → App  
   - Telemetry events are asynchronously sent to Event Bus → Ingestion Worker → Metrics DB  

2. **Anomaly detection flow**:  
   - Anomaly Engine fetches recent metrics + baseline → compares → triggers alert if abnormal → Notification System sends alert  

3. **Anomalies detected**:  
   - Request rate spike  
   - Latency degradation  
   - Error rate spike  
   - Token/cost drift  

---

## Quality Attributes

- **Latency** – Proxy is fast, telemetry is async  
- **Observability** – Metrics stored and analyzed continuously  
- **Reliability** – Failover between LLM providers, buffered telemetry  
- **Scalability** – Proxy, event bus, and anomaly engine can scale horizontally

---

## Notes

- All diagrams are provided as `.drawio` and `.png`.  
- Designed for modularity, observability, and minimal impact on request latency.  
- Works with both OpenAI and Gemini APIs but can be extended for other providers.