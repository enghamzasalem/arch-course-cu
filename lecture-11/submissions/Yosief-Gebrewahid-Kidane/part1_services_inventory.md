# Part 1 — Components vs Services Inventory (CityBite)

## 1. Overview

CityBite depends on a mix of internally managed platform components and external third-party services. Availability is therefore not only a property of the Kubernetes cluster itself, but also of every upstream and downstream dependency the system relies on.

This section separates what CityBite operates directly from what is provided by external vendors or cloud platforms.

---

## 2. Components and External Services

| Name | Type | Operated By | Connector | Main Risk if Unavailable |
|------|------|-------------|-----------|---------------------------|
| Order API (Kubernetes Deployment) | Internal Component | CityBite Engineering Team | HTTPS / REST | Customers cannot place or track orders |
| Notification Worker | Internal Component | CityBite Engineering Team | Queue (SQS/Kafka) | Delayed SMS, email, or push notifications |
| PostgreSQL Database | Managed Service | Cloud Provider (AWS RDS) | TCP / PostgreSQL protocol | Orders and payments cannot be stored or retrieved |
| Redis Cache | Internal Component | CityBite Engineering Team | TCP | Increased database load and slower dashboards |
| Payment Gateway | External Service | Third-Party Vendor | HTTPS API | Paid checkout fails or becomes unreliable |
| Maps / Routing API | External Service | Third-Party Vendor | HTTPS API | Delivery ETA and driver routing become inaccurate |
| SMS / Push Notification Provider | External Service | Third-Party Vendor | HTTPS API | Customers stop receiving delivery updates |
| CDN / Object Storage | Managed Service | Cloud Provider | HTTPS / Object Storage SDK | Menu images fail to load or upload |

---

## 3. Critical Vendor Dependencies

Some external services are critical enough that CityBite must treat them as part of its availability design, even though they are not operated internally.

### Payment Gateway

The payment gateway is directly tied to revenue generation. If it becomes unavailable or introduces breaking changes, customers will not be able to complete purchases. This is a high-impact business risk. CityBite should negotiate strong SLA guarantees and design fallback strategies such as alternative payment providers or deferred payment flows.

---

### Maps / Routing API

Routing and ETA calculations are core to the delivery experience. If this service fails, deliveries may still occur, but with reduced efficiency and poor customer experience. CityBite should reduce vendor lock-in by introducing an abstraction layer so that alternative providers can be swapped in if necessary.

---

## 4. Why External APIs Are a Product Risk

External dependencies are not just infrastructure concerns—they directly affect user experience and business outcomes.

If the payment gateway fails, customers cannot complete orders, leading to immediate revenue loss. If notification services fail, users may assume their order is lost even when backend processing is correct. If routing APIs are inaccurate, delivery times increase and trust in the platform decreases.

Because these failures are visible to end users, external API availability becomes a **product-level reliability concern**, not just a backend engineering issue.