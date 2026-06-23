## Part 1.2 – Architecture vs. Design (Smart Home Management System)

This document distinguishes architectural (strategic, system‑wide) decisions from design (tactical, local) decisions for the Smart Home Management System.

---

### 1. Architectural Decisions (Strategic)

#### AD-1: Use a Microservices Architecture
- Decision: Structure the Smart Home Management System as a set of loosely coupled microservices (e.g., Device Management, Security & Alerts, User & Access, Automation & Scheduling, Analytics, API Gateway) rather than a single monolith.
- Rationale:
  - Different parts of the system (e.g., security alerts vs. energy analytics) have different scalability and availability needs.
  - Enables independent deployment and evolution of services (and allows future ownership by separate teams as the organization or product grows).
  - Aligns well with cloud-native deployment (containers, orchestration).
- Alternatives Considered:
  - Monolithic web application: Simpler to build initially, but would become hard to scale and evolve as features grow.
  - Modular monolith: Better internal boundaries than a pure monolith, but still limited in independent scaling and technology heterogeneity.
- Consequences:
  - Positive:
    - Independent scaling per service (e.g., scale Security & Alerts separately from Analytics).
    - Fault isolation: failure in one service less likely to bring down the whole system.
    - Technology flexibility per service (e.g., time-series DB for analytics, relational DB for users).
  - Negative:
    - Increased operational complexity (service discovery, monitoring, distributed tracing).
    - Requires stronger DevOps maturity (CI/CD, container orchestration).
  - Neutral:
    - Requires clear API contracts between services, which can improve documentation discipline.

---

#### AD-2: Use an API Gateway as the Single Entry Point
- Decision: All external clients (mobile app, web app, voice assistants) interact through an API Gateway that routes, authenticates, and rate-limits requests to backend services.
- Rationale:
  - Centralized place to handle cross-cutting concerns (authentication, authorization, throttling, logging).
  - Simplifies clients by hiding internal service topology.
  - Enables backward compatibility and API versioning strategies.
- Alternatives Considered:
  - Direct client-to-service communication: Clients talk to each microservice directly; simpler infrastructure but leaks internal topology and complicates clients.
  - Multiple specialized gateways per client type: More tailored but increases duplication of cross-cutting logic.
- Consequences:
  - Positive:
    - Consistent security and logging policies.
    - Easier evolution of internal services without changing client endpoints.
  - Negative:
    - API Gateway becomes a potential bottleneck or single point of failure if not highly available.
    - Requires careful scaling and observability.
  - Neutral:
    - Adds an extra network hop; usually acceptable given modern infrastructure.

---

#### AD-3: Event-Driven Communication for Device Events and Alerts
- Decision: Use an event-driven architecture (e.g., message broker/topic-based pub/sub) for device telemetry, state changes, and security alerts between Device Management, Security & Alerts, Automation & Scheduling, and Analytics services.
- Rationale:
  - Device telemetry and events are naturally asynchronous; event volume grows with the number of homes and devices on the platform.
  - Multiple consumers (Analytics, Automation, Notification services) can react to the same events without tight coupling.
  - Improves decoupling and extensibility when adding new event consumers.
- Alternatives Considered:
  - Pure synchronous REST between services: Simpler to understand, but leads to tight coupling and cascading failures; not ideal for high-volume event streams.
  - Polling-based model: Services regularly polling a shared store; inefficient and less responsive.
- Consequences:
  - Positive:
    - Loose coupling between producers and consumers.
    - Natural fit for scalable, streaming analytics and automation triggers.
  - Negative:
    - More complex debugging and tracing due to asynchronous flows.
    - Requires robust message broker infrastructure and DLQ (dead-letter queue) handling.
  - Neutral:
    - Services must be designed to be idempotent when processing events.

---

#### AD-4: Cloud-Native Deployment with Containers and Orchestration
- Decision: Deploy all backend services as containers managed by a container orchestrator (e.g., Kubernetes) in a public cloud environment.
- Rationale:
  - Need for elasticity to handle variable workloads (e.g., evening peaks, periods of high concurrent usage).
  - Built-in support for rolling updates, self-healing, and declarative infrastructure.
  - Easier multi-environment management (dev, staging, prod) through templates.
- Alternatives Considered:
  - Traditional VMs with manual configuration: Works for smaller deployments but increases operational overhead.
  - Serverless functions-only approach: Very scalable but can complicate long-running processes and stateful services like device sessions.
