## Task 3.1: Replication

### Postgres: Sync vs Async Replica

CityBite uses an **async replica** for reporting and dashboard queries. Replication lag of a few seconds is acceptable for a restaurant manager viewing revenue summaries, and async replication avoids adding latency to every write on the primary. For **failover**, a **sync replica** is used: the primary waits for the replica to confirm each write before committing, so if the primary dies the replica has every committed transaction. The RPO for the sync replica is effectively zero. The async replica's RPO is whatever the replication lag was at the moment of failure, typically seconds.

### Split-Brain on Misconfigured Failover

If the primary fails and the async replica is promoted without confirming the old primary is truly unreachable, both nodes may briefly believe they are the primary and accept writes. Orders written to the old primary will never reach the new one, meaning those rows are permanently lost or create conflicting state when the old node comes back online. In CityBite's context this could mean a paid order exists in the payment gateway's records but not in the database, causing reconciliation failures and customer complaints.

### CAP

For the delivery ETA displayed to customers, CityBite chooses availability over strong consistency. If the read replica is slightly behind the primary, a customer may see an ETA that is a few seconds stale. This is acceptable because ETA is an estimate anyway. Serving the stale read from the replica keeps the feature working even if the primary is under heavy write load or briefly unreachable. Strong consistency here would require reading from the primary on every ETA request, which adds latency and load for no meaningful user benefit.