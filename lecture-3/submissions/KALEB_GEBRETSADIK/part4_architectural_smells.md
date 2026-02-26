# Part 4.2: Architectural Smells Detection

## Smell 1: God Component (The API Gateway)

- **Name of Smell**: God Component (or God Object / Blob)
- **Where it appears**: In the current architecture, the API Gateway is handling Authentication, Rate Limiting, Request Routing, *and* Session Caching (via direct connection to Redis). 
- **Why it's a problem**: The gateway has taken on too many responsibilities beyond simple routing. By coupling authentication logic and direct cache interaction into the gateway, it becomes a massive bottleneck for development teams. Every time the authentication schema changes, the routing layer must be rebuilt and redeployed. It violates the Single Responsibility Principle on an architectural level.
- **Proposed Solution**: Strip the API Gateway back to pure routing and rate-limiting. Extract the authentication logic into a dedicated **Identity & Access Management (IAM) Microservice**. The Gateway simply forwards the auth token to the IAM service for validation before routing the request to the backend.

---

## Smell 2: Scattered Concerns (Notification Dispatching)

- **Name of Smell**: Scattered Concerns (Cross-Cutting Concern creeping into domain logic)
- **Where it appears**: Currently, if the *Security Service* detects an intrusion, it formats and sends an email. If the *Device Manager* detects a device offline, it also formats and sends an email. The logic for interacting with SendGrid/Twilio is scattered across multiple independent microservices.
- **Why it's a problem**: If the company decides to switch from AWS SES to SendGrid for email, developers must find and update code in the Security Service, the Device Manager, the Automation Engine, etc. It violates the DRY (Don't Repeat Yourself) principle and makes the system brittle to external vendor changes.
- **Proposed Solution**: Introduce a dedicated **Notification Service**. Domain services (Security, Device Manager) simply publish internal domain events to the Message Broker (e.g., `DeviceOfflineEvent`). The standalone Notification Service listens to the broker, looks up user preferences, and formats/dispatches the actual SMS or Email.

---

*(Note: See `part4_smell_refactoring.drawio` for the visual representation of these refactorings).*
