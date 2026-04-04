# Task Management API – Compatibility & Coupling Analysis  
## Architecture Assignment Submission  

**Student:** Vamshi Krishna Jinka  
**Submission Date:** [04-04-2026]

---

# Overview

This submission presents the architectural analysis and evolution strategy of a **Task Management API System**.

The system supports:

- Task creation, retrieval, and updates via REST APIs  
- Multiple clients (Web SPA, Mobile Apps, Partner Integrations)  
- Notification handling for reminders  
- API evolution with backward compatibility  

The assignment focuses on:

- **Coupling and dependency analysis**
- **API compatibility and versioning**
- **Migration strategy and governance policy**

---

# Baseline System

The system consists of:

- Clients: Web SPA, Mobile App, Partner Integrations  
- API Gateway (routing and control)  
- Task API Service  
- Task Store (Database)  
- Notification Service  

Communication is primarily **synchronous REST**, with potential for asynchronous improvements.

---

## Part 1 – Coupling Analysis

### part1_coupling_analysis.md
Provides a detailed analysis of system dependencies:

- Identifies coupling types:
  - Data coupling (JSON DTOs)
  - Temporal coupling (sync REST calls)
  - Control coupling (gateway routing)
  - Deployment coupling
- Explains ripple effects of changes across components  
- Highlights:
  - **Intentionally tight coupling** (Task API ↔ Database, Gateway ↔ API)
  - **Areas for improvement** (Client ↔ API, API ↔ Notification)

---

### part1_coupling_diagram.drawio / .png
Visual representation of system dependencies:

- Components shown as boxes  
- Arrows represent dependencies  
- Labels indicate coupling types and strength  
- Includes legend for interpretation  

Key insights:
- Strong coupling between Task API and database  
- High risk coupling at external boundaries (clients ↔ API)  

---

## Part 2 – Compatibility and Versioning

### part2_compatibility_changes.md
Classification of API changes (A–E):

- Differentiates:
  - **Non-breaking changes** (additive fields, new endpoints)
  - **Breaking changes** (renaming fields, required headers)
  - **Semantic breaking changes** (validation tightening)

Includes:
- Justification for each change  
- Recommended semantic versioning (MAJOR / MINOR)  
- Risks for long-lived clients  

---

### part2_version_coexistence.md
Defines strategy for running multiple API versions:

- Uses **path-based versioning** (`/v1`, `/v2`)  
- Supports:
  - Legacy clients on v1  
  - New clients on v2  
- Includes:
  - Migration plan  
  - Deprecation timeline  
  - Sunset strategy  

Trade-offs:
- Increased operational complexity  
- Dual maintenance of API versions  

---

## Part 3 – Policy and Migration Story

### part3_compatibility_policy.md
Defines governance rules for API evolution:

- Clear distinction between additive and breaking changes  
- Mandatory versioning for breaking changes  
- Deprecation process:
  - Notice period  
  - Communication channels  
  - Sunset headers  

Includes:
- Stable error format policy  
- Error code consistency rules  
- Different handling for:
  - Partner integrations (strict stability)
  - First-party apps (faster adaptation)

---

### part3_migration_sequence.drawio / .png
Sequence diagram illustrating migration from v1 to v2:

- Shows:
  - Client calling v1 API  
  - Receiving deprecation notice  
  - Migrating to v2  
- Includes participants:
  - Client  
  - API Gateway  
  - Task API v1  
  - Task API v2  
  - Task Store  
  - Notification Service  

Highlights:
- Version coexistence  
- Gateway-based routing  
- Updated request/response contract in v2  

---

# Architectural Summary

The Task Management API demonstrates:

- **Layered architecture with gateway routing**
- **Strong internal coupling for performance-critical components**
- **Loose external coupling via versioning and contracts**
- **Safe API evolution through backward-compatible strategies**

Key architectural practices:

- Prefer additive, non-breaking changes  
- Use semantic versioning for controlled evolution  
- Support long-lived clients with stability guarantees  
- Introduce asynchronous communication to reduce temporal coupling  

---

# Conclusion

This submission demonstrates a structured approach to:

- Analyzing system coupling and dependencies  
- Designing backward-compatible API evolution strategies  
- Managing version coexistence and migration  
- Establishing governance policies for sustainable system growth  

The system is designed to balance **stability, flexibility, and scalability**, ensuring smooth evolution without disrupting existing clients.

---