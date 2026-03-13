# ADR-001: Adopt Hybrid Microservices & Event-Driven Architecture

## Status
Accepted


## Context

The Smart Home Management System must satisfy critical functional and non-functional requirements:

- 24/7 Availability for safety-critical operations (door locks, alarms)
- Strong Security for sensitive user data and physical device control
- Scalability to support growing IoT devices and bursty sensor traffic
- High Performance for real-time responsiveness
- Maintainability for frequent updates and new device integrations

A simpler architectural style risks tight coupling, limited scalability, fault isolation, and increased security exposure.


## Decision

We will implement a **Hybrid Microservices & Event-Driven Architecture**.

This includes:

- Independent microservices managed by business domain
- Database-per-Service pattern for data isolation
- A Message Broker to handle asynchronous communication
- An API Gateway as the single external entry point

Services will communicate primarily through asynchronous events. Each service will own its data and be independently deployable and scalable.

This decision prioritizes availability, scalability and maintainability over architectural simplicity.


## Consequences

### Positive Consequences

- **High Availability:** Failure in one service does not shut down the entire system.
- **Fault Isolation:** Critical services remain operational during partial failures.
- **Independent Scalability:** High-demand services can scale without scaling the whole system.
- **Maintainability:** Services evolve independently.
- **Security Improvement:** Internal services are not directly exposed to clients.

### Negative Consequences

- Increased infrastructure complexity.
- Higher operational and cloud costs.
- More complex monitoring and debugging in distributed systems.

### Neutral Consequences

- Eventual consistency due to Database-per-Service.
- Short propagation delays between services.


## Alternatives Considered

### 1. Monolithic Architecture

**Why not chosen:**

- Single point of failure.
- Hard to scale specific components independently.
- Not suitable for high IoT growth.


### 2. Direct Client-Server Architecture

**Why not chosen:**

- Exposes internal services to the public internet.
- Increases security risk.
- Violates maintainability and security requirements.


# ADR-002: Adopt Database-per-Service Pattern

## Status
Accepted



## Context

The Smart Home Management System is built using a Microservices Architecture. Each service represents a specific business capability such as Security, Energy Management, Automation, or Device Management.

The system handles safety-critical operations and sensitive data, therefore, strong service isolation and loose coupling are essential.


## Decision

Each microservice will own and manage its own database schema (Database-per-Service pattern).

- No service will directly access another service’s database.
- All cross-service data exchange will occur via asynchronous events.
- Data consistency across services will be achieved using event-driven communication.


## Consequences

### Positive Consequences

- **Strong Isolation:** A database failure in one service does not affect others.
- **Loose Coupling:** Services are independent at both application and data layers.
- **Independent Scaling:** Databases can scale according to service demand.
- **Technology Flexibility:** Each service can use the database type best suited for its needs.
- **Improved Security:** Direct cross-service data access is prevented.

### Negative Consequences

- Increased complexity in managing multiple databases.
- More difficult cross-service querying.
- Leads to eventual consistency instead of strong consistency.

### Neutral Consequences

- Requires event-driven synchronization mechanisms.


## Alternatives Considered

### 1. Shared Centralized Database

**Why not chosen:**

- Creates tight coupling at the data layer.
- Increases risk of cascading failures.
- Makes schema evolution difficult.
- Violates microservices autonomy principles.


### 2. Shared Schema with Logical Separation

**Why not chosen:**

- Still introduces implicit coupling.
- Schema changes may impact multiple services.
- Does not provide true data ownership.


# ADR-003: Use Message Broker for Asynchronous Inter-Service Communication

## Status
Accepted


## Context

The Smart Home Management System processes high-frequency IoT sensor data and user commands.

The system must:

- Handle traffic 
- Prevent cascading failures
- Ensure commands are not lost

A key architectural decision was whether services should communicate synchronously (REST calls only) or asynchronously via a message broker.


## Decision

We will use a Message Broker to enable asynchronous, event-driven communication between services.

- Services will publish events when state changes occur.
- Other services may subscribe to relevant events.
- Critical commands will be persisted in queues until successfully processed.





## Consequences

### Positive Consequences

- **Improved Reliability:** Messages are persisted and not lost.
- **Scalability:** Services consume events at their own pace.
- **Loose Coupling:** Services do not need direct knowledge of each other.
- **Extensibility:** New services can subscribe to existing events without modifying current services.
- **Resilience:** Prevents system overload during traffic spikes.

### Negative Consequences

- Harder debugging due to asynchronous flows.
- Eventual consistency between services.
- Requires monitoring of message queues and broker health.

### Neutral Consequences

- Requires additional infrastructure (message broker).



## Alternatives Considered

### 1. Pure Synchronous REST Communication

**Why not chosen:**

- Tight runtime coupling between services.
- High risk of cascading failures.
- Poor handling of IoT traffic.
- Increased latency during chained service calls.





