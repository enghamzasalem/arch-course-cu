# Assignment Submission: Lecture 3

**Student Name**: Sonia Mangane
**Student ID**:  
**Submission Date**: 26 - 02 - 2026

## Overview

This submission covers the architectural evolution of a Smart Home Management System. I transitioned the project from initial goal setting to a complex Hybrid Microservices and Event-Driven Architecture. The focus was on ensuring system reliability and scalability while identifying and refactoring critical technical debt, such as "God Components" and circular event dependencies.

## Files Included

- part1_architecture_vs_design.md: Explanation of the strategic vs. tactical split in the system.
- part1_component_connector_diagram.drawio (.png): Initial structural view of the system components.
- part2_quality_attributes.md: Documenting the "Must-Haves" like Availability and Scalability.
- part2_multiple_views.drawio (png) (Logical, Physical, Sequence): 3 View Model diagrams showing the system from different stakeholder perspectives.
- part3_architectural_pattern.drawio (.png): Visualizing the Hybrid Pattern featuring asynchronous event producers and consumers.
- part3_pattern_justification.md: Justifying the use of a Message Broker and Database-per-Service to ensure fault isolation.
- part4_technical_debt.md: Analysis of principal, interest, and severity of identified debt items.
- part4_architectural_smells.md: Identification of the "God Component" and "Cyclic Dependency" issues.
- part4_smell_refactoring.drawio (.png): Before-and-after refactoring diagrams demonstrating Saga Orchestration and service decomposition.
- assignment_overview: Offers a summary of the workings and assumptions made.

## Key Highlights

- Logic Decomposition: Refactored the monolithic "Device Manager" into specialized microservices (State, Scheduler, Comm) to satisfy the Single Responsibility Principle.
- Asynchronous Reliability: Utilized an Event-Driven backbone to ensure that sensor data spikes do not overwhelm the system, maintaining high availability.
- Decoupled Data: Applied a strict Database-per-Service architecture to prevent data-layer coupling and ensure that schema changes in one service don't impact others.

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation
4. Run code examples (if included) with Python 3