# Task 3.2 - Architectural Decision Records (ADRs)

# ADR-001: Adopt Microservices Architecture with an API Gateway

## Status
Accepted

## Context
The Smart Home Management System supports multiple client types (mobile app, web interface, voice assistant) and multiple backend capabilities such as authentication, device management, automation, and notifications.

To maintain modularity and scalability, the backend is organized into clearly separated services with a single entry point.

## Decision
Adopt a microservices architecture where the backend is decomposed into independent services (Authentication, Device Manager, Automation, Notification).

Use an API Gateway as the single entry point to route client requests to the appropriate internal services.

## Consequences
- Positive consequence: Clear separation of responsibilities and improved scalability.
- Negative consequence: Increased architectural complexity and more challenging debugging.
- Neutral consequence: Requires structured service-to-service communication through REST APIs.

## Alternatives Considered
- Monolithic Architecture: Not chosen because it reduces modularity and makes scaling and maintenance harder.
- Layered Architecture: Not chosen because the system is structured around independent services rather than strict layers.

---

# ADR-002: Use MQTT Publish/Subscribe for IoT Device Communication

## Status
Accepted

## Context
Smart devices continuously send telemetry and state updates and must receive control commands in real time. IoT environments require lightweight and asynchronous communication mechanisms.

## Decision
Use an MQTT Broker and MQTT publish/subscribe communication between Smart Devices and the Device Manager Service.

Devices publish telemetry/state events to the broker, and the Device Manager subscribes and publishes command messages.

## Consequences
- Positive consequence: Lightweight and scalable communication suitable for IoT devices.
- Negative consequence: Requires management of an MQTT broker and makes debugging more complex.
- Neutral consequence: Introduces asynchronous messaging into the system architecture.

## Alternatives Considered
- HTTP REST for device communication: Not chosen because continuous polling is inefficient for IoT telemetry.
- WebSocket communication: Not chosen because it adds more overhead compared to MQTT in constrained environments.

---

# ADR-003: Expose Only the API Gateway to the Public Network

## Status
Accepted

## Context
The system manages sensitive operations such as authentication, device control, and security alerts. Reducing the attack surface is important to protect internal services and databases.

## Decision
Deploy the API Gateway as the only public-facing component.

All backend services and databases are deployed within a private/internal network.

## Consequences
- Positive consequence: Reduced attack surface and improved security.
- Negative consequence: API Gateway becomes a critical component and requires proper monitoring.
- Neutral consequence: Requires network segmentation and configuration management.

## Alternatives Considered
- Expose all services publicly: Not chosen because it increases security risks.
- Single flat network without separation: Not chosen because it does not isolate sensitive backend components.