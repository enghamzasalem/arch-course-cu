# Part 1: Coupling Analysis

## Task 1.1: Coupling Inventory

### Objective
Map dependencies in the system and characterize the types of coupling between components.

---

## 1. System Elements

The following core elements are considered:

- Web SPA (Single Page Application)
- Mobile App
- Partner Clients (long-lived integrations)
- API Gateway
- Task API Service
- Task Store (Database)
- Notification Service

---

## 2. Dependency & Coupling Analysis

### 2.1 Web SPA → Task API
- **Direction**: Web SPA depends on Task API  
- **Type of Coupling**: Data coupling (JSON schema), Temporal coupling (request/response)  
- **Ripple Effect**:  
  - Changes in API response fields (e.g., renaming `done → completed`) can break UI rendering  
  - New required headers (e.g., `X-Client-Id`) may cause request failures  

---

### 2.2 Mobile App → Task API
- **Direction**: Mobile App depends on Task API  
- **Type of Coupling**: Data coupling, Temporal coupling  
- **Ripple Effect**:  
  - Mobile apps are harder to update → breaking API changes affect users longer  
  - Validation changes (e.g., title length reduction) may cause runtime errors  

---

### 2.3 Partner Clients → Public API
- **Direction**: Partner Clients depend on Public API  
- **Type of Coupling**: Data coupling, Contract coupling (strict API expectations), Temporal coupling  
- **Ripple Effect**:  
  - Renaming fields or changing required headers can break integrations  
  - Partners often use strict parsers → additive fields may also break them  

---

### 2.4 API Gateway → Task API Service
- **Direction**: API Gateway depends on Task API Service  
- **Type of Coupling**: Control coupling (routing logic), Deployment coupling  
- **Ripple Effect**:  
  - Changes in service endpoints require gateway configuration updates  
  - Versioning mismatches may cause routing failures  

---

### 2.5 Task API Service → Task Store (Database)
- **Direction**: Task API depends on Task Store  
- **Type of Coupling**: Data coupling (schema), Implementation coupling  
- **Ripple Effect**:  
  - Schema changes (e.g., adding/removing fields) require code updates  
  - Storage migration impacts service logic  

---

### 2.6 Task API Service → Notification Service
- **Direction**: Task API depends on Notification Service  
- **Type of Coupling**: Temporal coupling (triggering events), Control coupling  
- **Ripple Effect**:  
  - If notification service is unavailable, task operations may fail or degrade  
  - Changes in notification API affect task workflows  

---

## 3. Intentionally Tight Coupling (Acceptable Trade-offs)

### 3.1 Task API ↔ Task Store
- **Reason**:  
  - High performance and consistency requirements  
  - Direct schema access simplifies implementation  
- **Trade-off**:  
  - Reduced flexibility in changing storage layer  

---

### 3.2 API Gateway ↔ Task API
- **Reason**:  
  - Centralized routing and security enforcement  
  - Tight integration improves performance and control  
- **Trade-off**:  
  - Requires coordinated updates during API changes  

---

## 4. Areas to Reduce Coupling

### 4.1 Client (Web/Mobile/Partner) ↔ Task API

- **Problem**: Strong data and contract coupling  
- **Solution**:
  - Introduce **API versioning** (e.g., `/v1`, `/v2`)  
  - Use **backward-compatible changes** (additive fields)  
  - Provide **aliasing** (e.g., support both `done` and `completed`)  
  - Use **lenient parsing** on server side  

---

### 4.2 Task API ↔ Notification Service

- **Problem**: Temporal and control coupling (synchronous dependency)  
- **Solution**:
  - Introduce **asynchronous communication** (message queue/event bus)  
  - Use **event-driven architecture** (e.g., "TaskCreated" event)  
  - Decouple failure handling (notifications can retry independently)  

---

## 5. Summary

- The system exhibits multiple forms of coupling: **data, control, temporal, and deployment coupling**  
- **Client–API coupling is the most critical**, especially for long-lived partner integrations  
- Tight coupling is acceptable in **internal, performance-critical components**  
- Loose coupling should be prioritized at **external boundaries** using:
  - versioning  
  - abstraction  
  - asynchronous communication  

---