# Part 1.1 — Components vs Services Inventory

## Services & Components Map

| # | Name | Component or External Service | Who Operates | Connector | Main Risk if Unavailable |
|---|------|-------------------------------|--------------|-----------|--------------------------|
| 1 | Order API | **Component** | CityBite engineering | Internal (K8s pod-to-pod HTTP) | No orders can be placed or tracked |
| 2 | Postgres (managed) | **Component** (managed) | Cloud provider (e.g. AWS RDS) | TCP / connection pool | All order reads/writes fail; checkout is impossible |
| 3 | Payment Gateway | **External Service** (**formal SLA** or exit plan must be applied) | Third-party SaaS (e.g. Stripe) | HTTPS REST | Customers cannot pay; revenue stops immediately |
| 4 | Maps / Routing API | **External Service** (**formal SLA** or exit plan must be applied) | Third-party SaaS (e.g. Google Maps) | HTTPS REST | ETA estimates and dispatch routing unavailable |
| 5 | SMS / Push Provider | **External Service** | Third-party SaaS (e.g. Twilio) | HTTPS REST | Order status notifications not delivered to customers |
| 6 | CDN / Object Storage | **Component** (managed) | Cloud provider (e.g. S3 + CloudFront) | HTTPS | Restaurant menu images and static assets fail to load |
| 7 | Dispatch Worker | **Component** | CityBite engineering | Internal queue (K8s worker) | Orders accepted but never assigned to a courier |
| 8 | Restaurant Portal API | **Component** | CityBite engineering | Internal HTTPS | Restaurants cannot mark orders ready or update menus |


---

## Two Dependencies Requiring a Formal SLA or Exit Plan

### 1. Payment Gateway (e.g. Stripe)
This is the single most critical external dependency. Without it, CityBite cannot collect revenue. We require:
- A contractual **SLA of ≥ 99.95% monthly uptime** with financial penalties for breach.
- An **exit plan**: maintain a secondary payment processor (e.g. Adyen or Braintree) behind the same internal `PaymentPort` interface, switchable via a feature flag. If the primary vendor is acquired, raises prices unilaterally, or suffers repeated outages, we can cut over within hours rather than weeks.

### 2. Maps / Routing API (e.g. Google Maps Platform)
Dispatch routing and ETA display depend on this API. We require:
- A contractual SLA or a documented fallback to an alternative provider (e.g. HERE Maps, OpenRouteService).
- An **exit plan**: abstract the routing call behind a `RoutingPort` interface so the provider can be swapped. Cache the last-known ETA for active orders so a short outage degrades gracefully rather than breaking dispatch entirely.

---

## Why External API Availability Is a Product Risk, Not Just an IT Risk

When CityBite's checkout page shows "Payment failed — please try again" because the payment gateway is timing out, the customer does not know or care that the fault lies with a third-party vendor. From their perspective, **CityBite is broken**. They abandon the order, leave a negative review, and may switch to a competitor. The same logic applies to the maps API: a courier who receives no routing update is late, the customer is frustrated, and the restaurant's reputation suffers alongside CityBite's. External API outages therefore translate directly into lost revenue, customer churn, and brand damage — outcomes that belong to the product and business, not to the IT incident log. This is why availability of external dependencies must be tracked with the same SLOs and error budgets as internal components, and why contractual SLAs and architectural fallbacks are product decisions, not optional engineering niceties.
