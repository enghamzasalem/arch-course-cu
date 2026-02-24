### Exercise 4.1: Quality Attributes Analysis


## 1. Real-Time Multiplayer Game

| Quality Attribute | Why it matters | Trade-Offs |
|-------------------|--------------------|------------|
| Performance | Enables real-time responsiveness between players. | Reduce validation depth, increases consistency and to minimize delay. |
| Scalability | Must support large numbers of concurrent players globally. | Increases architectural complexity. |
| Availability | Downtime directly impacts player experience and revenue. | Requires redundant infrastructure and higher operational cost. |

### Architectural Impact

| Prioritized Attribute | Architectural Changes |
|----------------------|----------------------|
| Performance | UDP communication, in-memory state management, edge servers |
| Scalability | Horizontal scaling, distributed matchmaking, partitioned game state |
| Availability | Multi-region deployment, failover clusters, replication |

---

## 2. Banking System

| Quality Attribute | Why It’s Important | Trade-Offs |
|-------------------|--------------------|------------|
| Security | Protects sensitive financial data and prevents fraud. | Adds authentication steps and processing overhead. |
| Consistency | Ensures financial transactions are accurate (ACID compliance). | Reduces scalability and increases latency. |
| Reliability | Transactions must never be lost or corrupted. | Requires redundancy, backups, and monitoring systems. |

### Architectural Impact

| Prioritized Attribute | Architectural Changes |
|----------------------|----------------------|
| Security | Encryption (at rest and in transit), MFA, audit logging |
| Consistency | Strong transactional databases, synchronous replication |
| Reliability | Failover systems, redundant storage, disaster recovery |

---

## 3. Social Media Platform

| Quality Attribute | Why It’s Important | Trade-Offs |
|-------------------|--------------------|------------|
| Scalability | Handles millions to billions of users and content items. | Requires distributed databases and complex caching strategies. |
| Availability | Users expect continuous global access. | Multi-region deployments increase cost and operational complexity. |
| Performance | Fast loading improves engagement and retention. | Aggressive caching may result in stale data. |

### Architectural Impact

| Prioritized Attribute | Architectural Changes |
|----------------------|----------------------|
| Scalability | Microservices, sharded NoSQL databases |
| Availability | CDN usage, geo-replication |
| Performance | Distributed caching layers, asynchronous processing |

---

## 4. E-Commerce Website

| Quality Attribute | Why It’s Important | Trade-Offs |
|-------------------|--------------------|------------|
| Availability | Downtime directly affects revenue. | Higher infrastructure and operational cost. |
| Performance | Faster page loads improve conversion rates. | Optimization increases development complexity. |
| Security | Protects payment information and personal data. | Strong security measures may add checkout friction. |

### Architectural Impact

| Prioritized Attribute | Architectural Changes |
|----------------------|----------------------|
| Availability | Load balancing, redundancy, auto-scaling |
| Performance | CDN, query optimization, caching |
| Security | Secure payment gateways, encryption, tokenization |

---

## 5. IoT Sensor Network

| Quality Attribute | Why It’s Important | Trade-Offs |
|-------------------|--------------------|------------|
| Scalability | Supports potentially millions of sensors. | Requires distributed ingestion and processing systems. |
| Reliability | Data loss may impact analytics or system safety. | Adds network overhead and storage costs. |
| Energy Efficiency | Many sensors are battery-powered. | Reduced transmission frequency or lower data precision. |

### Architectural Impact

| Prioritized Attribute | Architectural Changes |
|----------------------|----------------------|
| Scalability | Message brokers, distributed data pipelines |
| Reliability | Acknowledgment protocols, retries, redundant ingestion |
| Energy Efficiency | Lightweight protocols (e.g., MQTT), edge preprocessing |



