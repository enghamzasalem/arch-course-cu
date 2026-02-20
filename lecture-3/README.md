# Lecture 3: Definitions and Terminology

## Overview

This folder contains practical Python examples demonstrating key concepts from Chapter 3: Definitions and Terminology.

This lecture establishes the vocabulary and definitions essential for discussing software architecture. Students learn standard terminology used by architects and understand key architectural concepts.

## Learning Objectives

By working through these examples, you will understand:

1. **Architecture vs. Design** - Strategic vs. tactical decisions
2. **Components and Connectors** - Building blocks of architecture
3. **Architectural Patterns vs. Design Patterns** - System-wide vs. component-level patterns
4. **Views and Viewpoints** - Different perspectives on the same system
5. **Architectural Decisions** - How to document and track decisions
6. **Technical Debt** - Understanding and managing accumulated shortcuts
7. **Architectural Smells** - Warning signs of architectural problems

## Example Files

### `example1_architecture_vs_design.py`
**Concepts:** Architecture, Design, Strategic Decisions, Tactical Decisions
- Demonstrates the difference between architecture (high-level, strategic) and design (detailed, tactical)
- Shows how architecture constrains design choices
- Real-world example: E-commerce platform architecture and design decisions

### `example2_components_and_connectors.py`
**Concepts:** Components, Connectors, Component Interfaces, Architecture Structure
- Components as computational units with clear responsibilities
- Connectors as communication mechanisms
- Architecture = Components + Connectors
- Real-world example: Online banking system with services, databases, and message queues

### `example3_architectural_patterns.py`
**Concepts:** Architectural Patterns, Design Patterns, Pattern Selection
- Architectural patterns: Layered, MVC, Microservices, Event-Driven
- Design patterns: Repository, Factory, Strategy, Observer
- When to use which pattern
- Real-world example: Content Management System with different pattern options

### `example4_views_and_viewpoints.py`
**Concepts:** Views, Viewpoints, Stakeholder Communication, Architecture Documentation
- Different viewpoints: Logical, Physical, Process, Development, Scenarios
- Creating views for different stakeholders
- How views help communicate architecture
- Real-world example: E-commerce platform from multiple viewpoints

### `example5_architectural_decisions.py`
**Concepts:** Architectural Decision Records (ADRs), Technical Debt, Architectural Smells
- Documenting architectural decisions
- Understanding technical debt (interest and principal)
- Identifying architectural smells
- Real-world example: Startup system evolution with decisions and debt

## Key Concepts

### Architecture vs. Design

**Architecture** (Strategic):
- High-level structure and organization
- System-wide, cross-cutting concerns
- Hard to change, expensive to modify
- Examples: Microservices vs. Monolith, Database choice, Communication patterns

**Design** (Tactical):
- Detailed implementation decisions
- Component-level, local concerns
- Easier to change
- Examples: Data structures, Algorithms, Design patterns, Class hierarchies

**Relationship**: Architecture constrains design choices. Design implements the architecture.

### Components and Connectors

**Components**:
- Computational units that encapsulate functionality
- Have clear responsibilities
- Expose interfaces for interaction
- Examples: Services, Databases, Queues, Gateways

**Connectors**:
- Communication mechanisms between components
- Define how components interact
- Can be synchronous or asynchronous
- Examples: REST API, Message Queue, Database Connection, Event Bus

**Architecture = Components + Connectors**

### Architectural Patterns vs. Design Patterns

**Architectural Patterns** (System-Wide):
- Define overall system structure
- Examples: Microservices, Layered, MVC, Event-Driven
- Hard to change, affect entire system

**Design Patterns** (Component-Level):
- Define component implementation
- Examples: Repository, Factory, Strategy, Observer
- Easier to change, affect specific components

**Relationship**: Multiple design patterns can be used within one architectural pattern.

### Views and Viewpoints

**Viewpoints**:
- Templates or patterns for creating views
- Standardized way to document architecture
- Examples: Logical, Physical, Process, Development, Scenarios

