# Part 3 – Quality Attributes and Trade-offs
## Task 3.2: How the Architecture Supports Key Quality Properties

---

## Overview

The LLM API Wrapper sits on the critical path of every AI-powered feature in the
organisation. Its quality attributes must therefore be held to a higher standard
than a typical internal microservice: callers depend on it for correctness,
operators depend on it for visibility, and the business depends on it for cost
control. Five quality attributes are discussed below, each with architectural
evidence and an honest trade-off.

---

## Quality Attribute 1: Latency

### Why it matters for this wrapper
The wrapper is a synchronous intermediary — every millisecond it adds is felt
directly by the end user of whichever application is calling it. LLM inference
is already slow (p95 often 2–8 seconds); the wrapper must not meaningfully worsen
that figure. A poorly designed proxy could double perceived latency and undermine
the entire value proposition of using an LLM.

### How the architecture supports it

**1. Fire-and-forget tracking.**
The API Gateway returns the completion to the caller *before* any tracking work
begins. After receiving the LLM response, the Gateway publishes a single Kafka
event (a non-blocking async produce) and immediately returns. The Tracking Service
and Anomaly Detection Service consume that event entirely off the critical path.
This ensures tracking adds zero latency to the caller.

**2. Async auth config caching.**
The Config & Auth Service response (routing rules, provider key reference) is
cached in-process in the Gateway with a short TTL (e.g. 30 seconds). The vast
majority of requests skip the network round-trip to the Config Service entirely.

**3. Connection pooling to LLM providers.**
The Gateway maintains persistent HTTPX async connection pools to OpenAI and Gemini,
eliminating TCP and TLS handshake overhead on every request.

**4. No synchronous database writes on the hot path.**
The Gateway never touches PostgreSQL or Redis synchronously during a request.
All storage operations happen downstream, in separate containers, after the
response has already been returned.

### Trade-off
Kafka's async publish is fire-and-forget: if the broker is temporarily unavailable,
request events are lost and that call will not appear in the audit log or anomaly
detection. This is a deliberate availability-over-durability trade-off on the
tracking path. Mitigation: the Kafka producer is configured with a small in-memory
retry buffer (up to 30 seconds of backpressure) and a dead-letter topic for events
that ultimately fail to deliver, so gaps in the audit log can be identified and
investigated.

---

## Quality Attribute 2: Availability

### Why it matters for this wrapper
If the wrapper goes down, every application that depends on it loses LLM
capability entirely — a single point of failure amplified across all consumers.
High availability is non-negotiable. Additionally, individual LLM providers
experience outages; the wrapper must survive a provider failure without
propagating it to callers.

### How the architecture supports it

**1. Stateless Gateway — horizontal scaling and fast restarts.**
The API Gateway holds no durable state (no session, no DB connection that blocks
startup). It can be replicated behind a load balancer, and new instances reach
full readiness in seconds. Any instance can handle any request.

**2. Provider failover via routing rules.**
The Config Service holds an ordered failover list per model tier (e.g. primary:
OpenAI gpt-4o → fallback: Gemini 1.5 Pro). If the Gateway receives a 5xx or
timeout from the primary provider, it automatically retries on the next provider
in the list before returning an error to the caller. This is transparent to the
caller.

**3. Bulkhead isolation between containers.**
The Tracking, Metrics, and Anomaly Detection Services are separate processes with
separate resource pools. A crash or memory exhaustion in the Anomaly Detection
Service does not affect the Gateway's ability to forward requests. Each container
has independent health checks and restart policies.

**4. Config Service high-availability pair.**
The Config & Auth Service is deployed as a two-instance active-active pair behind
an internal load balancer, with its own PostgreSQL read replica. Combined with the
Gateway's local config cache, the system continues operating normally even if the
Config Service is unavailable for up to the cache TTL duration.

### Trade-off
Provider failover introduces latency on the failure path: the Gateway must wait
for the primary provider's timeout (configurable, default 10 seconds) before
switching. During that window, the caller is waiting. Mitigation: a short
per-provider circuit breaker (half-open after 10 consecutive 5xx responses)
skips the timeout wait and routes immediately to the fallback provider until the
primary recovers, reducing the failure-path latency from ~10 seconds to
under 100 ms after the circuit opens.

