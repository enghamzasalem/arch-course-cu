# Part 3 – Anomaly Detection Design
## Task 3.1: Anomaly Types, Detection Approaches, and Design Decisions

---

## Overview

The Anomaly Detection Service monitors the real-time event stream produced by the
API Gateway and identifies deviations from expected behaviour across five dimensions:
volume, latency, reliability, cost, and access patterns. Each anomaly type has a
dedicated detection rule, its own input signals, and a typed output event.

---

## Anomaly Type 1: Request Rate Spike

### What it means
A sudden, abnormal surge in the number of LLM API calls within a short window —
relative to the established baseline for that time-of-day and caller. Indicates a
runaway loop, misconfigured client, or deliberate abuse.

### Inputs

| Input | Source | Field |
|---|---|---|
| Incoming request count | Stream Ingester | `request_id`, `timestamp`, `caller_id` |
| Rolling window counter | Baseline Calculator (Redis) | `call_rate_window[]` (last 5 min) |
| Statistical baseline | Baseline Calculator | `mean_call_rate`, `stddev_call_rate` |
| Config threshold | Config Loader | `spike_z_score_threshold` (default: 3.0) |

### Detection Approach
**Z-score over a rolling 5-minute tumbling window.**

```
z = (observed_rate - mean_call_rate) / stddev_call_rate

if z > spike_z_score_threshold → fire anomaly
```

- The rolling window is maintained as a Redis list (LPUSH / LTRIM) of per-minute
  counts for the past 60 minutes.
- Mean and standard deviation are recomputed on each window update using NumPy.
- A minimum sample size (e.g. ≥ 10 windows) is required before scoring begins,
  to avoid false positives during cold start.
- Severity scales with z-score:
  - z ∈ [3, 5) → MEDIUM
  - z ∈ [5, 8) → HIGH
  - z ≥ 8     → CRITICAL

### Output

```json
{
  "anomaly_type": "REQUEST_RATE_SPIKE",
  "caller_id": "app-service-prod",
  "severity": "HIGH",
  "score": 0.87,
  "evidence": {
    "observed_rate_rpm": 842,
    "baseline_mean_rpm": 120,
    "baseline_stddev_rpm": 18,
    "z_score": 6.1,
    "window_minutes": 5
  },
  "timestamp": "2025-03-12T14:23:01Z",
  "recommended_action": "Inspect caller for runaway loop or apply rate limit"
}
```

---

## Anomaly Type 2: Latency Degradation

### What it means
End-to-end response latency (Gateway receives request → Gateway returns completion)
rises significantly above the rolling baseline. Indicates provider-side slowness,
network degradation, or an oversized prompt causing unusually long inference time.

### Inputs

| Input | Source | Field |
|---|---|---|
| Per-request latency | API Gateway | `latency_ms` (t₁ − t₀) |
| Rolling latency window | Baseline Calculator (Redis) | `latency_window[]` (last 100 requests) |
| Percentile baseline | Baseline Calculator | `p50_latency_ms`, `p95_latency_ms` |
| Hard threshold | Config Loader | `latency_p95_hard_threshold_ms` (default: 8000) |
| Relative threshold | Config Loader | `latency_relative_multiplier` (default: 2.5×) |

### Detection Approach
**Dual-trigger: absolute hard threshold OR relative multiplier breach.**

```
current_p95 = percentile(latency_window[], 95)

if current_p95 > latency_p95_hard_threshold_ms → fire (absolute)
OR
if current_p95 > baseline_p95 * latency_relative_multiplier → fire (relative)
```

- Uses a sliding window of the last 100 requests (not time-based) so low-traffic
  periods don't produce stale baselines.
- Both conditions are evaluated independently; either alone is sufficient to fire.
- The absolute threshold catches sudden extreme spikes; the relative threshold
  catches gradual degradation that stays below the absolute ceiling.
- Provider dimension is tracked separately (OpenAI vs Gemini) to distinguish
  provider-specific slowness from global degradation.

### Output

```json
{
  "anomaly_type": "LATENCY_DEGRADATION",
  "provider": "openai",
  "severity": "MEDIUM",
  "score": 0.73,
  "evidence": {
    "current_p95_latency_ms": 9400,
    "baseline_p95_latency_ms": 1850,
    "hard_threshold_ms": 8000,
    "relative_multiplier_observed": 5.08,
    "trigger": "BOTH"
  },
  "timestamp": "2025-03-12T14:31:45Z",
  "recommended_action": "Check OpenAI status page; consider failover to Gemini"
}
```

---

## Anomaly Type 3: Error Rate Surge

### What it means
The proportion of failed LLM API calls (HTTP 4xx / 5xx from provider, or Gateway-
level errors) within a rolling window exceeds the acceptable SLA threshold.
Indicates provider outage, auth failure (rotated keys), quota exhaustion, or
malformed request patterns.

### Inputs

