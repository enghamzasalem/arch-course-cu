### Part 1: Contexts & Conway

#### 1.1 Bounded Context Map

To successfully decouple CityBite and evolve it into a flexible architecture, we must align our services with business capabilities rather than technical layers (e.g., avoiding generic "DAO services"). Below are four proposed bounded contexts for CityBite.

**1. Ordering Context**
*   **Ubiquitous Language:** Cart, Checkout, Coupon, Order Total, Payment Status.
*   **Primary User:** Customer (via mobile application).
*   **Owns:** Customer shopping sessions, cart management, pricing calculations, and order placement behavior.

**2. Kitchen Context**
*   **Ubiquitous Language:** Kitchen Board, Prep Time, Mark Ready, Menu Item, Active Orders.
*   **Primary User:** Restaurant Partner (via tablet application).
*   **Owns:** Restaurant menu catalogs, kitchen order acceptance, and meal preparation status.

**3. Dispatch Context**
*   **Ubiquitous Language:** Rider, Assignment, ETA, Map Route, Location Ping.
*   **Primary User:** Dispatcher / Delivery Rider.
*   **Owns:** Rider geographic tracking, delivery routing, and matching ready orders to available riders.

**4. Notifications Context**
*   **Ubiquitous Language:** SMS, Push Notification, Email Receipt, Template, Delivery Status.
*   **Primary User:** Internal System (triggered by other contexts to alert humans).
*   **Owns:** Outbound messaging integrations, user communication preferences, and notification delivery states.

---

#### Inter-Context Integration Styles

When these bounded contexts interact, their integration style must balance data consistency with system availability and flexibility. 

*   **Ordering ↔ Kitchen:** `Async Event` 
    *   **Why:** When a customer places an order, the Ordering context publishes an "Order Placed" event. This prevents a temporary network drop to the restaurant's tablet from blocking the customer's checkout process, trading immediate strong consistency for high availability.
*   **Kitchen ↔ Dispatch:** `Async Event`
    *   **Why:** When a restaurant hits "Mark Ready" on their kitchen board, an event is emitted so Dispatch can begin a rider assignment. The kitchen staff does not need to wait synchronously for a rider to be found before clearing their screen.
*   **Dispatch ↔ Ordering:** `Sync API`
    *   **Why:** When a hungry customer opens their app to track their active delivery, the Ordering context acts as a gateway and makes a synchronous API call to Dispatch to fetch the real-time ETA and map coordinates. This is a read-heavy query where the user is actively waiting for an immediate result.
*   **Any Context ↔ Notifications:** `Async Event` / `Message Queue`
    *   **Why:** Sending SMS or emails involves slow, outbound I/O to third-party vendors. Placing these tasks on an async queue decouples the user's latency from external network speeds and prevents retry storms from breaking the primary APIs.

---

#### Conway's Law & Single-Team Monoliths

Conway’s Law dictates that any organization designing a system will inevitably produce a design whose structure mirrors the organization's own communication lines. If CityBite attempts to build all four of the bounded contexts listed above using only a **single, unified engineering team**, I predict the resulting architecture will inevitably degrade back into a **monolithic architecture** or a tightly coupled "distributed monolith". Without strict team boundaries enforcing isolation, developers working under tight deadlines will bypass proper API contracts in favor of convenient shortcuts, such as reach-around imports, sharing database tables, or making chatty synchronous function calls. True architectural autonomy and flexibility require the "Reverse Conway Maneuver," where teams are intentionally split into autonomous units (e.g., two-pizza teams) explicitly assigned to individual bounded contexts.