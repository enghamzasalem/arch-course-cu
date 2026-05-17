# Part 1.1 - Coupling Inventory and Analysis

## System elements

I use these 7 elements from the baseline scenario:

1. Web SPA
2. Mobile App
3. Partner Client (long-lived integration)
4. API Gateway
5. Task API Service
6. Task Store (DB)
7. Notification Service

## Dependency inventory with coupling types

### 1) Web SPA -> API Gateway
- **Direction:** Web SPA depends on API Gateway.
- **Coupling type:** Data coupling + temporal coupling.
- **Ripple risk:** If response JSON fields change (`done` -> `completed`) or required header rules change (`X-Client-Id`), SPA requests or UI mapping can fail immediately.

### 2) Mobile App -> API Gateway
- **Direction:** Mobile App depends on API Gateway.
- **Coupling type:** Data coupling + temporal coupling.
- **Ripple risk:** Mobile app release cycles are slow; breaking contract changes force urgent app updates and can keep old broken clients in production.

### 3) Partner Client -> API Gateway
- **Direction:** Partner systems depend on API Gateway.
- **Coupling type:** Contract coupling + temporal coupling.
- **Ripple risk:** Partners often have strict schemas and less frequent deployments, so renamed fields or stricter validation can break integrations for long periods.

### 4) API Gateway -> Task API Service
- **Direction:** Gateway depends on Task API.
- **Coupling type:** Control coupling + temporal coupling (sync HTTP).
- **Ripple risk:** Route changes, auth checks, version routing, or error-shape changes require coordinated deployment and config updates in both layers.

### 5) Task API Service -> Task Store
- **Direction:** Task API depends on DB schema and query behavior.
- **Coupling type:** Data coupling + schema coupling.
- **Ripple risk:** If persistence schema changes (e.g., `done` column replaced by `completed`), API serialization and query code must change together.

### 6) Task API Service -> Notification Service
- **Direction:** Task API depends on notification API or event contract.
- **Coupling type:** Temporal coupling (if sync call) or event/data coupling (if async).
- **Ripple risk:** Synchronous reminder calls can increase request latency and failure propagation; contract mismatch in event payload causes missed reminders.

### 7) API Gateway -> Auth/Policy rules (cross-cutting)
- **Direction:** Gateway depends on policy configuration.
- **Coupling type:** Control coupling.
- **Ripple risk:** A new required header or policy rule can instantly reject traffic from all clients if rollout is not staged.

## Tight coupling that is acceptable (intentional)

### A) Task API <-> Task Store
- **Why acceptable:** This is a core business boundary where strict consistency and transactional behavior matter.
- **Trade-off:** Tight schema coupling enables efficient queries and predictable writes.

### B) API Gateway <-> Public API policy
- **Why acceptable:** Centralized enforcement (auth, quotas, required headers, version routing) is desirable for governance and observability.
- **Trade-off:** Policy changes must be staged carefully, but central control reduces duplicated logic in services.

## Coupling I would reduce

### A) Reduce synchronous coupling: Task API -> Notification
- **Current issue:** If Task API waits for notification service in request path, failures cascade.
- **Improve with:** Async eventing (`task.created`, `task.updated`) via queue/topic.
- **Benefit:** Lower temporal coupling; notification outages do not block task operations.

### B) Reduce client contract fragility: Clients -> API response schema
- **Current issue:** Strict field renames (`done` -> `completed`) break clients.
- **Improve with:** Versioned contracts (`/v1`, `/v2`), deprecation window, additive-first changes, and gateway field adapters where needed.
- **Benefit:** Reduced ripple effect and safer migration for mobile/partner clients.

## Coupling hotspots summary

1. **Public JSON contract** (clients break on schema/header changes).
2. **Gateway routing/policy layer** (single point of global behavior change).
3. **Task API to Notification synchronization** (runtime availability coupling).
4. **DB schema changes surfaced to API** (internal data coupling leaks externally if not abstracted).

## Conclusion

The system's main risk is not "many dependencies" alone, but **high-impact contract and temporal dependencies** at the public API boundary. The right strategy is:
- keep intentionally tight coupling where domain consistency needs it,
- reduce harmful coupling via versioning, async boundaries, and stable contracts.
