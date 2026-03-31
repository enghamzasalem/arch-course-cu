**Task 4.2: Architectural Smells Detection - Smart Home Management System**

**Identified Architectural Smells**

**Smell 1: Shared Persistence**

**Where it shows up:** All microservices, like Device Management, Security & Alerts, and Energy Monitoring, share the same single PostgreSQL database. But this goes against the microservices principle of a database per service.

**BEFORE (Current Smelly Architecture):**

**\[Mobile App\] → \[API Gateway\] → \[Device Service\] ──→ \[Shared PostgreSQL\]**

**↓**

**\[Security Service\] ──→ \[Shared PostgreSQL\] ←── \[Energy Service\]**

**Why this matters:**

- Tight coupling: Services cannot independently change the schema
- Single point of failure: System stalls when database goes down
- Limitations in scaling the services
- Limitations in deployment

**Remedy:** Database per Service

Each service should have its own database. Event Sourcing/CQRS should be used to handle cross-service queries.

**AFTER (Refactored):**

**\[Mobile App\] → \[API Gateway\] → \[Device Service\] ──→ \[Device DB\]**

**↓**

**\[Security Service\] ──→ \[Security DB\]**

**↓**

**\[Energy Service\] ──→ \[Energy DB (Timescale)\]**

**↓**

**\[Event Bus\] ←── Events for cross-service sync**

**Smell 2: God Component (API Gateway Overload)**

**Where it shows up:** The API Gateway is a multifunctional role that encompasses authentication, authorization, routing, rate limiting, logging, and actual business logic routing for device commands, security queries, and energy reports.

**BEFORE (Smelly Gateway):**

**\[Mobile App\] ──→ \[API Gateway\*\] ──→ \[Device Service\]**

**\*Does: Auth + Rate Limit + Logging +**

**Device Command Routing + Security Routing +**

**Energy Data Routing + Caching + Metrics**

**↓**

**\[Security Service\] \[Energy Service\]**

**Why it’s a problem:**

- If the API Gateway crashes, the entire system crashes.
- It becomes a performance bottleneck because all requests go through this one piece.
- It breaks the single responsibility principle by performing 8+ functions.
- It makes scaling the system inefficient because the API Gateway needs to be scaled for peak device traffic regardless of security traffic.

**Solution:** Break into Edge Services

Break this into an API Gateway and a Business Orchestration Service.

**AFTER (Refactored):**

**\[Mobile App\] ──→ \[API Gateway\] ──→ \[Orchestration Service\] ──→ \[Device Service\]**

**(Light routing, auth) (Business logic)**

**↓**

**\[Security Service\] \[Energy Service\]**