# Part 1.2 - Scale Up vs Scale Out Decision Log

| Subsystem | Primary bottleneck | Scale up option | Scale out option | Year 1 choice | Why |
|---|---|---|---|---|---|
| Order API pods | CPU per request + connection fan-out | Bigger node / larger pod CPU+RAM | More pods behind Service + HPA | **Scale out** | Traffic is bursty and stateless API replicas scale quickly with HPA. |
| Notification workers | Outbound I/O latency + queue lag | Larger worker instances | More worker replicas consuming queue | **Scale out** | Worker pool parallelism directly improves throughput during dinner spikes. |
| PostgreSQL primary | Write IOPS, CPU, lock contention | Larger DB instance + faster storage | Read replicas for reads; later partition/shard | **Scale up + replicas (hybrid)** | OLTP primary needs strong consistency for writes; reads can offload to replicas. |
| Kitchen active-order reads | Repeated hot queries | Bigger DB/cache instance | Redis cache + read replica + query partition key index | **Scale out with cache + replica** | Hot read path should not scale linearly with global order volume. |
| Menu images | Origin egress and latency | Bigger origin bandwidth | CDN edge cache + object storage | **Scale out via CDN** | Edge delivery reduces origin load and improves mobile latency. |

---

## Explicit limit: does not scale infinitely

**Single-writer OLTP primary does not scale infinitely.** Even with bigger instances, one write leader eventually hits CPU/IO/lock limits. Long-term growth requires architectural changes (careful partitioning/sharding strategy, write path simplification, and workload isolation).
