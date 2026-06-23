# Container Descriptions – LLM API Wrapper System

This document describes the main containers of the **LLM API Wrapper System** shown in the container diagram. The system acts as a proxy around LLM APIs to provide tracking, monitoring, and anomaly detection.

---

## 1. Proxy Gateway

**Technology:** Python / FastAPI

**Description:**  
The Proxy Gateway is the entry point of the system. Applications send their LLM requests to this gateway instead of calling external APIs directly.

**Responsibilities:**
- Receive prompt requests from applications
- Forward requests to the appropriate LLM provider (OpenAI or Gemini)
- Return responses back to the client
- Emit metadata events for tracking and monitoring

---

## 2. Tracking Service

**Technology:** Python

**Description:**  
The Tracking Service records metadata about every LLM API call processed by the Proxy Gateway.

**Responsibilities:**
- Store request and response metadata
- Record token usage and estimated cost
- Record latency and request information
- Store logs in the Request Log Database

---

## 3. Metrics / Monitoring Service

**Technology:** Python / Prometheus-style metrics collector

**Description:**  
This service collects and aggregates metrics about the system and LLM API usage.

**Responsibilities:**
- Monitor request throughput
- Track latency and response time
- Track error rates
- Store metrics in the Metrics Store
- Send metrics streams to the Anomaly Detection Service

---

## 4. Anomaly Detection Service

**Technology:** Python

**Description:**  
The Anomaly Detection Service analyzes metrics to detect unusual behavior in the system.

**Responsibilities:**
- Detect request rate spikes
- Detect latency degradation
- Detect abnormal token or cost usage
- Generate alerts when anomalies occur
- Send alerts to the Alerting System (Slack, PagerDuty, Email)

---

## Summary

The architecture separates responsibilities across specialized containers. This modular structure improves scalability, observability, and maintainability while enabling the system to monitor and analyze LLM API usage effectively.