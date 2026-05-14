# Part 1: Contexts & Conway
## Task 1.1: Bounded Context Map

## 1. Overview
CityBite should be divided into bounded contexts based on business capability, not technical layers. Each context has its own language, data, and rules so that teams can change one area without constantly breaking another.

---

## 2. Bounded Contexts

### 2.1 Ordering Context
**Ubiquitous language:** cart, checkout, order, order status, line item, cancel, confirm, place order  
**Primary user:** Customer  
**Owns:** order creation, order state transitions, checkout rules, cart-to-order conversion

### 2.2 Payments Context
**Ubiquitous language:** authorize, capture, refund, payment intent, payment method, transaction, settlement  
**Primary user:** Customer and finance operations  
**Owns:** payment authorization, payment capture, refunds, payment failures, payment audit trail

### 2.3 Restaurant Operations Context
**Ubiquitous language:** menu, availability, prep time, accept order, reject order, mark ready, opening hours  
**Primary user:** Restaurant staff  
**Owns:** menu management, restaurant availability, order acceptance, kitchen status, preparation updates

### 2.4 Dispatch Context
**Ubiquitous language:** courier, pickup, dropoff, assignment, ETA, route, delivery status  
**Primary user:** Dispatch team  
**Owns:** courier assignment, route tracking, delivery lifecycle, ETA updates, delivery exceptions

### 2.5 Notifications Context
**Ubiquitous language:** push, SMS, email, template, alert, retry, delivery receipt  
**Primary user:** Customer support and customer-facing communication  
**Owns:** outbound message generation, notification retries, templates, delivery receipts

---

## 3. Integration Between Adjacent Contexts

### Ordering → Payments
**Integration style:** Sync API  
**Why:** Checkout needs an immediate answer on whether payment was authorized. The ordering flow cannot complete cleanly without a fast response.

### Payments → Notifications
**Integration style:** Async event  
**Why:** Payment success or failure can trigger messages later without blocking checkout. This keeps the payment path small and reduces latency.

### Ordering → Restaurant Operations
**Integration style:** Async event  
**Why:** Restaurant systems should receive new orders quickly, but the customer should not wait for kitchen side effects. Events also allow multiple downstream consumers.

### Restaurant Operations → Dispatch
**Integration style:** Sync API for assignment, async event for status updates  
**Why:** The dispatch system may need an immediate courier lookup, but ongoing delivery updates are better as events.

### Dispatch → Notifications
**Integration style:** Async event  
**Why:** Delivery milestones such as “picked up” or “delivered” can be sent to customers without holding up the dispatcher or courier workflow.

---

## 4. Conway’s Law

If one team owns all CityBite contexts, the architecture will likely become a single shared monolith with one database, one release process, and many hidden dependencies. The code will probably be organized by technical layers such as controllers, services, and repositories rather than by business capability. Over time, this tends to create tight coupling, slow releases, and a shared schema that makes every change risky. Conway’s Law predicts that the software will mirror the team structure, so one large team usually produces one large interdependent system instead of clean bounded contexts.

---

## 5. Summary
CityBite should be split along business boundaries: Ordering, Payments, Restaurant Operations, Dispatch, and Notifications. Each context has its own language and ownership, and integration should use the lightest mechanism that fits the business need. That keeps the design flexible without turning the system into a distributed monolith too early.
