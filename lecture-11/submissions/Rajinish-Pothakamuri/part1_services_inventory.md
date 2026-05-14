### Part 1: Services Inventory

**Task 1.1: Components vs. Services Inventory**

**1. Inventory Table**
The following table delineates the architectural boundaries of the CityBite platform. It distinguishes between internally operated components and externally managed services, detailing their respective integration connectors and primary availability risks.

| Name | Component or External Service | Who Operates | Connector | Main Risk if Unavailable |
| :--- | :--- | :--- | :--- | :--- |
| Order Application Programming Interface | Component | CityBite Operations | HTTPS | Customers are entirely unable to load menus or place orders, resulting in a total user-facing system outage. |
| Notification Worker | Component | CityBite Operations | Message Queue | Dispatch personnel and restaurant partners cease receiving asynchronous order updates, causing degraded operational efficiency. |
| Managed PostgreSQL Database | Component | Cloud Provider | TCP | The application state freezes completely, preventing all data read and write operations and causing a critical system failure. |
| Payment Gateway Software as a Service | External Service | Third-Party Vendor | HTTPS | [Requires Formal Service Level Agreement and Exit Plan] Customers cannot complete financial transactions, leading to direct, immediate revenue loss and checkout abandonment. |
| Maps and Routing Application Programming Interface | External Service | Third-Party Vendor | HTTPS | [Requires Formal Service Level Agreement and Exit Plan] Dispatch systems cannot calculate delivery estimates or route drivers, severely disrupting logistical operations and delivery timelines. |
| Short Message Service and Push Provider | External Service | Third-Party Vendor | HTTPS | Customers remain uninformed regarding their order status, significantly increasing the burden on customer support channels. |

**2. The Product Risk of External Services**
The reliance on external Application Programming Interfaces introduces significant product and business risks that extend beyond conventional Information Technology challenges. When CityBite integrates a third-party service, the organization inherently relinquishes control over the operational lifecycle and availability of that component to an external entity. End-users do not differentiate between internal infrastructure failures and third-party service outages; an unavailable payment gateway is perceived strictly as a CityBite application failure, which directly impacts revenue and erodes brand reputation. Consequently, because the internal engineering team lacks the direct access required to resolve external outages, product managers must proactively design user experiences that gracefully handle these failures through fallback mechanisms. This emphasizes the absolute necessity of robust service level agreements and comprehensive exit plans.