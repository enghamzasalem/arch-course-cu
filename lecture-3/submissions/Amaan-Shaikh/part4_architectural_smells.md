# Part 4.2 - Architectural Smells Detection

## Smell 1 - God Component (Device Manager)

**Where It Appears**

The Device Manager Service is responsible for:
- Handling communication with all smart devices
- Processing MQTT messages from devices
- Managing device state (on/off, temperature, lock status)
- Sending commands to devices
- Processing telemetry data from sensors
- Generating alerts based on device events
- Executing automation scenes
- Validating user commands
- Communicating with other services (Automation, Notification, Analytics)

**Why It Is a Problem**

This concentrates multiple responsibilities in a single service.
When one component handles too many responsibilities:
- It becomes harder to maintain and understand
- Changes increase the risk of breaking other functionality
- Scaling the system becomes more complex because all functions scale together
- Over time, this service may grow too large and difficult to manage
- Bug in telemetry processing could affect device control
- Single point of failure for all device-related operations

**Proposed Solution**

Refactor the Device Manager by separating responsibilities into specialized services:
- **Device Control Service**: Handle commands and real-time device control
- **Device State Service**: Manage device states and caching
- **Telemetry Service**: Process sensor data and energy monitoring
- **Alert Service**: Generate security alerts and notifications
- **Automation Service**: Execute scenes and automation rules

Services communicate asynchronously through an event bus (Kafka) to maintain loose coupling.

---

## Smell 2 - Circular Dependencies (Between Services)

**Where It Appears**

Multiple services have circular dependencies on each other:
- Device Manager calls Automation Service to check scene conditions
- Automation Service calls Device Manager to execute device actions
- Automation Service calls Notification Service to send alerts
- Notification Service queries Automation Service for context
- Notification Service calls User Service for preferences
- User Service updates Notification Service with settings
- Device Manager calls User Service for permissions
- User Service validates device access with Device Manager

**Why It Is a Problem**

Circular dependencies create several issues:
- Hard to understand the flow of requests through the system
- Changes in one service may require changes in others
- Difficult to test services in isolation
- Deployment must happen in a specific order
- Failure in one service can cascade through the cycle
- Potential for deadlocks if services wait for each other
- Services cannot be scaled independently

**Proposed Solution**

Introduce an event bus (Kafka) to break circular dependencies:
- Services publish events instead of calling each other directly
- Device Manager publishes device state changes
- Automation Service subscribes to device events and publishes scene triggers
- Notification Service subscribes to alert events
- User Service publishes user preference changes
- All communication becomes unidirectional through the event bus
- New services can subscribe without modifying existing ones

This transforms synchronous circular calls into asynchronous event flows with clear direction.

---

## Summary

| Smell | Location | Problem | Solution |
|:------|:---------|:--------|:---------|
| **God Component** | Device Manager Service | Too many responsibilities, hard to maintain, cannot scale independently | Split into specialized services (Control, State, Telemetry, Alert, Automation) |
| **Circular Dependencies** | Multiple service interactions | Complex flow, cascade failures, deployment ordering issues | Introduce event bus for asynchronous communication |