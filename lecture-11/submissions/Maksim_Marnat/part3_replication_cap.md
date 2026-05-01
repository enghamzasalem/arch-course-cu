# Part 3.1 — Replication, failover intuition, and CAP (CityBite)

## 1. Postgres: sync vs async replica — reporting vs failover, RPO

| Replica type | Typical use for CityBite | Failover / reporting | RPO intuition |
|--------------|-------------------------|----------------------|---------------|
| **Synchronous** replica to a **sync standby** in another AZ | **Failover candidate** when we need **minimal data loss** on primary death | Promote standby only when commit **acknowledged** on sync replica → **RPO ≈ 0** for committed writes (at cost of write latency and availability if sync peer is down). | Few seconds to **zero** for committed transactions, depending on sync commit settings. |
| **Asynchronous** streaming replica | **Reporting**, analytics, **read scaling** for non-critical reads | **Not** first-choice automatic failover without careful tooling—**lag** means **lost or stale** data if promoted blindly. | **RPO** can be **seconds to minutes** of **lost writes** if primary dies before replication catches up. |

**Practice:** Use **async** replicas for **BI / restaurant dashboards** that tolerate **eventual consistency**. Reserve **sync or quorum sync** (managed HA) for the **orders ledger** tier where **money and fulfillment** matter.

## 2. Split-brain or stale read (misconfigured failover)

If two nodes both believe they are **primary**, applications can write **divergent histories**—**split-brain**—and reconciliation becomes expensive or impossible without downtime. If we **promote an async replica** that is **hours behind**, restaurants may see **old order states** while customers were charged—**stale reads** and **integrity violations**. Mis-tuned **automatic failover** without **fencing** (STONITH) or **leader election** from Postgres HA stack can cause **double writes** or **lost commits**. **One paragraph takeaway:** failover is not “DNS flip”; it is a **consistency protocol**—wrong promotion **breaks trust** in the order log.

## 3. CAP — availability vs strong consistency on a read path (ETA)

For **driver ETA** shown to the customer, **fresh perfect routing** is less critical than **always showing something useful**. We often choose **high availability** of the **read path** with **cached or slightly stale** route/ETA from a **regional cache** or **async replica**, accepting **eventual consistency**, rather than blocking the UI on a **strongly consistent** cross-region read that fails when the maps API blips. Strong consistency is reserved for **payment and order state transitions**; **ETA** is a **best-effort read model** where **AP-style** behavior improves perceived uptime.
