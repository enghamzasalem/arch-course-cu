# Task 1.1 - Bounded context map

## Contexts

### 1. Orders
- **Ubiquitous language:** order, cart, line item, status (placed / preparing / ready / delivered), customer
- **Primary user:** customer (placing orders), restaurant staff (accepting and preparing)
- **Owns:** the Order API, order lifecycle rules, cart and order data, what "an order" means

### 2. Dispatch
- **Ubiquitous language:** courier, route, ETA, pickup, drop-off, assignment
- **Primary user:** dispatch operator, courier on the road
- **Owns:** courier assignment logic, ETA calculation, route data, integration with the Maps / routing API

### 3. Payments
- **Ubiquitous language:** charge, authorization, capture, refund, payment method
- **Primary user:** customer (at checkout), finance team
- **Owns:** charge state, refund rules and state, integration with the external payment gateway, idempotency of money operations

### 4. Notifications
- **Ubiquitous language:** message, channel (SMS / push / email), template, delivery receipt
- **Primary user:** customer and restaurant staff (receivers), product team (templates)
- **Owns:** templates, sending logic, integration with the SMS / push provider, delivery status

## Integration between pairs

| Pair | Style | Why |
|-|-|-|
| Orders - Dispatch | async event | Dispatch reacts to "order ready for pickup" events. Orders should not wait for a courier to be assigned to confirm the order. |
| Orders - Payments | sync API | At checkout Orders calls Payments to request authorization and stores only the payment decision and reference. Payment state itself stays in Payments. |
| Orders - Notifications | async event | When order status changes, an event is emitted and Notifications sends the message. Orders should not block on SMS delivery. |
| Dispatch - Payments | no direct link | Dispatch does not talk to Payments. Orders may request a refund, but Payments owns refund rules and state. |
| Dispatch - Notifications | async event | "Courier on the way" or "delivered" events trigger messages to the customer. |
| Payments - Notifications | async event | Payment success or failure emits an event; Notifications sends receipts or failure messages. |

## Conway's Law - one team for everything

If a single team owns all four contexts, Conway's Law says the architecture will copy the team's communication structure: one team, one informal way of talking, and so one big shared codebase with one database. We would predict a monolith (or worse, a distributed monolith if someone tries to split it without splitting the team), because there is no organizational pressure to keep the contexts separate. People will reach across boundaries, share tables to "save time", and the bounded contexts will exist on paper but not in the code.