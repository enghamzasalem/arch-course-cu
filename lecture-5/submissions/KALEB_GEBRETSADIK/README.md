# Lecture 5 Assignment: Component Architecture & Loose Coupling

**Student Name:** Kaleb Gebretsadik

## Project Overview

This submission contains the implementation and documentation for the Lecture 5 assignment, which focuses on modularizing a monolithic Task Management System into a component-based architecture with low coupling and high cohesion.

### Part 1: Implementation
The `code/` directory contains the refactored Task Management System.

- **Modular Components (Task 1.1)**: The system is broken down into `TaskValidator`, `TaskSearch`, `TaskNotifier`, `ITaskStorage` implementations, and `ITaskExporter` implementations.
- **Interfaces & Dependency Injection (Task 1.2)**: To ensure loose coupling, `TaskManager` relies entirely on injected interfaces (`ITaskStorage`, `ITaskExporter`) rather than concrete dependencies. 
- **Swappable Implementations**: We implemented both an `InMemoryTaskRepository` and a `FileTaskRepository` for storage, alongside a `JsonExporter` and `CsvExporter` for data exporting.

#### How to Run the Code
You can run the demonstration script from the command line. Ensure you have Python installed.

```bash
cd code
python main.py
```

The script will execute a demo that showcases the `TaskManager` operating with two completely different configurations of injected dependencies, proving the flexibility of the architecture.

### Part 2: Architecture Modeling & Analysis
- **Component Diagram (Task 2.1)**: Open `part2_component_diagram.drawio` in the Draw.io application to view the component and connector diagram of the refactored system. (An exported `part2_component_diagram.png` is additionally expected here).
- **Cohesion, Coupling & SRP (Task 2.2)**: Open `part2_cohesion_coupling.md` to read the analysis of how the system achieves functional cohesion, avoids tight coupling through abstraction, and adheres to the Single Responsibility Principle.

### Additional Documentation
- `part1_component_design.md`: Explains the responsibilities of the five core modules established in Part 1.1.
- `part1_interfaces.md`: Explains the rationale behind the interfaces and Dependency Injection introduced in Part 1.2.
