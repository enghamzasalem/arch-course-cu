# Task 3.1 - Replication and CAP

## Sync vs async Postgres replica

**Sync replica (failover)**: the primary acknowledges a write only after the replica has also stored it. Writes are slower because two machines have to confirm, but the replica is always up to date. If the primary dies we can promote it with no data loss. RPO is close to zero. We use this for failover, where losing a paid order is not acceptable.

**Async replica (reporting)**: the primary acknowledges the write right away and the replica catches up a few seconds later. Writes are fast, but the replica is always a bit behind. We use it for reporting and read-heavy queries (dashboards, analytics). If we lose the primary and only have the async replica, we lose whatever was not yet replicated, so RPO equals the replication lag.

The rule: sync for data safety, async for read scale.

## Split-brain

Split-brain happens when failover is misconfigured and two nodes both think they are the primary. Usually it comes from a network partition: the replica cannot reach the primary, assumes it is dead, and promotes itself, while the old primary is actually still alive. Now both nodes accept writes, data diverges, and when the network heals there is no clean way to merge two histories of the same orders. We can end up with duplicate order ids or lost payments. The fix is fencing or quorum so only one node can win the promotion, and the old primary must step down before failover completes.

## CAP for ETA display

For the ETA shown on the order screen we choose availability over consistency. A slightly stale ETA (computed a few minutes ago or from a cached route) is much better than an error or a blank screen. The customer just wants a rough idea of when the food arrives, and a small lag does not break the experience. For payment status or order status we would choose the opposite, because showing wrong data there is worse than showing no data.