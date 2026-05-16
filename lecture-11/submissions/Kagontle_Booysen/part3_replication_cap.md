# Part 3 — Task 3.1: Data Redundancy
**Assignment:** Software Architecture — Lecture 11 (Availability and Services)  
**Product:** CityBite  
**Component:** Managed Postgres + read models

---

## 3.1.1 Sync vs Async Replication — Failover and Reporting

CityBite runs a managed Postgres cluster with one primary and two replicas. The two replicas serve different purposes and are configured with different replication modes to match their availability and consistency requirements.

### Synchronous replica — standby for failover

One replica is configured with **synchronous replication** (`synchronous_commit = on` / `synchronous_standby_names` in `postgresql.conf`). In synchronous mode, the primary does not acknowledge a `COMMIT` to the application until the WAL (Write-Ahead Log) record has been written to the standby's WAL buffer and flushed to disk. The Order API therefore never receives a successful write confirmation until at least one replica has a durable copy of that transaction.

**Use case:** Automated failover. If the primary becomes unavailable — pod crash, AZ failure, OOM kill — the cluster manager (e.g., Patroni on AWS RDS Multi-AZ) promotes the synchronous standby to primary. Because every committed transaction was already present on the standby before acknowledgement, **no committed data is lost**. The RPO (Recovery Point Objective) for the synchronous replica is effectively **zero**: the promoted primary is byte-for-byte identical to the last committed state of the old primary.

**Cost:** Each write on the primary blocks until the standby acknowledges. Under normal network conditions within a single region (< 1 ms RTT between AZs), this adds negligible latency — typically 1–3 ms per commit. Under network degradation between AZs, write latency increases proportionally. This is an acceptable trade-off for the checkout path, where a lost order row would be a serious data integrity failure.

### Asynchronous replica — reporting and read scale-out

The second replica is configured with **asynchronous replication** (`synchronous_commit = off`). The primary writes WAL records and acknowledges commits immediately, without waiting for the replica to confirm receipt. The replica streams WAL changes in the background and typically lags the primary by **50–500 ms** under normal load, potentially several seconds under heavy write throughput.

**Use case:** Read-heavy workloads that tolerate slight staleness. This covers: restaurant analytics dashboards (order counts, revenue per hour), the operations team's reporting queries (driver utilisation, zone performance), and the Lecture 10 read models that serve the customer-facing ETA display and menu browse. Routing these queries to the async replica keeps them off the primary entirely, protecting write throughput during peak load. If the async replica becomes unavailable, reporting queries degrade but the primary and synchronous standby are unaffected.

**RPO intuition:** The async replica's RPO is not zero — it is equal to the current replication lag at the moment of failure. If the primary crashes when the async replica is 400 ms behind, those 400 ms of writes exist only in the primary's WAL and are irrecoverable. For reporting workloads this is acceptable. For the order write path, it is not — which is why the Order API's writes always target the primary, and critical reads (e.g., checking whether an `order_id` already exists before accepting a new order) also target the primary or the synchronous replica only.

### Summary

| | Synchronous replica | Asynchronous replica |
|--|---|---|
| `synchronous_commit` | on | off |
| Replication lag | ~0 (flush before ACK) | 50 ms – seconds |
| RPO at failover | 0 (no committed data lost) | Equal to lag at failure time |
| Use case | Automated failover, critical reads | Reporting, analytics, read scale-out |
| Write latency impact | +1–3 ms per commit (same region) | None |
| Risk if unavailable | Writes block (primary waits for ACK) | Reporting degrades; primary unaffected |

---

## 3.1.2 Split-Brain and Stale Read — What Goes Wrong with Misconfigured Failover

**Split-brain** occurs when two nodes both believe they are the primary and accept writes simultaneously. In CityBite's context, the most likely trigger is a **network partition** rather than a hardware failure: the primary becomes temporarily unreachable from the cluster manager (e.g., a flapping network interface between AZs), which causes the manager to promote the synchronous standby to primary — but the original primary is still running, still accepting connections from Order API pods that have cached its address, and still processing checkout requests. For a window of 10–60 seconds (until the original primary is fenced via STONITH or its DNS entry is updated), both nodes are writing. Order rows created on the original primary during this window will never appear on the new primary; payment gateway callbacks that arrive for those orders will find no matching `order_id` and fail with 404. When the original primary is eventually demoted and reconnected, Postgres replication cannot automatically merge the diverged write histories — the rows created during the split window must be manually reconciled or discarded, creating a data integrity incident that requires engineering intervention hours after the original outage was declared resolved.

