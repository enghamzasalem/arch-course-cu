# Part 3.1 — Data Redundancy, Replication & CAP

## 1. Postgres: Sync vs Async Replica

CityBite runs a managed Postgres instance (e.g. AWS RDS Multi-AZ or GCP Cloud SQL). It maintains two types of replicas:

### Synchronous Replica — Failover

| Attribute | Detail |
|-----------|--------|
| Mode | **Synchronous** streaming replication |
| Use | **Automatic failover** (high availability) |
| Behaviour | The primary waits for the standby to confirm it has written the WAL record before acknowledging the commit to the application. |
| RPO | Near-zero (≤ 1 transaction). If the primary fails, the standby has every committed transaction. |
| RTO | ~30–60 seconds for managed failover (DNS flip + connection pool reconnect). |
| Trade-off | Every write incurs the round-trip latency to the standby. Acceptable for CityBite's order writes (< 5 ms intra-AZ), but would be painful across regions. |

### Asynchronous Replica — Reporting

| Attribute | Detail |
|-----------|--------|
| Mode | **Asynchronous** streaming replication |
| Use | **Read-heavy reporting** queries (revenue dashboards, restaurant analytics, dispatch history) |
| Behaviour | The primary does not wait for the replica to confirm writes. The replica lags behind by seconds to minutes depending on write volume. |
| RPO | Minutes of potential data loss if the async replica were promoted (which is why it is **not** used for failover). |
| Trade-off | Reporting queries run on a separate host, so they cannot slow down or lock the primary. Stale data is acceptable for dashboards that refresh every few minutes. |

**RPO intuition:** RPO (Recovery Point Objective) is the maximum acceptable data loss measured in time. Sync replication gives RPO ≈ 0 because the standby is always current. Async replication gives RPO = replication lag (could be 30 seconds to several minutes), which is fine for analytics but unacceptable for the order ledger.

---

## 2. Split-Brain and Stale Reads

**Split-brain** occurs when a network partition causes both the primary and the standby to believe they are the authoritative writer. In a misconfigured failover setup — for example, if the health check that triggers promotion is too aggressive and fires during a brief network hiccup rather than a true primary failure — the standby is promoted while the original primary is still running and accepting writes. Both nodes now accept writes independently. When the partition heals, the two transaction logs have diverged: some orders exist only on the old primary, others only on the new primary. Reconciling them is non-trivial and may require manual intervention or data loss.

For CityBite, a split-brain scenario on the orders table is catastrophic: a customer could be charged twice (once on each node), or an order could be confirmed on one node and invisible on the other. Managed services like RDS Multi-AZ use STONITH (Shoot The Other Node In The Head) fencing to prevent this — the old primary is forcibly shut down before the standby is promoted. CityBite must ensure that the managed service's fencing is enabled and that the application's connection pool uses the cluster endpoint (which always points to the current primary) rather than a hardcoded IP.

**Stale reads** are a softer problem: a read replica that is lagging by 10 seconds will return order data that is 10 seconds out of date. For the dispatch worker reading "which orders are ready for pickup?", a 10-second lag is harmless. For the checkout confirmation page ("did my payment go through?"), a stale read could show `status: pending` when the order is already `confirmed`, confusing the customer. CityBite routes all post-payment reads to the primary for 5 seconds after a write to avoid this, then falls back to the replica.

---

## 3. CAP Trade-off: Choosing Availability Over Strong Consistency on the Read Path

The CAP theorem states that a distributed system can guarantee at most two of: **Consistency**, **Availability**, and **Partition tolerance**. In practice, network partitions happen, so the real choice is between **CP** (stay consistent, possibly unavailable) and **AP** (stay available, possibly stale).

CityBite deliberately chooses **availability over strong consistency** on the ETA display path. When a customer is watching their order's estimated arrival time, the ETA is read from the async replica (or a Redis cache populated by the dispatch worker). If the replica is lagging or the cache is slightly stale, the customer sees an ETA that is 30–60 seconds out of date. This is acceptable — the customer does not need millisecond-accurate ETA data, and showing a slightly stale ETA is far better than showing an error or a spinner.

By contrast, the **payment and order confirmation path** is CP: CityBite always reads from the primary after a write, accepting the higher latency cost to guarantee that the customer sees the correct, up-to-date order status. Showing a stale "payment pending" when the payment has already been captured would erode trust and generate unnecessary support tickets.

This split — AP for display/read paths, CP for transactional paths — is a deliberate architectural decision that maps directly to the lecture's guidance: choose the consistency model that matches the user's tolerance for stale data in each specific context.
