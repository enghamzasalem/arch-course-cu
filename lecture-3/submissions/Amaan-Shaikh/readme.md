# Assignment Submission: Lecture 3

**Student Name**: Amaan Shaikh   
**Submission Date**: 27/02/2026

## Overview

This assignment presents the architectural design of a Smart Home Management System.  
It includes component and connector diagrams, multiple architectural views, quality attribute analysis, architectural pattern selection, architectural decision records, and technical debt evaluation.

## Files Included

### Part 1 – Architecture Fundamentals

- `part1_component_connector_diagram.drawio` – Component and connector diagram showing high-level architecture with 6+ components and 5+ connectors
- `part1_component_connector_diagram.png` – Exported image version of the diagram
- `part1_architecture_vs_design.md` – Documentation distinguishing 5 architectural decisions and 5 design decisions

### Part 2 – Quality Attributes & Multiple Views

- `part2_quality_attributes.md` – Analysis of 5 quality attributes with definitions, importance, architecture support, and trade-offs
- `part2_multiple_views.drawio` – Three architectural views (Logical, Sequence, Deployment) in one file
- `part2_multiple_views-Logical View.png` – Logical view showing functional components and relationships
- `part2_multiple_views-Sequence View.png` – Sequence view showing "User turns on lights via mobile app" scenario
- `part2_multiple_views-Deployment View.png` – Physical/deployment view showing infrastructure and cloud services

### Part 3 – Architectural Pattern & Decisions

- `part3_architectural_pattern.drawio` – Event-Driven Microservices pattern diagram
- `part3_architectural_pattern.png` – Exported pattern diagram image
- `part3_pattern_justification.md` – Justification of selected pattern with trade-offs and alternatives
- `part3_architectural_decisions.md` – Three Architectural Decision Records (ADRs) covering architecture, technology, and deployment

### Part 4 – Technical Debt & Architectural Smells

- `part4_technical_debt.md` – Technical debt analysis with 5 items, including principal, interest, and prioritized backlog
- `part4_architectural_smells.md` – Identification and analysis of two architectural smells (God Component and Circular Dependencies)
- `part4_smell_refactoring.drawio` – Before and after refactoring diagrams for both smells
- `part4_smell_refactoring-Smell 1 - God Component.png` – God Component before/after refactoring
- `part4_smell_refactoring-Smell 2 - Circular Dependencies.png` – Circular Dependencies before/after refactoring

## Additional Files

- `code/` – Directory containing supporting code examples (optional)

## Key Highlights

- Applied core architectural concepts from Chapters 1, 2, and 3
- Documented architectural decisions using ADR format
- Created multiple architectural views for different stakeholders
- Analyzed quality attributes with trade-off considerations
- Identified technical debt with principal vs. interest analysis
- Detected and refactored architectural smells

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable diagrams
2. View `.png` files for quick reference without needing draw.io
3. Read `.md` files in any text editor or Markdown viewer
4. Check the `code/` directory for implementation examples

## Notes

- All diagrams include legends explaining symbols and color coding
- ADRs follow the required format with context, decision, consequences, and alternatives
- Technical debt items include severity, principal, interest, and impact
- Refactoring diagrams show clear before/after comparisons