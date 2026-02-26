# Part 3.2: Architectural Decision Records (ADRs)

---

# ADR-001: Adopt Microservices Architecture over Monolith

## Status
Accepted

## Context
The Smart Home Management System needs to handle varied workloads: high-throughput, small-payload telemetry from IoT devices (lights, thermostats) alongside resource-intensive tasks like processing security camera feeds and sending immediate push notifications. A single monolithic backend application would force all these components to scale together, and a failure in one complex module (like video processing) could bring down essential services (like turning off a light).

## Decision
We will adopt a Microservices Architecture, decomposing the backend into independently deployable services organized around business capabilities (e.g., Device Management, Security, Automation).

## Consequences
- **Positive**: Services can scale independently based on their specific resource needs (CPU vs. Memory vs. Network).
- **Positive**: Fault isolation; a memory leak in the Automation service will not crash the Security service.
- **Negative**: Increased operational overhead requiring container orchestration (Kubernetes) and complex CI/CD pipelines.
- **Neutral**: Requires shifting the engineering culture to value strict API contracts and backward compatibility.

## Alternatives Considered
- **Layered Monolith**: Easier to design and deploy initially, but rejected because it lacks fault isolation and cannot scale specific domains independently.
- **Service-Oriented Architecture (SOA)**: Rejected because the heavyweight Enterprise Service Bus (ESB) and SOAP protocols introduce unnecessary complexity and latency compared to lightweight microservices.

---

# ADR-002: Use PostgreSQL as the Primary Data Store

## Status
Accepted

## Context
The system requires a persistent data store for user accounts, appliance configurations, home layouts (rooms, zones), and scheduled routines. This data is highly relational; a user owns homes, homes contain rooms, rooms contain devices, and routines trigger devices. Data integrity is paramount (e.g., a routine cannot reference a deleted device).

## Decision
We will use PostgreSQL, a mature relational database management system, as the primary data store for the system's core configuration and user data.

## Consequences
- **Positive**: Strong ACID compliance ensures data integrity and prevents orphaned records via foreign key constraints.
- **Positive**: Excellent ecosystem support, tooling, and developer familiarity.
- **Negative**: Relational databases are harder to scale horizontally across multiple regions compared to some NoSQL alternatives.
- **Neutral**: Requires structured schema migrations during deployments.

## Alternatives Considered
- **MongoDB (NoSQL Document Store)**: Rejected because our data is highly structured and relational. Managing relationships and data consistency in application code would be error-prone.
- **InfluxDB (Time-Series DB)**: While excellent for storing historical temperature readings, it cannot handle relational configuration data (users, homes, permissions). We may consider this later *strictly* for telemetry history, but PostgreSQL remains the primary DB.

---

# ADR-003: Use MQTT for IoT Telemetry and Event Messaging

## Status
Accepted

## Context
Smart home devices (sensors, switches) operate in constrained environments with limited battery life and sometimes unreliable Wi-Fi connections. The system needs to ingest thousands of state changes (e.g., motion detected, temperature changed) per minute and distribute these events to multiple backend services (e.g., triggering a routine, updating a UI, logging to a database).

## Decision
We will use the MQTT (Message Queuing Telemetry Transport) protocol with a centralized Message Broker for asynchronous communication between devices and backend services.

## Consequences
- **Positive**: MQTT is extremely lightweight, minimizing bandwidth and power consumption on constrained IoT devices.
- **Positive**: The Publish/Subscribe model naturally decouples the event producers (devices) from the consumers (microservices).
- **Negative**: Introduces a new critical infrastructure component (the MQTT Broker) that must be highly available; if the broker goes down, telemetry stops.
- **Neutral**: Operations are asynchronous; immediate acknowledgment to clients is handled differently than standard HTTP request/response.

## Alternatives Considered
- **REST via HTTP/HTTPS**: Rejected because the HTTP header overhead is too large for frequent small telemetry payloads, and it lacks native publish/subscribe semantics for event distribution.
- **WebSockets**: Considered for real-time bidirectional communication, but rejected for device telemetry because maintaining thousands of persistent, stateful TCP connections per server is difficult to load balance and scale compared to an MQTT broker.
