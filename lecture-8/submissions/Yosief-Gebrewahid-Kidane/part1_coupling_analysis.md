# Part 1.1 — Coupling Analysis

## 1. System Elements

The system is made up of the following components:

- Web SPA (browser client)  
- Mobile App  
- Partner Integrations (external clients)  
- API Gateway  
- Task API Service  
- Task Store (database)  
- Notification Service  

---

## 2. Dependency and Coupling Analysis

### 1. Web SPA → API Gateway  
- **Direction:** The Web SPA depends on the API Gateway  
- **Coupling type:**  
  - Data coupling (relies on JSON structure)  
  - Temporal coupling (synchronous HTTP requests)  
- **Ripple effect:**  
  - If response fields change (e.g. renaming `done`), the UI may break  
  - Any latency or downtime directly impacts the user experience  

---

### 2. Mobile App → API Gateway  
- **Direction:** The Mobile App depends on the API Gateway  
- **Coupling type:**  
  - Data coupling (shared JSON schema)  
  - Version coupling (apps update slowly)  
- **Ripple effect:**  
  - Breaking API changes require users to update their apps  
  - Older app versions may stop working entirely  

---

### 3. Partner Integrations → API Gateway  
- **Direction:** Partner systems depend on the API Gateway  
- **Coupling type:**  
  - Strong data/contract coupling via the public API  
  - Long-lived dependency  
- **Ripple effect:**  
  - Breaking changes can disrupt external business systems  
  - Coordination is difficult, making changes risky  

---

### 4. API Gateway → Task API Service  
- **Direction:** The Gateway depends on the Task API  
- **Coupling type:**  
  - Control coupling (routing and request forwarding)  
  - Interface coupling (endpoint definitions)  
- **Ripple effect:**  
  - Changes to endpoints or routes require updates in the gateway  
  - Versioning introduces additional routing complexity  

---

### 5. Task API → Task Store (Database)  
- **Direction:** The Task API depends on the database  
- **Coupling type:**  
  - Data coupling (schema, tables, fields)  
  - Implementation coupling  
- **Ripple effect:**  
  - Database schema changes require corresponding API changes  
  - Tight coupling reduces flexibility when evolving the system  

---

### 6. Task API → Notification Service  
- **Direction:** The Task API depends on the Notification Service  
- **Coupling type:**  
  - Temporal coupling (if calls are synchronous)  
  - Looser coupling if implemented asynchronously  
- **Ripple effect:**  
  - If synchronous, failures in the notification service can impact API responses  
  - Adds complexity through retries and error handling  

---

## 3. Intentionally Tight Coupling (Acceptable Trade-offs)

### 1. Task API ↔ Task Store  
- **Reason:**  
  - Ensures high performance and strong consistency  
- **Trade-off:**  
  - Less flexibility, but faster and more reliable operations  

---

### 2. Web SPA ↔ API (JSON contract)  
- **Reason:**  
  - The UI depends directly on API data to render correctly  
- **Trade-off:**  
  - While some coupling is necessary, it should still be minimized through stable contracts and versioning  

---

## 4. Areas to Reduce Coupling

### 1. Task API → Notification Service  
- **Problem:**  
  - Strong temporal coupling due to synchronous calls  
- **Solution:**  
  - Introduce asynchronous messaging (e.g. event bus or queue)  
- **Benefit:**  
  - Better failure isolation and improved scalability  

---

### 2. Clients → API (strict schema dependency)  
- **Problem:**  
  - Clients break when the API changes  
- **Solution:**  
  - Use API versioning (e.g. v1, v2)  
  - Prefer backward-compatible, additive changes  
- **Benefit:**  
  - Allows clients and API to evolve independently  

