# ADR-001: Where to Run Anomaly Detection — Separate Service vs. In-Process Proxy

| Field        | Value                                         |
|--------------|-----------------------------------------------|
| **ID**       | ADR-001                                       |
| **Date**     | 2025-03-12                                    |
| **Status**   | Accepted                                      |
| **Deciders** | Platform Architecture Team                   |
| **Ticket**   | PLAT-204                                      |

---

## Context

The LLM API Wrapper must detect anomalies (call-rate spikes, latency degradation,
error-rate surges, cost drift, unusual caller behaviour) in real time and raise
alerts before damage accumulates. During the design phase, three candidate
placements were identified for the detection logic:

1. **In-process inside the API Gateway / Proxy** — detection runs synchronously
   (or in a background thread) within the same process that forwards LLM requests.
2. **Sidecar container** — a second container deployed alongside every Gateway pod,
   receiving a copy of each request event via a local Unix socket or loopback HTTP.
3. **Dedicated anomaly detection service** — a standalone container that consumes
   events from the shared Kafka Message Bus asynchronously.

This decision record documents why Option 3 was chosen.

---

## Decision

**Anomaly detection runs as a dedicated, separate service that consumes the Kafka
event stream. It does not run inside the API Gateway process or as a sidecar.**

---

## Options Considered

---

### Option 1: In-Process (inside the API Gateway)

**How it works:**
After the LLM response is received, the Gateway synchronously (or via asyncio tasks)
runs detection logic — updating rolling windows in local memory and evaluating rules
— before (or concurrently with) returning the response to the caller.

**Pros:**
- Zero additional infrastructure: no Kafka consumer, no extra container.
- Lowest event delivery latency: detection sees each request immediately.
- Simpler deployment: one container to manage.

**Cons:**
- **Latency coupling:** Any slowness in detection logic (Redis reads, NumPy window
  computations) can delay the response returned to the caller. Even async tasks
  compete for the event loop.
- **Resource coupling:** A burst of anomaly scoring CPU work can starve the Gateway's
  ability to process new incoming requests promptly. Under high load, the two
  workloads fight for the same CPU and memory.
- **Restart coupling:** Restarting the Gateway to deploy new detection rules (e.g.
  new thresholds, new rule types) takes down the proxy for all callers.
- **Single responsibility violation:** The Gateway's job is to forward requests
  fast and reliably. Embedding detection logic makes it harder to reason about,
  test, and operate each concern independently.
- **Scaling mismatch:** Detection is CPU/memory-intensive (statistical baselines,
  window management). The Gateway scales on request throughput. Tying them together
  means over-provisioning one to satisfy the other.

**Verdict:** Rejected. The latency and coupling risks are unacceptable for a
component on the critical path.

---

### Option 2: Sidecar Container

**How it works:**
Every Gateway pod has a companion "anomaly sidecar" container. The Gateway emits
a fire-and-forget UDP/local-HTTP event to the sidecar after each response. The
sidecar maintains its own in-memory state and runs detection logic.

**Pros:**
- Decoupled from the Gateway's event loop (separate process/container).
- Can be restarted independently of the Gateway.
- Low event delivery latency (loopback or Unix socket).

**Cons:**
- **Per-pod state fragmentation:** Each Gateway pod has its own sidecar with its
  own in-memory rolling windows. If traffic is distributed across 5 Gateway pods,
  each sidecar sees only ~20% of the event stream. A call-rate spike spread across
  pods would appear normal to each individual sidecar — the anomaly is invisible.
- **No shared baseline:** Per-caller baselines computed in one sidecar are invisible
  to all others. The Unusual Caller detection becomes unreliable.
- **Operational overhead:** N Gateway pods means N sidecar containers to monitor,
  health-check, and upgrade. A sidecar crash is silent from the Gateway's perspective.
- **Synchronisation complexity:** To fix state fragmentation, sidecars would need
  to share state (e.g. via Redis), which largely eliminates the latency advantage
  of the sidecar pattern and adds coordination complexity.

**Verdict:** Rejected. State fragmentation across pods makes baseline-dependent
detection unreliable. Fixing it reintroduces the complexity of a shared-state
service anyway.

---

### Option 3: Dedicated Service consuming Kafka (Chosen)

**How it works:**
The API Gateway publishes a `RequestEvent` to a Kafka topic (`llm.requests`) after
every response — fire-and-forget, never blocking the caller. The Anomaly Detection
Service is a standalone container running a Faust stream processor that consumes
this topic. It maintains all sliding-window state in a shared Redis instance and
evaluates detection rules on every event.

