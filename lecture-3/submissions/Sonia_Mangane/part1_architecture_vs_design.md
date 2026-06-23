# Architectural Decisions

## 1. Microservices Architecture

I have chossen the microservice architecture to separate the business logic into independent services: User Service, Device Management, Security & Alert, Energy Monitoring, and Automation.

### Rationale

A microservice architecture ensures the scalability of the application. Since each service handles a single responsibility, this ensures the separation of concerns. A failure in one service does not crash the other services. The independent services promote maintainability and are easily modifiable.

### Alternatives Considered

I considered a monolithic architecture, however it can get complex and is hard to scale.  
Another alternative is a modular monolith architecture which is just one application but is defined into isolated modules. However if one module crashes, it affects the whole system.

### Consequences

It can be too complex to deploy and there is high network communication overhead.

---

## 2. API Gateway Architecture

Introduced an API Gateway as the single entry point for all clients to handle routing, authentication and request validation.

### Rationale

Creates a single entry point for all client applications. This ensures a centralised authentication and authorization. It also hides the internal service structure from the client.

### Alternatives Considered

I considered exposing each microservice to the client but this exposes the internal architecture of the system. I also considered the Backend-for-Frontend pattern but that can cause code duplication.

### Consequences

The gateway can become a bottleneck which will affect the overall performance of the system.

---

## 3. Event Driven Architecture

Used a message broker for asynchronous communication between services to decouple service interactions and support real-time event processing.

### Rationale

The event-driven architecture with a message broker for asynchronous communication between services reduces coupling between services. It enables real-time event processing and improves responsiveness.

### Alternatives Considered

I considered synchronous REST communication because it is simpler to implement but has poor performance under heavy load.

### Consequences

Increased debugging complexity.

---

## 4. Database per Service Pattern

Each microservice will own and manage its own database schema or a dedicated database.

### Rationale

This ensures loose coupling between services. By having a database for each service we prevent direct data access across services. It enables independent scaling and deployment.

### Alternatives Considered

I also considered a centralized database but then the services will be coupled at the data layer.

### Consequences

By having a database for each service, we have more complex data management and cross service transactions become harder.

---

## 5. Cloud-Based Deployment

Deploy backend services on cloud infrastructure to enable elastic scaling, high availability, and global access.

### Rationale

Reduces operational overhead for infrastructure management and supports global access for mobile and web clients.

### Alternatives Considered

I considered on-premises hosting but it involves higher maintenance cost and limited scalability.

### Consequences

Ongoing operational costs based on usage.

---

# Design Decisions

## 1. Repository Pattern

Here we separate the business logic from the data access logic. The Device Manager Service has a Device Repository class that handles the database queries. This abstracts the database access in the Device Manager Service.

### Rationale

The biggest motivation for this design pattern is the separation of concern. This also allows the ease of unit testing. If we want to test the workings of the Device Manager service, we can just create a 'Mock Repository'.

**Design Pattern Used:** Repository Pattern  
**Scope:** Component — this pattern manages the internal communication between classes within the Device Manager service.

---

## 2. Observer Pattern

We used the Observer Pattern to notify multiple channels when a security alert occurs.

### Rationale

This design pattern promotes extensibility. If a user adds a new notification type, we just create a new Observer class. The Security & Alert service remains untouched.

**Design Pattern Used:** Observer Pattern  
**Scope:** Component — this pattern manages the internal communication between classes within the Security Service.

---

## 3. Singleton Pattern

We used the Singleton Pattern to manage the lifecycle of the Message Broker. Instead of the service opening a new connection to the broker (like RabbitMQ or Mosquitto) every time an event occurs, it uses one connection that can be used by all events.

### Rationale

It provides a single point of entry for any class within the service to publish a message without needing to pass connection objects through every constructor.

**Design Pattern Used:** Singleton Pattern  
**Scope:** Component — this pattern manages the internal communication between classes within all the services.

---

## 4. Factory Pattern

Use the Factory Method Pattern to instantiate different automation actions within the Automation Service.

### Rationale

By using the factory pattern, we create an abstraction layer. The automation service does not need to know the specific setup for the devices, it just asks the factory for an "action" object.

**Design Pattern Used:** Factory Pattern  
**Scope:** Component — this pattern manages the internal communication between classes within the Automation service.

---

## 5. Mediator Pattern

Used the Mediator Pattern to coordinate interactions between different device controllers within the Automation service. Individual device controllers do not need to know about each other. They only notify the Mediator when their state changes.

### Rationale

It will be easier to maintain because adding a new type of device to a routine only requires updating the Mediator, not every other device class in the system.

**Design Pattern Used:** Mediator Pattern  
**Scope:** Component — this pattern manages the internal communication between classes within the Automation service.