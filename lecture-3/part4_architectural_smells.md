# Architecture vs. Design Decisions
## Part 1: Architectural Decisions
   ### AD-1: Use API Gateway as Single Entry Point
**Decision**
The Smart Home system uses an API Gateway as the single entry point for all client requests.
**Rationale**
This approach centralizes request routing, improves security, and simplifies client communication with backend services.
Alternatives Considered
Direct client-to-service communication
Backend-for-Frontend 
**Consequences**
   +Improves security and monitoring
   +Simplifies client integration
   -Adds additional network hop
   -Gateway becomes a critical component
   ### AD-2: Decompose System into Independent Services
**Decision**
The system is decomposed into multiple independent services (Auth, Device Management, Automation, Security).
**Rationale**
This improves modularity, maintainability, and allows independent development and scaling.
Alternatives Considered
Monolithic architecture
Layered monolith
**Consequences**
   +Better modularity and flexibility
   +Easier future scaling
   -Increased operational complexity
   -More inter-service communication
   ### AD-3: Use MQTT for IoT Device Communication
**Decision**
MQTT protocol is used between the Device Management Service and Smart Devices.
**Rationale**
MQTT is lightweight and well-suited for real-time communication with resource-constrained IoT devices.
Alternatives Considered
HTTP polling
WebSocket communication
**Consequences**
  +Low bandwidth usage
  +Real-time device updates
  -Requires MQTT broker infrastructure
  -Additional operational overhead
   ### AD-4: Use Centralized Relational Database
**Decision**
A centralized relational database is used to store users, devices, and automation data.
**Rationale**
Relational databases provide strong consistency, structured schema, and reliable transactions.
Alternatives Considered
NoSQL database
Database per service
**Consequences**
   +Strong data integrity
   +Mature ecosystem
   -Potential scalability bottleneck
   -Tighter coupling between services
### AD-5: Secure Communication Using HTTPS and JWT
**Decision**
All client-server communication uses HTTPS with JWT-based authentication.
**Rationale**
This ensures secure data transmission and supports stateless authentication across services.
Alternatives Considered
Session-based authentication
API key authentication
**Consequences**
   +Improved security
   +Scalable authentication model
   -Token management complexity
   -Requires careful key management
   ---------------------------------------------------------------------------------------------
## Part 2: Design Decisions
### DD-1: Use JWT Library for Token Handling
**Decision**
The Auth Service uses a standard JWT library for token generation and validation.
**Rationale**
Using a well-tested library reduces implementation errors and improves reliability.
Design Pattern Used
Library / Adapter pattern
Scope
Auth & User Service
### DD-2: Use In-Memory Cache for Device State
**Decision**
Device Management Service maintains an in-memory cache of device states.
**Rationale**
This reduces database load and improves response time.
Design Pattern Used
Cache pattern
Scope
Device Management Service
### DD-3: Use Retry with Exponential Backoff
**Decision**
Device commands implement retry with exponential backoff.
**Rationale**
Improves reliability when communicating with unstable IoT devices.
Design Pattern Used
Retry pattern
Scope
Device Management Service
### DD-4: Use Scheduler for Automation Rules
**Decision**
Automation Service uses a scheduler to execute time-based routines.
**Rationale**
Supports reliable and predictable automation execution.
Design Pattern Used
Scheduler pattern
Scope
Automation Service
### DD-5: Use Structured JSON Logging
**Decision**
All services use structured JSON logging.
**Rationale**
Improves observability and simplifies monitoring and debugging.
Design Pattern Used
Logging pattern
Scope