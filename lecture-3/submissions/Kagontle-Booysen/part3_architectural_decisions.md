# Architectural Decision Records (ADRs)
System: Smart Home Management System  
Architecture: Microservices + Event-Driven  

---

# ADR-001: Adopt Microservices Architecture Instead of Monolithic Architecture

## Status
Accepted

## Context

The Smart Home Management System must support:

- Real-time device control (low latency)
- High availability for safety-critical operations
- Scalability for increasing numbers of devices and telemetry events
- Independent evolution of domains (Identity, Device Management, Automation, Notifications)
- Long-term modifiability and extensibility

A key architectural decision was required regarding system structure:  
**Monolithic vs Microservices architecture.**

This decision directly impacts core quality attributes including:
- Scalability
- Availability
- Modifiability
- Deployability
- Performance

## Decision

The system will adopt a **domain-oriented Microservices architecture**, where each business capability (Identity, Device Manager, Automation, Notification, Analytics) is implemented as an independently deployable service with its own data store.

## Consequences

### Positive Consequences
- Improves **scalability** (services scale independently)
- Enhances **availability** (fault isolation between services)
- Increases **modifiability** (clear domain boundaries reduce coupling)
- Enables **independent deployment**, reducing release risk
- Aligns with event-driven design

### Negative Consequences
- Increased **operational complexity**
- Distributed system challenges (network latency, observability)
- Requires careful management of **eventual consistency**
- Higher infrastructure cost

### Neutral Consequences
- Requires DevOps maturity
- Increases need for monitoring and distributed tracing

## Alternatives Considered

### 1. Monolithic Architecture
Rejected because:
- Limited independent scaling
- Reduced fault isolation
- Slower deployment cycles
- Higher coupling reduces modifiability

### 2. Layered Architecture (Single Deployment)
Rejected because:
- Still results in a single deployable unit
- Does not address scalability and availability concerns adequately

---

# ADR-002: Use Event-Driven Communication with Message Broker (MQTT)

## Status
Accepted

## Context

Smart home systems are inherently event-driven:

- Device state changes
- Security alerts
- Telemetry streams
- Automation triggers

The architecture required a communication strategy between services.

This decision directly affects:
- Performance (latency and throughput)
- Scalability
- Reliability
- Availability
- Modifiability

## Decision

The system will use an **Event-Driven architecture supported by a message broker (MQTT)** for asynchronous communication between services and IoT devices.

Synchronous REST calls are used only for client-facing operations.

## Consequences

### Positive Consequences
- Improves **scalability** via decoupled publish/subscribe model
- Enhances **availability** (services can operate independently)
- Supports high-throughput telemetry ingestion
- Improves **modifiability** (new consumers can subscribe without changing producers)
- Reduces tight coupling between services

### Negative Consequences
- Introduces **eventual consistency**
- More complex debugging
- Requires schema governance and versioning
- Risk of duplicate message handling (requires idempotency)

### Neutral Consequences
- Requires additional infrastructure (broker cluster)
- Necessitates observability tooling

## Alternatives Considered

### 1. Pure REST-Based Synchronous Communication
Rejected because:
- Tighter coupling
- Reduced scalability
- Poor handling of bursty event loads

### 2. Direct Database Sharing Between Services
Rejected because:
- Violates service autonomy
- Reduces modifiability
- Increases coupling
- Creates scalability bottlenecks

---

# ADR-003: Deploy Using Containerization (Docker + Kubernetes in Cloud Environment)

## Status
Accepted

## Context

Given the microservices architecture, deployment strategy must support:

- Independent scaling
- High availability
- Automated recovery
- Environment consistency
- Infrastructure portability

This decision directly impacts:
- Deployability
- Availability
- Scalability
- Maintainability
- Operational complexity

## Decision

All services will be containerized using **Docker** and deployed on a **Kubernetes cluster in a cloud environment**.

The deployment model includes:
- Horizontal pod autoscaling
- Load balancing
- Health checks
- Rolling updates

## Consequences

### Positive Consequences
- Improves **scalability** (horizontal scaling per service)
- Enhances **availability** (auto-restart and self-healing)
- Improves **deployability** (consistent environments)
- Enables blue-green and rolling deployments
- Increases infrastructure portability

### Negative Consequences
- Increased operational complexity
- Higher infrastructure and management cost
- Requires DevOps expertise
- More complex debugging compared to single-node deployment

### Neutral Consequences
- Requires CI/CD pipeline setup
- Introduces learning curve for orchestration tools

## Alternatives Considered

### 1. VM-Based Deployment Without Containers
Rejected because:
- Lower resource efficiency
- Harder scaling and deployment automation
- Reduced portability

### 2. On-Premise Deployment
Rejected because:
- Limited elasticity
- Higher capital expenditure
- Reduced global availability
- Less flexibility for scaling

---
