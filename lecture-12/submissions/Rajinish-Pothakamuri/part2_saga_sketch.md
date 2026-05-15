### Part 2.3: Saga Sketch

**1. Selected Business Journey: Place Paid Order**
In a microservices architecture, maintaining data consistency across independent services requires abandoning traditional distributed two-phase commits across arbitrary software-as-a-service boundaries. To handle the "Place Paid Order" cross-context workflow, the architecture will implement the Saga pattern. A saga is a sequence of local transactions where each step updates data within a single service; if a local transaction fails, the saga executes compensating transactions to semantically undo or repair the preceding steps and restore a consistent system state.

**2. Local Steps and Compensating Actions**
The workflow executes the following local steps sequentially, with predefined compensating actions ready if a downstream failure occurs:

*   **Step 1: Ordering Context**
    *   **Local Action:** The Ordering service receives the checkout request and persists a new order record with a "Pending" status in its local database. 
    *   **Compensating Action:** If any subsequent step fails, the Ordering service executes a compensating transaction to update the order status to "Cancelled" and alerts the customer.
*   **Step 2: Payment Context**
    *   **Local Action:** The Payment service interfaces with the external payment gateway to authorize and capture the required funds from the customer's account.
    *   **Compensating Action:** If the kitchen validation step fails (e.g., the restaurant closes unexpectedly), the Payment service executes a compensating transaction to automatically issue a full refund to the customer and cancel the hold.
*   **Step 3: Kitchen Context**
    *   **Local Action:** The Kitchen service validates the current restaurant inventory and capacity, then generates a preparation ticket for the kitchen staff.
    *   **Compensating Action:** If a severe internal error or immediate dispatch failure occurs, the Kitchen service cancels the preparation ticket and removes it from the restaurant's operational board to prevent food waste.

**3. Coordination Choice: Orchestration**
To manage the distributed transaction across the CityBite platform, this architecture will utilize the **Orchestration** approach rather than Choreography. 

*   **Pro 1:** Orchestration utilizes a central workflow engine that actively drives the discrete execution steps, which significantly aids operational visibility and monitoring for complex, long-running, human-in-the-loop flows.
*   **Pro 2:** It simplifies the design of participating services (such as the Payment or Kitchen services), as they only need to respond to direct commands and do not need to understand the broader domain events or the overall checkout state machine.
*   **Con 1:** The primary drawback of orchestration is that the central workflow engine can inadvertently become a highly coupled "central brain" or bottleneck, which can slowly degrade team autonomy and recreate a monolithic coordination layer.