# Lecture 4: Modeling Software Architecture

## Overview

This folder contains practical Python examples and assignments for Chapter 4: Modeling Software Architecture.

This lecture covers techniques and tools for modeling software architecture. Students learn how to represent, visualize, and document architectural decisions and system structures.

## Learning Objectives

By working through these materials, you will:

1. **C4 Model** - Create hierarchical architecture documentation (Context, Container, Component, Code)
2. **UML for Architecture** - Use Component, Deployment, and Sequence diagrams
3. **Architecture Diagrams** - Choose the right diagram for the right audience
4. **Modeling Notation** - Apply standard conventions consistently
5. **Architecture Documentation** - Maintain and communicate models effectively

## Example Files

### `example1_c4_model_and_diagrams.py`

**Concepts:** C4 Model, System Context, Container Diagram, Component Diagram

- Demonstrates the four levels of C4 (Context, Container, Component, Code)
- Shows when to use each diagram level
- Real-world example: Online Food Delivery System
- Diagram type catalog and selection guide

### `example2_uml_and_sequence_diagrams.py`

**Concepts:** UML, Component Diagram, Deployment Diagram, Sequence Diagram

- UML component diagram with interfaces
- UML deployment diagram with nodes and artifacts
- UML sequence diagram for use case flows
- Modeling notation reference and best practices

## Key Concepts

### C4 Model

| Level | Name | Shows | Audience |
|-------|------|-------|----------|
| 1 | Context | System + users + external systems | Everyone |
| 2 | Container | Applications/services in the system | Developers, DevOps |
| 3 | Component | Internal structure of containers | Developers |
| 4 | Code | Classes, interfaces (optional) | Developers |

### UML Diagram Types

- **Component Diagram**: Static structure, interfaces, dependencies
- **Deployment Diagram**: Physical nodes, artifacts, infrastructure
- **Sequence Diagram**: Interactions over time, message flow

### Modeling Best Practices

- Use consistent notation across diagrams
- Keep diagrams focused (one concern per diagram)
- Match diagram detail to audience
- Maintain diagrams alongside code
- Add legends for complex diagrams

## Running the Examples

```bash
cd arch-course-cu/lecture-4
python3 example1_c4_model_and_diagrams.py
python3 example2_uml_and_sequence_diagrams.py
```

## Assignment

See **`ASSIGNMENT.md`** for the modeling assignment, which requires:

- C4 diagrams (Context, Container, Component)
- UML diagrams (Sequence, Deployment)
- Architecture documentation
- Submission via GitHub Pull Request (drawio + png files)

## Related Materials

- **Chapter 3**: Definitions and Terminology (views, viewpoints)
- **Chapter 5**: Modularity and Components (next lecture)
- **C4 Model**: https://c4model.com/
- **Draw.io**: https://app.diagrams.net/

## Next Steps

After this lecture, you will be able to:

- Create professional architecture diagrams
- Use C4 and UML notations correctly
- Document architecture for different stakeholders
- Maintain architecture documentation over time
