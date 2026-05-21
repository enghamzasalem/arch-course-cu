# Part 1.1: Services Inventory

| Name | Component/External Service | Who Operates | Connector | Main Risk if Unavailable |
|---|---|---|---|---|
| Order API Deployment | Component | CityBite | HTTPS (Ingress) | Users cannot place orders. |
| Background Workers | Component | CityBite | Message Queue | Orders accepted but not processed. |
| Managed Postgres | External Service | Cloud Provider | TCP | Total system failure (cannot read/write). |
| Payment Gateway SaaS | External Service | Vendor (e.g. Stripe) | HTTPS API | Checkout fails; retry storms. |
| Maps/Routing API | External Service | Vendor (e.g. Google) | HTTPS API | Delayed/failed driver dispatch. |
| SMS/Push Provider | External Service | Vendor (e.g. Twilio) | HTTPS API | Customers miss notifications. |

**Dependencies with Formal SLAs:**
1. **Payment Gateway SaaS:** Directly tied to revenue; downtime severely impacts the business. Needs strong uptime SLA.
2. **Maps/Routing API:** Critical for operations; dispatch relies on routing.

**Why Availability of External APIs is a Product Risk:**
When an external API (like a payment gateway) goes down, customers experience the failure on CityBite's platform. They do not blame the third party; they blame CityBite. Therefore, relying on external APIs without safeguards translates external downtime directly into CityBite's product unreliability.