**Pros:**
- **Zero impact on Gateway latency:** Detection is entirely off the critical path.
  The Gateway's only obligation is a non-blocking Kafka produce, which completes
  in microseconds.
- **Shared, consistent state:** All consumer instances of the Anomaly Detection
  Service share the same Redis baseline state. Scaling the service from 1 to 5
  replicas does not fragment the view of the event stream — each Kafka partition
  is assigned to exactly one consumer, and all consumers read/write the same Redis
  keys.
- **Independent scaling:** The detection workload (CPU-bound statistical computation)
  scales independently of the Gateway (I/O-bound request forwarding). Detection
  replicas are added by increasing Kafka partition count and consumer group size.
- **Independent deployment:** New detection rules, threshold changes, or algorithm
  upgrades are deployed by restarting the Anomaly Detection Service only. The
  Gateway continues serving requests without interruption.
- **Independent resilience:** If the Anomaly Detection Service crashes, the Gateway
  continues forwarding requests. Kafka retains unprocessed events (configurable
  retention, default 7 days); when the service restarts it replays the missed
  window and catches up.
- **Reuses existing infrastructure:** The Kafka topic is already required for the
  Tracking & Ingestion Service. The Anomaly Detection Service is a second consumer
  group on the same topic — no new infrastructure.

**Cons:**
- **Event delivery latency:** Events reach the Anomaly Detection Service with a
  small lag (typically 50–500 ms) relative to the in-process option. For anomaly
  detection operating on rolling minutes-scale windows, this is negligible.
- **Operational complexity:** Requires operating Kafka (or Redis Streams as a
  lighter alternative) and Faust. These are mature, well-understood systems, but
  they add infrastructure surface area.
- **At-least-once delivery:** Kafka consumer semantics mean a restart could
  reprocess a small batch of events, briefly double-counting them in rolling
  windows. Mitigated by idempotent window updates (Redis SET with NX where
  appropriate) and a small grace window in Faust watermark handling.

**Verdict:** Accepted. The separation of concerns, consistent shared state, and
zero impact on the critical-path latency outweigh the small event delivery lag
and the incremental operational complexity.

---

## Decision Rationale Summary

The fundamental constraint is that **the Gateway must not be burdened with work
that does not directly serve the caller's request**. Anomaly detection is
analytically valuable but has no bearing on whether a prompt is forwarded
correctly or a completion returned promptly.

The sidecar pattern solves the coupling problem but introduces a worse problem:
fragmented per-pod state that makes baseline-dependent detection statistically
unreliable. The whole value of anomaly detection depends on accurate baselines;
an architecture that systematically breaks them is worse than no detection at all.

The dedicated service pattern is the only option that satisfies all three
requirements simultaneously: (a) no latency added to the critical path, (b)
consistent global view of the event stream, and (c) independent lifecycle.

---

## Consequences

### Positive
- Gateway latency is unaffected by detection workload under any load condition.
- Detection baselines are globally consistent regardless of Gateway replica count.
- Detection rules and thresholds can be updated and deployed without Gateway downtime.
- Missed events during a service restart are automatically recovered from Kafka.

### Negative / Accepted risks
- A Kafka outage interrupts both tracking and anomaly detection simultaneously.
  Mitigation: Kafka is deployed as a 3-broker cluster with replication factor 3;
  the Gateway's producer uses an in-memory retry buffer for short outages.
- The ~50–500 ms event delivery lag means anomaly detection operates on a slightly
  delayed view of reality. For rolling-window detection (5-min, 1-hour windows),
  this lag is inconsequential. If sub-second detection were required (e.g. detecting
  a single malformed request), a different approach (circuit breaker in the Gateway)
  would be used instead.
- Adds Kafka and Faust to the operational skillset required. Mitigated by choosing
  Redis Streams as a drop-in alternative for teams that prefer not to operate Kafka.

---

## Revisit Criteria

This decision should be revisited if:
- Request volume drops permanently to a level where a single Gateway instance
  suffices and sidecar state fragmentation is no longer a concern.
- A hard requirement emerges for sub-100 ms anomaly detection (e.g. real-time
  abuse blocking on the request path) — at which point a synchronous in-process
  circuit breaker would complement (not replace) this service.
- The team adopts a service mesh (e.g. Istio) that provides built-in telemetry
  sidecars with shared aggregation, making Option 2 viable.
