# Architectural Pattern Justification

## 1. Pattern Selection: Hybrid Microservices & Event-Driven Architecture 

The system is designed as a collection of  microservices that maintain their own state via the database-per-Service pattern. These services are unified by an event-driven architecture that manages asynchronous communication.

We chose this architecture because the Smart Home Management applications requires avilability, high speed, large-scale IoT data processing and reliability. By using microservices, a failure in a non-critical component (like the Energy Service) does not impact life-safety features (like the Security Service). The Event-Driven architecture allows sensors to "fire and forget" data into the Message Broker, preventing the system from locking up during a massive influx.

The hybrid approach combines:
- The modularity and independence of Microservices
- The decoupling bennefits of event-driven architecture

By giving each service its own database, we eliminate the shared database limitation. If the energy service database becomes locked or corrupted, the security service remains unaffected. This ensures that critical features continue operating even if non-critical components fail.

## 2. How the Architecture Addresses System Requirements

The system requirements are primarily expressed through five key quality attributes: Availability, Security, Scalability, Performance, and Maintainability. The Hybrid Microservices and Event-Driven Architecture directly supports each of these attributes as follows.


### A. Availability 

**System Requirement:**  
Smart home services must be reachable 24/7, especially safety-critical operations such as unlocking doors or disabling gas alarms.

**Architectural Support:**  
- The Microservices Architecture isolates failures.
- If one service (e.g., Energy Monitoring) fails, others (e.g., Security or Door Control) remain operational.

The system avoids total shutdown and ensures continuous access to critical features.


### B. Security 

**System Requirement:**  
The system must protect sensitive data and prevent unauthorized access.

**Architectural Support:** 
- Service boundaries reduce lateral movement during a breach. 
- Direct access to internal services is restricted.
- The Repository Pattern prevents raw database exposure to business logic.

Access control is enforced at a single secure entry point, minimizing attack surface.


### C. Scalability 

**System Requirement:**  
The system must handle growth in:
- Number of devices  
- Sensor traffic  
- Concurrent users  

**Architectural Support:**  
- Microservices allow independent scaling of high-demand services.
- The Event-Driven Architecture buffers bursts of IoT events through the message broker.
 
The system can grow without degrading performance or requiring complete redesign.


### D. Performance 

**System Requirement:**  
Device commands must execute with minimal latency to provide real-time responsiveness.

**Architectural Support:**  
- Event processing improves throughput during peak traffic.
- Asynchronous messaging reduces blocking operations.
 
Users experience near-instant feedback when interacting with smart devices.


### E. Maintainability 

**System Requirement:**  
The system must support frequent updates, new device integrations, and evolving automation rules without breaking existing functionality.

**Architectural Support:**  
- Microservices isolate business domains.
- Database-per-Service prevents cross-service schema dependency.
- Event-Driven Architecture allows new services to subscribe to existing events without modifying current components.

The system can evolve incrementally without large-scale refactoring.


While this introduces increased complexity and operational overhead, it ensures the smart home system remains resilient, secure, and adaptable over time.


## 3. Trade-Offs
We trade the simplicity of a monolithic application for a hyvrid architecture (distributed) system. This indroduced infrastructure complexity and increased costs. However, because of the nature of a smart home management system, reliability triumphs simplicity. This result improved scalability and fault tolerance.

We decided to use the database-per-service to ensure that the system is eventually consistent. For example, after a user renames a device, the Automation Service might briefly see the old name until the update event is issued.

## 4. Alternative patterns considered

- Monolithic Architecture: A unified model where all functional components are bundled into a single application and share a single database.

We rejected it because it fails the maintainability and scalability requirements. A bug in a minor feature like a "Weather Widget" could crash the entire system, including critical security functions. As the system grows to support hundreds of new IoT device types, the monolith becomes too large and "brittle" to update without significant risk.

- Direct Client-Server Architecture: A model where the Mobile App (Client) talks directly to each specific backend service (Server) without an intermediary.

We rejected it because it places too much burden on the Mobile App to manage security, authentication, and multiple connections simultaneously which will expose internal service IP addresses to the public internet violating the security requirement.

