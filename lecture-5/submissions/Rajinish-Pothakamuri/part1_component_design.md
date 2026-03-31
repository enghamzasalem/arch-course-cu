# Part 1: Component Decomposition

## 1. Module Structure

The Task Management System is organized using a modular architecture.
Each component has a single responsibility and communicates through well-defined interfaces.

```
code/
├── task_manager.py        # Main orchestrator
├── models.py              # Data structures
├── main.py                # Demo / application entry point
└── components/
    ├── validator.py       # Task validation logic
    ├── repository.py      # Task storage implementations
    ├── search.py          # Filtering and searching tasks
    ├── exporter.py        # Export tasks to different formats
    └── notifier.py        # Task reminder notifications
```

This structure separates concerns and allows each module to evolve independently.

---

# 2. Components and Responsibilities

## 2.1 TaskValidator

**Location:** `components/validator.py`

**Responsibility**

Validates task data and enforces business rules before tasks are created or updated.

**Examples of validation**

* Task ID must exist
* Task title must not be empty
* Title must be at least 3 characters

**Reason to Change**

Validation rules or business constraints change.

---

## 2.2 TaskRepository

**Location:** `components/repository.py`

**Responsibility**

Handles task persistence and retrieval.

**Implementations**

* `InMemoryTaskRepository` – stores tasks in memory
* `FileTaskRepository` – stores tasks in a JSON file

**Reason to Change**

Storage mechanisms or database systems change.

---

## 2.3 TaskSearch

**Location:** `components/search.py`

**Responsibility**

Provides task search and filtering capabilities.

**Supported operations**

* Search tasks by text
* Filter by task status
* Filter by assignee

**Reason to Change**

Search logic or filtering rules evolve.

---

## 2.4 TaskExporter

**Location:** `components/exporter.py`

**Responsibility**

Exports tasks to external formats.

**Supported formats**

* JSON (`JsonTaskExporter`)
* CSV (`CsvTaskExporter`)

**Reason to Change**

New export formats are introduced.

---

## 2.5 TaskNotifier

**Location:** `components/notifier.py`

**Responsibility**

Handles task reminder notifications.

**Implementations**

* `ConsoleTaskNotifier` – prints reminders to the console
* `SilentTaskNotifier` – disables notifications (useful for testing)

**Reason to Change**

Notification channels change (e.g., email, SMS, push notifications).

---

## 2.6 TaskManager (Orchestrator)

**Location:** `task_manager.py`

**Responsibility**

Coordinates the interaction between all components.

The `TaskManager`:

* Creates tasks
* Updates tasks
* Assigns tasks
* Filters and searches tasks
* Exports tasks
* Sends reminders

It does **not implement business logic itself**, but delegates tasks to the appropriate components.

**Reason to Change**

Task workflows or orchestration logic change.

---

# 3. Design Rationale

The system follows core modular design principles.

### Single Responsibility Principle (SRP)

Each component has exactly one responsibility:

| Component   | Responsibility                   |
| ----------- | -------------------------------- |
| Validator   | Validate task data               |
| Repository  | Store and retrieve tasks         |
| Search      | Query and filter tasks           |
| Exporter    | Export tasks to external formats |
| Notifier    | Send task reminders              |
| TaskManager | Coordinate system operations     |

---

### High Cohesion

Each component contains closely related functionality:

* Validation logic stays inside `validator.py`
* Storage logic stays inside `repository.py`

---

### Low Coupling

Components interact through **interfaces (Protocols)** such as:

* `ITaskRepository`
* `ITaskExporter`
* `ITaskNotifier`

This allows implementations to be replaced without modifying other modules.

---

### Dependency Injection

Dependencies are injected into `TaskManager`:

```
TaskManager(
    validator,
    repository,
    search,
    exporters,
    notifier
)
```

Benefits:

* Components are independently testable
* Implementations can be swapped easily
* Improves maintainability

---

# 4. Summary

The Task Management System is decomposed into modular components that follow software architecture best practices:

* Single Responsibility Principle
* High cohesion
* Low coupling
* Dependency injection

This design ensures the system is **maintainable, extensible, and testable**.
