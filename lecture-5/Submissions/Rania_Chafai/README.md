# Lecture 5: Modularity and Components
**Student Name**: Rania Chafai
**Student ID**:30009596
**Submission Date**: 12/03/2026

## Overview

This folder contains practical Python examples and assignments for Chapter 5: Modularity and Components.

This lecture focuses on modularity as a fundamental architectural principle. Students learn how to decompose systems into well-defined, independent components that can be developed, tested, and maintained separately.

## Learning Objectives

By working through these materials, you will:

1. **Principles of Modularity** - Decompose systems into independent, well-defined units
2. **Separation of Concerns** - Each component handles one concern
3. **Single Responsibility Principle (SRP)** - One reason to change per component
4. **Component Interfaces** - Define clear contracts between components
5. **Cohesion and Coupling** - Achieve high cohesion, low coupling
6. **Component Lifecycle** - Design for creation, use, and replacement

## Example Files

### `example1_modularity_and_separation_of_concerns.py`

**Concepts:** Modularity, Separation of Concerns, Single Responsibility Principle

- Compares monolithic vs modular order processing
- Demonstrates SRP: OrderValidator, InventoryChecker, PaymentProcessor, etc.
- Shows component composition and orchestration
- Real-world scenario: Order Processing System

### `example2_component_interfaces_and_coupling.py`

**Concepts:** Component Interfaces, Cohesion, Coupling, Dependency Injection

- Interface-based design with Protocol/ABC
- Loose coupling via dependency injection
- High cohesion in DocumentManager
- Component lifecycle concepts
- Real-world scenario: Document Management System

## Key Concepts

### Modularity Principles

- **Decompose**: Break system into independent units
- **Encapsulate**: Hide implementation, expose interface
- **Compose**: Build system from modules

### Single Responsibility Principle (SRP)

Each component should have one reason to change. If you need to change a component for multiple unrelated reasons, it has multiple responsibilities.

### Cohesion and Coupling

| | Low | High |
|---|-----|------|
| **Cohesion** | Bad - unrelated parts | Good - single purpose |
| **Coupling** | Good - independent | Bad - tightly dependent |

**Goal**: High cohesion + Low coupling

### Component Interfaces

- Define contracts (what, not how)
- Enable swapping implementations
- Support testing with mocks

## Running the Examples

```bash
cd arch-course-cu/lecture-5
python3 example1_modularity_and_separation_of_concerns.py
python3 example2_component_interfaces_and_coupling.py
```

## Assignments

**`ASSIGNMENT.md`** – Modular design (Task Management System): Python implementation, component diagram, cohesion/coupling analysis.

**`ASSIGNMENT_EXTRA_LLM_MONITORING.md`** – Extra: design the architecture for an **OpenAI/Gemini wrapper** that tracks and monitors API calls and detects anomalies. Deliverables: C4 and component diagrams, sequence diagrams, anomaly detection design, quality-attributes doc; optional minimal proxy code or ADR.

See **`ASSIGNMENT.md`** for the main modular design assignment, which requires:

- Python implementation of a Task Management System
- Modular component decomposition (5+ components)
- Interfaces and dependency injection
- Component diagram (draw.io + png)
- Cohesion and coupling analysis
- Submission via GitHub Pull Request

## Related Materials

- **Chapter 4**: Modeling (component diagrams)
- **Chapter 6**: Reusability and Interfaces (next lecture)
- **Chapter 3**: Definitions (components and connectors)

## Next Steps

After this lecture, you will be able to:

- Design modular systems with clear component boundaries
- Apply SRP and separation of concerns
- Create well-defined component interfaces
- Balance cohesion and coupling
- Use dependency injection for flexibility
