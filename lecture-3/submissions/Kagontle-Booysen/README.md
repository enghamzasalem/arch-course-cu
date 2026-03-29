# Smart Home Management System  
## Software Architecture Assignment — Lecture 3  

**Student Name:** Kagontle Booysen  
**Student ID:** 30009255  
**Course:** Software Architecture  
**Submission Date:** 27/02/2026

---

# 1. Project Overview

This project presents the complete architectural design and analysis of a **Smart Home Management System**.

The system allows homeowners to:

- Control smart devices (lights, thermostats, locks, cameras)
- Receive security alerts
- Schedule automation routines
- Monitor energy consumption
- Access the system via mobile app, web interface, and voice assistants

The architecture was designed following principles from **Chapter 2 and 3 (Quality Attributes & Architectural Design)**.

---

# 2. Repository Structure
submissions/YOUR_NAME/
├── part1_component_connector_diagram.drawio
├── part1_component_connector_diagram.png
├── part1_architecture_vs_design.md
├── part2_quality_attributes.md
├── part2_multiple_views.drawio
├── part2_multiple_views.png
├── part3_architectural_pattern.drawio
├── part3_pattern_justification.md
├── part4_technical_debt.md
├── part4_architectural_smells.md
├── part4_smell_refactoring.drawio
└── README.md


---

# 3. Part 1 — Architecture Foundations

## 3.1 Component and Connector Diagram

The system architecture includes:

- Mobile App
- Web App
- API Gateway
- Identity Service
- Device Manager
- Automation Service
- Notification Service
- Event Bus
- Databases

The diagram shows:
- REST communication
- Event-driven messaging
- Database connections
- Device communication (MQTT/WebSocket)

This establishes the high-level system structure.

---

## 3.2 Architecture vs Design Decisions

### Architectural Decisions (Strategic)
- Use Microservices architecture
- Introduce API Gateway
- Use Event-Driven communication
- Database per service
- OAuth2/OIDC authentication

### Design Decisions (Tactical)
- Cache device state in memory
- Strategy pattern for automation rules
- Repository pattern for persistence
- Circuit breaker for external providers
- Observer pattern for notifications

Architectural decisions shape the whole system.  
Design decisions shape individual components.

---

# 4. Part 2 — Quality Attributes & Views

## 4.1 Quality Attributes Analysis

Top 5 prioritized attributes:

1. Security (Highest)
2. Availability
3. Performance
4. Scalability
5. Modifiability

A priority matrix was created to:
- Identify critical attributes
- Detect conflicts (e.g., Security vs Performance)
- Explain architectural trade-offs

Trade-offs were clearly documented.

---

## 4.2 Multiple Architectural Views

Three stakeholder-specific views were created:

### Logical View (Developers)
Shows functional components and relationships.

### Deployment View (DevOps)
Shows infrastructure, servers, cloud services, and databases.

### Sequence View (Product/Testers)
Scenario: "User turns on light via mobile app"
Step-by-step interaction from user to device confirmation.

This ensures different stakeholders understand the system from their perspective.

---

# 5. Part 3 — Architectural Pattern Selection

## Selected Pattern:
Hybrid: **Microservices + Event-Driven Architecture**

### Why this pattern:
- Natural fit for device events
- Independent scaling
- Fault isolation
- Strong support for quality attributes

### Trade-offs:
- Increased operational complexity
- Eventual consistency
- Higher infrastructure cost

Alternative patterns considered:
- Layered
- MVC
- Client-Server
- Pure Event-Driven

The hybrid approach best satisfies system requirements.

---

# 6. Part 4 — Technical Debt & Architectural Smells

## 6.1 Technical Debt Analysis

Three potential debt items identified:

1. Overloaded API Gateway (Architectural Debt)
2. Missing Event Schema Versioning (Critical Architectural Debt)
3. Limited Integration Testing (Test Debt)

Each item includes:
- Description
- Type
- Severity
- Principal (cost to fix)
- Interest (ongoing cost)
- Impact
- Prioritized backlog

Debt prioritization considered:
- Interest rate
- Impact on system
- Effort to fix

---

## 6.2 Architectural Smells

Two architectural smells identified:

1. God Component (API Gateway overload)
2. Scattered Security Concerns

For each smell:
- Location identified
- Problem explained
- Refactoring solution proposed
- Before and After diagram provided

Refactoring improves:
- Separation of concerns
- Maintainability
- Scalability
- Security

---

# 7. Key Architectural Strengths

- Clear separation of concerns
- Domain-based microservices
- Event-driven decoupling
- Database-per-service pattern
- Explicit quality attribute prioritization
- Stakeholder-focused documentation
- Technical debt awareness
- Refactoring strategy defined

---

# 8. How to View the Submission

1. Open `.drawio` files using draw.io (diagrams.net)
2. View `.png` files for quick reference
3. Read `.md` files for detailed documentation

---

# 9. Conclusion

This submission demonstrates:

- Systematic architectural reasoning
- Alignment between requirements and architectural decisions
- Clear trade-off analysis
- Multiple stakeholder perspectives
- Identification of risks and improvement strategies

The architecture is scalable, secure, and maintainable while acknowledging technical debt and potential architectural improvements.
