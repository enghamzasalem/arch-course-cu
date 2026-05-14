# Part 1: Services Map & SLOs
## Task 1.1 — Components vs Services Inventory

**Assignment:** Software Architecture — Lecture 11 (Availability and Services)  
**Product:** CityBite (food-delivery platform)  
**Baseline:** Kubernetes + Postgres (Lecture 9), scaled read models (Lecture 10)

---

## 1.1.1 Inventory Table

| # | Name | Type | Operated By | Connector | Main Risk if Unavailable |
|---|------|------|-------------|-----------|--------------------------|
| 1 | **Order API** (K8s Deployment) | Component | CityBite engineering | Internal HTTP / K8s Service | No orders can be placed or updated; entire customer flow breaks |
| 2 | **Postgres (managed)** | Component | CityBite via cloud provider (e.g., AWS RDS / Supabase) | TCP / `psycopg2` connection pool | Order state lost, no reads or writes; all downstream workers stall |
| 3 | **Dispatch Worker** (K8s worker pods) | Component | CityBite engineering | Internal queue (Redis Streams / SQS) | Driver assignment freezes; orders pile up in "pending" indefinitely |
| 4 | **CDN / Object Storage** (menus, images) | Component | CityBite via cloud provider (e.g., CloudFront + S3) | HTTPS | Restaurant menus and item images unavailable; degraded browsing, reduced conversion |
| 5 | **Payment Gateway** ⚠️ | External Service | Third-party SaaS (e.g., Stripe / Adyen) | HTTPS REST | Checkout fails entirely; no revenue; cannot complete any paid order |
| 6 | **Maps / Routing API** ⚠️ | External Service | Third-party SaaS (e.g., Google Maps Platform) | HTTPS REST | ETA estimates broken; dispatch routing fails or falls back to straight-line guesses |
| 7 | **SMS / Push Notification Provider** | External Service | Third-party SaaS (e.g., Twilio / FCM) | HTTPS REST | Customers and drivers receive no status updates; support load spikes; no silent order failures, but UX degrades severely |
| 8 | **Identity / Auth Provider** | External Service | Third-party SaaS (e.g., Auth0 / Cognito) | HTTPS / OIDC | Login and token validation fail; users cannot authenticate; entire platform effectively inaccessible |

> **⚠️ SLA / Exit Plan Required** — rows 5 and 6 are flagged in Section 1.1.2 below.

---

## 1.1.2 Dependencies Requiring a Formal SLA or Exit Plan

### Dependency 1 — Payment Gateway (e.g., Stripe / Adyen)

The payment gateway sits on the **critical checkout path**. Every completed order requires a successful charge authorization. An outage here means zero revenue, not degraded revenue. CityBite must therefore:

- Hold a **signed SLA** guaranteeing at minimum 99.95 % monthly uptime with defined response-time targets for authorization endpoints (target: < 500 ms p99).
- Maintain a **secondary payment processor** (e.g., Adyen as fallback to Stripe) with routing logic in the Order API that can switch providers with no customer-visible change.
- Define an **exit plan** covering: data portability of stored payment methods (tokenization portability), notice period for contract termination, and a 30-day parallel-run window when migrating processors.

Vendor bankruptcy scenario: if the processor enters insolvency, PCI-DSS token vaults may be frozen. The exit plan must include pre-agreed escrow or migration of tokenized card data to an alternative vault before shutdown.

### Dependency 2 — Maps / Routing API (e.g., Google Maps Platform)

The routing API determines driver dispatch order, ETA windows shown to customers, and zone-based surge pricing inputs. A breaking API change (e.g., deprecation of a route-matrix endpoint) or a quota suspension due to billing anomaly would silently corrupt dispatch logic — potentially worse than a clean outage, because pods would stay "green" while returning stale or incorrect ETAs.

CityBite must therefore:

- Hold a **quota SLA** (guaranteed request budget per second, not just uptime) with alert thresholds at 80 % quota consumption.
- Maintain a **fallback routing library** (e.g., OpenRouteService on self-hosted OSRM) that activates automatically when the primary API returns 429 or 5xx for more than 30 consecutive seconds.
- Define a **breaking-change exit plan**: pin to a versioned API endpoint, subscribe to deprecation notices, and allocate a 90-day migration sprint in the roadmap backlog when a major version is sunset.

---

## 1.1.3 Why External API Availability Is a Product Risk, Not Only an IT Risk

When CityBite's Order API returns HTTP 503, the engineering team knows immediately: dashboards fire, on-call gets paged, and the incident timeline begins. When Stripe's authorization endpoint silently degrades to 8-second response times, the symptom surfaces only as a spike in cart abandonment — a metric owned by the product and growth teams, not the infrastructure team. This is the central reason external API availability must be treated as a **product risk**.

Customers do not distinguish between "our servers are down" and "our payment provider is slow." They experience a broken checkout, leave, and may not return. Because CityBite's revenue model is entirely transactional (no subscription buffer), every degraded minute on the payment or routing API translates directly to lost gross merchandise value — a number that appears in quarterly reporting, not just in the ops postmortem. Similarly, a maps API vendor that introduces breaking changes with short notice forces a reactive engineering sprint that displaces roadmap work, delays feature launches, and erodes trust with restaurant and driver partners who depend on accurate ETAs for their own scheduling.

Product leadership must therefore co-own vendor SLA negotiations, monitor third-party error rates as part of the same observability stack that monitors internal services, and treat "vendor goes down" scenarios in the same business-continuity planning that covers datacenter failures. Resilience mechanisms — circuit breakers, fallback providers, graceful degradation — are product decisions about user experience, not purely infrastructure decisions about uptime percentages.

---
