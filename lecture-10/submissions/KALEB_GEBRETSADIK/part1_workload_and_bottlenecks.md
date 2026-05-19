# Part 1.1: Workload Model and Bottlenecks

## 1. Five Core Workload Dimensions
For a regional food delivery platform like CityBite, growth isn't a single metric. It hits the system across multiple distinct dimensions:

1. **Concurrent Customers Browsing:** As traffic spikes, the number of users viewing restaurant menus concurrently surges. 
   - **Resource Saturating First:** **CPU and Network Egress** at the API Gateway/Web tier, as rendering and transmitting heavy JSON menu structures consumes bandwidth and compute.
2. **Orders Created Per Minute:** The actual transactional volume of successful checkouts.
   - **Resource Saturating First:** **Database Connection Pool and DB Locks**. Writing to the `orders` table involves ACID constraints. Too many simultaneous writes will exhaust connections and trigger heavy row-level locking.
3. **Concurrent Active Delivery Drivers:** Drivers continuously ping the server for GPS dispatch updates.
   - **Resource Saturating First:** **API Pod CPU / Memory**. Handling high-frequency, low-latency polling or maintaining thousands of open WebSockets eats up RAM on the application layer.
4. **Restaurant Active Dashboard Queries:** Kitchens checking their "Active Orders" queue every 5 seconds.
   - **Resource Saturating First:** **Database CPU/IOPS**. Constantly querying an unindexed or poorly indexed database table for "all unfulfilled orders for Restaurant ID X" causes massive disk reads.
5. **Menu Image Uploads / Downloads:** Restaurants onboarding new dishes resulting in heavy file transfers.
   - **Resource Saturating First:** **Disk IOPS and Object Storage Throughput**. Reading and writing thousands of heavy JPEGs will bottleneck disk drives or block network throughput limits.

## 2. The Hero Scenario: Friday Dinner Rush (19:00–21:00)

**Scenario:** It's Friday night in a major metropolitan area. Heavy rain has triggered an unprecedented surge in delivery demand, layered on top of a "Free Delivery Hour" marketing campaign.

**If the system is scaled well:** The customer experience remains fluid and responsive. The restaurant menus load instantaneously (cache hits), and checkout completes within 500ms. Drivers see notifications instantly. The system feels completely native and synchronous, protecting the brand's premium reputation.

**If the system is scaled poorly:** The friction compounds exponentially. The p95 latency spikes to 5000+ milliseconds. Customers stare at loading spinners, assuming the app is broken, resulting in cart abandonment. Database connections max out, meaning that even restaurants trying to mark an order as "ready" face 503 HTTP errors. Drivers show up to restaurants before the kitchen even receives the ticket, causing physical real-world chaos and angry merchants.