**Stale reads** are a subtler failure. If the async replica's replication lag grows to 30 seconds during a write storm (e.g., a flash sale), and a customer cancels their order (write to primary: `status = CANCELLED`), but the cancellation confirmation screen reads from the async replica, the customer sees their order still in `PENDING` state. They tap "Cancel" again — the second cancel request hits the primary, which now correctly returns 409 Conflict (already cancelled). The customer, seeing inconsistent state, contacts support convinced there is a bug. This is not a data loss event, but it is a trust-eroding UX failure. The mitigation is **read-after-write consistency** for user-visible state changes: immediately after a write, the Order API directs the subsequent read for that `order_id` to the primary (using a session-level `SET default_transaction_read_only = off` or a connection routing hint), bypassing the replica for the first read that the same user session makes within a 2-second window. Outside that window, the replica will have caught up and can be trusted again.

---

## 3.1.3 CAP at High Level — Availability over Strong Consistency on the Read Path

The CAP theorem states that a distributed system under a network partition can provide at most two of: Consistency (every read returns the most recent write), Availability (every request receives a response), and Partition tolerance (the system continues operating despite network failures). Because network partitions are not optional in a multi-node cloud deployment — they happen — the practical choice is between CP (sacrifice availability to preserve consistency) and AP (sacrifice consistency to preserve availability).

CityBite makes the **AP choice deliberately on the ETA display path**. The ETA a customer sees on their order tracker screen is derived from the Maps/Routing API response and the driver's last known GPS position, both of which are stored in the async read model (Lecture 10) updated every 5–10 seconds. If the read model's replica is partitioned from the primary during a network event, CityBite has two options: (a) refuse to serve the tracker screen until consistency is restored — CP — which means the customer sees an error on a screen they are anxiously watching; or (b) serve the last known ETA from the replica even though it may be 10–30 seconds stale — AP — which means the customer sees a slightly outdated but plausible ETA. CityBite chooses AP because the cost of stale ETA data (customer sees "8 minutes" when it should be "6 minutes") is negligibly low — it is a soft real-time display, not a transactional commitment. The cost of unavailability on the same screen (customer cannot see any ETA during what is already an anxious wait) is measurably higher in customer satisfaction terms. The ETA value itself is already an estimate with inherent uncertainty; strong consistency on an inherently imprecise value would add infrastructure cost and latency for no user-visible benefit.

The same AP reasoning applies to the restaurant menu browse screen: a customer viewing a menu that is 30 seconds behind the latest price update is a tolerable inconsistency (a mitigated stale read), not a correctness failure. The strong-consistency requirement applies only where the data is **transactional and irrevocable** — the order row, the payment record, and the driver assignment. Those paths always read from the primary or the synchronous replica, accepting the CP trade-off and its associated write latency penalty, because a stale read on a payment status is a financial data integrity issue, not a display imprecision.

---

## Summary

| Path | Replica type | Consistency model | CAP choice | Tolerable staleness |
|------|---|---|---|---|
| Order write (checkout) | Primary | Serializable | CP | None — RPO = 0 required |
| Failover reads | Synchronous replica | Strong (no lag) | CP | None |
| ETA display / tracker | Async read model | Eventual | AP | 10–30 s |
| Menu browse | Async replica | Eventual | AP | 30–60 s |
| Reporting / analytics | Async replica | Eventual | AP | Minutes |
| Read-after-write (cancel, confirm) | Primary (2 s window) | Strong (session) | CP (briefly) | 0 for the issuing session |

The principle throughout is to **match the consistency model to the consequence of being wrong**. Where being wrong costs money or trust (payments, order state), CityBite pays the latency and infrastructure cost of synchronous replication and primary reads. Where being wrong costs only mild display imprecision (ETA, menus), CityBite buys availability and read throughput by tolerating eventual consistency.

---

*End of Part 3. Assignment deliverables complete: `part1_services_inventory.md`, `part1_slo_error_budget.md`, `part2_monitoring_probes.md`, `part2_cascading_failures.md`, `part3_replication_cap.md`.*