- Consequences:
  - Positive:
    - Horizontal scaling of critical services (e.g., API Gateway, Security & Alerts).
    - Strong ecosystem for monitoring, logging, and service mesh integration.
  - Negative:
    - Steeper learning curve for the team (Kubernetes concepts, manifests, Helm, etc.).
    - Additional complexity for local development environments.
  - Neutral:
    - Infrastructure definition moves into version-controlled configuration (IaC).

---

#### AD-5: Centralized Identity and Access Management (IAM) Service
- Decision: Introduce a dedicated User & Access Service responsible for user identities, roles, permissions, and token issuance/validation (e.g., OAuth2/OIDC).
- Rationale:
  - Security is critical for controlling access to home devices and data.
  - Centralizing authentication/authorization simplifies enforcement across all services.
  - Supports integration with external identity providers (e.g., Google, Apple, Amazon accounts).
- Alternatives Considered:
  - Embedding auth logic in each service: Increases duplication and risks inconsistent policies.
  - Relying solely on external identity provider: Reduces implementation work but limits fine-grained, domain-specific authorization.
- Consequences:
  - Positive:
    - Single source of truth for access control.
    - Easier to audit and update security policies.
  - Negative:
    - The IAM service becomes a high-value target and must be highly available and secure.
    - Additional latency for token validation if not cached properly.
  - Neutral:
    - Requires coordination with API Gateway to enforce access tokens.

---

### 2. Design Decisions (Tactical)

#### DD-1: In-Memory Device State Cache Using HashMap
- Decision: The Device Management Service maintains an in-memory cache (e.g., `HashMap<DeviceId, DeviceState>`) for the most recent state of each device to reduce database reads for frequent status checks.
- Rationale:
  - Device status is read far more frequently than it changes.
  - In-memory lookups are significantly faster than repeated queries to the database.
- Design Pattern Used: Cache-aside pattern: read from cache first, fall back to database on miss, and populate cache.
- Scope: Within the Device Management Service module/class responsible for device state handling.

---

#### DD-2: Repository Pattern for Persistence in Core Services
- Decision: Use a Repository pattern for persistence in services (e.g., User & Access, Device Management, Automation & Scheduling) to abstract the underlying database technology.
- Rationale:
  - Keeps domain logic decoupled from the persistence mechanism.
  - Simplifies unit testing by mocking repositories.
- Design Pattern Used: Repository pattern with interfaces like `UserRepository`, `DeviceRepository`, `RoutineRepository`.
- Scope: Component-level; applied inside each microservice’s data access layer.

---

#### DD-3: Strategy Pattern for Automation Trigger Evaluation
- Decision: Implement different types of automation triggers (time-based, event-based, condition-based) using the Strategy pattern, where each trigger type encapsulates its own evaluation logic.
- Rationale:
  - New trigger types (e.g., based on device events or sensor thresholds) should be easy to add without modifying existing code.
  - Keeps trigger evaluation logic modular and testable.
- Design Pattern Used: Strategy pattern, e.g., `TriggerStrategy` interface with concrete implementations like `TimeTrigger`, `EventTrigger`, `ConditionTrigger`.
- Scope: Methods and classes within the Automation & Scheduling Service.

---

#### DD-4: Circuit Breaker for External Device Integrations
- Decision: Use a Circuit Breaker mechanism when calling third-party device vendor APIs (e.g., for proprietary smart bulbs or locks) to prevent cascading failures when a vendor is down or slow.
- Rationale:
  - External APIs have variable reliability and latency.
  - Protects internal services from being overwhelmed by slow or failing dependencies.
- Design Pattern Used: Circuit Breaker pattern with configurable thresholds and fallback behavior.
- Scope: Connector layer/adapters in the Device Management Service that integrate with vendor APIs.

---

#### DD-5: Observer Pattern for UI State Updates in Mobile App
- Decision: Implement UI state updates in the mobile app using an Observer-style mechanism (e.g., reactive state management) so that UI components automatically refresh when device states or routines change.
- Rationale:
  - The mobile app must stay synchronized with real-time device status and alerts.
  - Decouples data sources from UI components and avoids manual refresh logic scattered across the app.
- Design Pattern Used: Observer pattern (concrete implementation may be via reactive libraries or pub/sub within the app).
- Scope: Client-side (mobile app) presentation and state management layer. Included here because the app is a core part of the system from the user’s perspective, even though it is not part of the backend architecture.

---

### 3. Summary

- Architectural decisions (AD-1 to AD-5) define the high-level structure, deployment, and cross-cutting concerns of the Smart Home Management System; they are strategic, system-wide, and costly to change.
- Design decisions (DD-1 to DD-5) focus on local implementation choices within specific components or modules; they are tactical, easier to revise, and often use classic design patterns to improve maintainability and flexibility.