| Input | Source | Field |
|---|---|---|
| Per-request HTTP status | API Gateway | `status_code`, `provider_error_code` |
| Rolling error counter | Baseline Calculator (Redis) | `error_count_window[]`, `total_count_window[]` |
| SLA threshold | Config Loader | `error_rate_sla_threshold_pct` (default: 5%) |
| Minimum sample size | Config Loader | `error_rate_min_requests` (default: 20) |

### Detection Approach
**Sliding-window error rate against a fixed SLA threshold, with error-type
stratification.**

```
error_rate_pct = (error_count / total_count) * 100   [over last 5-min window]

if total_count >= min_requests AND error_rate_pct > sla_threshold_pct → fire
```

- A minimum request count guard prevents a single failed request in a quiet period
  from producing a 100% error rate alert.
- Errors are stratified by type to aid diagnosis:
  - `4xx_client` → likely malformed requests or auth issues
  - `429_quota`  → quota exhaustion (actionable: rotate key or back off)
  - `5xx_provider` → provider-side outage (actionable: failover)
- Severity scales with magnitude:
  - 5–15%   → MEDIUM
  - 15–40%  → HIGH
  - > 40%   → CRITICAL

### Output

```json
{
  "anomaly_type": "ERROR_RATE_SURGE",
  "provider": "openai",
  "caller_id": "batch-job-nightly",
  "severity": "CRITICAL",
  "score": 0.96,
  "evidence": {
    "error_rate_pct": 42.3,
    "sla_threshold_pct": 5.0,
    "total_requests_window": 214,
    "error_breakdown": {
      "5xx_provider": 89,
      "429_quota": 1,
      "4xx_client": 0
    },
    "window_minutes": 5
  },
  "timestamp": "2025-03-12T14:55:12Z",
  "recommended_action": "Probable provider outage — trigger failover to Gemini"
}
```

---

## Anomaly Type 4: Token / Cost Drift

### What it means
The average token count per request or the rolling hourly cost rises significantly
above the established baseline. Indicates prompt injection, a new feature sending
unexpectedly large prompts, a misconfigured system prompt, or deliberate abuse
inflating usage costs.

### Inputs

| Input | Source | Field |
|---|---|---|
| Per-request token counts | API Gateway (from LLM response) | `prompt_tokens`, `completion_tokens` |
| Per-request cost | Tracking Service | `cost_usd` (computed from token × price table) |
| Rolling cost window | Baseline Calculator (Redis) | `cost_per_hour_window[]` (last 24 hrs) |
| Rolling token window | Baseline Calculator (Redis) | `avg_tokens_per_request_window[]` |
| Budget threshold | Config Loader | `hourly_cost_budget_usd` (per caller) |
| Token relative multiplier | Config Loader | `token_drift_multiplier` (default: 2.0×) |

### Detection Approach
**Dual-signal: absolute hourly budget threshold AND relative token-per-request
drift detection.**

```
# Signal 1 — Cost budget breach
rolling_cost_1h = sum(cost_window[last 60 min])
if rolling_cost_1h > hourly_cost_budget_usd → fire COST_BUDGET_BREACH

# Signal 2 — Token drift (sudden increase in average prompt/completion size)
avg_tokens_recent  = mean(token_window[last 20 requests])
avg_tokens_baseline = mean(token_window[last 500 requests])
if avg_tokens_recent > avg_tokens_baseline * token_drift_multiplier → fire TOKEN_DRIFT
```

- Both signals fire independently with distinct anomaly sub-types so operators
  can distinguish "we spent too much" from "prompts are suddenly much larger".
- Cost is computed using a versioned price table (updated when providers change
  pricing) stored in the Config Service.
- Per-caller budgets allow different thresholds for a batch job vs. an interactive
  API, preventing high-volume legitimate callers from masking abuse.

### Output

```json
{
  "anomaly_type": "TOKEN_COST_DRIFT",
  "sub_type": "TOKEN_DRIFT",
  "caller_id": "app-service-prod",
  "severity": "HIGH",
  "score": 0.81,
  "evidence": {
    "avg_tokens_recent_20req": 14820,
    "avg_tokens_baseline_500req": 3240,
    "drift_multiplier_observed": 4.57,
    "configured_multiplier_threshold": 2.0,
    "rolling_cost_1h_usd": 18.43,
    "hourly_budget_usd": 25.00
  },
  "timestamp": "2025-03-12T15:02:38Z",
  "recommended_action": "Inspect recent prompts for injection or misconfigured system prompt"
}
```

---

## Anomaly Type 5: Unusual Caller Behaviour

### What it means
A specific caller ID generates request volume, token usage, or cost that is
anomalous relative to *that caller's own* historical baseline — even if the
absolute numbers look normal at the system level. Catches slow-burn abuse,
credential sharing, or a new integration that hasn't been registered.

### Inputs

| Input | Source | Field |
|---|---|---|
| Per-request caller ID | API Gateway | `caller_id` |
| Per-caller rolling volume | Baseline Calculator (Redis) | `caller_rate_window[caller_id][]` |
| Per-caller baseline | Baseline Calculator | `caller_mean_rpm`, `caller_stddev_rpm` |
| Time-of-day profile | Baseline Calculator (Redis) | `caller_hourly_profile[caller_id][hour]` |
| Config multiplier | Config Loader | `unusual_caller_z_threshold` (default: 4.0) |

