# Part 2.2 — Version Coexistence Strategy

## 1. Chosen Strategy: Path-Based Versioning

We use **URL path versioning**:

- v1: `/api/v1/tasks`  
- v2: `/api/v2/tasks`  

### Why this approach?
- Simple and explicit for clients  
- Easy to implement routing at the API Gateway  
- Clearly separates breaking changes between versions  
- Well-suited for external partner integrations  

---

## 2. Coexistence Plan (v1 + v2)

### New Clients
- Use **v2 endpoints** (`/api/v2/...`)  
- Receive the new behavior:  
  - Renamed fields (e.g., `completed`)  
  - Updated validation rules  
  - Required headers (e.g., `X-Client-Id`)  

### Existing Clients (Legacy)
- Continue using **v1 endpoints**  
- Behavior remains unchanged:  
  - `done` field is still present  
  - No `X-Client-Id` required  
  - Title length limit remains 500 characters  

---

### API Gateway Role
The **API Gateway** handles version routing:

- `/api/v1/*` → Task API v1  
- `/api/v2/*` → Task API v2  

Benefits:  
- Each version can be deployed independently  
- Gradual migration is possible without downtime  

---

## 3. Sunset and Migration

- Deprecation of **v1** is announced in advance (e.g., 6–12 months)  
- Provide clear migration guidance:  
  - Documentation on field mapping (`done` → `completed`)  
  - Examples of v2 usage  
- After the sunset period, v1 endpoints are removed  

---

## 4. Operational Cost

Running multiple versions introduces:  

- **Maintenance effort:** Both API versions need support and testing  
- **Gateway complexity:** Routing rules and monitoring per version  
- **Documentation overhead:** Separate guides for v1 and v2  

