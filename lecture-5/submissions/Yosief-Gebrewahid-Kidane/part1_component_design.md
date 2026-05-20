# Part 1.1 – Component Decomposition

## Overview

The Task Management System is designed using modular architecture principles.

The system is decomposed into independent components where each component follows the **Single Responsibility Principle (SRP)**.

Each component has a single clearly defined responsibility and communicates with other components through well-defined interfaces.  
This design improves maintainability, readability, and testability.

The main orchestrator (`TaskManager`) coordinates these components using **dependency injection**, allowing components to remain loosely coupled.
---

# System Components

The system is composed of the following components:

| Component | Responsibility |
|-----------|---------------|
| TaskValidator | Validates task data before processing |
| TaskRepository | Stores and retrieves tasks |
| TaskSearch | Filters and searches tasks |
| TaskExporter | Exports tasks to external formats |
| TaskNotifier | Sends task reminders |

---

# Component Descriptions

## 1. TaskValidator

### Responsibility
Ensures that task data is valid before being stored or processed.

### Why this component exists
Separating validation from business logic prevents duplication and keeps the system modular.

### Examples of validation
- Task ID must exist
- Task title cannot be empty
- Assignee name must be valid

### Benefits
- High cohesion: only validation logic
- Easy to extend validation rules

---

## 2. TaskRepository

### Responsibility
Handles storage and retrieval of tasks.

This component abstracts data persistence so the rest of the system does not depend on storage details.

### Responsibilities include
- Add tasks
- Retrieve tasks
- List tasks
- Delete tasks

### Implementation
Current implementation:
- `InMemoryTaskRepository`

Possible future implementations:
- Database repository
- File-based repository

### Benefits
- Storage logic isolated
- Allows easy replacement of storage mechanism

---

## 3. TaskSearch

### Responsibility
Provides searching and filtering functionality for tasks.

This component processes collections of tasks and returns filtered results.

### Supported operations
- Filter tasks by status
- Search tasks by keyword

### Benefits
- Keeps search logic separate from storage
- Improves readability and reuse

---

## 4. TaskExporter

### Responsibility
Exports tasks into different file formats.

Export logic is separated from the rest of the system so new formats can be added easily.

### Current implementations
- JSON exporter
- CSV exporter

### Benefits
- Supports extensibility
- Decouples export logic from business logic

---

## 5. TaskNotifier

### Responsibility
Handles task notifications and reminders.

In this implementation, notifications are simulated using console output.



### Benefits
- Notification logic separated from core functionality
- Future support for email or messaging systems

---

# TaskManager (Orchestrator)

The `TaskManager` class acts as the central coordinator of the system.

Instead of implementing business logic directly, it delegates responsibilities to the appropriate components.

Example workflow for creating a task:

1. TaskManager receives a new task
2. TaskValidator validates the task
3. TaskRepository stores the task

This orchestration ensures **clear separation of concerns**.

---

# Benefits of the Modular Design

The system design provides several advantages.

### High Cohesion
Each component focuses on one well-defined responsibility.

### Low Coupling
Components communicate through interfaces rather than direct dependencies.

### Maintainability
Changes to one component do not affect others.

### Testability
Each component can be tested independently.

### Extensibility
New features can be added by introducing new components without modifying existing ones.



 