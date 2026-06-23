# Model Documentation

## Overview

This document describes the modeling approach used to design and document the architecture of the **Video Streaming Platform**.  
The architecture was modeled using **C4 model diagrams** and **UML diagrams** to represent the system from different perspectives and abstraction levels.

The diagrams created in this assignment help explain the system structure, interactions between components, and deployment infrastructure.

---

# a) Modeling Approach

## Modeling Notations Used

Two main modeling notations were used:

### C4 Model
The **C4 model** was used to represent the software architecture at different levels of abstraction.

The following C4 diagrams were created:

- **System Context Diagram (Level 1)**
- **Container Diagram (Level 2)**
- **Component Diagram (Level 3)**

The C4 model was chosen because it provides a **clear hierarchical structure**, allowing stakeholders to understand the system from a high-level overview down to internal components.

### UML Diagrams
Two **UML diagrams** were used to model system behavior and infrastructure:

- **Sequence Diagram**
- **Deployment Diagram**

UML diagrams were chosen because they are a **standardized modeling language widely used in software engineering** and provide clear notation for interactions and infrastructure.

---

## Why These Notations Were Chosen

The combination of **C4 and UML** provides a complete view of the system architecture.

| Modeling Approach | Purpose |
|-------------------|--------|
| C4 Model | Explains the structure of the system and its components |
| UML Sequence Diagram | Shows how system components interact over time |
| UML Deployment Diagram | Shows where software components are deployed |

This approach allows both **technical and non-technical stakeholders** to understand the system.

---

## Relationship Between the Diagrams

The diagrams follow a **top-down architectural approach**.

1. **System Context Diagram**
   - Shows the video streaming platform and its external users and systems.

2. **Container Diagram**
   - Breaks the system into major applications and services.

3. **Component Diagram**
   - Decomposes one container (Backend API) into internal components.

4. **Sequence Diagram**
   - Demonstrates runtime interaction between components during a use case.

5. **Deployment Diagram**
   - Shows the physical infrastructure where containers are deployed.

This layered approach ensures that the architecture is **easy to understand and trace from high-level system overview to detailed interactions**.

---

# b) Diagram Index

| Diagram Name | Diagram Type | Purpose | Audience |
|---------------|--------------|---------|----------|
| Video Streaming Platform Context | C4 System Context | Shows system boundary, users, and external systems | Stakeholders, Developers |
| Video Streaming Platform Containers | C4 Container Diagram | Shows high-level software architecture and services | Developers, Architects |
| Backend API Components | C4 Component Diagram | Shows internal structure of the backend API container | Developers |
| User Watches Video | UML Sequence Diagram | Shows interaction flow when a user watches a video | Developers, Testers |
| Infrastructure Deployment | UML Deployment Diagram | Shows servers, infrastructure, and deployment environment | DevOps, Architects |

---

# c) Consistency Check

## Ensuring Consistency Across Diagrams

Consistency between diagrams was maintained by:

- Using **the same container and component names across all diagrams**
- Maintaining **consistent terminology** (e.g., Backend API, Recommendation Service)
- Ensuring **sequence diagram participants match components from container diagrams**
- Mapping containers to **deployment nodes in the deployment diagram**
- Following **standard C4 and UML notation conventions**

This ensures that all diagrams represent the same architecture without contradictions.

---

## Assumptions and Simplifications

Some assumptions and simplifications were made to keep the architecture clear:

- The **Backend API and Streaming Service were grouped within the Application Server** in the deployment diagram.
- The **Recommendation Service was modeled as a separate service** for scalability.
- The **CDN was represented as a single node**, although in reality it would consist of multiple distributed servers.
- Security layers, caching systems, and monitoring tools were simplified or omitted to keep diagrams focused.

These simplifications help maintain readability while still representing the key architectural elements.

---

# Diagram References

The following diagrams are included in this project:

- `part1_context_diagram.png`
- `part1_container_diagram.png`
- `part1_component_diagram.png`
- `part2_sequence_diagram.png`
- `part2_deployment_diagram.png`
