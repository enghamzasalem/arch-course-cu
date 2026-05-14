# Part 1.1 — Bounded Contexts & Conway’s Law

## Bounded Contexts

| Context | Ubiquitous Language | Primary User | Owns |
|---|---|---|---|
| Order Context | cart, checkout, order status, order item | Customer | Orders, cart management, checkout logic |
| Payment Context | payment, refund, transaction, invoice | Customer / Finance | Payment processing, refunds, transaction records |
| Restaurant Context | menu, availability, restaurant profile, item price | Restaurant Staff | Menus, restaurant information, item availability |
| Delivery Context | courier, route, ETA, delivery status | Dispatch Team | Delivery tracking, driver assignment, ETA calculation |
| Notification Context | SMS, push notification, email, alert | System / Customer | User notifications and messaging |

---

## Context Integration Styles

### Order Context ↔ Payment Context
- Integration Style: **Synchronous API**
- Reason:
The Order service needs an immediate payment confirmation before finalizing an order.

---

### Order Context ↔ Notification Context
- Integration Style: **Asynchronous Event**
- Reason:
Notifications do not need to block checkout. Events improve responsiveness.

---

### Delivery Context ↔ Order Context
- Integration Style: **Asynchronous Event**
- Reason:
Delivery updates are eventually consistent and can be processed independently.

---

### Restaurant Context ↔ Order Context
- Integration Style: **Synchronous API**
- Reason:
The system must verify menu availability before confirming an order.

---

## Conway’s Law

Conway’s Law states that system architecture tends to reflect the communication structure of the organization.

If CityBite keeps a single team responsible for all contexts, the architecture will likely remain a tightly coupled monolith.  
Changes in one area (for example payments) may impact unrelated parts such as notifications or delivery.

This creates:
- Slower deployments
- Increased coordination overhead
- Higher risk of regressions

By separating teams around bounded contexts, CityBite can improve flexibility and allow services to evolve independently.