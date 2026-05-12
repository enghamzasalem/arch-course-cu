# Task 1.2 - Scale Up vs Scale Out Decision Log

| Subsystem | Primary bottleneck | Scale up | Scale out | Year 1 choice | Why |
| - | - | - | - | - | - |
| Order API pods | CPU under high load | bigger nodes | more pods | scale out | stateless, easy to replicate |
| Notification workers | worker CPU during spikes | bigger machines | more workers | scale out | jobs can run in parallel |
| PostgreSQL | write throughput and DB CPU | larger instance | read replicas or sharding | scale up | single primary handles writes |
| Object storage / CDN | network bandwidth | higher bandwidth storage | CDN distribution | scale out | static content is easy to distribute |

Note: PostgreSQL does not scale infinitely because it has a single write primary, so all writes are limited by one node.