### Detection Approach
**Per-caller z-score with time-of-day normalisation.**

```
expected_rate = caller_hourly_profile[caller_id][current_hour]
z = (observed_rate - expected_rate) / caller_stddev_rpm

if z > unusual_caller_z_threshold → fire
```

- Each caller maintains its own rolling baseline stored as a per-key Redis hash,
  so a high-volume legitimate caller does not suppress detection on a low-volume
  caller.
- Time-of-day normalisation prevents a batch job that always runs at midnight from
  alerting every night.
- Minimum history requirement (≥ 7 days of data) before per-caller detection
  activates; before that, system-level thresholds apply.

### Output

```json
{
  "anomaly_type": "UNUSUAL_CALLER_BEHAVIOUR",
  "caller_id": "internal-tool-dev",
  "severity": "MEDIUM",
  "score": 0.68,
  "evidence": {
    "observed_rate_rpm": 340,
    "expected_rate_rpm_this_hour": 12,
    "caller_stddev_rpm": 4,
    "z_score": 5.2,
    "z_threshold": 4.0
  },
  "timestamp": "2025-03-12T15:11:04Z",
  "recommended_action": "Verify caller credentials have not been shared or leaked"
}
```

---

## Anomaly Summary Table

| # | Anomaly Type | Detection Method | Window | Primary Signal | Min Severity |
|---|---|---|---|---|---|
| 1 | Request Rate Spike | Z-score (rolling baseline) | 5 min | `call_rate_rpm` | MEDIUM |
| 2 | Latency Degradation | Dual-trigger: absolute + relative | Last 100 req | `latency_ms p95` | MEDIUM |
| 3 | Error Rate Surge | SLA threshold (sliding window) | 5 min | `error_rate_pct` | MEDIUM |
| 4 | Token / Cost Drift | Budget ceiling + relative multiplier | 1 hour / 20 req | `cost_usd`, `avg_tokens` | HIGH |
| 5 | Unusual Caller | Per-caller z-score + time-of-day | 5 min | `caller_rate_rpm` | LOW |

---

## Key Design Decision: Real-Time Stream Processing vs. Batch Detection

### The decision
Detection runs as a **continuous real-time stream processor** (Apache Faust /
Kafka Streams) co-located in the Anomaly Detection Service — **not** as a
periodic batch job against the metrics database.

### Options considered

| Option | Approach | Latency to alert | Complexity |
|---|---|---|---|
| **A — Batch query** | Cron job queries PostgreSQL / Prometheus every N minutes | Minutes | Low |
| **B — Polling metrics store** | Service polls Prometheus `/query` API on a short interval | 30–60 s | Medium |
| **C — Real-time stream (chosen)** | Faust consumer processes each Kafka event as it arrives | < 2 s | Medium-High |

### Why real-time stream processing was chosen

**1. Alert latency matters.**
A cost-drift or error-surge anomaly that runs for 5 minutes before detection can
cause significant financial or reputational damage. A streaming approach reduces
time-to-alert from minutes to under 2 seconds.

**2. Kafka events are already produced.**
The API Gateway already publishes a `RequestEvent` to Kafka for tracking purposes.
Consuming the same topic for anomaly detection adds zero overhead to the critical
request path — the stream is free.

**3. Stateful windowing is natural in stream processors.**
Faust and Kafka Streams have built-in support for tumbling and sliding windows,
which maps directly onto the rolling-window baseline model. Implementing the same
logic in a batch SQL query requires complex window functions and is harder to
reason about.

**4. Separation from the metrics store.**
Batch detection against Prometheus/PostgreSQL would couple the anomaly detector
to the health of those stores. If the metrics store is slow or unavailable, batch
detection stops. The stream processor is independent — it reads directly from
Kafka, which has its own durability guarantees.

### Trade-offs accepted

| Trade-off | Mitigation |
|---|---|
| Higher operational complexity (Kafka + Faust) | Kafka is already required for tracking; no new infrastructure |
| State must survive restarts | Sliding-window state persisted to Redis with TTL; Kafka consumer offsets committed |
| Cold-start: no baseline on first deploy | System-level hard thresholds active until per-caller baselines mature (7 days) |
| Out-of-order events possible | Faust watermark handling; late events within 30 s grace window are accepted |

### Where detection runs: separate service, not inside the proxy

Detection was deliberately placed in a **dedicated container** rather than inside
the API Gateway for three reasons:

1. **Latency isolation** — anomaly detection involves Redis reads and NumPy
   computations. Running this synchronously inside the Gateway would add latency
   to every request on the critical path.
2. **Independent scaling** — the detector can be scaled, restarted, or redeployed
   without any impact on request forwarding.
3. **Single responsibility** — the Gateway's job is to forward requests fast and
   reliably. Bundling detection logic into it would violate that principle and
   make both harder to test.
