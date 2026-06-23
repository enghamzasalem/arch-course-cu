# Assignment Submission: Lecture 4

**Student Name**: Khaoula Adouli
**Student ID**:30009381
**Submission Date**: 05/03/2026 

---

# Overview

This assignment presents the architecture modeling of a **Video Streaming Platform** similar to Netflix.

The goal of this assignment is to model the system using **C4 architecture diagrams and UML diagrams** in order to represent the system structure, interactions, and infrastructure.

The platform allows users to browse videos, stream content, manage watchlists, and receive personalized recommendations.

---

# Files Included

- `part1_context_diagram.drawio (.png)`
  - System Context Diagram (C4 Level 1)

- `part1_container_diagram.drawio (.png)`
  - Container Diagram (C4 Level 2)

- `part1_component_diagram.drawio (.png)`
  - Component Diagram (C4 Level 3)

- `part2_sequence_diagram.drawio (.png)`
  - UML Sequence Diagram showing the **User Watches Video** use case

- `part2_deployment_diagram.drawio (.png)`
  - UML Deployment Diagram showing the system infrastructure

- `part3_model_documentation.md`
  - Documentation describing modeling approach and diagram consistency

---

# Architecture Highlights

### System Context
Shows the interaction between users and the Video Streaming Platform, including external services such as the CDN and Payment Gateway.

### Container Architecture
The system is decomposed into major containers such as:
- Web Application
- API Server
- Recommendation Service
- Database

### Component Structure
The API container is further decomposed into internal components responsible for authentication, video management, and recommendation integration.

### Runtime Interaction
The Sequence Diagram models the process of a user watching a video and the interactions between the client, API, services, and database.

### Infrastructure Deployment
The Deployment Diagram illustrates how the system is deployed across multiple nodes including the user device, web server, application server, and database server.

---

# Tools Used

- **Draw.io / diagrams.net** for architecture diagrams
- **Markdown** for documentation

---

# How to View

1. Open `.drawio` files using **draw.io / diagrams.net**
2. View `.png` files for quick diagram visualization
3. Read `.md` files for documentation