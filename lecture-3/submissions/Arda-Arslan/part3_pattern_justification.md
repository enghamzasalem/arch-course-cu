# Part 3.1 - Architectural Pattern Justification

## Selected Pattern

Hybrid Architecture  
Primary Pattern: Microservices  
Secondary Pattern: Event-Driven (IoT Layer)

---

## Why This Pattern Was Chosen

The Smart Home Management System includes multiple distinct backend responsibilities:

- Authentication
- Device management
- Automation routines
- Notifications and alerts

These responsibilities are implemented as separate services:
- Authentication Service
- Device Manager Service
- Automation Service
- Notification & Alert Service

Using Microservices allows each responsibility to be isolated and managed independently.

For device communication, the system uses MQTT publish/subscribe.  
Smart devices continuously send telemetry and receive commands.  
Because of this, an Event-Driven approach is more suitable for the IoT layer.

- Clients communicate through REST APIs.
- Devices communicate asynchronously through MQTT.

---

## How It Addresses System Requirements

### Security
- A dedicated Authentication Service handles JWT-based authentication.
- API Gateway acts as a controlled entry point.
- Internal services are not directly exposed to clients.
- MQTT communication is handled through a broker.

This structure reduces the attack surface and centralizes access control.

---

### Scalability
- Services can scale independently if needed.
- MQTT publish/subscribe allows multiple devices to communicate efficiently.
- Telemetry data is separated from operational data, reducing database overload.

---

### Performance
- MQTT is lightweight and suitable for IoT devices.
- Caching recent device state improves response time.
- Service separation prevents a single large component from becoming slow.

---

### Reliability and Modularity
- Each service focuses on a specific capability.
- Device Manager acts as a single communication hub for devices.
- Failure in one service does not necessarily stop the entire backend logic.

---

## Trade-offs

- Increased architectural complexity compared to a monolithic system.
- Distributed services are harder to debug.
- API Gateway and Device Manager become critical components.

---

## Alternative Patterns Considered

### Monolithic Architecture
Not chosen because all responsibilities would be tightly coupled.  
Scaling or modifying one feature would require redeploying the entire system.

---

### Layered Architecture
Not chosen because the system is structured around independent services rather than strict horizontal layers.  
IoT messaging using MQTT does not naturally fit a layered model.

---

### Pure Event-Driven Architecture
Not chosen because most backend interactions use REST APIs through the API Gateway.  
A fully event-driven backend would add unnecessary complexity for this system.