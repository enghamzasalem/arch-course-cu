# Part 1: Workload Model and Bottlenecks
## Task 1.1: Workload Dimensions

## 1. Overview
CityBite is a regional food delivery system that faces sharp traffic spikes during dinner hours and marketing campaigns. To understand scalability, we measure how different workload dimensions grow and which resource becomes the first bottleneck.

---

## 2. Workload Dimensions

| Workload dimension | What it measures | Typical growth pattern | Resource that saturates first |
|---|---|---|---|
| Concurrent customers | Number of users browsing, ordering, and tracking orders at the same time | Increases quickly during dinner rush and coupon campaigns | Application CPU and RAM |
| Orders per minute | Number of new orders placed every minute | Spikes heavily between 19:00 and 21:00 | Database connections and CPU |
| Active restaurant count | Number of restaurants receiving live traffic at the same time | Grows as CityBite expands to more restaurants | DB CPU and query load |
| Menu image bytes | Total size of uploaded menu images and food images | Grows with restaurant onboarding and content updates | Disk I/O and object storage bandwidth |
| Dispatch dashboard queries | Number of queries from restaurant tablets and dispatch dashboard | Rises when many orders are being tracked and updated | Database read load and application locks |
| Notification volume | Number of emails, push notifications, and SMS messages sent after checkout | Grows linearly with completed orders | Network egress and worker throughput |
| Order status updates | Number of status changes such as placed, accepted, cooking, ready, delivered | Increases with active delivery operations | Database write IOPS and lock contention |

---

## 3. Hero Scenario

### Friday 19:00–21:00 in one city
This is the main dinner rush window. Many customers open the app at the same time, place orders, check delivery status, and browse restaurant menus. Restaurants and dispatch users also refresh their dashboards frequently.

### If the system is scaled well
- Pages load quickly even when traffic rises.
- Checkout completes without long waits.
- Restaurant dashboards refresh smoothly.
- Notifications arrive shortly after checkout.
- p95 latency stays stable and the database does not become overloaded.

### If the system is scaled poorly
- The app becomes slow or times out during checkout.
- Users may see delayed order confirmation.
- Restaurant dashboards feel stuck or refresh slowly.
- Database CPU and connection pools become exhausted.
- Notifications are delayed, and some users may think their order failed.

---

## 4. Summary
CityBite does not grow in only one way. Some workloads increase user-facing latency, while others stress the database, storage, or outbound network. A good scalability design must match each workload dimension to the resource that fails first and protect the checkout path from heavy background work.
