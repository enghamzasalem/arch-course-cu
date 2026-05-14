# Part 2: Compatibility and Versioning

## Task 2.2: Version Coexistence

### Objective
Define a strategy to allow v1 and v2 of the API to coexist during client migration.

---

## 1. Chosen Strategy: Path-Based Versioning

We use **path versioning**:

- v1 → `/v1/tasks`
- v2 → `/v2/tasks`

This approach is explicit, easy to understand, and widely supported across clients and gateways.

---

## 2. Coexistence Plan

### 2.1 Legacy Clients (v1)
- Continue using existing endpoints under `/v1`
- No changes required in request/response format
- Supported during a defined **sunset period**

### 2.2 New Clients (v2)
- Use `/v2` endpoints with updated API contract:
  - `done → completed`
  - Required `X-Client-Id` header
  - Updated validation rules (e.g., title length ≤ 100)
  - New features (e.g., `/tasks/bulk`, `priority` field)

---

## 3. Migration Strategy

- Release v2 alongside v1 (no immediate deprecation)
- Communicate changes clearly via:
  - API documentation
  - Release notes
  - Migration guides
- Encourage new integrations to adopt v2
- Gradually migrate internal and partner clients
- Monitor usage of v1 endpoints

---

## 4. Sunset Plan

- Define a **deprecation timeline** (e.g., 6–12 months)
- Notify clients in advance using:
  - API response headers (e.g., `Deprecation`, `Sunset`)
  - Email or partner communication
- After the sunset period:
  - Disable `/v1` endpoints
  - Return appropriate error responses

---

## 5. Operational Cost

- **Dual maintenance overhead**:
  - Two API versions must be deployed, tested, and monitored simultaneously
  - Increased complexity in routing (API Gateway must handle `/v1` and `/v2`)
  - Documentation must be maintained for both versions

---

## 6. Summary

- Path versioning enables **clear separation** between versions  
- v1 ensures **stability for legacy clients**  
- v2 enables **safe evolution and improvements**  
- A controlled sunset process ensures smooth migration without breaking clients  

---