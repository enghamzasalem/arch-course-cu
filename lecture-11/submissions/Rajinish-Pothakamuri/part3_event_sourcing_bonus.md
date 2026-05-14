### Part 3: Replication and Optional Event Log

**Task 3.3: Event Sourcing (Bonus)**

**1. Bounded Context: Order Lifecycle Management**
In the CityBite architecture, managing the state of a customer order is a highly critical workflow that benefits significantly from the application of an event sourcing pattern. Instead of persistently overwriting a single database row to reflect the current status of an order, the system records every state transition as a discrete, immutable fact within an append-only event log. 

**2. Events List**
The lifecycle of a single order generates a chronological sequence of persistent events. For a standard delivery workflow, the underlying event log records the following entries:
*   OrderPlaced: Captures the initial cart contents, customer identifier, geographic coordinates, and initialization timestamp.
*   PaymentAuthorized: Confirms the external payment gateway successfully processed and secured the financial transaction.
*   OrderAccepted: Indicates the restaurant partner has acknowledged the request and commenced food preparation operations.
*   CourierAssigned: Logs the routing mechanism allocating a specific delivery driver to the order.
*   OrderPickedUp: Records the courier physically collecting the prepared items from the restaurant premises.
*   OrderDelivered: Confirms the final handover of the items to the end customer.

**3. System Recovery and Bug Replay**
The primary architectural advantage of utilizing an append-only log is demonstrated during system recovery following the introduction of a software defect. Consider a scenario where a flawed application update introduces a logical bug into the dispatch dashboard read model, causing it to prematurely flag active orders as delivered. This defect effectively hides ongoing deliveries from dispatch operators. In a traditional state-based database configuration, this destructive overwrite would result in severe data corruption, requiring complicated and partial database restorations from backups.

Because event sourcing guarantees that historical events remain immutable, the underlying transactional truth is completely preserved. Once the engineering team identifies and rectifies the software defect, operators can simply discard the corrupted read model. By programmatically replaying the entire event log from the origin state through the corrected application logic, the system sequentially rebuilds the true present state of all active orders. This deterministic replay mechanism ensures zero operational data loss and provides a provable recovery process. Additionally, this pattern inherently provides a strict audit trail, allowing analysts to accurately determine the exact chronological sequence of operations for dispute resolution or logistical performance auditing.