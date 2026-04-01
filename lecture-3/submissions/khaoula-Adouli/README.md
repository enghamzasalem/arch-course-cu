# Assignment Submission: Lecture 3
Student Name: Khaoula Adouli
Student ID: 30009381 
Submission Date: 26-02-2026

## Overview
This submission presents the architectural design and analysis of a Smart Home Management System developed using concepts from Chapters 1, 2, and 3.
The system follows a Microservices Architecture with an API Gateway to ensure scalability, modularity, and maintainability. The design emphasizes key quality attributes such as availability, performance, security, and scalability.
Potential architectural risks (shared database coupling and API Gateway bottleneck) were identified and refactored to improve system robustness and future scalability.

## Files Included
assignment_overview.md
High-level summary of the assignment and system assumptions.
part1_architecture_vs_design.md
Clear distinction between architectural decisions and design decisions.
part1_component_connector_diagram.drawio (.png)
High-level component and connector view of the Smart Home system.
Part 2 — Multiple Views
part2_multiple_views-Logical View.drawio (.png)
Logical view showing functional components and their relationships.
part2_multiple_views-Physical_Deployment View.drawio (.png)
Physical/deployment view showing where components are deployed in the cloud environment.
part2_multiple_views-Scenarios_Sequence View.drawio (.png)
Sequence view illustrating the scenario: User turns on light via mobile app.
part2_quality_attributes.md
Analysis and prioritization of key quality attributes.
Part 3 — Architectural Pattern
part3_architectural_pattern.drawio (.png)
Diagram illustrating the Microservices architecture with API Gateway.
part3_architectural_decisions.md
Architectural Decision Records (ADRs) documenting key technical choices.
Part 4 — Technical Debt & Smells
part4_architectural_smells.md
Identification and analysis of architectural smells.
part4_smell_refactoring gateway.drawio (.png)
Refactoring of the API Gateway bottleneck using load balancing.
part4_smell_refactoring-Smell 1 - SharedDBSmell.drawio (.png)
Refactoring of the shared database smell toward better service decoupling.

## Key Highlights
Microservices Decomposition
The system is split into independent services (Auth, Device Management, Automation, Security & Notification) enabling scalability and maintainability.
IoT Communication Ready
MQTT over TCP is used for efficient communication with smart devices.
Quality-Driven Architecture
Design decisions were guided by key quality attributes (availability, scalability, performance, security).
Risk Identification & Refactoring
Major architectural smells were detected and improved through targeted refactoring.

## How to View
Open .drawio files in draw.io / diagrams.net for editable diagrams.
Use .png files for quick visualization.
Read .md files for detailed architectural documentation.
## Conclusion
This assignment demonstrates the application of software architecture principles to design a realistic Smart Home Management System. The final architecture is modular, scalable, and maintainable, with identified risks addressed through appropriate refactoring strategies.
End of README