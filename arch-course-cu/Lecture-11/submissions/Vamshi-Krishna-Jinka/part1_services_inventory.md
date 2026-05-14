# Part 1: Services Map & SLOs
## Task 1.1: Components vs Services Inventory

## 1. Overview
CityBite depends on both systems it operates itself and external services operated by other companies. Availability design must treat these differently because CityBite can directly fix or scale its own components, but it can only limit the damage from remote service failures through timeouts, retries, circuit breakers, and fallback behavior.

---

## 2. Components vs External Services Inventory

| Name | Component or External Service | Who Operates It | Connector | Main Risk if Unavailable |
|---|---|---|---|---|
| Order API | Component | CityBite | HTTPS / REST | Customers cannot place orders or view live order status |
| Worker Service | Component | CityBite | Queue / async jobs | Notifications, dispatch updates, and background tasks stop |
| PostgreSQL | Component / managed data service | CityBite or cloud provider, depending on deployment | SQL / TCP | Orders may fail, checkout may time out, and data consistency is affected |
| CDN / Object Storage | External or managed service | Cloud provider | HTTPS | Menu images and assets load slowly or not at all |
| Payment Gateway | External service | Third-party vendor | HTTPS | Checkout cannot be completed; retry storms may hurt availability |
| Maps / Routing API | External service | Third-party vendor | HTTPS | Delivery ETA, routing, or courier assignment may degrade |
| SMS / Push Provider | External service | Third-party vendor | HTTPS / webhook | Customers may not receive order confirmations or delivery alerts |
| Identity / Auth Provider | External service | Third-party vendor or platform service | HTTPS / OIDC | Login and account access may fail |

---

## 3. Dependencies that need a formal SLA or exit plan

### Payment Gateway
CityBite should insist on a formal SLA and a tested exit plan for the payment gateway. This dependency sits on the critical checkout path, so an outage or breaking API can directly stop revenue. If the vendor becomes unreliable, changes the contract, or increases cost unexpectedly, CityBite must have a fallback path or a replacement provider ready.

### Maps / Routing API
CityBite should also require an SLA and exit plan for the maps or routing API. Even if order placement still works, delivery operations and ETA accuracy can suffer badly when this service fails. Since routing failures can impact customer trust and dispatch efficiency, CityBite should be able to switch providers or degrade gracefully with cached or simplified routing logic.

---

## 4. Why external API availability is also a product risk

External API availability is a product risk because customers experience one combined service, not separate technical systems. If the payment gateway is down, the user does not care that the failure happened outside CityBite; they only see that checkout failed. If the maps API is slow, delivery estimates become unreliable and the product feels broken even when the Order API is healthy. For that reason, product, operations, and engineering should treat partner availability as part of the user experience and revenue model, not only as an infrastructure issue.

---

## 5. Summary
CityBite owns the core customer experience, but several important dependencies are external. The most critical external services are payment and routing, so they need formal SLAs, failure handling, and exit plans. Availability work should focus not only on CityBite's own pods, but also on the trust boundaries where third-party failures can affect the product.
