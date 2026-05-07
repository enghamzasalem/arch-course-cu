# Part 3 — Replication and CAP Trade-offs (CityBite)

## 1. Overview

CityBite relies heavily on PostgreSQL for critical business operations such as orders, payments, and restaurant management. To improve availability and reduce downtime, the platform uses database replication and redundancy strategies.

This section explains how CityBite uses synchronous and asynchronous replication, the risks of failover misconfiguration, and where the system prioritizes availability over strict consistency.

---

## 2. PostgreSQL Replication Strategy

CityBite uses a primary PostgreSQL instance together with replica databases.

---

## 2.1 Synchronous Replication

### Purpose
Synchronous replication is used for high-priority failover protection.

In this model:
- The primary database waits for replica acknowledgment before confirming a transaction
- Data is copied immediately to the replica

---

### Benefits

- Stronger consistency guarantees
- Lower risk of data loss during failover
- Useful for critical financial or payment-related operations

---

### Drawbacks

- Higher write latency
- Slower transaction throughput
- Performance depends on replica network health

---

### CityBite Usage

CityBite would use synchronous replication selectively for:
- Critical order and payment durability
- High-availability failover replicas in the same region

---

## 2.2 Asynchronous Replication

### Purpose
Asynchronous replicas are mainly used for scaling reads.

In this model:
- The primary database responds immediately
- Replicas receive updates shortly afterward

---

### Benefits

- Lower write latency
- Better scalability for dashboards and reporting
- Reduced load on primary database

---

### Drawbacks

- Replica data may be slightly stale
- Some recent writes may not appear immediately

---

### CityBite Usage

CityBite uses asynchronous replicas for:
- Restaurant reporting dashboards
- Analytics queries
- Read-heavy operational views

This improves performance without increasing load on the primary database.

---

## 3. RPO (Recovery Point Objective)

CityBite aims for a very small Recovery Point Objective (RPO).

### Example Intuition

- Synchronous failover replica:
  - Near-zero data loss
  - Higher operational cost

- Asynchronous replica:
  - Possible loss of a few seconds of recent writes
  - Better performance and scalability

The acceptable RPO depends on the business impact of losing recent transactions.

---

## 4. Split-Brain and Stale Read Risks

Improper failover configuration can create serious consistency problems.

### Example Problem

If two database nodes both believe they are the primary:
- Different writes may occur independently
- Data becomes inconsistent
- Orders or payments may conflict

This is known as a split-brain scenario.

---

### Stale Reads

Asynchronous replicas can also return outdated information.

For example:
- A customer submits an order
- The restaurant dashboard reads from a lagging replica
- The new order does not appear immediately

This may temporarily confuse restaurant staff or customers.

---

### Mitigation Strategies

CityBite reduces these risks by:
- Using managed PostgreSQL failover tooling
- Limiting write access to a single authoritative primary
- Monitoring replica lag continuously
- Sending critical reads to the primary database when necessary

---

## 5. CAP Trade-offs in CityBite

The CAP theorem describes trade-offs between:
- Consistency
- Availability
- Partition tolerance

Because distributed systems must tolerate network failures, CityBite sometimes chooses availability over strict consistency for non-critical read paths.

---

## 6. Availability Over Strong Consistency

### Example: Delivery ETA Display

Estimated delivery times do not require perfect consistency.

If a replica is a few seconds behind:
- The customer still sees a usable ETA
- The application remains responsive
- Temporary stale data is acceptable

In this case, CityBite prioritizes:
- Fast response time
- High availability
- Lower load on the primary database

---

### Where Strong Consistency Still Matters

CityBite still requires strong consistency for:
- Payment confirmation
- Final order creation
- Inventory deduction

These workflows must remain authoritative and correct.

