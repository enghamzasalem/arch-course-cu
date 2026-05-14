# Part 3: Data Redundancy
## Task 3.1: Replication and CAP

## 1. Overview
CityBite needs replication so that the system can keep serving users even when a node fails. Replication is not only about durability; it also affects read performance, failover behavior, and the consistency that customers see on different screens.

---

## 2. PostgreSQL Replicas: Sync vs Async

### Synchronous replica
A synchronous replica confirms that a write is committed on both the primary and the replica before the transaction completes. CityBite would use this only for the most critical data if the business requires very strong protection against data loss. The trade-off is higher write latency, so it can slow checkout during peak traffic.

### Asynchronous replica
An asynchronous replica receives changes after the primary commits them. CityBite should use async replicas for **reporting**, dashboards, and many read-heavy views because they reduce load on the primary and improve scalability. The trade-off is that the replica can lag behind the primary, so the data may be slightly stale.

### RPO intuition
- **Sync replica:** near-zero RPO, because the replica is updated before commit completes.
- **Async replica:** small non-zero RPO, because a crash can lose the last few seconds of unreplicated writes.

### Recommended use in CityBite
- **Reporting / analytics:** async replica
- **Failover protection for critical orders:** sync if the latency cost is acceptable, otherwise async with backups and careful recovery planning

For a food delivery system, reporting can tolerate some delay, but order creation and payment records need stronger protection than a casual dashboard query.

---

## 3. What Goes Wrong if Failover Is Misconfigured

If failover is misconfigured, CityBite can run into split-brain or stale-read problems. In a split-brain case, two database nodes may both think they are primary and accept writes at the same time, which can create conflicting order states, duplicate payment records, or corrupted dispatch data. In a stale-read case, the system may redirect reads to a replica that has not caught up yet, so the customer sees an old order status or an outdated ETA. Both problems are dangerous because the UI may look healthy while the underlying truth is wrong. The result is confusion for customers, incorrect restaurant actions, and hard-to-repair data inconsistencies. This is why failover must be carefully controlled with clear leader election and replica lag checks.

---

## 4. CAP at a High Level

CityBite should choose availability over strong consistency for some read paths, especially for user-facing screens like ETA display, menu browsing, and order tracking summaries. If a read replica is slightly stale, it is often better to show a recent estimate than to block the user completely while waiting for a perfectly consistent answer. For example, a courier ETA can be approximate as long as checkout and payment remain correct. This is a practical CAP trade-off: the system accepts that some read paths may be eventually consistent so that users still get a fast response during peak load or partial failures. The important rule is that the critical write path, such as order creation and payment confirmation, should remain strongly controlled even if some display data is eventually consistent.

---

## 5. Summary
CityBite should use asynchronous replicas for reporting and read-heavy workloads, while keeping the critical write path protected. Sync replication gives stronger protection but costs latency. Async replication improves availability and performance, but it requires careful handling of stale reads, failover, and replica lag. The best design is to match replication mode to the user journey and the business risk.
