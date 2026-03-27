# Part 1 – Container Descriptions
## C4 Level 2: LLM API Wrapper System

---

## Containers (Services)

---

### 1. API Gateway / Proxy

| Field | Detail |
|---|---|
| **Technology** | Python 3.11, FastAPI, HTTPX (async HTTP client) |
| **Deployment** | Docker container, horizontally scalable |
| **Protocol (inbound)** | HTTPS REST (OpenAI-compatible schema) |
| **Protocol (outbound)** | HTTPS to OpenAI / Gemini APIs |

**Responsibility**

The single entry point for all LLM requests from callers (Application Services, Backend APIs, Batch Jobs). It:

- Authenticates incoming requests (validates JWT or API key via the Config & Auth Service).
- Applies per-caller rate limits and quota enforcement.
- Routes the request to the correct upstream LLM provider (OpenAI, Gemini, etc.) based on routing rules fetched from the Config Service.
- Streams or buffers the provider response back to the caller.
- Publishes a structured **request-event** (prompt hash, model, caller ID, token counts, latency, status) onto the Message Bus immediately after a response is received — fire-and-forget so the critical path is not blocked.

**Why it exists**

Decouples all callers from provider-specific SDKs. Any provider change (new model, new key, failover) is handled here without touching caller code.

---

### 2. Tracking & Ingestion Service

| Field | Detail |
|---|---|
| **Technology** | Python 3.11, FastAPI, Celery (async workers), SQLAlchemy |
| **Deployment** | Docker container + Celery worker pool |
| **Protocol (inbound)** | Consumes events from Message Bus (Kafka / Redis Streams) |
| **Protocol (outbound)** | SQL writes to Request Log Store; metric pushes to Time-Series Store |

**Responsibility**

Consumes every request event published by the Gateway and persists the full audit trail:

- Writes a complete audit record to the **Request Log Store** (PostgreSQL): caller ID, timestamp, model, prompt token count, completion token count, estimated cost, latency (ms), HTTP status, provider used.
- Computes derived cost figures using a configurable token-price table.
- Pushes incremental counters and histograms (token totals, cost totals, call counts, latency buckets) to the **Time-Series Metrics Store** for aggregation.
- Exposes a REST API (`GET /usage`, `GET /cost`) for on-demand reporting queries against the log store.

**Why it exists**

Separates the concern of durable persistence from the latency-sensitive Gateway. Async consumption means a slow DB write never delays a caller.

---

### 3. Metrics & Monitoring Service

| Field | Detail |
|---|---|
| **Technology** | Python 3.11, Prometheus Python client, FastAPI |
| **Deployment** | Docker container (singleton or small replica set) |
| **Protocol (inbound)** | Prometheus scrape pull from Time-Series Store |
| **Protocol (outbound)** | Exposes `/metrics` (Prometheus format), `/health`, `/dashboard-api` (JSON) |

**Responsibility**

Aggregates and exposes the operational health of the entire wrapper system:

- Maintains gauges and counters: **requests/sec**, **p50/p95/p99 latency**, **error rate (%)**, **token usage (rolling 1 h / 24 h)**, **cost (rolling)**, **provider availability**.
- Exposes a `/health` endpoint (used by load balancers and uptime monitors).
- Provides a `/metrics` Prometheus-format scrape endpoint consumed by Grafana for live dashboards.
- Optionally exposes a lightweight JSON REST API for embedding metrics widgets in internal portals.

**Why it exists**

Gives operators real-time visibility into system health, cost burn rate, and throughput without querying the raw log store.

---

### 4. Anomaly Detection Service

| Field | Detail |
|---|---|
| **Technology** | Python 3.11, Faust (stream processing) or Apache Spark Structured Streaming |
| **Deployment** | Docker container, stateful stream processor |
| **Protocol (inbound)** | Consumes events from Message Bus (Kafka / Redis Streams) |
| **Protocol (outbound)** | Reads/writes anomaly state to Redis; fires HTTPS webhooks to Alerting System |

**Responsibility**

Continuously analyzes the real-time event stream for unusual patterns and raises alerts:

