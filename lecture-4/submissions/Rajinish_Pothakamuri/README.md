# Video Streaming Platform - Architecture Models

**Author:** Rajin  
**Course Assignment:** Architecture Modeling with C4 and UML  

## Overview
This repository contains the architectural models and documentation for a hypothetical Video Streaming Platform (e.g., Netflix-style). The system is designed to allow subscribers to browse, search, and stream adaptive video content, while enabling content creators to upload media and administrators to manage the platform. 

The architecture is modeled using the **C4 Model** for static structural representations and **UML** for dynamic behavior and physical infrastructure mapping.

## Modeled Technology Stack
The architectural diagrams reflect a modern, scalable microservices-oriented approach utilizing the following hypothetical stack:
* **Frontend:** React (Web), Swift/Kotlin (Mobile)
* **API Gateway / Backend:** Node.js / Express
* **Recommendation Service:** Python / FastAPI
* **Database:** Managed PostgreSQL
* **Infrastructure & Deployment:** Docker, hosted on a cloud provider (e.g., Render / Google Cloud), utilizing a global CDN for video delivery.

## Deliverables & Repository Structure

The assignment is divided into three main parts, and all deliverables are included in this directory:

### Part 1: C4 Model Diagrams
* `part1_context_diagram.drawio` & `.png` - C4 Level 1: System boundary and external actors.
* `part1_container_diagram.drawio` & `.png` - C4 Level 2: High-level deployable software units.
* `part1_component_diagram.drawio` & `.png` - C4 Level 3: Internal decomposition of the API Gateway container.

### Part 2: UML Diagrams
* `part2_sequence_diagram.drawio` & `.png` - UML Sequence: Maps the chronological message flow for the "User watches a video" use case.
* `part2_deployment_diagram.drawio` & `.png` - UML Deployment: Illustrates how the software containers are mapped to physical/virtual infrastructure nodes.

### Part 3: Architecture Documentation
* `part3_model_documentation.md` - Details the modeling approach, notation rationale, and cross-diagram consistency checks.

## How to View
* **Images:** All diagrams have been exported to `.png` format for immediate viewing. You can open these in any standard image viewer or web browser.
* **Source Files:** To edit or view the raw diagram models, import the `.drawio` files directly into [draw.io](https://app.diagrams.net/).