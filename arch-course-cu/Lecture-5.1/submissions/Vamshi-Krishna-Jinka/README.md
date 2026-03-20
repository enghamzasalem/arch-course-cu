# Task Management System

## Modularity and Components Assignment Submission

**Student:** Vamshi Krishna Jinka
**Submission date:** [12-03-2026]

---

# Overview

This submission presents the architectural design and modular implementation of a **Task Management System**.

The system allows users to:

* Create tasks
* Update tasks
* Delete tasks
* Assign tasks to users
* Search and filter tasks
* Export tasks to different formats (JSON / CSV)
* Send task reminders (simulated via console output)

The system architecture follows **modular design principles**, emphasizing:

* Separation of Concerns
* Single Responsibility Principle (SRP)
* High Cohesion
* Low Coupling
* Interface-based design
* Dependency Injection

The implementation demonstrates how a system can be decomposed into independent components that are easier to maintain, test, and extend.

---

# Part 1 – Modular System Implementation

## code/ Directory

Contains the Python implementation of the Task Management System following modular architecture.

### task_manager.py

Main orchestrator of the system.

Responsibilities:

* Coordinates task operations
* Connects all components
* Handles task creation, deletion, searching, exporting, and reminders

Uses **dependency injection** to receive required components.

---

### models.py

Defines the system data structures.

Contains:

**Task Model**

* id
* title
* description
* assigned_to
* status

This file isolates data representation from business logic.

---

## components/

This folder contains modular components, each following the **Single Responsibility Principle**.

---

### validator.py

**TaskValidator Component**

Responsibility:

* Validates task data before storing it.

Example validations:

* Task title must not be empty
* Task must be assigned to a user

This ensures data integrity before persistence.

---

### repository.py

**Task Storage Layer**

Defines storage interface and implementations.

Contains:

**ITaskStorage (Interface)**
Defines required storage operations:

* add_task()
* get_tasks()
* delete_task()

**InMemoryTaskRepository**
Stores tasks in memory.

The interface allows storage implementation to be replaced easily.

---

### search.py

**TaskSearch Component**

Responsibility:

* Filter tasks
* Search tasks by title
* Retrieve tasks assigned to specific users

Separating search logic improves modularity and testability.

---

### exporter.py

**Task Export Components**

Defines exporting interface and implementations.

Contains:

**ITaskExporter (Interface)**

Defines export behavior.

Implementations:

**JsonExporter**
Exports tasks to JSON format.

**CsvExporter**
Exports tasks to CSV format.

Using interfaces allows export formats to be easily swapped.

---

### notifier.py

**TaskNotifier Component**

Responsibility:

* Send task reminders.

Currently implemented as **console output simulation**, but it can be extended to support:

* Email notifications
* SMS reminders
* Push notifications

---

# Part 1 Documentation

### part1_component_design.md

Describes the **component decomposition** of the Task Management System.

Includes:

* Explanation of each component
* Responsibility of each module
* Justification of modular design
* Explanation of high cohesion and separation of concerns

---

### part1_interfaces.md

Documents the **interfaces and dependency injection strategy**.

Includes:

* Definition of system interfaces
* Explanation of storage abstraction
* Explanation of exporter abstraction
* Example of dependency injection usage
* Benefits for modularity and testing

---

# Part 2 – Architectural Analysis

## Component Diagram

### part2_component_diagram.png

Visual representation of the modular system architecture.

The diagram shows:

* System components
* Interfaces
* Dependencies between modules
* Direction of data flow

The diagram was created using **draw.io**.

---

## Cohesion and Coupling Analysis

### part2_cohesion_coupling.md

This document evaluates architectural quality in terms of:

### Cohesion Analysis

For each component, the document explains:

* The type of cohesion (functional cohesion)
* Why the component is highly cohesive
* How responsibilities are clearly separated

### Coupling Analysis

Describes dependencies between components and explains:

* How low coupling is achieved
* The use of interfaces
* The role of dependency injection

### SRP Application

For each component, the document identifies:

* The single responsibility
* The “one reason to change”

This ensures compliance with the **Single Responsibility Principle**.

---

# Architectural Summary

The Task Management System follows several important architectural principles:

### Modularity

The system is decomposed into independent components that can be developed and tested separately.

### High Cohesion

Each component performs a single focused responsibility.

### Low Coupling

Components interact through well-defined interfaces.

### Dependency Injection

Dependencies are passed into the TaskManager rather than created internally.

### Interface-Based Design

Interfaces allow flexible replacement of implementations such as storage systems or export formats.

---

# Key Benefits of the Architecture

The modular architecture provides several advantages:

* Improved maintainability
* Easier testing of individual components
* Flexible extension of system features
* Reduced impact of code changes
* Clear separation of responsibilities

---

# Conclusion

This assignment demonstrates the application of **modular architecture principles** through the design and implementation of a Task Management System.

By applying **SRP, interfaces, dependency injection, high cohesion, and low coupling**, the system achieves a flexible and maintainable architecture suitable for future extension.
