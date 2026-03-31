## Part 3.2 – Architectural Decision Records (ADRs)

---

# ADR-001: Choose Microservices Architecture over Monolith

## Status
Accepted

## Context
The Smart Home Management System must support:
- A growing number of households and smart devices.
- Real-time control and monitoring (lights, locks, thermostats, cameras).
- Security-critical features (alerts, access control).
- Continuous evolution as new device types, vendors, and automation scenarios emerge.

A monolithic architecture would be simpler initially but may become difficult to scale and evolve as the system grows. Different parts of the system (e.g., security alerts vs. analytics) have different scalability, availability, and performance needs.

## Decision
Adopt a microservices architecture with services such as:
- API Gateway
- User & Access (Identity and Access Management)
- Device Management
- Security & Alerts
- Automation & Scheduling
- Analytics & Reporting

Each service will own its own data store and be independently deployable and scalable.

## Consequences
- Positive:
  - Independent scaling of services based on load characteristics.
  - Fault isolation: failures in one service (e.g., Analytics) are less likely to affect critical services (e.g., Security & Alerts).
  - Enables autonomous teams to own specific services and domains.
- Negative:
  - Increased operational complexity (service discovery, observability, distributed tracing).
  - Requires mature DevOps practices and tooling for CI/CD, monitoring, and incident response.
- Neutral:
  - Requires clearly defined APIs and contracts between services, which can improve documentation and communication.

## Alternatives Considered
- Monolithic architecture:
  - Not chosen due to limited scalability and difficulty evolving distinct functional areas independently.
- Modular monolith:
  - Better structuring than a pure monolith but still limited in independent deployment and technology heterogeneity.

---

# ADR-002: Choose PostgreSQL for Core Relational Data

## Status
Accepted

## Context
The system needs to persist core relational data, including:
- Users, roles, and permissions.
- Households and device registrations.
- Automation routines and schedules.

This data requires strong consistency, transactions, and support for complex queries and reporting. The chosen database should be widely supported, reliable, and integrate well with cloud environments.

## Decision
Use PostgreSQL as the primary relational database for core services (e.g., User & Access, Device Management, Automation & Scheduling).

## Consequences
- Positive:
  - Mature, feature-rich relational database with strong ACID guarantees.
  - Broad ecosystem support (drivers, ORMs, tooling) and compatibility with major cloud providers.
  - Good support for JSON fields where semi-structured data is needed.
- Negative:
  - Vertical scaling has limits; for extreme workloads, sharding/partitioning strategies are required.
  - Requires operational expertise for tuning, backups, and high availability setups (e.g., replicas, failover).
- Neutral:
  - Does not preclude using other specialized stores (e.g., time-series DB, cache) for non-relational or high-volume telemetry data.

## Alternatives Considered
- MySQL/MariaDB:
  - Similar capabilities but PostgreSQL’s richer feature set and JSON support gave it an edge.
- NoSQL store as primary DB (e.g., DynamoDB, MongoDB):
  - Better horizontal scalability but weaker support for complex relational queries and transactions, which are important for security and configuration data.

---

# ADR-003: Deploy on Managed Kubernetes in Public Cloud

## Status
Proposed

## Context
Backend services must be deployed in an environment that supports:
- High availability and automatic recovery.
- Horizontal scaling based on workload.
- Rolling updates and controlled deployments.

The team wants to avoid managing low-level infrastructure manually (servers, OS patching) and prefers leveraging managed services where possible.

## Decision
Deploy backend microservices on a managed Kubernetes offering in a public cloud (e.g., GKE, EKS, or AKS). Use containers for all services, with:
- Declarative deployment manifests (or Helm charts).
- Horizontal Pod Autoscalers for critical services.
- Managed load balancers and persistent storage.

## Consequences
- Positive:
  - Built-in support for self-healing, rolling updates, and autoscaling.
  - Strong ecosystem for observability (metrics, logging, tracing) and service mesh integration if needed.
  - Portable deployment model across cloud providers (to some extent).
- Negative:
  - Steep learning curve for Kubernetes concepts (pods, services, ingresses, RBAC, etc.).
  - More complex local development and testing environments.
- Neutral:
  - Some operational responsibility remains (cluster configuration, upgrades), but less than fully self-managed infrastructure.

## Alternatives Considered
- VM-based deployment:
  - Simpler for small systems but requires more manual work for scaling, failover, and deployments.
- Serverless-only approach (functions as a service):
  - Attractive for event-driven workloads, but less suitable for long-running services, stateful components, and complex networking needs.
