# Part 2: Quality Attributes

**System**: Smart Home Management System

## 1. Quality Attributes Analysis

### 1. Security
- **Definition**: The ability of the system to prevent unauthorized access while providing access to legitimate users. (External, Dynamic)
- **Importance**: Smart homes contain highly sensitive data (camera feeds, physical access controls like door locks). A security breach could lead to physical harm or severe privacy violations.
- **Architectural Support**: The API Gateway acts as a single point of entry, enforcing authentication and TLS encryption. The Security Service isolates critical monitoring logic.
- **Trade-offs**: Implementing strict security (e.g., multifactor authentication, encrypted payloads) introduces slight latency and increases development/operational complexity.

### 2. Performance (Latency)
- **Definition**: The system's ability to respond to events or user commands within a given time constraint. (External, Dynamic)
- **Importance**: Users expect instantaneous reactions when controlling physical devices (turning on a light). High latency leads to a poor user experience.
- **Architectural Support**: Asynchronous messaging (MQTT) ensures rapid delivery of IoT telemetry. The API Gateway and Microservices are decoupling heavy processing from immediate request acknowledgment.
- **Trade-offs**: Bypassing heavy synchronous database writes for faster message queues risks theoretical event loss if the broker crashes before persistence, trading durability for speed.

### 3. Availability
- **Definition**: The proportion of time the system is functional and reachable by users. (External, Dynamic)
- **Importance**: Homeowners rely on the system for critical functions like security monitoring and heating. Downtime renders the smart home "dumb" and potentially unsafe.
- **Architectural Support**: The microservices architecture allows instances of services (like the Device Manager) to be replicated. If one instance fails, others continue serving requests.
- **Trade-offs**: High availability requires deploying redundant infrastructure (multiple servers, database replication), which significantly increases hosting and maintenance costs.

### 4. Scalability
- **Definition**: The ability of the system to handle increasing loads (more users or more devices) without performance degradation. (External, Dynamic)
- **Importance**: A homeowner may start with 5 devices and grow to 50. The central backend may need to manage thousands of homes.
- **Architectural Support**: Microservices allow specific bottlenecks (e.g., the Device Manager handling high device telemetry) to scale independently via load balancers, without scaling the entire system.
- **Trade-offs**: Designing for horizontal scalability requires complex state management (stateless services, distributed caching like Redis) rather than simple in-memory session tracking.

### 5. Modifiability
- **Definition**: The ease with which the system can be adapted to changing requirements or new features without introducing defects. (Internal, Static)
- **Importance**: IoT standards frequently change, and new types of smart devices are constantly entering the market. The system must adapt quickly.
- **Architectural Support**: Microservices enforce strict boundaries. An update to support a new protocol in the Device Manager can be deployed without altering the Security Service.
- **Trade-offs**: Modifiability often conflicts with performance. Abstraction layers and network calls between services (instead of direct function calls in a monolith) add processing overhead.

---

## 2. Quality Attribute Priority Matrix

| Quality Attribute | Priority Level | Competes / Conflicts With | Resolution Strategy |
| :--- | :--- | :--- | :--- |
| **Security** | Critical (1) | Performance, Modifiability | **Security takes precedence**. Added latency from encryption is accepted. Isolated the Security Service to minimize modifiability risks. |
| **Availability** | Critical (2) | Cost, Modifiability | High Availability is guaranteed for core functions (auth, locks) but relaxed for non-critical analytics to balance cost. |
| **Performance** | High (3) | Security, Data Durability | Used Redis cache and MQTT for fast reads/writes, occasionally risking slight eventual consistency in DB records to ensure low latency commands. |
| **Scalability** | Medium (4) | Simplicity, Performance | Accepted the overhead of microservices to allow future scaling, but prioritized direct fast paths for immediate performance. |
| **Modifiability** | Medium (5) | Performance, Availability | Enforced through API contracts and microservice boundaries. Changes are isolated to avoid bringing down the available system. |

### Balancing Competing Attributes

The most frequent conflict in this architecture is **Security vs. Performance**. Encryption and token validation inherently take time. To balance this, the architecture localizes the heavy lifting of security (e.g., JWT validation) to the API Gateway at the edge. Once a request enters the trusted internal network, inter-service communication uses faster, lightweight protocols (like gRPC) with mutual TLS, ensuring security is maintained without unnecessarily crippling internal performance.
