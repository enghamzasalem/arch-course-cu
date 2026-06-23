# Part 1.1 — Components vs Services Inventory

## Services and Components Table

| Name | Type | Operated by | Connector | Main Risk if Unavailable |
|------|------|------------|-----------|--------------------------|
| Order API | Component | CityBite | HTTPS (internal) | Users cannot place orders |
| Notification Worker | Component | CityBite | Queue | No notifications sent to users |
| PostgreSQL Database | Component | CityBite / Cloud Provider | TCP | Orders cannot be stored or retrieved |
| Object Storage (menu images) | Service | Cloud Provider | HTTPS | Menu images not displayed |
| Payment Gateway | External Service | Third-party (Stripe/PayPal) | HTTPS API | Payments fail → revenue loss |
| Maps / Routing API | External Service | Third-party | HTTPS API | Delivery routing fails |
| SMS / Push Provider | External Service | Third-party | HTTPS API | Users not notified of order status |

---

## Critical Dependencies (SLA Required)

- **Payment Gateway** → Critical for revenue → must have SLA or fallback (pay later / retry later)
- **Maps API** → Critical for delivery → need SLA or backup provider (e.g. fallback routing)

---

## Why External APIs Are a Product Risk

External services such as payment gateways, maps APIs, and notification providers are not under CityBite’s control.  
If one of these services fails, the entire user experience is directly impacted (e.g. users cannot pay or track orders).

This makes availability not only an IT concern, but a **product-level risk**, because:
- It affects revenue (failed payments)
- It impacts customer satisfaction
- It can damage trust in the platform

Therefore, CityBite must design fallback mechanisms and not assume that external services are always available.