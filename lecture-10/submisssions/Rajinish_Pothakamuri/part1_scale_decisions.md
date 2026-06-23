## Part 1.2: Scale Up vs. Scale Out Decision Log

The following table outlines the strategic decisions for scaling CityBite's core subsystems during Year 1. These choices balance operational simplicity with the ability to handle peak dinner traffic and growth.

| Subsystem                              | Primary Bottleneck     | Scale Up (Vertical)                                              | Scale Out (Horizontal)                                        | Year 1 Choice | Justification                                                                                                               |
| :------------------------------------- | :--------------------- | :--------------------------------------------------------------- | :------------------------------------------------------------ | :------------ | :-------------------------------------------------------------------------------------------------------------------------- |
| **Order API Pods**                     | **CPU / RAM**          | Increase Kubernetes resource requests/limits per pod.            | Add more replicas via Horizontal Pod Autoscaler (HPA).        | **Scale Out** | The API is stateless, so horizontal scaling improves throughput and availability while handling traffic spikes efficiently. |
| **Notification Workers**               | **I/O Wait / Network** | Increase CPU/RAM for worker processes.                           | Increase the number of worker instances processing the queue. | **Scale Out** | Workers are I/O-bound; scaling out allows parallel processing of events, reducing queue backlog during peak load.           |
| **PostgreSQL (Primary DB)**            | **DB CPU / Disk IOPS** | Upgrade to a larger instance with more vCPUs and faster storage. | Add read replicas or implement sharding.                      | **Scale Up**  | Vertical scaling keeps the architecture simple and preserves strong consistency for transactional workloads in Year 1.      |
| **Object Storage / CDN (Menu Images)** | **Network Egress**     | Upgrade storage tier for higher throughput.                      | Use a CDN to cache images closer to users.                    | **Scale Out** | Serving static assets via a CDN reduces origin load and improves latency for geographically distributed users.              |

---

### Critical Limit Note

> **Does not scale infinitely:** The **single-writer PostgreSQL primary** is a fundamental bottleneck. All write operations (e.g., new orders) must pass through this node to maintain strong consistency. While read replicas can reduce read pressure, they do not help with write scalability. As demand grows, vertical scaling will eventually hit hardware limits, requiring more complex solutions such as sharding or distributed databases, which introduce operational overhead and consistency trade-offs.


