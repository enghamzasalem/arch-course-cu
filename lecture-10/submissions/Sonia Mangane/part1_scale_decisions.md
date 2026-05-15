# Task 1.2: Scale Up vs. Scale Out Decision Log

## Decision Table
The following table outlines the strategic choices for scaling CityBite's core subsystems during Year 1.

| Subsystem | What Slows It Down | Scale Up (Bigger Machine) | Scale Out (More Machines) | Year 1 Choice | Why |
| --- | --- | --- | --- | --- | --- |
| **Order API Pods** | CPU / RAM | Give each pod more CPU/RAM | Add more pods using HPA | **Scale Out** | The API is stateless, so adding more pods is cheap and reliable. |
| **PostgreSQL DB** | Writes / CPU | Use faster SSDs + more vCPUs | Add read replicas or shard | **Scale Up** | Sharding is too complex for Year 1. A bigger primary DB is simpler and safer. |
| **Notification Workers** | Network I/O / Threads | Give each worker more CPU/RAM | Add more worker instances | **Scale Out** | Workers run tasks in parallel, so more workers = faster processing. |
| **Image Storage** | Network Bandwidth | Increase server bandwidth | Use a CDN | **Scale Out** | A CDN reduces load on our servers and speeds up image delivery. |

## Operational Limits
**Note: The Primary DB does not scale infinitely.**
Even though we can easily add more API pods or read replicas, the primary Postgres writer is still a single machine doing all the writes. Eventually:
- It hits hardware limits
- Vertical scaling becomes very expensive
- We cannot push more writes into one node
To go beyond this, we would need bigger architectural changes like splitting features across databases or sharding, which is too complex for Year 1.



