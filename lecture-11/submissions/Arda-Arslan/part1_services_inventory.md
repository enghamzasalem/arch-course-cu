# Task 1.1 - Services Inventory

## Components vs services

| Name | Component or external service | Who operates | Connector | Main risk if unavailable |
|-|-|-|-|-|
| Order API | Component | CityBite | HTTPS (Ingress) | Customers cannot place orders, restaurants cannot receive them |
| Background worker | Component | CityBite | Internal queue + HTTPS | Async jobs stop, no data loss but bad UX |
| Managed Postgres | External service (managed) | Cloud provider | TCP connection pool | Full outage, no orders read or written |
| Object storage / CDN | External service (managed) | Cloud provider | HTTPS | Static assets do not load, app looks broken |
| Payment gateway (*) | External service | Third party | HTTPS (REST) | Checkout fails, retry storms can take down our API |
| Maps / routing API (*) | External service | Third party | HTTPS (REST) | Dispatch cannot compute ETAs, delivery breaks |
| SMS / push provider | External service | Third party | HTTPS (REST) | No order confirmations, support load goes up |

(*) marks dependencies where we insist on a formal SLA and an exit plan.

## SLA and exit plan

The payment gateway is the money path. If it goes down or raises fees suddenly, we cannot keep selling, and switching providers is slow because of compliance and integration work.

The maps / routing API is what dispatch runs on. Pricing or API terms can change with little notice, and a sudden break would block deliveries, so we want a fallback provider we could move to in weeks.

## Why availability of external APIs is a product risk

External API availability is not just an IT problem because the user cannot tell who is at fault. If the payment gateway is slow, the customer sees CityBite as broken and abandons the cart. If maps is down, the restaurant blames our app for missing ETAs. Our revenue and brand depend on services we do not run, so the product itself (fallbacks, pay later, cached ETAs, clear errors) has to assume those services will fail.