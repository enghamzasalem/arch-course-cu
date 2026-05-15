# Part 1 — Bounded Contexts and Conway’s Law (CityBite)

## 1. Overview

As CityBite grows, the system becomes harder to change safely when every feature shares the same database, deployment pipeline, and release cycle. To improve flexibility, the platform can gradually evolve into multiple bounded contexts aligned with real business capabilities instead of technical layers.

The goal is not to split everything into microservices immediately, but to create clearer ownership boundaries so teams can move independently without constantly breaking each other’s work.

---

# 2. Bounded Context Map

## 2.1 Ordering Context

### Primary User
Customers placing food orders.

### Ubiquitous Language
- Cart
- Checkout
- Order
- Payment status
- Delivery address
- Order total

### Owns
- Order lifecycle
- Checkout workflow
- Cart validation
- Order persistence
- Customer checkout API

### Notes
This context is the core transactional system of CityBite. It requires strong consistency because failed or duplicated orders directly impact revenue and customer trust.

---

## 2.2 Restaurant Operations Context

### Primary User
Restaurant staff using kitchen dashboards and restaurant tablets.

### Ubiquitous Language
- Active orders
- Kitchen queue
- Ready for pickup
- Menu item
- Prep time
- Restaurant availability

### Owns
- Restaurant menus
- Kitchen workflow
- Restaurant order status updates
- Active order dashboards

### Notes
This context focuses on operational speed and visibility inside restaurants. It frequently reads active orders and benefits heavily from caching and partitioning by `restaurant_id`.

---

## 2.3 Dispatch and Delivery Context

### Primary User
Drivers and dispatch coordinators.

### Ubiquitous Language
- Courier
- Delivery route
- ETA
- Pickup
- Dropoff
- Driver assignment

### Owns
- Courier assignment
- Delivery tracking
- ETA calculations
- Dispatch optimization

### Notes
This context interacts heavily with external mapping and routing APIs. Availability is often more important than strict consistency because ETA estimates can tolerate small delays or stale data.

---

## 2.4 Payments Context

### Primary User
Finance systems and checkout workflows.

### Ubiquitous Language
- Authorization
- Capture
- Refund
- Transaction
- Payment gateway
- Settlement

### Owns
- Payment processing
- Gateway integration
- Refund logic
- Transaction records

### Notes
Payments are isolated because they integrate with external gateways and require stricter security, auditing, and retry controls.

---

## 2.5 Notifications Context

### Primary User
Customers and restaurants receiving updates.

### Ubiquitous Language
- Push notification
- SMS
- Email
- Retry queue
- Delivery event
- Notification template

### Owns
- Notification delivery
- Retry handling
- Message templates
- Push/SMS/email integrations

### Notes
Notifications are naturally asynchronous and can scale independently from the core checkout path.

---

# 3. Integration Between Contexts

| Context Pair | Integration Style | Reason |
|---|---|---|
| Ordering ↔ Payments | Synchronous API | Checkout requires immediate payment authorization |
| Ordering → Notifications | Async event | Notifications should not block checkout |
| Ordering → Restaurant Operations | Async event | Restaurants consume order events independently |
| Dispatch ↔ Restaurant Operations | Sync API + events | Dispatch needs near real-time order readiness updates |
| Dispatch → Notifications | Async event | Delivery updates are eventually consistent |

---

# 4. Why Async Communication Matters

CityBite avoids making every service call synchronous because tightly coupled request chains increase latency and failure risk. For example, checkout should not wait for SMS delivery or analytics updates. Using events and queues allows services to scale independently and reduces cascading failures during dinner rush traffic.

---

# 5. Conway’s Law

Conway’s Law states that software architecture tends to mirror the communication structure of the organization building it.

If CityBite keeps a single engineering team responsible for every feature, the architecture will likely remain a tightly coupled monolith because all changes move through the same coordination path. Shared ownership usually leads to shared databases, overlapping responsibilities, and slower release cycles.

As teams become more specialized — for example, separate teams for Ordering, Payments, and Dispatch — clearer service boundaries naturally emerge. Each team begins optimizing for its own workflows, APIs, and deployment schedules. Over time, this organizational structure encourages modular architectures and cleaner bounded contexts.

However, splitting services too early without corresponding team boundaries can create unnecessary operational complexity. For CityBite’s current size, a modular monolith with well-defined internal boundaries may still be more practical than a large microservice ecosystem.