## Task 1.1: Workload Dimensions

### Dimensions and First-Saturating Resource

| Workload dimension                              | Resource that saturates first
| ----------------------------------------------- | ----------------------------------------------
| Concurrent active customers                     | Application CPU / thread pool → DB connections
| Orders per minute (checkout writes)             | DB CPU / WAL I/O
| Dispatch dashboard queries (per restaurant QPS) | DB connections / CPU
| Restaurants onboarded (catalog size growth)     | RAM (buffer cache) → query latency
| Total orders stored (historical data growth)    | Disk storage / index size

### Hero Scenario - Friday 19:00–21:00

**Scaled well:** The app feels normal. Menus load quickly, checkout completes in under a second, and restaurant tablets receive new orders without delay. Users have no idea a rush is happening.

**Scaled poorly:** The app slows noticeably around 19:05. Checkout spins and times out for some users. Restaurant managers see their dashboards stall. Engineers receive alerts. The outage lasts through the peak of the promotion - the worst possible time.