# Container Descriptions – LLM API Wrapper

This document describes the containers used in the LLM API Wrapper system.  
The wrapper acts as a proxy around LLM providers (OpenAI, Gemini) to enable request tracking, monitoring, and anomaly detection.

---

## 1. Proxy Gateway

**Responsibility**

The Proxy Gateway is the entry point for all application requests. It receives prompt requests from client applications and forwards them to the appropriate LLM provider (e.g., OpenAI or Gemini). It also ensures responses are returned to the caller.

**Key Functions**

- Accepts API requests from applications
- Routes requests to the correct provider
- Handles response forwarding
- Emits tracking events

**Technology (Example)**

- Python FastAPI or Node.js Express
- REST HTTP API

**Interfaces**

- Client API (HTTP REST)
- LLM Provider APIs (HTTPS)

---

## 2. Tracking / Ingestion Service

**Responsibility**

The Tracking Service records metadata for every request and response passing through the proxy. This enables auditing, cost tracking, and usage monitoring.

**Data Captured**

- Timestamp
- Application ID
- Model used
- Prompt size
- Completion size
- Token usage
- Latency
- Cost estimate
- Response status

**Technology (Example)**

- Python worker service
- Message queue consumer (optional)

**Interfaces**

- Receives events from Proxy Gateway
- Writes logs to Metrics Database

---

## 3. Metrics / Monitoring Service

**Responsibility**

The Metrics Monitoring service aggregates operational metrics from request logs and exposes them for dashboards and monitoring tools.

**Metrics Examples**

- Requests per second
- Average latency
- Error rate
- Token usage
- Cost per request

**Technology (Example)**

- Prometheus
- Grafana dashboards

**Interfaces**

- Reads data from Metrics Database
- Provides monitoring APIs

---

## 4. Anomaly Detection Service

**Responsibility**

The Anomaly Detection service analyzes collected metrics to detect abnormal behavior in system usage or performance.

**Examples of anomalies**

- Sudden spike in request rate
- Unusual increase in token usage
- Latency spikes
- Error rate increase

**Technology (Example)**

- Python analytics service
- Statistical analysis or rule-based detection

**Interfaces**

- Consumes metrics from monitoring service
- Sends alerts to alerting system

---

## Datastores

### Metrics Database

Stores request logs and aggregated metrics.

**Possible technologies**

- PostgreSQL
- ClickHouse
- TimescaleDB

---

### Anomaly State Store

Stores anomaly detection results and historical baseline values.

**Possible technologies**

- Redis
- NoSQL datastore

---

### 2. Container Diagram
![Container Diagram](part1_container_diagram.png)