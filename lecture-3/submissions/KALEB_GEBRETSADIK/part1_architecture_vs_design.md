# Part 1: Architecture vs. Design Documentation

**System**: Smart Home Management System

---

## Architectural Decisions

> Architectural decisions are **strategic, system-wide** choices that shape the overall structure and cannot be easily changed without significant effort.

---

### AD-1: Adopt a Microservices Architecture

- **Decision Statement**: The system will be decomposed into independently deployable microservices (Device Manager, Security Service, etc.) rather than a single monolithic application.
- **Rationale**: Each domain (device control, security, scheduling) has different scaling needs and development lifecycles. Microservices allow each to be deployed and scaled independently.
- **Alternatives Considered**:
  - *Monolithic Architecture*: Simpler to develop initially but creates a single point of failure and makes independent scaling impossible.
  - *SOA (Service-Oriented Architecture)*: Too heavyweight in terms of governance and middleware overhead for this use case.
- **Consequences**:
  - ✅ Independent scaling per service
  - ✅ Fault isolation — one service failure does not crash the whole system
  - ❌ Increased operational complexity (more services to deploy and monitor)
  - ❌ Network latency between services

---

### AD-2: Use an API Gateway as the Single Entry Point

- **Decision Statement**: All external client requests (Mobile App, Web UI) must go through a centralized API Gateway that handles authentication, routing, and rate limiting.
- **Rationale**: Provides a single enforcement point for cross-cutting concerns such as authentication, TLS termination, and rate limiting, avoiding duplication across services.
- **Alternatives Considered**:
  - *Direct client-to-service communication*: Simpler but exposes internal services and duplicates auth logic across every service.
  - *Backend-for-Frontend (BFF)*: Adds a tailored API per client type, which is unnecessary overhead at this stage.
- **Consequences**:
  - ✅ Centralized auth and security enforcement
  - ✅ Clients are decoupled from internal service topology
  - ❌ API Gateway is a potential single point of failure (mitigated by running multiple instances)

---

### AD-3: Use Asynchronous Messaging (MQTT) for IoT Device Communication

- **Decision Statement**: Smart devices (thermostats, lights, locks) communicate with the backend using MQTT over a Message Broker rather than synchronous HTTP calls.
- **Rationale**: IoT devices are resource-constrained and network conditions are unreliable. MQTT's lightweight Pub/Sub model is designed precisely for this scenario.
- **Alternatives Considered**:
  - *REST over HTTP*: Too heavy for constrained IoT devices; not designed for high-frequency telemetry.
  - *WebSockets*: Suitable for real-time bidirectional communication but adds complexity and session management overhead.
- **Consequences**:
  - ✅ Supports thousands of concurrent device connections
  - ✅ Decouples devices from backend services
  - ❌ Requires a separate Message Broker component to manage and operate

---

### AD-4: Persist All Data in a Relational Database (PostgreSQL)

- **Decision Statement**: A single relational database (PostgreSQL) is chosen as the primary data store for device records, user accounts, configurations, and event history.
- **Rationale**: The system's data (devices, users, routines, alerts) is highly relational. A relational database ensures data integrity with foreign key constraints and supports complex queries for reporting.
- **Alternatives Considered**:
  - *NoSQL (MongoDB)*: Flexible schema is not needed; relational integrity is more important.
  - *Time-series DB (InfluxDB)*: Ideal for sensor data but requires operating a second database type; deferred to a future optimization.
- **Consequences**:
  - ✅ Strong data consistency and integrity (ACID transactions)
  - ✅ Mature tooling and wide developer familiarity
  - ❌ Vertical scaling limitations at very high write throughput (can be addressed with read replicas)

---

### AD-5: Deploy the System on Cloud Infrastructure with Containerization (Docker/Kubernetes)

- **Decision Statement**: All microservices will be containerized using Docker and orchestrated with Kubernetes, deployed on a cloud provider (e.g., AWS or GCP).
- **Rationale**: Containerization ensures environment consistency across development, staging, and production. Kubernetes provides automated scaling, self-healing, and rolling deployments.
- **Alternatives Considered**:
  - *Virtual Machines (VMs)*: Heavier, slower to provision, and less portable than containers.
  - *Serverless Functions*: Suitable for event-driven tasks but introduces cold-start latency and is harder to debug for stateful services.
- **Consequences**:
  - ✅ Consistent environments from dev to production
  - ✅ Auto-scaling and high availability
  - ❌ Kubernetes has a steep learning curve and operational overhead

---

## Design Decisions

> Design decisions are **tactical, component-level** choices that determine the internal implementation of a specific component.

---

### DD-1: Use JWT (JSON Web Tokens) for Session Management in the API Gateway

- **Decision Statement**: The API Gateway will validate incoming requests using stateless JWT tokens, verifying the signature without calling a central session store.
- **Rationale**: JWTs are self-contained and stateless, eliminating the need for a distributed session store and allowing any Gateway instance to validate a token independently.
- **Design Pattern**: Token-based authentication
- **Scope**: Component — API Gateway

---

### DD-2: Apply the Repository Pattern for Database Access in Device Manager

- **Decision Statement**: The Device Manager will use a Repository pattern to abstract all database queries behind a `DeviceRepository` interface.
- **Rationale**: Decouples business logic from the persistence layer, making it easy to swap out the database implementation and unit-test the service with mock repositories.
- **Design Pattern**: Repository Pattern
- **Scope**: Class — `DeviceRepository` within the Device Manager service

---

### DD-3: Use an In-Memory HashMap for Device State Cache in Device Manager

- **Decision Statement**: The Device Manager will maintain a `HashMap<DeviceId, DeviceState>` in memory to serve the latest known device state without hitting the database on every read.
- **Rationale**: Device state reads are far more frequent than writes. An in-memory cache dramatically reduces database load and reduces read latency from ~10ms to <1ms.
- **Design Pattern**: Cache-Aside Pattern
- **Scope**: Class — `DeviceStateCache` within the Device Manager service

---

### DD-4: Use the Observer Pattern for Alert Dispatching in the Security Service

- **Decision Statement**: The Security Service will implement an Observer pattern where alert handlers (email, push notification, SMS) subscribe to security events and are notified automatically.
- **Rationale**: Decouples alert generation from alert delivery. New notification channels can be added by registering a new observer without modifying the alert detection logic.
- **Design Pattern**: Observer Pattern
- **Scope**: Component — Security Service, `AlertDispatcher` class

---

### DD-5: Use Exponential Backoff for Device Command Retries in Device Manager

- **Decision Statement**: When a command sent to a smart device fails (e.g., no acknowledgment within timeout), the Device Manager will retry using an exponential backoff strategy with a maximum of 3 retries.
- **Rationale**: Devices may be temporarily offline or unreachable. Exponential backoff prevents thundering-herd conditions caused by simultaneous retries from multiple devices.
- **Design Pattern**: Retry with Exponential Backoff
- **Scope**: Method — `sendCommand()` in the `DeviceCommandService` class
