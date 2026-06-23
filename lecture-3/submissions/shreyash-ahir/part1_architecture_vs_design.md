**Task 1.2: Architecture vs. Design Documentation**

**Architectural Decisions (Strategic, System-wide)**

1.  **Selection of a Cloud-Based Foundation:**

- **Decision:** The system shall be deployed on to the Cloud Platform instead of making on physical on site hardware.
- **Rationale:** The reason behind this decision because to provide the flexible foundation which can support the elasticity, because when number of user increase the platform can scale without having to develop the hardware or the OS.
- **Alternatives:** The alternative of this decision is physical on site hardware or developing there’s own hardware or instruction sets.
- **Consequences:** This type of systems can dependent on to the service provider. And due to that if they were alter their policies and prices can affect the viability.

1.  **Adoption of a Layered Architecture:**

- **Decision:** This System is implement on a ‘Layer Cake’ Architecture.
- **Rationale:** The reason behind this to make things less complicated by hiding hardware details and making sure that each layers can interacts with its below one’s.
- **Alternatives:** A Closed System or the flat architecture in that all the components have direct access to each other.
- **Consequences:** It can restricts that part which can communicate with other part of the systems. Which can create a stable and organized system but it might cause a slightly decrease in performance because the data has to pass through different layers.

1.  **High-Availability Redundancy Strategy:**

- **Decision:** Adoption of a Five Nines (99.999%) Availability Model with Redundant Active-Active Nodes.
- **Rationale:** The idea here is to ensure that the system is available for use for a maximum of five minutes a year, thereby fulfilling stringent Service Level Agreements (SLAs).
- **Alternatives:** Active-passive failover solutions, which involve a higher downtime period, and a single node solution.
- **Consequences:** This increases the cost as well as the complexity of the system, thereby requiring sophisticated automated fault detection and recovery solutions (MTTR).

1.  **Definition of an ‘Open System’ Boundary:**

- **Decision:** Design the system with the public APIs so that other developers can connect and built on it.
- **Rationale:** The reason behind that is the Morden systems cannot work alone they need to connect with the other different systems to provide the best result or the value.
- **Alternatives:** The other alternative is keep the system close it means that no data can be communicate with the other outside systems.
- **Consequences:** The system will be open to external changes which introduced by other outside developer beyond the control of the system designers.

1.  **Prioritization of Security over Ease of Use:**

- **Decision:** Mandate Multi-Factor Authentication (MFA) and implement end-to-end encryption for all data interactions.
- **Rationale:** To ensure confidentiality and integrity, thereby safeguarding the system against intentional hostile attacks.
- **Alternatives:** Utilization of simple password-only authentication to enhance initial user learnability.
- **Consequences:** Potential adverse effects on usability metrics, including efficiency and user satisfaction, for expert users.

**Design Decisions (Tactical, Component-level)**

1.  **Implementation of a Read-Through Cache:**

- **Decision:** Implement a distributed Hash Map-based cache for storing frequently accessed user profiles.
- **Rationale:** This design pattern intends to improve system performance by reducing database latency for read operations.
- **Design Pattern:** Proxy / Cache.
- **Scope:** Component level - Data Access Layer.

1.  **Automated Error Reporting Logic:**

- **Decision:** Implement an automated crash report bot, which is intended to send stack trace and memory dump information to developers.
- **Rationale:** The rationale is to improve serviceability and supportability by providing context information for intermittent, hard-to-debug problems, such as the class of problems known as "Heisenbugs," without depending on the users themselves.
- **Design Pattern:** Observer.
- **Scope:** Global Class (Exception Handling Service).

1.  **Standardized Naming Conventions:**

- **Decision:** Implement a strict camelCase naming standard for all methods and variables across the project.
- **Rationale:** Adoption of a naming standard will improve the design's consistency, clarity, and hence ease of understanding for new developers.
- **Design Pattern:** N/A (Coding Standard).
- **Scope:** Method level, Class level.

1.  **Encapsulation of File Operations:**

- **Decision:** Hide the complexity of internal file systems by providing a simple interface for open, read, and write operations.
- **Rationale:** This approach encourages simplicity and hides the complex internal details of the operating system from programs.
- **Design Pattern:** Facade.
- **Scope:** Component boundary.

1.  **Robust Input Validation with Undo:**

- **Decision:** Implement a command-based history system for all data editing operations.
- **Rationale:** This approach is more robust because users can recover from unintended erroneous inputs.
- **Design Pattern:** Command / Memento.
- **Scope:** Method level (User Interface Controllers).