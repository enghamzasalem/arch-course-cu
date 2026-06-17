# Part 1.2 – Scale Up vs Scale Out Decision Log

## Decision Table

| Subsystem | Primary Bottleneck | Scale Up Option | Scale Out Option | Choice (Year 1) | Why |
|-----------|-------------------|-----------------|------------------|-----------------|-----|
| Order API pods | CPU + memory | Larger instance (4x vCPU) | More replicas (HPA) | **Scale Out** | Stateless, handles spikes cheaply with HPA |
| Notification workers | Network + external API | Larger instance | More replicas + queue | **Scale Out** | Queue decouples; more workers consume faster |
| PostgreSQL | Connection pool + disk IOPS | Larger instance + more RAM + SSD | Read replicas (scale out reads) | **Scale Up** with read replicas | Single writer still required; replicas help reads |
| Menu images (S3) | Bandwidth | No meaningful up | CDN + replication | **Scale Out** | Object storage scales automatically |

## Does Not Scale Infinitely

**PostgreSQL single primary writer** cannot scale writes beyond a single node. Writes stay limited even with read replicas. For extreme growth, sharding or CockroachDB would be needed, but that's beyond Year 1.

## Summary

| Decision | Rationale |
|----------|-----------|
| Stateless API → Scale out | Cheap, easy, HPA ready |
| Stateful DB → Scale up + replicas | Write bottleneck requires careful limits |
| Queue + workers → Scale out | Natural fit for async tasks |