---

## Quality Attribute 3: Observability

### Why it matters for this wrapper
The wrapper is the single point through which all LLM usage flows. Without
deep observability, operators cannot answer: Which caller is consuming the most
tokens? Is latency getting worse over time? Are we on track to exceed the monthly
budget? Is an anomaly real or noise? Observability is not a nice-to-have — it is
the primary product promise of the "Monitor" pillar.

### How the architecture supports it

**1. Structured audit log (PostgreSQL).**
Every request is written to a structured relational log with a stable schema:
`request_id`, `caller_id`, `provider`, `model`, `prompt_tokens`,
`completion_tokens`, `cost_usd`, `latency_ms`, `status_code`, `timestamp`.
This enables arbitrary SQL queries for billing, debugging, and compliance without
pre-aggregating data.

**2. Time-series metrics (Prometheus + Grafana).**
The Metrics Service maintains Prometheus counters and histograms for all key
signals: `llm_requests_total`, `llm_latency_ms` (histogram), `llm_tokens_total`,
`llm_cost_usd_total`, `llm_error_rate`. Grafana dashboards provide live
visualisation with configurable time ranges and per-caller / per-provider
drill-down.

**3. Distributed trace context propagation.**
The Gateway injects a `request_id` (UUID) into every outbound LLM call header
and every Kafka event. This ID threads through the audit log, metrics labels,
and anomaly event evidence, making it possible to trace a single request from
the caller's HTTP call all the way through to the audit record and any anomaly
it contributed to.

**4. Typed anomaly events with structured evidence.**
Anomaly Detection outputs are not free-text alerts but structured JSON events
with `anomaly_type`, `severity`, `score`, and `evidence` fields. Operators can
filter by type, query by caller, and correlate with the audit log using
`request_id` references.

**5. `/health` and `/metrics` endpoints on every container.**
Each service exposes a standardised `/health` (liveness + readiness) endpoint
and a Prometheus `/metrics` endpoint. Infrastructure-level monitoring (uptime
checks, Kubernetes probes) and application-level monitoring use the same
endpoints, avoiding a two-tier monitoring setup.

### Trade-off
Structured logging to PostgreSQL at high throughput (e.g. 10,000 requests/min)
requires write capacity planning and will eventually require partitioning or
archival to keep query performance acceptable. At low-to-medium scale this is
invisible; at high scale, naive unbounded growth will cause the audit log to
become a bottleneck. Mitigation: table partitioning by month from day one, an
automated archival job that moves records older than 90 days to cold storage
(S3/GCS), and a read replica for analytics queries so reporting never competes
with write throughput.

---

## Quality Attribute 4: Security

### Why it matters for this wrapper
The wrapper holds and manages API keys for commercial LLM providers — credentials
that, if leaked, could generate unbounded financial liability. It also proxies
potentially sensitive prompt data (PII, confidential business context). A security
failure here is both a financial and a compliance risk.

### How the architecture supports it

**1. Centralised secret management via HashiCorp Vault.**
LLM provider API keys are never stored in environment variables, config files, or
application code. They live exclusively in Vault, are accessed at runtime via
short-lived leases, and are rotated automatically on a configurable schedule.
The Gateway requests a key reference from the Config Service; the Config Service
retrieves the key from Vault; the key is used once and not logged.

**2. Caller authentication via JWT.**
Every inbound request to the Gateway must present a signed JWT issued by the
Config & Auth Service. The Gateway validates the signature and expiry locally
(no network call on the hot path, after the public key is cached). Unauthenticated
requests are rejected at the Gateway boundary before any LLM call is made.

**3. Prompt data never persisted in plaintext.**
The audit log records token *counts* and *costs* but not the prompt or completion
content. If content logging is required (for debugging), it must be explicitly
enabled per-caller via a Config Service flag, and content is stored encrypted
at rest with per-caller encryption keys.

**4. Per-caller rate limits and quota enforcement.**
The Gateway enforces per-caller request rate limits and monthly token quotas
configured in the Config Service. A compromised or abusive caller credential
cannot exhaust the organisation's entire LLM budget; it is capped at its
assigned quota and blocked thereafter.

