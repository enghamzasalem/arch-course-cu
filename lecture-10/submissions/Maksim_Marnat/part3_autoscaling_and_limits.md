# Part 3.2 — Autoscaling and backpressure (Order API, queue, and DB)

## 1) One HPA rule for the Order API (assumptions)

| Field | Proposed value | Assumptions (labels) |
|-------|----------------|----------------------|
| **Metric** | `cpu` (average **utilization** of **requested** CPU per pod) | CPython/Node handlers are **CPU+JSON**-heavy; **RPS** could be a **custom** metric later. |
| **Target** | **60% of requested** CPU (e.g. 500m request → keep ~300m used on average) | Tuned so we **add** capacity **before** **queueing** in the app **threads**. |
| **minReplicas** | **2** (HA + rolling updates) | **Not** a single point for **Ingress** distribution. |
| **maxReplicas** | **20** in prod namespace for Year-1 | Stops runaway if **config** is wrong; **revisit** with **SLOs**. **Assumption:** one region. |

*(Example: `KEDA` or HPA on `requests/second` from the ingress is an alternative; numbers above are **illustrative** and must be **validated** in a **staging** cluster.)*

## 2) One backpressure / degradation policy (downstream overload)

When the **Postgres** primary is **saturated** (rejects **connections** or **pool** wait grows), the API first **sheds** best-effort work: return **503** on **idempotent** routes with **`Retry-After`**, and disable “**suggested for you**” and other **heavy** `GET` paths that are not needed to **place** an order.

If the **notify** backlog exceeds a **safety** depth, we throttle new outbox work only after `POST /orders` has **committed** (orders stay **accurate**; **pushes** may be **late**); **ops** sees a **"delayed notifications"** banner.

**Principle:** degrade **features** before **safety**; be **predictable** with **503** + **Retry-After** instead of **hanging**.

## 3) Failure lesson: scale **stateless** only, forget the **database**

If you only add **stateless** Order API **pods** without growing **Postgres** capacity, you get a common **failure** mode. Under a traffic spike, each new pod still opens a **connection pool** to the **same primary**, so the database hits **max connections**, **CPU/WAL I/O** saturation, and **row locks** first; users see **p95** blow up and **5xx** even if **HPA** keeps adding **pods** that look “busy.”

**HPA** can make this worse: **retries** from the edge multiply load; **replicas** rise while **RPS** does not improve, a pattern that is easy to mistake for an **application** bug instead of a **data-plane** cap.

**Detection** combines **DB** **telemetry** (primary **CPU**, **`active_connections`**, **lock** wait, **I/O** queue) with app **SLOs**: e.g. **HPA** at high replica count, **RPS** flat, **p95** poor — “stateless is scaling, nothing gets faster.”

**Mitigation** is to **right-size** total pool slots vs **DB** limits, **offload** eligible reads to a **replica** and **caches**, **queue** work that should not sit in the **OLTP** path, **upgrade** the **primary** when TPS is the true ceiling, and set **HPA** **max** from **e2e** **capacity** numbers, not **only** from node **CPU** headroom.
