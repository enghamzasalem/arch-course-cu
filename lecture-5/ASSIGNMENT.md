# Assignment: Modular Component Design

## Overview

This assignment requires you to design and implement a modular system applying concepts from **Chapter 5: Modularity and Components**. You will create Python code demonstrating modular design, separation of concerns, and low coupling, plus a component diagram.

## Learning Objectives

By completing this assignment, you will:
- Apply modularity principles to system design
- Implement components with clear interfaces
- Apply Single Responsibility Principle (SRP)
- Manage cohesion and coupling
- Document component structure with diagrams

## Assignment Scenario

Design and implement a **Task Management System** that allows users to:
- Create, update, and delete tasks
- Assign tasks to users
- Filter and search tasks
- Export tasks to different formats (JSON, CSV)
- Send task reminders (simulate with console output)

## Part 1: Modular Design and Implementation

### Task 1.1: Component Decomposition

**Objective**: Decompose the system into modular components following SRP.

**Requirements**:
1. Identify **at least 5 components** with single responsibilities. Examples:
   - TaskValidator (validates task data)
   - TaskRepository (persists tasks)
   - TaskSearch (filters/searches tasks)
   - TaskExporter (exports to JSON/CSV)
   - TaskNotifier (sends reminders)

2. Create a Python module structure:
   ```
   code/
   ├── task_manager.py      # Main orchestrator
   ├── components/
   │   ├── validator.py
   │   ├── repository.py
   │   ├── search.py
   │   ├── exporter.py
   │   └── notifier.py
   └── models.py            # Data structures (Task, etc.)
   ```

3. Each component must:
   - Have ONE clear responsibility
   - Expose a minimal interface
   - Be independently testable (inject dependencies)

**Deliverables**: 
- Python code in `code/` directory
- `part1_component_design.md` - Document your decomposition with rationale

**Grading**: 30 points

---

### Task 1.2: Interfaces and Dependency Injection

**Objective**: Use interfaces and dependency injection for low coupling.

**Requirements**:
1. Define **at least 2 interfaces** (using `Protocol` or ABC):
   - e.g., `ITaskStorage`, `ITaskExporter`

2. Implement **at least 2 implementations** per interface:
   - e.g., InMemoryTaskRepository and FileTaskRepository
   - e.g., JsonExporter and CsvExporter

3. Main `TaskManager` must receive dependencies via constructor (dependency injection)

4. Demonstrate that you can swap implementations without changing TaskManager

**Deliverables**: 
- Python code in `code/`
- `part1_interfaces.md` - Describe your interfaces and how they enable low coupling

**Grading**: 25 points

---

## Part 2: Component Diagram and Documentation

### Task 2.1: Component Diagram

**Objective**: Create a component diagram showing your modular architecture.

**Requirements**:
1. Use draw.io to create a diagram showing:
   - **All components** with names and responsibilities
   - **Interfaces** (provided/required)
   - **Dependencies** between components (arrows)
   - **Data flow** or call direction

2. Use appropriate notation:
   - Boxes for components
   - Arrows for dependencies
   - Labels for interfaces
   - Legend

3. The diagram should match your implementation

**Deliverables**: 
- `part2_component_diagram.drawio`
- `part2_component_diagram.png`

**Grading**: 25 points

---

### Task 2.2: Cohesion and Coupling Analysis

**Objective**: Document your design decisions regarding cohesion and coupling.

**Requirements**:
1. Create `part2_cohesion_coupling.md` with:

   **a) Cohesion Analysis**
   - For each component: What type of cohesion does it have? (Functional, Sequential, etc.)
   - Justify why each component has high cohesion

   **b) Coupling Analysis**
   - Describe coupling between components (low/medium/high)
   - Explain how you achieved low coupling
   - Identify any coupling you would reduce with more time

   **c) SRP Application**
   - For each component: What is its single responsibility?
   - What would be the "one reason to change" for each?

2. Reference your diagram: `![Component Diagram](part2_component_diagram.png)`

**Deliverable**: `part2_cohesion_coupling.md`

**Grading**: 20 points

---

## Submission Requirements

### Submission Method: Pull Request (PR)

**All submissions must be made via GitHub Pull Request.** (See `../lecture-3/SUBMISSION_GUIDE.md` for PR process)

### File Structure

```
submissions/YOUR_NAME/
├── code/
│   ├── task_manager.py
│   ├── models.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── validator.py
│   │   ├── repository.py
│   │   ├── search.py
│   │   ├── exporter.py
│   │   └── notifier.py
│   └── main.py              # Demo/usage
├── part1_component_design.md
├── part1_interfaces.md
├── part2_component_diagram.drawio
├── part2_component_diagram.png
├── part2_cohesion_coupling.md
└── README.md
```

### Code Requirements

- Python 3.8+
- Clear, commented code
- Runnable demo (main.py or similar)
- No external dependencies required (stdlib only, or document requirements)

---

## Grading Rubric

| Part | Task | Points |
|------|------|--------|
| Part 1 | Component Decomposition (code + doc) | 30 |
| Part 1 | Interfaces and DI (code + doc) | 25 |
| Part 2 | Component Diagram | 25 |
| Part 2 | Cohesion/Coupling Analysis | 20 |
| **Total** | | **100** |

### Quality Criteria

- **Modularity (25%)**: Clear component boundaries, SRP applied
- **Interfaces (25%)**: Proper use of interfaces, low coupling
- **Code Quality (25%)**: Readable, runnable, well-structured
- **Documentation (25%)**: Clear diagrams, thoughtful analysis

---

## Getting Started

1. **Review examples**: `example1_modularity_and_separation_of_concerns.py`, `example2_component_interfaces_and_coupling.py`
2. **Start with decomposition**: List responsibilities, then assign to components
3. **Define interfaces first**: What does each component need to expose/consume?
4. **Implement incrementally**: One component at a time, test as you go

---

## Important Notes

- Keep it simple but demonstrate the concepts
- You may use dataclasses, typing, ABC, or Protocol
- Mock external systems (e.g., email) with print statements
- Focus on structure over features

---

## Deadline

**Due Date**: [To be announced by instructor]

**Submission**: GitHub Pull Request to `arch-course-cu/lecture-5/submissions/YOUR_NAME/`

Good luck! 🚀
