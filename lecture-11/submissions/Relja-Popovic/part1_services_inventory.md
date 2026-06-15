## Task 1.1: Components vs Services Inventory

| Name | Type | Who operates | Connector | Main risk if unavailable | Fromal SLA required? |
|---|---|---|---|---|---|
| Order API | Component | CityBite | Internal (K8s pod) | Customers cannot place orders | No |
| PostgreSQL primary | Component | CityBite (managed) | TCP / connection pool | All order reads and writes fail | No |
| Notification worker | Component | CityBite | Internal queue | Order confirmations not delivered | No |
| Payment gateway ⭐ | External service | Third-party SaaS | HTTPS | Checkout cannot be completed; revenue stops | Yes |
| Maps / routing API ⭐ | External service | Third-party SaaS | HTTPS | Delivery ETAs unavailable; dispatch cannot assign riders | Yes |
| SMS / push provider | External service | Third-party SaaS | HTTPS | Customers and restaurants receive no notifications | No |


**Payment gateway** and **maps/routing API** are marked because their unavailability directly blocks core revenue flows. A payment gateway outage makes checkout impossible regardless of CityBite's own uptime. A maps API outage disables dispatch, meaning orders are placed but cannot be routed to riders. Both vendors should provide a contractual SLA so that if there is downtime, CityBite does not suffer. If they cannot provide a contractual SLA, CityBite needs a fallback vendor ready to switch to.

### Why External API Availability Is a Product Risk, Not Only an IT Risk

When a third-party API goes down, customers experience it as CityBite being broken. They do not know or care which vendor caused the failure. A payment gateway outage during a dinner rush means lost orders and lost revenue that cannot be recovered. A maps API outage means restaurants receive orders with no rider assigned, leading to cancellations and customer complaints that damage CityBite's brand. These failures appear in app store reviews, social media, and support ticket queues as CityBite failures, affecting retention and trust. Availability of external APIs is therefore a product and business continuity concern that belongs in vendor selection, contract negotiation, and product incident response - not only in an engineering backlog.