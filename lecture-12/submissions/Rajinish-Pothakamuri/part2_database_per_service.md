### Part 2.1: Database Per Service Design

The transition from a monolithic architecture to a microservices architecture fundamentally requires the decentralization of data. Independent schema evolution necessitates abandoning shared row-level databases. To achieve genuine team autonomy, each bounded context must completely encapsulate its own data, strictly forbidding cross-context SQL joins. 

#### 1. Logical Datastore Schemas

Below are the proposed independent logical schemas for two distinct bounded contexts within the CityBite architecture.

**Ordering Context Database**
This database acts as the system of record for customer-facing checkout processes and financial totals. 
*   CustomerCarts: Manages active shopping sessions and temporary item reservations.
*   PlacedOrders: Stores the immutable financial record of a confirmed transaction, including total price, customer identifier, and timestamp.
*   OrderLineItems: Details the specific quantities and pricing of items purchased within a given order.

**Kitchen Context Database**
This database manages the operational workflow within the restaurant and the catalog of available offerings.
*   RestaurantMenus: Stores the authoritative catalog of available dishes, descriptions, and current restaurant-level availability.
*   KitchenTickets: Represents the operational workflow of an order sent to the kitchen for preparation.
*   PreparationStatus: Tracks the discrete stages of a ticket (e.g., received, cooking, packaged, ready for handover).

#### 2. The Lost Query and Mitigation Strategy

**The Lost Query:** In the previous monolithic design, a restaurant manager could run a single synchronous SQL JOIN query to generate a comprehensive "Item Profitability and Prep-Time Report." This query would join the `PlacedOrders` and `OrderLineItems` tables (now in the Ordering Context) with the `RestaurantMenus` and `PreparationStatus` tables (now in the Kitchen Context) to correlate the financial revenue of specific menu items with their average kitchen preparation times. By enforcing the database-per-service rule, this cross-table join is no longer physically possible.

**The Replacement Strategy:** To replace this functionality without coupling the databases, we must utilize asynchronous event-driven architecture to build a Command Query Responsibility Segregation (CQRS) Read Model. When an order is finalized, the Ordering context publishes an "Order Finalized" event containing the financial payload. Concurrently, as kitchen staff update their boards, the Kitchen context publishes "Ticket Completed" events containing prep-time metrics. A downstream Analytics Service consumes both of these event streams to project and construct a consolidated, read-optimized database. While this introduces eventual consistency, that means the report may not reflect transactions that occurred mere seconds ago, it successfully preserves the strict isolation and independent deployment lifecycles of the core operational services.

#### 3. RPO and RTO Intuition for Asynchronous Replication

For the Ordering Context, maintaining high availability and rapid write throughput during peak dinner rushes is critical. If the architecture utilizes asynchronous replication to maintain a failover database replica, the primary database will acknowledge a customer's successful checkout before the data is fully duplicated to the standby node. 

Because the replicas lag slightly behind the primary, this architectural choice introduces a non-zero Recovery Point Objective (RPO). In the event of a catastrophic hardware failure on the primary database, any recent orders that were acknowledged to the customer but not yet asynchronously replicated will be permanently lost. The Recovery Time Objective (RTO) i.e., the duration required to restore service availability will depend on the speed of the automated failover mechanisms detecting the primary node failure and promoting the secondary replica to accept new write operations. The business must explicitly accept this small threshold of potential data loss (RPO) as the fundamental trade-off for achieving lower write latency and higher throughput during peak workloads.