| Anomaly Type | Detection Method |
|---|---|
| **Call-rate spike** | Rolling window count vs. baseline (z-score or threshold) |
| **Latency spike** | p95 latency exceeds configurable threshold (e.g. > 5 s) |
| **Cost drift** | Rolling cost per hour exceeds budget threshold |
| **Error-rate surge** | Error % over sliding window exceeds SLA threshold |
| **Unusual caller** | A caller ID generates anomalously high volume |

- Reads and writes cooldown/deduplication state from **Anomaly State Store** (Redis) to suppress duplicate alerts within a cooldown window.
- When an anomaly is confirmed, fires a webhook to the configured **Alerting System** (PagerDuty, Slack, email).

**Why it exists**

Proactively catches runaway usage, cost overruns, and infrastructure degradation before they become outages or budget breaches.

---

### 5. Config & Auth Service

| Field | Detail |
|---|---|
| **Technology** | Python 3.11, FastAPI, HashiCorp Vault (secrets), PostgreSQL (config) |
| **Deployment** | Docker container (high-availability pair) |
| **Protocol (inbound/outbound)** | gRPC or internal HTTPS from Gateway |

**Responsibility**

Centralises all sensitive configuration and access control:

- Stores and rotates **LLM provider API keys** (OpenAI, Gemini) in Vault; the Gateway never holds keys in memory longer than needed.
- Manages **routing rules**: which caller uses which model, failover priority, model version pinning.
- Issues and validates **caller JWT tokens** (or API keys) for authentication and authorization.
- Provides a management REST API for operators to update keys, add callers, and modify routing without redeploying the Gateway.

**Why it exists**

Prevents secrets sprawl and makes routing changes operational (no code deploy needed).

---

## Datastores

---

### 6. Request Log Store

| Field | Detail |
|---|---|
| **Technology** | PostgreSQL 16 |
| **Owned by** | Tracking & Ingestion Service |

Durable, queryable audit log of every LLM call. Schema captures: `caller_id`, `timestamp`, `provider`, `model`, `prompt_tokens`, `completion_tokens`, `cost_usd`, `latency_ms`, `http_status`, `request_id`. Used for billing reports, debugging, and compliance.

---

### 7. Time-Series Metrics Store

| Field | Detail |
|---|---|
| **Technology** | Prometheus (with optional long-term storage via Thanos or InfluxDB) |
| **Owned by** | Metrics & Monitoring Service (read); Tracking Service (write) |

Stores aggregated numeric metrics with timestamps. Optimised for range queries and rate calculations. Scraped by Grafana for dashboards.

---

### 8. Anomaly State Store

| Field | Detail |
|---|---|
| **Technology** | Redis 7 |
| **Owned by** | Anomaly Detection Service |

Short-lived key-value store for sliding-window counters, alert cooldown flags, and recent anomaly history. TTL-based expiry ensures stale state does not accumulate.

---

### 9. Message Bus

| Field | Detail |
|---|---|
| **Technology** | Apache Kafka (production) / Redis Streams (lightweight/dev) |
| **Owned by** | Shared infrastructure |

Async event backbone. Decouples the Gateway from all downstream consumers (Tracker, Anomaly Detection). Provides durability, replay capability, and backpressure handling. Topics: `llm.requests`, `llm.anomalies`.

---

## Connection Summary

| From | To | Protocol | Sync/Async |
|---|---|---|---|
| Callers | API Gateway | HTTPS REST | Sync |
| API Gateway | OpenAI / Gemini | HTTPS | Sync |
| API Gateway | Config & Auth | gRPC / HTTPS | Sync |
| API Gateway | Message Bus | Kafka produce | Async |
| Message Bus | Tracking Service | Kafka consume | Async |
| Message Bus | Anomaly Detection | Kafka consume | Async |
| Tracking Service | Request Log Store | SQL (TCP) | Sync |
| Tracking Service | Time-Series Store | HTTP push | Sync |
| Metrics Service | Time-Series Store | Prometheus scrape | Async pull |
| Metrics Service | Grafana | HTTP `/metrics` | Pull |
| Anomaly Detection | Anomaly State Store | Redis TCP | Sync |
| Anomaly Detection | Alerting System | HTTPS webhook | Async |
