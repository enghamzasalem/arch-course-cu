# Part 2 – Component Rationale
## C4 Level 3: Anomaly Detection Service — Component Breakdown

---

## Why the Anomaly Detection Service?

The Anomaly Detection Service was chosen because it has the most complex internal logic:
it must ingest a high-throughput stream, maintain stateful baselines, score multiple
anomaly types in parallel, deduplicate alerts, and publish to external systems — all
with low latency. Decomposing it clearly is critical for maintainability and testability.

---

## Components

---

### 1. Stream Ingester

| Field | Detail |
|---|---|
| **Technology** | Python, Faust / Kafka consumer, Pydantic |
| **Responsibility** | Consumes raw request events from the Message Bus (Kafka topic `llm.requests`), deserializes and validates each event against a strict schema, and fans out typed `RequestEvent` objects to downstream components via an internal event bus. |
| **Provided interface** | `on_event(RequestEvent)` — pushes validated events internally |
| **Required interface** | Kafka / Redis Streams consumer API |

**Rationale:** Isolates all I/O and schema concerns at the boundary. If the Message Bus changes (Kafka → Pulsar) or the event schema evolves, only this component changes. Downstream components never touch raw bytes.

**Single Responsibility:** Consume, validate, and deserialize — nothing else.

---

### 2. Baseline Calculator

| Field | Detail |
|---|---|
| **Technology** | Python, NumPy, Redis (sliding window state) |
| **Responsibility** | Maintains rolling statistical baselines per metric dimension (call rate, latency, cost, error rate) using configurable sliding windows (e.g. 5-min, 1-hour). Computes mean, standard deviation, and percentile bands. Persists window state to Redis so baselines survive restarts. |
| **Provided interface** | `get_baseline(metric, caller_id, window) → BaselineStats` |
| **Required interface** | Anomaly State Store (Redis) for read/write of window buffers |

**Rationale:** Separates the statistical modeling concern from detection logic. Baselines can be tuned (window size, algorithm) without touching scoring rules. Also enables future swap to a more sophisticated model (e.g. ARIMA, Prophet) in isolation.

**Single Responsibility:** Compute and maintain statistical baselines — nothing else.

---

### 3. Anomaly Scorer

| Field | Detail |
|---|---|
| **Technology** | Python, configurable rule engine (dataclass-based rules) |
| **Responsibility** | Receives each `RequestEvent` plus current `BaselineStats` and evaluates a set of pluggable detection rules in parallel: call-rate spike, latency spike, cost drift, error-rate surge, unusual-caller volume. Produces a scored `AnomalyCandidate` (type, severity, score, evidence) when any rule fires. |
| **Provided interface** | `score(event, baseline) → AnomalyCandidate or None` |
| **Required interface** | `get_baseline()` from Baseline Calculator |

**Detection rules (each independently pluggable):**

| Rule | Method |
|---|---|
| Call-rate spike | Rolling count > baseline mean + N×σ |
| Latency spike | p95 latency > configurable threshold (ms) |
| Cost drift | Rolling cost/hour > budget threshold |
| Error-rate surge | Error % over window > SLA threshold |
| Unusual caller | Caller volume > N×personal baseline |

**Rationale:** Decouples "what is anomalous" from both data ingestion and alert publishing. New rule types can be added as plugins without modifying other components. Severity scoring makes alert fatigue manageable.

**Single Responsibility:** Evaluate detection rules and produce scored candidates — nothing else.

---

### 4. Deduplication & Cooldown Guard

| Field | Detail |
|---|---|
| **Technology** | Python, Redis (TTL keys) |
| **Responsibility** | Receives `AnomalyCandidate` objects and suppresses duplicates using Redis TTL keys. If an alert of the same type + caller has fired within the cooldown window (configurable, e.g. 10 min), the candidate is dropped. Only novel or re-escalated anomalies are passed forward. |
| **Provided interface** | `filter(candidate) → AnomalyCandidate or None` |
| **Required interface** | Anomaly State Store (Redis) for cooldown key read/write |

**Rationale:** Without deduplication, a sustained spike would flood the alerting system with hundreds of identical alerts. This component is the sole owner of alert-suppression logic, making cooldown policies easy to tune independently.

**Single Responsibility:** Suppress duplicate and cooldown-bound alerts — nothing else.

---

### 5. Alert Publisher

| Field | Detail |
|---|---|
| **Technology** | Python, HTTPX (async), Jinja2 (message templates) |
| **Responsibility** | Receives confirmed, deduplicated `AnomalyCandidate` objects and dispatches formatted alert payloads to configured channels: PagerDuty webhook, Slack webhook, or email. Formats messages using templates per anomaly type and severity. Logs all published alerts to the Anomaly State Store for audit. |
| **Provided interface** | `publish(candidate) → AlertReceipt` |
| **Required interface** | HTTPS webhooks (PagerDuty, Slack); Anomaly State Store (alert audit log) |

**Rationale:** Isolates all external I/O for alerting. New notification channels (Teams, OpsGenie) can be added here without touching detection logic. Template-driven formatting keeps messages human-readable and consistent.

**Single Responsibility:** Format and dispatch alerts to external channels — nothing else.

---

### 6. Config Loader *(supporting component)*

| Field | Detail |
|---|---|
| **Technology** | Python, Pydantic Settings, HashiCorp Vault client |
| **Responsibility** | Loads and hot-reloads detection thresholds, window sizes, cooldown durations, alert channel URLs, and severity mappings from the Config & Auth Service / Vault. Exposes a typed config object consumed by all other components. |
| **Provided interface** | `get_config() → AnomalyConfig` |
| **Required interface** | Config & Auth Service (gRPC/HTTPS) |

**Rationale:** Centralises all tunable parameters so operators can adjust thresholds (e.g. tighten cost-drift sensitivity) at runtime without redeployment. Without this component each rule would hard-code its own config loading — a maintenance anti-pattern.

**Single Responsibility:** Load, validate, and serve runtime configuration — nothing else.

---

## Interface & Dependency Summary

```
Message Bus
    │
    ▼
[Stream Ingester]  ←── Config Loader
    │  RequestEvent
    ▼
[Baseline Calculator] ←──→ Redis (window state)
    │  BaselineStats
    ▼
[Anomaly Scorer]   ←── Config Loader (thresholds)
    │  AnomalyCandidate
    ▼
[Dedup & Cooldown Guard] ←──→ Redis (cooldown keys)
    │  Confirmed AnomalyCandidate
    ▼
[Alert Publisher]  ──→ PagerDuty / Slack / Email
                   ──→ Redis (alert audit log)
```

---

## Modularity Principles Applied

| Principle | How Applied |
|---|---|
| **Single Responsibility** | Each component owns exactly one concern (ingest, baseline, score, deduplicate, publish) |
| **Open/Closed** | New detection rules added as plugins to Scorer; new alert channels added to Publisher — no other components change |
| **Dependency Inversion** | Components depend on interfaces (`get_baseline()`, `filter()`, `publish()`) not concrete implementations |
| **Separation of I/O** | All external I/O (Kafka, Redis, webhooks) is isolated to boundary components (Ingester, Publisher, Config Loader) |
| **Testability** | Each component can be unit-tested in isolation by mocking its single required interface |
