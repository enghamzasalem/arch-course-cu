# Architectural Smells Analysis  

---

# 1. Introduction

Architectural smells are warning signs of structural design problems.  
They indicate potential violations of architectural principles such as low coupling, high cohesion, and clear separation of concerns.

This document identifies two architectural smells in the Smart Home Management System and proposes refactoring solutions.

---

# 2. Identified Architectural Smells

---

## Smell 1: God Component

### Name of Smell
God Component

### Where It Appears

The **Device Manager Service** handles:

- Device communication
- Retry logic
- Device state tracking
- Device authentication
- Command routing
- Error handling
- Logging

Because it directly communicates with all smart devices and manages multiple responsibilities, it risks becoming overly centralized.

---

### Why It Is a Problem

A God Component:

- Violates Single Responsibility Principle
- Increases coupling
- Becomes hard to maintain
- Becomes difficult to scale
- Increases risk of cascading failures

If Device Manager fails, device communication across the entire system may fail.

---

### Proposed Solution

Refactor Device Manager into smaller components:

- Device Communication Service
- Device State Service
- Device Authentication Service
- Retry & Monitoring Module

This distributes responsibilities and improves modularity.

---

## Smell 2: Shared Database Coupling

### Name of Smell
Tangled Dependencies (Shared Data Coupling)

### Where It Appears

All microservices (Device Manager, Security Service, Automation Service, Energy Monitoring) use the same centralized database.

This creates implicit coupling between services.

---

### Why It Is a Problem

Shared database coupling:

- Reduces service independence
- Prevents independent deployment
- Creates schema-level coupling
- Increases risk of cascading data changes
- Violates microservices best practices

Services become tightly connected through shared data structures.

---

### Proposed Solution

Adopt database-per-service approach:

- Device Service Database
- Automation Service Database
- Security Service Database
- Energy Monitoring Database

Services communicate through APIs instead of direct database access.

This increases decoupling and improves scalability.

---

# 3. Refactoring Summary

| Smell | Risk Level | Refactoring Strategy |
|-------|-----------|---------------------|
| God Component | High | Decompose Device Manager into smaller services |
| Shared Database Coupling | Critical | Introduce database-per-service model |

---

# 4. Benefits of Refactoring

After refactoring:

- Improved service isolation
- Reduced coupling
- Easier scaling
- Improved maintainability
- Clearer responsibility boundaries
- Better alignment with microservices principles

---

# 5. Conclusion

Two architectural smells were identified:

1. God Component (Device Manager overload)
2. Shared Database Coupling (Tangled dependencies)

Addressing these smells strengthens the system architecture and improves long-term sustainability.