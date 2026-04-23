---
marp: true
theme: default
paginate: true
header: 'Software Architecture — Lecture 10'
footer: 'Scalability — What / Why (presenter)'
style: |
  section { font-size: 22px; }
  h1 { font-size: 1.5em; color: #1e40af; }
  li { line-height: 1.4; }
---

<!--
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o Lecture10.pptx
  Read bullets aloud: **Label** — What: … Why: …
-->

# Scalability

**Chapter 10** — Software Architecture (Pautasso)

- **What:** runtime quality — the system keeps **SLOs** (latency, throughput, cost) as **load** grows.  
- **Why:** Lecture 9 made **shipping** easy; Lecture 10 asks whether the system **survives** success and spikes.

---

## Learning objectives

- **Workload & curves** — *What:* linear region → saturation → overload. *Why:* you explain **why** latency spikes, not only “CPU is red.”
- **Scale up / out & patterns** — *What:* bigger box vs more boxes; LB, scatter/gather, master/worker, **shard**. *Why:* named patterns are how teams **coordinate** fixes under pressure.
- **Location transparency** — *What:* directory vs dependency injection. *Why:* replicas move — callers must not bake in **physical addresses**.
- **Evidence** — *What:* p95, queues, replication lag, load tests. *Why:* stops arguments — shows **which** tier actually limits users.

---

# Recap — Lecture 9

- **What:** deployability, portability, **containers**, CI/CD, config, health probes.  
- **Why:** repeatable deploys are the **foundation** — you cannot tune scale you cannot **safely ship**.

---

## Chapter roadmap

- **Workloads vs resources** — *What:* demand (RPS, bytes, jobs) vs supply (CPU, IOPS, pools, $). *Why:* vocabulary must be **precise** or teams optimize the wrong layer.
- **Curves & levers** — *What:* saturation; work faster / less / later / get help; cache & edge. *Why:* gives a **checklist** when Friday traffic jumps.
- **Central vs decentral** — *What:* one truth vs many nodes; SPoF vs partial failure. *Why:* drives **consistency** and **failure** architecture (preview of availability).
- **Patterns & case studies** — *What:* same ideas in Google, Netflix, Uber, chains. *Why:* intuition + “**as seen in industry**” credibility.

---

## Scalability — definition

- **What:** handle **more** users, data, or events by adding **resources** while meeting agreed **targets** (e.g. p95 checkout &lt; 2s).  
- **Why:** the business question is “**10× Friday** — does the product still work?” not “is my loop O(n)?” alone.

---

## Workload vs resources

- **Workload (demand)** — *What:* concurrent clients, RPS, payload size, rows touched, background jobs, partner fan-out. *Why:* you **load-test** and **provision** against this — not against hope.
- **Resources (supply)** — *What:* vCPU, RAM, disk **IOPS**, network, **connection pools**, threads, budget. *Why:* the **first saturated** resource is the bottleneck — others may be idle.

---

## Throughput vs latency (three regimes)

- **Linear (healthy)** — *What:* throughput rises with load; latency **flat**. *Why:* proves extra traffic is still **within** capacity.
- **Saturation** — *What:* throughput **plateaus**; queues grow; latency **rises**. *Why:* signals “**add supply**, shed load, or optimize**” — the system is full.
- **Overload (failure mode)** — *What:* errors, timeouts, **retry storms**, dropping work. *Why:* past limits the system **hurts itself** — need backpressure and emergency policies.

---

## Scale levers (read as checklist)

- **Work faster** — *What:* better algorithms; faster chips; more cores per box. *Why:* often first fix when **CPU-bound** — until diminishing returns.
- **Work less** — *What:* approximations; turn off heavy features in peak; cheaper UI mode. *Why:* protects **revenue path** when you cannot instantly scale out.
- **Work later** — *What:* **queues** — accept now, process when capacity exists. *Why:* **decouples** arrival rate from service rate (notifications, indexing, webhooks).
- **Get help** — *What:* **scale out** — more parallel workers/pods/shards. *Why:* multiplies throughput **only if** work is **partitionable** or reads are **offloadable**.

---

## Cache & edge (friends of the levers)

- **What:** **Cache** stores prior answers (CDN, Redis); **edge** runs work on device or near user (maps, thumbnails).  
- **Why:** avoids repeated **origin** work — same economic idea as **Netflix / YouTube** edge caches.

---

## Scale up vs scale out

- **Scale up** — *What:* one **bigger** machine or disk. *Why:* simplest ops story; great for a **single** strong OLTP node — until cost per GB or core **explodes**.
- **Scale out** — *What:* **many** smaller units side by side. *Why:* elasticity and fault isolation — requires **stateless** tiers or a **data partitioning** story.
- **Together** — *What:* grow the box until painful, then **replicate reads** or **shard writes**. *Why:* real systems **combine** both — not a religious choice.

---

## Strong vs weak scaling

- **Strong** — *What:* **fixed** job; more machines ⇒ shorter wall time (batch render). *Why:* proves parallel decomposition **works** for that job.
- **Weak** — *What:* problem size grows with cluster; steady work per node. *Why:* models always-on services adding capacity **with** traffic.
- **Trap** — *What:* double pods but **same** hot DB row. *Why:* **serial** bottleneck — no amount of stateless replicas fixes one **contended** row.

---

## Centralized vs decentralized

- **Centralized** — *What:* many clients → **one** logical hub or primary. *Why:* **easier consistency** (one truth); obvious place to optimize — risk is **SPoF** unless replicated well.
- **Decentralized** — *What:* many peers/replicas; work and data **spread**. *Why:* throughput and isolation — pay **coordination**, replication lag, **partial failure** recovery.
- **Hot spot & churn** — *What:* one shard overloaded; nodes constantly join/leave. *Why:* decentralized systems still need **rebalance** and **membership** engineering (P2P, spot fleets).

---

## Graph limits (scalability “at scale”)

- **What:** each node has finite **connections** and **bandwidth** — full mesh does **not** remove physics.  
- **Why:** forces **hierarchies**, **super-peers**, or **gossip** — topology is part of the **architecture**, not only drawing boxes.

---

## Case — Netflix / YouTube

- **What:** **CDN** caches content at the edge; **encoding** splits video into chunks processed by **worker pools**.  
- **Why:** users are global — one datacenter cannot serve everyone; transcoding is classic **master/worker**.

---

## Case — Google Search

- **What:** query **scattered** to **index shards**; **gathered** and ranked into one result page.  
- **Why:** index too large for one machine — **partition** data; ranking step becomes the **gather** bottleneck to watch.

---

## Case — Amazon-scale services

- **What:** many **bounded contexts** / services; **Dynamo-style** partitioned storage on hot paths.  
- **Why:** limits blast radius; spreads **catalog/cart** keys — teams own **scale** of their slice.

---

## Case — Uber / Lyft & X (Twitter)

- **Uber/Lyft** — *What:* **geo** cells, dispatch, **surge** pricing. *Why:* partitions the world; economics aligns demand with **finite** drivers.  
- **X/Twitter** — *What:* timeline **fan-out**; **celebrity** hotspots. *Why:* few accounts drive huge reads — classic **shard/cache** stress.

---

## Scaling dimensions (map problems → fixes)

- **Clients** — *What:* concurrency, retries, WebSockets. *Why:* drives **session** placement (sticky vs Redis).
- **Input size** — *What:* big uploads, batches. *Why:* needs **streaming** or **master/worker**, not one giant request in RAM.
- **State** — *What:* carts, orders, positions. *Why:* **stateful** tiers resist blind scale-out — **externalize** or **shard**.
- **Dependencies** — *What:* payment, maps **quotas**. *Why:* your system stops when **their** limit hits — cache, queue, or renegotiate contracts.

---

## CityBite — dinner rush

- **What:** customers checkout; kitchens refresh boards; dispatch reads maps — **different** read/write mixes.  
- **Why:** one overloaded **OLTP primary** often caps **every** experience — find that **weakest link** in design reviews.

---

## Bottleneck archetypes

- **CPU** — *What:* JSON, crypto, transforms on hot path. *Why:* profile before blaming the database.
- **I/O & pools** — *What:* blocking DB; **pool wait** despite idle CPU. *Why:* requests wait on **locks outside** CPU — tune pools, async, replicas.
- **Contention** — *What:* one lock; one **hot** DB row. *Why:* **serializes** work — scale-out does not help until you **split** the contended resource.

---

## Stateless tier + affinity trade-off

- **Stateless** — *What:* any pod serves any request; session in **Redis**; files on **S3**. *Why:* load balancer **sprays** — simple horizontal scale.
- **Affinity** — *What:* sticky sessions, shard routing, pinned WebSockets. *Why:* sometimes required — trade is **hot shards** and harder failover.

---

## Load balancing

- **What:** L4/L7 distributor; health checks; round-robin, least-conn, **consistent hash** (caches).  
- **Why:** spreads work and masks dead instances — tune timeouts to avoid **retry storms** when backends slow.
- **Real ops** — *What:* **AWS ALB/NLB**, **GCP GLB**, **Cloudflare** in front of GitHub, Shopify. *Why:* shows the pattern is **production standard**, not textbook-only.

---

## Location transparency — directory vs DI

- **Directory / registry** — *What:* logical name → **current** address of service or shard. *Why:* replicas **move** — no hard-coded IPs in app code.
- **Dependency injection** — *What:* framework **wires** implementations to interfaces. *Why:* swap endpoints (tests, canary, new region) **without** rewriting business logic.
- **Same as sharding** — *What:* “**which shard holds this key?**” is also a **lookup** problem. *Why:* one mental model for discovery everywhere.

---

## Database — primary & replicas

- **Primary** — *What:* single writer for OLTP **truth**. *Why:* keeps transactions **tractable** — the usual **serial line** for writes.
- **Read replicas** — *What:* copies for dashboards / search. *Why:* scale reads — you consciously accept **replication lag** as staleness budget.
- **Pools** — *What:* each app instance holds DB connections. *Why:* pods × pool must stay under **max_connections** — invisible second bottleneck.

---

## Caching

- **What:** store responses (CDN edge, Redis) with TTL or explicit invalidation.  
- **Why:** avoids repeating expensive reads — decide **stale OK** (menu image) vs **never** (inventory you sold under ACID).

---

## Queues & workers

- **What:** accept fast → durable queue → **workers** drain at sustainable rate (SQS, Kafka, Rabbit).  
- **Why:** **smooths** spikes (dinner rush, marketing push) — same idea as **Stripe-style** async webhooks; see `example2_*.py`.

---

## Sharding (partitioned data)

- **What:** split dataset by **shard key**; **router** sends each query to the right partition when possible.  
- **Why:** exceeds one disk or one writer — enables **parallel** I/O; cross-shard queries cost **scatter/gather** tax.
- **Resharding** — *What:* changing key strategy or shard count **moves data on disk**. *Why:* expensive — early key choice is **architecture**, not tuning.

---

## Shard keys — strategies (pick with access patterns)

- **Range / geo / time / hash** — *What:* map records to shards by value ranges, country, month, or hash(mod N).  
- **Why:** balances **even spread** vs **locality** — monthly logs make range queries cheap; bad geo split makes **skewed** shards.

---

## Blockchain sharding (same idea, harder trust)

- **What:** split **state or execution** across chains/shards so not every validator runs **every** transaction (e.g. Ethereum roadmap, Polkadot, Cosmos-style designs).  
- **Why:** same **partition + route** idea as databases — adds **Byzantine** actors, consensus, and **hard cross-shard atomicity** (bridges, proofs).
- **Contrast DBs** — *What:* **MongoDB / Citus** shard under **trusted** ops for **IOPS/storage**. *Why:* presenter line: “**Same routing problem**; blockchain pays extra for **trustless** participation.”

---

## Partition vocabulary (read vendor docs)

- **Shard / Region / Tablet / vnode** — *What:* different product names for **horizontal partitions** (Mongo, HBase, Bigtable, Cassandra…).  
- **Why:** in interviews and on-call you **decode** docs faster when you recognize the same pattern under new words.

---

## Scatter / gather

- **What:** **broadcast** a request to N shards/workers; **aggregate** partial answers (min, merge, vote, deadline best).  
- **Why:** exploits parallelism when each replica holds **part** of the answer — CityBite “trending citywide” might fan out by region.
- **Kayak / Google Flights** — *What:* query airlines in parallel; pick offer under price/time **deadline**. *Why:* concrete story for **latency vs completeness** trade-off.

---

## When does scatter/gather reply?

- **Wait for all** — *Why:* only if every shard **must** answer — latency = **slowest** straggler.  
- **Deadline / k-of-n / fastest good / majority** — *Why:* caps tail latency; **majority vote** helps flaky or **untrusted** backends (Byzantine-style aggregation).

---

## Master / worker

- **What:** master **splits** input; workers process **chunks** in parallel; master **merges** — idempotent workers for retries.  
- **Why:** scales **one huge job** (transcode, render farm, **AWS Batch** ETL) — the “**embarrassingly parallel**” family.

---

## SETI@home — trust at internet scale

- **What:** volunteers processed radio data blocks; **leaderboards** led some clients to return **fake** results quickly.  
- **Why:** at scale you **verify** work — duplicate assignments and **compare**; expect a **minimum plausible** compute time before trusting an answer.

---

## Anti-pattern — global in-memory state

- **What:** one process holds **all** orders or carts in RAM; every read scans **everything**.  
- **Why:** breaks horizontal scale or forces **sticky** routing — becomes **O(planet)** work per request; see `example1_*.py`.

---

## Kubernetes HPA + measurement

- **HPA** — *What:* Horizontal Pod Autoscaler changes replica count from CPU/RPS/custom metrics. *Why:* elastic **stateless** tier — **pointless** if DB is still one tiny primary.
- **Measure** — *What:* **p95/p99**, queue depth, pool wait, replication lag. *Why:* **mean** latency hides unhappy users; tails show **saturation** early.

---

## Example 1 — CityBite kitchen (`example1_*.py`)

- **What:** naive **full scan** of all orders vs **index** by `restaurant_id`.  
- **Why:** proves each request’s work should scale with **tenant**, not with **global** catalog size.

---

## Example 2 — CityBite checkout (`example2_*.py`)

- **What:** synchronous SMS/email in request vs **enqueue + worker pool**.  
- **Why:** **decouples** user-facing latency from slow outbound I/O — the dinner-spike **throughput** story.

---

## Assignment — CityBite at peak

- **What:** written architecture (**150 pts**) — workload model, scale table, data plane, steady vs peak diagram, HPA/backpressure.  
- **Why:** practices explaining **trade-offs** to PM/ops — details in `ASSIGNMENT.md`.

---

## References (optional mention)

- **Abbott & Fisher** — *The Art of Scalability*  
- **Hohpe & Woolf** — *Enterprise Integration Patterns*  
- **Kleppmann** — *Designing Data-Intensive Applications*

---

## Takeaways — closing

- **Name the bottleneck** before buying hardware.  
- **Patterns answer different “why slow?”** — LB, cache, queue, shard, scatter/gather each has a **job description**.  
- **Watch tails and queues** — saturation is predictable if you measure **p99** and **depth**.

---

# Questions?

- **What:** Chapter **10** PDF; optional transcript `lectrue10.txt`.  
- **Why:** next arc — **availability** and **failure design** — assumes you already know **how load behaves**.
