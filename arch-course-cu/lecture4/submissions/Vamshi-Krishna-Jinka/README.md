# Video Streaming Platform  
## Software Architecture Modeling Assignment  

**Student:** Vamshi Krishna Jinka  
**Submission date:** [05-03-2026]


---

# Overview

This submission presents the architectural modeling of a **Video Streaming Platform** using industry-standard architecture modeling techniques.

The platform allows users to:

- Browse and watch video content
- Receive personalized video recommendations
- Manage subscriptions
- Upload and manage video content (for creators)
- Deliver video streams efficiently through a CDN

The architecture was modeled using:

- **C4 Model diagrams** for system structure
- **UML diagrams** for interaction flow and infrastructure

All diagrams were created using **draw.io (diagrams.net)**.

---

# Part 1 – C4 Architecture Diagrams

## part1_system_context.drawio

Contains the **System Context Diagram (C4 Level 1)** showing:

- The **Video Streaming Platform** as the main system
- External users:
  - Subscriber
  - Content Creator
  - Admin
- External systems:
  - Payment Gateway
  - Content Delivery Network (CDN)
- Relationships describing how users and systems interact with the platform

This diagram provides a **high-level overview of the system boundary and external interactions**.

---

## part1_container_diagram.drawio

Contains the **Container Diagram (C4 Level 2)** showing the high-level software architecture of the system.

Containers included:

- Web Application (React)
- Mobile Application
- Backend API (Node.js)
- Recommendation Service
- Streaming Service
- Database (PostgreSQL)

The diagram illustrates:

- Container responsibilities
- Communication protocols (HTTPS, REST, SQL)
- Data flow between services

This diagram explains **how the system is structured into major applications and services**.

---

## part1_component_diagram.drawio

Contains the **Component Diagram (C4 Level 3)** for the **Backend API container**.

Components include:

- Auth Controller
- Video Controller
- Recommendation Client
- User Repository

The diagram shows:

- Internal structure of the backend API
- Dependencies between components
- Interfaces used for communication

This diagram provides **a detailed internal view of one container**.

---

# Part 2 – UML Behavioral and Infrastructure Models

## part2_sequence_diagram.drawio

Contains a **UML Sequence Diagram** for the use case:

**User Watches a Video**

Participants include:

- User
- Web Application
- API Gateway
- Streaming Service
- Database
- CDN
- Recommendation Service

The diagram shows:

- Request flow when a user selects a video
- Metadata retrieval
- Streaming service interaction
- CDN video delivery
- Recommendation system update

This diagram illustrates **runtime interaction between system components**.

---

## part2_deployment_diagram.drawio

Contains the **UML Deployment Diagram** showing the infrastructure used to deploy the platform.

Nodes included:

- User Device
- Web Server
- Application Server
- Recommendation Server
- Database Server
- CDN Network

Artifacts deployed:

- React Web App
- Backend API
- Streaming Service
- Recommendation Service
- PostgreSQL Database

The diagram illustrates **where system containers are deployed and how infrastructure nodes communicate**.

---

# Part 3 – Model Documentation

## part3_model_documentation.md

This document explains the **modeling approach and relationships between diagrams**.

It includes:

- Modeling notations used (C4 and UML)
- Rationale for choosing these modeling techniques
- Explanation of diagram relationships
- Diagram index table
- Consistency checks across diagrams
- Assumptions and simplifications made during modeling

The documentation ensures that the architecture models are **clear, consistent, and well explained**.

---

# Architectural Summary

The Video Streaming Platform architecture combines **structural and behavioral models** to represent the system from multiple perspectives.

The architecture includes:

- C4 Context diagram for system boundary
- C4 Container diagram for high-level services
- C4 Component diagram for internal service structure
- UML Sequence diagram for runtime interactions
- UML Deployment diagram for infrastructure design

The system is designed with emphasis on:

- Scalability
- Performance
- Maintainability
- Modular service architecture

Video streaming is optimized using a **Content Delivery Network (CDN)**, while personalization is handled by a **Recommendation Service**.

---

# Conclusion

This submission demonstrates a structured architecture modeling approach using **C4 and UML diagrams**.

The diagrams collectively provide a **complete architectural view of the Video Streaming Platform**, from high-level system context to detailed component interactions and infrastructure deployment.

The modeling approach ensures the architecture is **well documented, understandable, and maintainable** for both technical and non-technical stakeholders.