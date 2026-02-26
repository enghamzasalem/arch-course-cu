# Assignment Submission: Lecture 3

**Student Name**: Kaleb Gebretsadik  
**Student ID**: 30008744  
**Submission Date**: 2/26/2026

## Overview

This repository contains my submission for the **Lecture 3: Architecture Diagramming** assignment. The architecture designed across these documents details a **Smart Home Management System**. It utilizes a hybrid Microservices and Event-Driven architecture to successfully handle both synchronous UI requests and high-frequency, asynchronous IoT telemetry.


## Files Included

- **`part1_component_connector_diagram.drawio`** & **`.png`**: High-level Component and Connector diagram (6 components, 5 connectors).
- **`part1_architecture_vs_design.md`**: Breakdown and rationale for 5 strategic Architectural decisions and 5 tactical Design decisions.
- **`part2_quality_attributes.md`**: Analysis of the top 5 quality attributes for the system, including definitions, architectural support, and a priority matrix resolving trade-offs.
- **`part2_multiple_views.drawio`** & **`.png`**: Architecture diagrams presented in 3 views (Logical, Physical/Deployment, and Scenario/Sequence).
- **`part3_architectural_pattern.drawio`** & **`.png`**: Diagram highlighting the chosen Microservices (with Event-Driven hybrid) architectural pattern.
- **`part3_pattern_justification.md`**: Rationale for why the Microservices/Event-Driven pattern was selected and how it meets system requirements.
- **`part3_architectural_decisions.md`**: Three formatted Architectural Decision Records (ADRs) covering Microservices, PostgreSQL, and MQTT.
- **`part4_technical_debt.md`**: Identification of 3 technical debt items (e.g., Relational DB for telemetry) prioritized in a debt backlog.
- **`part4_architectural_smells.md`**: Document identifying the "God Component" (API Gateway) and "Scattered Concerns" (Notification dispatching) smells.
- **`part4_smell_refactoring.drawio`** & **`.png`**: "Before" and "After" architectural diagrams demonstrating how to refactor the identified smells.

## Key Highlights

- **Hybrid Architecture**: Leveraged Microservices for domain isolation alongside an MQTT Message Broker to specifically handle the constraints of IoT devices.
- **Microservice Isolation**: Delegated concerns effectively to prevent a "God Component", proposing dedicated IAM and Notification services during the refactoring phase.
- **Stakeholder Views**: Clearly separated architectural views (Logical, Physical, Sequence) to address the distinctly different needs of Developers, DevOps, and Product Managers.

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable diagrams (Note: `part2_multiple_views.drawio` has multiple pages/tabs at the bottom).
2. View `.png` files for quick reference.
3. Read `.md` files for documentation.


AI Usage
I acknowledge the use of antigravity IDE to automate the versioning and pormpting process, Gemini LLM to refine my architecture diagrams, and draw.io to create the diagrams.