**Views**:
- Specific representations from a viewpoint
- Created for specific stakeholders
- Show relevant concerns, hide irrelevant details
- Multiple views are complementary

**Stakeholders Need Different Views**:
- Developers: Logical, Development views
- DevOps: Physical, Process views
- Business: Logical, Scenarios views
- Security: Security view

### Architectural Decisions

**Architectural Decision Records (ADRs)**:
- Document the context, decision, consequences, and alternatives
- Help future developers understand "why"
- Can be superseded as system evolves

**Key Elements**:
- Context: Why this decision is needed
- Decision: What was decided
- Consequences: What happens as a result
- Alternatives: What other options were considered

### Technical Debt

**Definition**: Shortcuts taken for speed that create ongoing costs.

**Components**:
- **Principal**: Cost to fix the debt
- **Interest**: Ongoing cost of having the debt
- **Types**: Architectural, Code, Test, Documentation, Dependency

**Management**:
- Track debt in backlog
- Prioritize based on interest rate
- Regularly refactor to pay down debt

### Architectural Smells

**Definition**: Warning signs of architectural problems.

**Common Smells**:
- **God Component**: Component that does too much
- **Circular Dependency**: Components depend on each other in a cycle
- **Scattered Concern**: Concern spread across many components
- **Tangled Dependencies**: Complex, hard-to-understand dependencies

**Management**:
- Identify smells through code reviews
- Address root causes, not just symptoms
- Refactor to eliminate smells

## Running the Examples

### Good Architecture Examples

```bash
# Run all examples
python3 example1_architecture_vs_design.py
python3 example2_components_and_connectors.py
python3 example3_architectural_patterns.py
python3 example4_views_and_viewpoints.py
python3 example5_architectural_decisions.py
```

## Business Examples

Each example includes real-world business scenarios:
- **E-commerce Platform**: Architecture vs. design decisions, multiple views
- **Online Banking System**: Components and connectors
- **Content Management System**: Different architectural patterns
- **Startup Evolution**: Architectural decisions and technical debt over time

## Terminology Summary

### Core Terms

- **Architecture**: High-level structure and strategic decisions
- **Design**: Detailed implementation and tactical decisions
- **Component**: Computational unit with clear responsibilities
- **Connector**: Communication mechanism between components
- **Pattern**: Reusable solution to a recurring problem
- **View**: Representation of system from a specific perspective
- **Viewpoint**: Template for creating views
- **Technical Debt**: Shortcuts that create ongoing costs
- **Architectural Smell**: Warning sign of architectural problems

### Decision Making

- **Architectural Decision**: Strategic, system-wide, hard to change
- **Design Decision**: Tactical, local, easier to change
- **ADR**: Architectural Decision Record (documentation format)

### Patterns

- **Architectural Pattern**: System-wide structural pattern
- **Design Pattern**: Component-level implementation pattern

## Next Steps

After understanding these concepts, you'll be able to:
- Distinguish between architecture and design
- Identify components and connectors in systems
- Choose appropriate patterns for problems
- Create views for different stakeholders
- Document architectural decisions
- Identify and manage technical debt
- Recognize architectural smells

## Related Materials

- **Chapter 1**: Introduction to Software Architecture
- **Chapter 2**: Quality Attributes
- **Chapter 4**: Modeling Software Architecture (next lecture)
- **Assignment**: Create architecture diagrams using draw.io (see `ASSIGNMENT.md`)

## Assignment Submission

This lecture includes a comprehensive assignment that requires:
- Creating architecture diagrams using draw.io
- Exporting diagrams as PNG images
- Submitting via GitHub Pull Request
- Including code examples (optional)

**See**:
- `ASSIGNMENT.md` - Complete assignment instructions
- `SUBMISSION_GUIDE.md` - Step-by-step PR submission guide
- `EXPORT_DIAGRAMS_GUIDE.md` - How to export draw.io diagrams as images
- `sol/` - Example solutions and code

## Additional Resources

- Review the example files to see concepts in action
- Study the terminology used in each example
- Practice identifying components and connectors in real systems
- Document your own architectural decisions using ADR format