**5. Network segmentation.**
All inter-container communication uses an internal private network. Only the
API Gateway's ingress port is exposed outside the system boundary. The Config
Service, Tracking Service, Redis, and PostgreSQL have no public ingress.

### Trade-off
Vault-based secret retrieval adds a network call to the secret-fetch path. If
Vault is unavailable during a key rotation cycle, the Gateway cannot retrieve
a fresh key and will serve errors until Vault recovers. Mitigation: the Config
Service caches the current key in an encrypted in-memory store with a lease
duration slightly longer than the Vault TTL, providing a grace window during
short Vault outages. The Config Service HA pair further reduces the blast radius
of a single Vault node failure.

---

## Quality Attribute 5: Cost Efficiency

### Why it matters for this wrapper
LLM API calls are billed by token. At scale, uncontrolled usage — caused by
runaway loops, unexpectedly large prompts, or lack of per-caller budgets — can
generate thousands of dollars of unexpected charges within hours. The wrapper's
core value is visibility and control over this cost, so cost efficiency must be
a first-class architectural concern, not an afterthought.

### How the architecture supports it

**1. Real-time cost computation and accumulation.**
The Tracking Service computes the cost of every request immediately using a
versioned token-price table (updated when providers change pricing). Rolling
hourly and daily cost totals are maintained in the Time-Series Metrics Store,
giving operators a live view of spend rather than a monthly surprise invoice.

**2. Per-caller budget thresholds with anomaly detection.**
Each caller has a configurable hourly cost budget in the Config Service. The
Anomaly Detection Service's Token/Cost Drift rule monitors rolling spend against
these budgets and fires an alert before the threshold is breached, not after.
Operators can act (throttle the caller, investigate prompt size) while there is
still budget remaining.

**3. Token-count visibility before cost accumulates.**
The Token/Cost Drift anomaly type separately monitors average tokens per request
(prompt + completion). A sudden doubling in average token count is flagged
immediately, even if the hourly cost threshold has not yet been reached. This
gives an early warning that cost is about to spike.

**4. Lightweight infrastructure choices.**
The tracking and monitoring containers are stateless Python services with minimal
memory footprints. Redis is used for short-lived state (not as a primary database)
and sized to hold only the rolling windows needed for anomaly detection. The
architecture deliberately avoids heavyweight components (e.g. a full data
warehouse, a commercial APM platform) that would themselves become significant
cost line items.

### Trade-off
Real-time cost computation requires maintaining an up-to-date token-price table
in the Config Service. If a provider changes pricing and the table is not updated
promptly, reported costs will be inaccurate — potentially causing the system to
under-alert on budget breaches. Mitigation: the price table has a schema version
field and a `last_updated` timestamp that is monitored. A staleness alert fires
if the table has not been updated within 30 days, prompting the operator to verify
current provider pricing.

---

## Scalability Note

### API Gateway / Proxy
The Gateway is the highest-throughput component and is designed to scale
horizontally without coordination. Because it is fully stateless (no session
affinity, no local DB), a load balancer can distribute requests across any number
of replicas. In a Kubernetes deployment, a Horizontal Pod Autoscaler (HPA) scales
replicas based on CPU and request-rate metrics. Each replica maintains its own
HTTPX connection pool to LLM providers; provider-side rate limits are enforced
at the Config Service level (shared quota counters in Redis) to prevent the sum
of all replicas from exceeding the organisation's API quota.

### Anomaly Detection Service
The Anomaly Detection Service scales by increasing the number of Kafka consumer
group members. Each partition of the `llm.requests` topic is processed by exactly
one consumer instance, so adding replicas increases throughput linearly up to the
partition count. Stateful baseline data is stored in Redis (not in-process memory),
so all consumer instances share the same window state and produce consistent
baseline calculations regardless of which instance processes a given event.
The Redis instance itself can be scaled to Redis Cluster if the window state
volume exceeds single-node capacity, with consistent hashing ensuring each
`caller_id` key lands on a predictable shard.

### Tracking & Ingestion Service
The Tracker also scales as a Kafka consumer group. Write throughput to PostgreSQL
is the likely bottleneck at scale; this is addressed by batching INSERT statements
(writing 50–100 audit records per transaction rather than one per event) and by
directing analytics queries to a read replica, keeping write latency low on the
primary node.
