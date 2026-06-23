# Part 3.1 — Replication & CAP

## PostgreSQL Replication Strategy

CityBite uses replication to improve availability and performance.

### Asynchronous Replication
- Used for: **read replica**
- Purpose: serve read-heavy operations (dashboard, reporting)
- Advantage: improves performance and availability
- Trade-off: data may be slightly stale

### Synchronous Replication
- Used for: **failover (critical writes)**
- Purpose: ensure data consistency between primary and replica
- Advantage: no data loss
- Trade-off: higher latency

---

## RPO (Recovery Point Objective)

- Async replication → small data loss possible (few seconds)
- Sync replication → near zero data loss

CityBite prefers:
- Async for performance (reads)
- Sync for critical operations (writes)

---

## Risk: Split-Brain / Stale Reads

If failover is misconfigured:

- Two nodes act as primary (split-brain)
- Data inconsistency occurs
- Conflicting writes

OR:

- Read replica is outdated
- Users see incorrect order status

=> This can break user trust and system correctness

---

## CAP Trade-off

CityBite sometimes chooses **Availability over Consistency**

Example:
- Showing estimated delivery time (ETA)
- Menu display

=> Slightly outdated data is acceptable  
=> System must remain responsive

However:

- Order placement and payment require **strong consistency**

---

## Conclusion

Replication improves availability but introduces trade-offs.  
CityBite balances consistency and availability depending on the use case.