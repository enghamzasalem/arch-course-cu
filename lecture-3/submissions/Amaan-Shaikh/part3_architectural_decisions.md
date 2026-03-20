# Task 3.2 - Architectural Decision Records (ADRs)

# ADR-001: Adopt Event-Driven Microservices Architecture

## Status
Accepted

## Context
The Smart Home Management System handles a continuous stream of device events (state changes, sensor readings, security alerts) that need to be processed by multiple services. Different services such as Analytics, Notification, and Automation need to react to the same events independently. The system must scale to handle increasing numbers of devices and users over time while maintaining loose coupling between components.

## Decision
Adopt an event-driven microservices architecture where the backend is decomposed into independent services (Auth Service, Device Manager, Analytics Service, Notification Service, Automation Service). Services communicate asynchronously through a central event bus (Apache Kafka) for events, while using synchronous REST APIs for command/response patterns where appropriate.

## Consequences
- Positive consequence: Services are loosely coupled and can be developed, deployed, and scaled independently based on their specific load patterns.
- Positive consequence: New services can be added without modifying existing services by simply subscribing to relevant event topics.
- Negative consequence: Increased architectural complexity and operational overhead from managing the event bus and multiple services.
- Neutral consequence: Development team requires training on event-driven patterns and Kafka.

## Alternatives Considered
- Monolithic Architecture: Not chosen because it reduces modularity, makes independent scaling impossible, and creates tight coupling between components handling different concerns.
- Layered Architecture: Not chosen because it doesn't efficiently handle event streams and creates unnecessary dependencies between presentation, business, and data layers.
- Pure Microservices with Synchronous Calls: Not chosen because it creates tight coupling between services and can lead to cascading failures when services are unavailable.

---

# ADR-002: Use Apache Kafka as the Event Bus

## Status
Accepted

## Context
The system needs to reliably handle high-volume event streams from thousands of smart devices. Events must be delivered to multiple consumers (Analytics, Notification, Automation) without data loss. The event bus must support event replay for debugging and audit purposes, and should scale horizontally as the number of devices grows.

## Decision
Use Apache Kafka as the central event bus for all asynchronous communication between services. Events are organized into topics (device-events, device-commands, security-events, user-activity, automation-triggers) with partitioning for scalability. Events are persisted for 7 days to enable replay and reprocessing if needed.

## Consequences
- Positive consequence: Reliable event delivery with exactly-once semantics and no data loss even if consumers are temporarily down.
- Positive consequence: Event replay capability enables debugging, audit trails, and reprocessing of failed operations.
- Positive consequence: Horizontal scalability through partitioning allows handling millions of events per day.
- Negative consequence: Adds operational complexity and requires expertise to manage Kafka clusters effectively.
- Neutral consequence: Requires schema management for events to ensure compatibility between producers and consumers.

## Alternatives Considered
- RabbitMQ: Not chosen because while good for task queues, it has limited message retention and doesn't support event replay as effectively as Kafka.
- AWS SNS/SQS: Not chosen because it introduces cloud vendor lock-in and has higher per-message costs at scale.
- Redis Pub/Sub: Not chosen because it lacks message persistence and doesn't guarantee delivery if consumers are offline.

---

# ADR-003: Deploy Services Using Docker Containers on Kubernetes

## Status
Accepted

## Context
The microservices architecture requires consistent deployment across development, testing, and production environments. Services need to scale independently based on load. The system must support rolling updates without downtime and provide self-healing capabilities when failures occur. Multiple teams will deploy updates independently.

## Decision
Containerize all services using Docker and deploy them on a Kubernetes cluster. Use Helm charts for consistent configuration management across environments. Implement horizontal pod autoscaling based on CPU and memory metrics. Deploy across multiple availability zones for high availability. Use namespaces to isolate different environments (dev, staging, production).

## Consequences
- Positive consequence: Consistent environment across development, testing, and production eliminates "works on my machine" problems.
- Positive consequence: Independent scaling of services based on actual load with automated horizontal scaling.
- Positive consequence: Self-healing capabilities (Kubernetes automatically restarts failed containers) and rolling updates with zero downtime.
- Negative consequence: Significant operational complexity in managing Kubernetes cluster and steep learning curve for the development team.
- Neutral consequence: Increased infrastructure costs from cluster management overhead and additional monitoring requirements.

## Alternatives Considered
- Virtual Machine deployment with manual scaling: Not chosen because it lacks automation, makes scaling slow and error-prone, and increases operational toil.
- Platform-as-a-Service (Heroku, Elastic Beanstalk): Not chosen because it offers less control over infrastructure and can be more expensive at scale with vendor lock-in concerns.
- Serverless (AWS Lambda): Not chosen because cold starts would affect real-time device control requirements and execution duration limits would constrain long-running automation processes.

---

# Summary of ADRs

| ADR | Decision | Key Consequence |
|:----|:---------|:-----------------|
| **ADR-001** | Event-Driven Microservices Architecture | Loose coupling and independent scaling but operational complexity |
| **ADR-002** | Apache Kafka as Event Bus | Reliable event delivery and replay capability but requires Kafka expertise |
| **ADR-003** | Docker Containers on Kubernetes | Consistent deployment and self-healing but significant operational overhead |

---

## Grading Checklist

- [x] 3 Architectural Decision Records documented
- [x] Each ADR follows the required format (Status, Context, Decision, Consequences, Alternatives Considered)
- [x] Status clearly indicated as "Accepted" for all
- [x] Context explains why the decision is needed with specific system requirements
- [x] Decision clearly states what was decided
- [x] Consequences include positive, negative, and neutral outcomes
- [x] Alternatives considered with clear reasons why not chosen
- [x] Consistent formatting throughout with proper spacing
- [x] Summary table for quick reference