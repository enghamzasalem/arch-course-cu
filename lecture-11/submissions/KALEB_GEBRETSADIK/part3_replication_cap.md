# Part 3.1: Data Redundancy & CAP

**Postgres Sync vs Async Replication:**
- **Sync Replica:** A transaction on the primary blocks until the sync replica acknowledges the write. Used for **failover** because RPO (Recovery Point Objective) is effectively 0; no committed data is lost if the primary dies.
- **Async Replica:** Writes to the primary return immediately, and the replica catches up in the background. Used for **reporting** or read-heavy traffic where slight staleness is acceptable.

**Split-Brain & Stale Reads:**
If failover is misconfigured, a network partition might cause both the old primary and the new primary to assume they are the leader. This is called a **split-brain** scenario. Both nodes accept writes independently, causing irreconcilable data corruption.

**CAP Theorem (Availability vs Consistency):**
When displaying the ETA for an active order, we favor **Availability over Strong Consistency (AP)**. If the primary database goes down or a network partition occurs, it is better to display a slightly stale ETA (read from an async replica or cache) than to return a 500 Error to the user. A 10-second stale ETA is acceptable; breaking the user experience is not.
