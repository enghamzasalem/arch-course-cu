## Part 4.2 – Architectural Smells Detection (Smart Home Management System)

This document identifies two potential architectural smells in the Smart Home Management System, describes where they appear, why they are problematic, and proposes solutions. The refactoring is illustrated in `part4_smell_refactoring.drawio` (before and after diagrams).

---

### Smell 1: God Component

#### Name
**God Component** (a single component with too many responsibilities)

#### Where It Appears
A hypothetical or early version of the system combines **Device Management**, **Security & Alerts**, and **Automation & Scheduling** into one large service (e.g., "Device & Security & Automation Service"). This component would handle device control, security event processing, alerting, routine scheduling, and automation triggers in a single deployment unit.

#### Why It's a Problem
- **Single point of failure**: If this component fails or is redeployed, all three domains (devices, security, automation) go down together.
- **Hard to scale**: Cannot scale device management independently from security or automation; all share the same resources.
- **Hard to maintain**: Changes in one area (e.g., security rules) risk breaking others; testing and deployment become risky.
- **Unclear ownership**: Multiple teams or concerns mixed in one codebase lead to merge conflicts and blurred boundaries.
- **Violates single responsibility**: One component does too much, making it difficult to reason about, test, and evolve.

#### Proposed Solution
**Split the God Component into bounded microservices**:
- **Device Manager**: Device registry, commands, state, and publishing device events.
- **Security & Alerts**: Consume security-related events, evaluate rules, send notifications.
- **Automation & Scheduling**: Store and execute routines; subscribe to events; trigger actions.

Introduce an **Event Bus** (message broker) so that Device Manager publishes events, and Security & Alerts and Automation subscribe as independent consumers. This preserves loose coupling and allows independent deployment and scaling. See **Smell 1** in `part4_smell_refactoring.drawio` for the before/after diagram.

---

### Smell 2: Circular Dependencies

#### Name
**Circular Dependencies** (components depend on each other in a cycle: A → B → C → A)

#### Where It Appears
In a design where **Device Manager (A)** calls **Security Service (B)** (e.g., to check if an action is allowed), **Security Service (B)** calls **Automation Service (C)** (e.g., to trigger a routine), and **Automation Service (C)** calls back to **Device Manager (A)** (e.g., to send a device command). This creates a runtime dependency cycle: A → B → C → A.

#### Why It's a Problem
- **Tight coupling**: Components cannot be developed, tested, or deployed independently; a change in one may force changes in all.
- **Risk of deadlocks or infinite loops**: Circular call chains can lead to subtle bugs under load or in error paths.
- **Hard to reason about**: Execution flow is difficult to trace and debug; initialization order and lifecycle become complex.
- **Blocks independent scaling and deployment**: The cycle forces these services to be considered together, reducing flexibility.
- **Violates dependency inversion**: High-level flow is dictated by low-level call chains instead of events or clear boundaries.

#### Proposed Solution
**Break the cycle using event-driven communication**:
- Remove direct synchronous calls between Device Manager, Security, and Automation.
- Introduce a **Message Broker**: Device Manager (and other producers) publish **events** (e.g., device state change, security event, schedule trigger).
- Security and Automation (and other consumers) **subscribe** to relevant topics and react asynchronously. They do not call back to Device Manager directly; instead, they may publish new events (e.g., "execute routine") that are consumed by a dedicated command handler or Device Manager via the broker.
- Result: **No direct runtime dependency cycle**. Data flows one way: producers → broker → consumers. See **Smell 2** in `part4_smell_refactoring.drawio` for the before/after diagram.

---

### Summary

| Smell                  | Location (hypothetical/early design)     | Solution                          | Diagram reference   |
|------------------------|------------------------------------------|-----------------------------------|--------------------|
| God Component          | Single "Device & Security & Automation" service | Split into Device Manager, Security & Alerts, Automation; use Event Bus | Page 1 in drawio   |
| Circular Dependencies  | A → B → C → A (Device Manager, Security, Automation) | Replace direct calls with Message Broker; events only | Page 2 in drawio   |

Refactoring diagrams (before and after) are in **part4_smell_refactoring.drawio**.
